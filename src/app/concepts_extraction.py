import ollama
from typing_extensions import deprecated
import json
from app.database.models import Questions
from app.database.session import get_session
from app.prompts import get_template
from app.schemas import Concept, KeyConcepts
from app.config import KEY_CONCEPTS_MODEL_CONFIG, OLLAMA_URL

ollama_aclient = ollama.AsyncClient(host=OLLAMA_URL)


@deprecated("Use async version instead - aextract_key_concepts")
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


async def aextract_key_concepts(
    model: str, temperature: float, system_prompt: str, user_prompt: str
) -> tuple[KeyConcepts, ollama.GenerateResponse]:
    response = await ollama_aclient.generate(
        model=model,
        system=system_prompt,
        prompt=user_prompt,
        format=KeyConcepts.model_json_schema(),
        options={"temperature": temperature},
    )

    if not response.response:
        raise ollama.ResponseError("Response is None")

    return KeyConcepts.model_validate(json.loads(response.response)), response


async def key_concepts_generate(question_id: int) -> list[Concept]:
    async with get_session() as session:
        question = await session.get(Questions, question_id)

    system_template = get_template("concepts_extraction/system")
    user_template = get_template("concepts_extraction/user")

    model_name = KEY_CONCEPTS_MODEL_CONFIG["name"]
    temperature = KEY_CONCEPTS_MODEL_CONFIG["temperature"]
    key_concepts, _ = await aextract_key_concepts(
        model_name,
        temperature,
        system_template.render(),
        user_template.render({"question": question}),
    )

    return key_concepts.concepts
