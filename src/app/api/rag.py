import asyncio

from fastapi import File, UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.exc import IntegrityError
from app.database.session import SessionDep
from app.database.models import Documents, QuestionDocumentLinks
from app.utils import write_file_with_uuid
from app.config import documents_dir
from app.schemas.api import BasicResponse, DocumentRead, QuestionDocumentLink
from app.database.queries import get_all, get_qd_link
from app.rag import store_to_chroma

documents_router = APIRouter(prefix="/documents")
qd_links_router = APIRouter(prefix="/question-document-links")

rag_router = APIRouter(prefix="/rag")
rag_router.include_router(documents_router)
rag_router.include_router(qd_links_router)


@documents_router.post("/", response_model=DocumentRead)
async def create_document(db_session: SessionDep, file: UploadFile = File(...)):
    file_bytes = await file.read()

    uuid_filename = write_file_with_uuid(
        documents_dir, file_bytes, suffix="." + file.filename.split(".")[-1]
    )
    document = Documents(original_filename=file.filename, stored_filename=uuid_filename)
    db_session.add(document)
    await db_session.commit()
    asyncio.to_thread(store_to_chroma(document.id))

    return DocumentRead(id=document.id, name=document.original_filename)


@documents_router.get("/", response_model=list[DocumentRead])
async def documents_list(db_session: SessionDep):
    documents = await get_all(db_session, Documents)
    return [DocumentRead(id=doc.id, name=doc.original_filename) for doc in documents]


@qd_links_router.put("/", response_model=BasicResponse)
async def qd_link_create(
    db_session: SessionDep, question_document_link: QuestionDocumentLink
):
    link = QuestionDocumentLinks(**question_document_link.model_dump())
    db_session.add(link)
    try:
        await db_session.commit()
        return BasicResponse(success=True)
    
    except IntegrityError:
        await db_session.rollback()
        return BasicResponse(success=True)


@qd_links_router.get("/", response_model=list[QuestionDocumentLink])
async def qd_links_list(db: SessionDep):
    links = await get_all(db, QuestionDocumentLinks)
    return links


@qd_links_router.delete(
    "/{question_id}/{document_id}", response_model=BasicResponse
)
async def qd_link_delete(db_session: SessionDep, question_id: int, document_id: int):
    link = await get_qd_link(
        db_session,
        QuestionDocumentLink(question_id=question_id, document_id=document_id),
    )
    if not link:
        return BasicResponse(success=False)

    await db_session.delete(link)
    await db_session.commit()

    return BasicResponse(success=True)
