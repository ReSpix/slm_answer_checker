import asyncio
import json
import logging
from typing_extensions import deprecated

import ollama
from pydantic import Field, create_model

from app.config import GRADING_MODEL_CONFIG, OLLAMA_URL
from app.database.models import ConceptScores, Gradings
from app.database.session import get_session
from app.database.queries import get_full_answer_data
from app.prompts import get_template
from app.schemas import ConceptScore, GradingResult
from app.managers.reference_answers import get_reference_answers_manager
from app.managers.key_concepts import get_key_concepts_manager

from .cosine_similarity import get_cosine_similarity

logger = logging.getLogger(__name__)
ollama_aclient = ollama.AsyncClient(host=OLLAMA_URL)


def make_grading_result_class(concept_count: int):
    return create_model(
        "GradingResult",
        concepts=(
            list[ConceptScore],
            Field(..., min_length=concept_count, max_length=concept_count),
        ),
        feedback=(str, ...),
        manipulation=(bool, ...),
    )


@deprecated("Use async version instead - agrade_answer")
def grade_answer(
    model: str,
    temperature: float,
    system_prompt: str,
    user_prompt: str,
    concepts_len: int,
) -> tuple[GradingResult, ollama.GenerateResponse]:
    response = ollama.generate(
        model=model,
        system=system_prompt,
        prompt=user_prompt,
        format=make_grading_result_class(concepts_len).model_json_schema(),
        options={"temperature": temperature},
    )

    if not response.response:
        raise ollama.ResponseError("Response is None")

    return GradingResult.model_validate(json.loads(response.response)), response


async def agrade_answer(
    model: str,
    temperature: float,
    system_prompt: str,
    user_prompt: str,
    concepts_len: int,
) -> tuple[GradingResult, ollama.GenerateResponse]:
    response = await ollama_aclient.generate(
        model=model,
        system=system_prompt,
        prompt=user_prompt,
        format=make_grading_result_class(concepts_len).model_json_schema(),
        options={"temperature": temperature},
    )

    if not response.response:
        raise ollama.ResponseError("Response is None")

    return GradingResult.model_validate(json.loads(response.response)), response


async def grading_generate(answer_id: int):
    async with get_session() as session:
        answer = await get_full_answer_data(session, answer_id)
        if not answer:
            raise ValueError("Wrong answer id")

        question = answer.question

    await get_reference_answers_manager().ensure_reference_ready(question.id)
    await get_key_concepts_manager().ensure_key_concepts_ready(question.id)

    async with get_session() as session:
        answer = await get_full_answer_data(session, answer_id)
        if not answer:
            raise ValueError("Wrong answer id")

        question = answer.question
        key_concepts = question.key_concepts

    system_grading_template = get_template("grading/system")

    system_prompt = system_grading_template.render(
        {
            "question": question,
            "key_concepts": key_concepts,
        }
    )

    if len(key_concepts) == 0:
        raise ValueError(f"Key concepts are empty for question(id={question.id})")

    model_name = GRADING_MODEL_CONFIG["name"]
    temperature = GRADING_MODEL_CONFIG["temperature"]

    async def perform_grading_result():
        logger.info(f"Start generating grading result for answer(id={answer_id})")
        grading_result, _ = await agrade_answer(
            model_name,
            temperature,
            system_prompt,
            answer.text,
            len(key_concepts),
        )
        logger.info(f"End generating grading result for answer(id={answer_id})")
        return grading_result

    async def perform_cosine_similarity():
        logger.info(f"Start calculating cosine similarity for answer(id={answer_id})")
        cos_sim = await get_cosine_similarity(question.reference_answer, answer.text)
        logger.info(f"End calculating cosine similarity for answer(id={answer_id})")
        return cos_sim

    grading_result, cos_sim = await asyncio.gather(
        perform_grading_result(),
        perform_cosine_similarity(),
    )

    async with get_session() as session:
        grading = Gradings(
            answer_id=answer.id,
            cosine_similarity=cos_sim,
            feedback=grading_result.feedback,
        )
        session.add(grading)
        await session.flush()

        concept_scores = [
            ConceptScores(
                grading_id=grading.id,
                concept_id=key_concepts[concept.id - 1].id,
                score=concept.coverage,
            )
            for concept in grading_result.concepts
        ]
        session.add_all(concept_scores)
        await session.commit()
