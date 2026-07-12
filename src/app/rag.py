import logging

from langchain_chroma import Chroma
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_classic.output_parsers import PydanticOutputParser
from langchain_classic.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import CHROMA_COLLECTION_NAME, chromadb_dir, documents_dir, OLLAMA_URL
from app.database.models import Documents, Questions
from app.database.queries import get_qd_links_for_question
from app.database.session import get_session
from app.init_objects import get_embedding_model, get_vectorstore
from app.schemas.rag import RagAnswer

logger = logging.getLogger(__name__)


async def rag_generate(question_id: int):
    async with get_session() as session:
        question = await session.get(Questions, question_id)

        if not question or question.reference_answer is not None:
            raise ValueError(
                f"Question with id={question_id} already have reference answer"
            )

        qd_links = await get_qd_links_for_question(session, question_id)
        document_ids = [link.document_id for link in qd_links]

    vectorstore = get_vectorstore()

    filter_condition = {"document_id": {"$in": document_ids}}

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4, "filter": filter_condition}
    )
    llm = ChatOllama(model="qwen3:8b", base_url=OLLAMA_URL)

    parser = PydanticOutputParser(pydantic_object=RagAnswer)

    prompt_template = """
    Ты — ассистент, отвечающий на вопросы по документу. 
    Используй следующий контекст для ответа. Если контекст не содержит информации, 
    сообщи об этом в поле message и установи success = false.

    Контекст:
    {context}

    Вопрос: {question}

    Ответь в формате JSON.
    {format_instructions}
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    raw_output = await qa_chain.ainvoke(question.text)
    parsed = parser.parse(raw_output["result"])

    if parsed.success:
        return parsed.message

    logger.warning(
        "Unable to generate reference answer. Language model cannot find information in context"
    )
    return ""


async def store_to_chroma(document_id: int):
    async with get_session() as db_session:
        document = await db_session.get(Documents, document_id)

    if not document:
        raise ValueError("Wrong document id")

    logging.info(
        f"Start vectorizing document: {document.stored_filename}({document.original_filename})"
    )
    document_path = documents_dir / document.stored_filename

    loader = PyMuPDF4LLMLoader(document_path)
    documents = await loader.aload()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    for chunk in chunks:
        chunk.metadata["document_id"] = document_id

    embeddings = get_embedding_model()

    vectorstore = get_vectorstore()
    vectorstore.add_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=chromadb_dir,
    )
    async with get_session() as db_session:
        document = await db_session.get(Documents, document_id)
        document.vectorized = True
        await db_session.commit()

    logging.info(
        f"End vectorizing document: {document.stored_filename}({document.original_filename})"
    )
