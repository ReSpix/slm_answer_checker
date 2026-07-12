import asyncio
import logging
from typing import Annotated

from fastapi import Depends

from app.database.session import get_session
from app.database.models import Questions
from app.rag import rag_generate


logger = logging.getLogger(__name__)


class ReferenceAnswersManager:
    def __init__(self):
        self._events: dict[int, asyncio.Event] = {}

    async def ensure_reference_ready(self, question_id: int) -> None:
        event = self._events.get(question_id)
        if event is None:
            event = asyncio.Event()
            self._events[question_id] = event
            asyncio.create_task(self._process(question_id, event))

        await event.wait()
        self._events.pop(question_id)

    async def _process(self, question_id: int, event: asyncio.Event):
        try:
            async with get_session() as session:
                question = await session.get(Questions, question_id)
                if question and question.reference_answer is not None:
                    return

            logger.info(f"Start generating reference answer for question(id={question_id})")
            answer = await rag_generate(question_id)
            logger.info(f"End generating reference answer for question(id={question_id})")

            async with get_session() as session:
                question = await session.get(Questions, question_id)
                if not question:
                    raise ValueError(f"No question with id={question_id} after rag_generate")
                
                question.reference_answer = answer
                await session.commit()

        finally:
            event.set()


reference_answers_manager = ReferenceAnswersManager()


def get_reference_answers_manager() -> ReferenceAnswersManager:
    return reference_answers_manager


RefAnsManagerDep = Annotated[
    ReferenceAnswersManager, Depends(get_reference_answers_manager)
]
