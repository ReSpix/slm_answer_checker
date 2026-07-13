from typing import TypeVar, Any

from sqlalchemy import select
from app.schemas.api import QuestionDocumentLink
from app.database.models import (
    Answers,
    ConceptScores,
    Gradings,
    QuestionDocumentLinks,
    Questions,
)
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import DeclarativeBase, selectinload

T = TypeVar("T", bound=DeclarativeBase)


async def get_all(session: AsyncSession, cls: type[T], *options: Any) -> list[T]:
    query = select(cls).options(*options)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_qd_link(session: AsyncSession, link: QuestionDocumentLink):
    query = select(QuestionDocumentLinks).where(
        QuestionDocumentLinks.document_id == link.document_id,
        QuestionDocumentLinks.question_id == link.question_id,
    )
    result = await session.execute(query)
    return result.scalar()


async def get_qd_links_for_question(session: AsyncSession, question_id: int):
    query = select(QuestionDocumentLinks).where(
        QuestionDocumentLinks.question_id == question_id
    )
    result = await session.execute(query)

    return result.scalars().all()


async def get_full_answer_data(session: AsyncSession, answer_id: int) -> Answers | None:
    stmt = (
        select(Answers)
        .where(Answers.id == answer_id)
        .options(selectinload(Answers.question).selectinload(Questions.key_concepts))
    )
    result = await session.execute(stmt)
    answer = result.scalar()

    return answer


async def get_all_gradings_for_answer(session: AsyncSession, answer_id: int):
    query = (
        select(Gradings)
        .where(Gradings.answer_id == answer_id)
        .options(
            selectinload(Gradings.concept_scores).selectinload(ConceptScores.concept)
        )
    )
    result = await session.execute(query)

    return result.scalars().all()
