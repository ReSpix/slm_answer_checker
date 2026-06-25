from pydantic import BaseModel, ConfigDict, Field


class Question(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str
    reference_answer: str
    key_concepts: tuple[str, ...]
    min_score: int | float
    max_score: int | float
    score_step: int | float


class Answer(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    answer_type: str
    language: str
    text: str
    min_score: int | float
    max_score: int | float
