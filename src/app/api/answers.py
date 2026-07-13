import asyncio

from fastapi.routing import APIRouter

from app.database.models import Answers
from app.database.queries import get_all, get_all_gradings_for_answer
from app.database.session import SessionDep
from app.grading import grading_generate
from app.schemas.api import AnswerCreate, AnswerRead, ConceptScoreRead, GradingRead

answers_router = APIRouter(prefix="/answers")


@answers_router.post("/", response_model=AnswerRead)
async def create_answer(answer_create: AnswerCreate, db: SessionDep):
    answer = Answers(**answer_create.model_dump())
    db.add(answer)
    await db.commit()
    asyncio.create_task(grading_generate(answer.id))
    return answer


@answers_router.get("/", response_model=list[AnswerRead])
async def answers_list(db: SessionDep):
    answers = await get_all(db, Answers)
    return answers


@answers_router.get("/{answer_id}/gradings", response_model=list[GradingRead])
async def grading_result_for_answer(answer_id: int, db_session: SessionDep):
    gradings = await get_all_gradings_for_answer(db_session, answer_id)

    output = [
        GradingRead(
            id=grading.id,
            answer_id=answer_id,
            concept_scores=[
                ConceptScoreRead(
                    concept_id=cs.concept.id,
                    concept_text=cs.concept.text,
                    concept_importance=cs.concept.importance,
                    coverage=cs.score,
                )
                for cs in grading.concept_scores
            ],
            cosine_similarity=grading.cosine_similarity,
        )
        for grading in gradings
    ]
    return output
