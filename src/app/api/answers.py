from fastapi.routing import APIRouter

from app.schemas.api import AnswerCreate, AnswerRead
from app.database.models import Answers
from app.database.session import SessionDep
from app.database.queries import get_all

answers_router = APIRouter(prefix="/answers")


@answers_router.post("/", response_model=AnswerRead)
async def create_answer(answer_create: AnswerCreate, db: SessionDep):
    question = Answers(**answer_create.model_dump())
    db.add(question)
    await db.commit()
    return question


@answers_router.get("/", response_model=list[AnswerRead])
async def answers_list(db: SessionDep):
    answers = await get_all(db, Answers)
    return answers
