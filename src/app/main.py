import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.questions import questions_router
from app.api.rag import rag_router
from app.database.models import Base
from app.database.session import engine
from app.init_objects import init_embedding_model, init_vectorstore
from app.config import SKIP_EMBEDDING_INIT_ON_STARTUP

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Database init start")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database init done")

    if not SKIP_EMBEDDING_INIT_ON_STARTUP:
        init_embedding_model()
        init_vectorstore()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(questions_router)
app.include_router(rag_router)


@app.get("/health")
async def healthcheck():
    return "ok"
