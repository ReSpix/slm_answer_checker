from fastapi.routing import APIRouter

from app.schemas.api import QuestionCreate, QuestionRead
from app.database.models import Questions
from app.database.session import SessionDep
from app.database.queries import questions_list

questions_router = APIRouter(prefix="/questions")


@questions_router.post("/create")
async def create_question(question_create: QuestionCreate, db: SessionDep):
    question = Questions(**question_create.model_dump())
    db.add(question)
    await db.commit()


@questions_router.get("/list", response_model=list[QuestionRead])
async def create_question(db: SessionDep):
    questions = await questions_list(db)
    return questions