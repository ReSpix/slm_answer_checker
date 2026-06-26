from pydantic import BaseModel, ConfigDict, Field


class ConceptScore(BaseModel):
    id: int
    concept_name: str
    coverage: int = Field(
        ge=0, le=2, description="0=not covered, 1=partial coverage, 2=fully covered"
    )


class GradingResult(BaseModel):
    concepts: list[ConceptScore]
    feedback: str
    manipulation: bool


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


class Concept(BaseModel):
    text: str
    importance: int = Field(..., ge=1, le=10)


class KeyConcepts(BaseModel):
    concepts: list[Concept]
