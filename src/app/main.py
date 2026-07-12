from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database.models import Base
from app.database.session import engine
from app.api.questions import questions_router
from app.api.rag import rag_router
from app.init_objects import init_embedding_model, init_vectorstore
from app.managers.reference_answers import get_reference_answers_manager

import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Database init start")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database init done")

    init_embedding_model()
    init_vectorstore()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(questions_router)
app.include_router(rag_router)

@app.get("/health")
async def healthcheck():
    return "ok"
