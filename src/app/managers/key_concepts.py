import asyncio
from typing import Annotated

from fastapi import Depends

from app.database.session import get_session
from app.database.models import Questions, KeyConcepts
from app.concepts_extraction import key_concepts_generate


class KeyConceptsManager:
    def __init__(self):
        self._events: dict[int, asyncio.Event] = {}

    async def ensure_key_concepts_ready(self, question_id: int) -> None:
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
                if question and len(question.key_concepts) > 0:
                    return

            concepts = await key_concepts_generate(question_id)

            async with get_session() as session:
                concepts = [
                    KeyConcepts(
                        text=concept.text,
                        importance=concept.importance,
                        question_id=question_id,
                    )
                    for concept in concepts
                ]
                session.add_all(concepts)
                await session.commit()

        finally:
            event.set()


key_concepts_manager = KeyConceptsManager()


def get_reference_answers_manager() -> KeyConceptsManager:
    return key_concepts_manager


KeyConcManagerDep = Annotated[
    KeyConceptsManager, Depends(get_reference_answers_manager)
]
