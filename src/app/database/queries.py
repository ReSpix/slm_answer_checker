from typing import TypeVar, Any

from sqlalchemy import select
from app.schemas.api import QuestionDocumentLink
from app.database.models import QuestionDocumentLinks
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


async def get_all(session: AsyncSession, cls: T, *options: Any) -> list[T]:
    query = select(cls).options(*options)
    result = await session.execute(query)
    return result.scalars().all()


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
