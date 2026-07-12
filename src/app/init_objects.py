from langchain_huggingface import HuggingFaceEmbeddings

from langchain_chroma import Chroma

from app.config import CHROMA_COLLECTION_NAME, chromadb_dir
import logging

logger = logging.getLogger(__name__)

embedding = None


def init_embedding_model():
    global embedding
    logger.info("Start init embedding model")
    embedding = HuggingFaceEmbeddings(model_name="cointegrated/rubert-tiny2")
    logger.info("End init embedding model")


def get_embedding_model():
    if embedding is None:
        init_embedding_model()

    return embedding


vectorstore = None


def init_vectorstore():
    global vectorstore
    logger.info("Start init vectorstore")
    vectorstore = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=chromadb_dir,
        embedding_function=get_embedding_model(),
    )
    logger.info("End init vectorstore")


def get_vectorstore():
    if vectorstore is None:
        init_vectorstore()

    return vectorstore
