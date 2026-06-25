from pydantic import BaseModel, ConfigDict, Field


class ConceptScore(BaseModel):
    id: int
    concept_name: str
    coverage: int = Field(ge=0, le=2, description="0=not covered or just named, 1=partial coverage, 2=fully covered")


class GradingResult(BaseModel):
    concepts: list[ConceptScore]
    feedback: str


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
