from fastapi.routing import APIRouter

from app.schemas.api import QuestionCreate, QuestionRead
from app.database.models import Questions
from app.database.session import SessionDep
from app.database.queries import get_all

questions_router = APIRouter(prefix="/questions")


@questions_router.post("/", response_model=QuestionRead)
async def create_question(question_create: QuestionCreate, db: SessionDep):
    question = Questions(**question_create.model_dump())
    db.add(question)
    await db.commit()
    return question


@questions_router.get("/", response_model=list[QuestionRead])
async def questions_list(db: SessionDep):
    questions = await get_all(db, Questions)
    return questions