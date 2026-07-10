from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database.models import Base
from app.database.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def healthcheck():
    return "ok"
