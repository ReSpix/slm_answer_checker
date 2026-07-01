import ollama
import json
from app.schemas import GradingResult, ConceptScore

from pydantic import Field, create_model


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
