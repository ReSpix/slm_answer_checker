from sqlalchemy import select

from app.database.models import Questions
from sqlalchemy.ext.asyncio import AsyncSession


async def questions_list(session: AsyncSession) -> list[Questions]:
    query = select(Questions)
    result = await session.execute(query)

    return result.scalars().all()