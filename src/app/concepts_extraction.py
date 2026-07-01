import ollama
import json
from app.schemas import KeyConcepts


def extract_key_concepts(
    model: str, temperature: float, system_prompt: str, user_prompt: str
) -> tuple[KeyConcepts, ollama.GenerateResponse]:
    response = ollama.generate(
        model=model,
        system=system_prompt,
        prompt=user_prompt,
        format=KeyConcepts.model_json_schema(),
        options={"temperature": temperature},
    )

    if not response.response:
        raise ollama.ResponseError("Response is None")

    return KeyConcepts.model_validate(json.loads(response.response)), response
