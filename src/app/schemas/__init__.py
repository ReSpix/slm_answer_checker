import ollama
from pydantic import BaseModel, Field

# Key concepts


class Concept(BaseModel):
    text: str
    importance: int = Field(..., ge=1, le=10)


class KeyConcepts(BaseModel):
    concepts: list[Concept]


# Grading


class ConceptScore(BaseModel):
    id: int
    concept_name: str
    coverage: int = Field(
        ge=0,
        le=2,
        description="0=not covered, 1=partial coverage, 2=fully covered",
    )


class GradingResult(BaseModel):
    concepts: list[ConceptScore]
    feedback: str
    manipulation: bool


# Test cases


class Question(BaseModel):
    """Вопрос"""

    domain: str = Field(..., description="Общая сфера вопроса")
    theme: str = Field(..., description="Конкретное направление вопроса")
    text: str = Field(..., description="Текст вопроса")
    reference_answer: str = Field(..., description="Эталонный ответ")


class Answer(BaseModel):
    """Ответ на вопрос"""

    answer_type: str = Field(
        ...,
        description="Общее качество ответа: отличный, хороший, недопонимание, итд",
    )
    text: str = Field(..., description="Текст ответа")
    quality: int = Field(
        ..., ge=0, le=100, description="Совпадение с эталонным ответом, в процентах"
    )


class TestCase(BaseModel):
    """Тестовый случай, содержащий вопрос и список ответов."""

    question: Question = Field(..., description="Вопрос")
    answers: list[Answer] = Field(..., description="Список ответов")


# Evaluation


class ModelEvaluation(BaseModel):
    case_uuid: str
    model: str
    temperature: float
    question: Question
    key_concepts: KeyConcepts
    answer: Answer
    grading_results: GradingResult
    eval_duration: int | None
    eval_count: int | None
