from pydantic import BaseModel, Field, computed_field
from app.schemas import Concept
from annotated_types import Le


class BasicResponse(BaseModel):
    success: bool


class QuestionCreate(BaseModel):
    text: str
    reference_answer: str | None = None


class QuestionRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    text: str
    reference_answer: str | None = None
    key_concepts: list[Concept]


class DocumentRead(BaseModel):
    id: int
    name: str


class QuestionDocumentLink(BaseModel):
    question_id: int
    document_id: int


class AnswerCreate(BaseModel):
    text: str
    question_id: int


class AnswerRead(BaseModel):
    id: int
    text: str
    question_id: int


class ConceptScoreRead(BaseModel):
    concept_id: int
    concept_text: str
    concept_importance: int
    coverage: int = Field(ge=0, le=2)

    @classmethod
    def max_coverage(cls) -> int:
        coverage_field = cls.model_fields["coverage"]
        for meta in coverage_field.metadata:
            if isinstance(meta, Le):
                assert isinstance(meta.le, int)
                return meta.le
        raise ValueError(
            "ConceptScoreRead.coverage must have 'le' constraint of type int"
        )


class GradingRead(BaseModel):
    id: int
    answer_id: int
    concept_scores: list[ConceptScoreRead]
    cosine_similarity: float

    @computed_field
    @property
    def score(self) -> float:
        return calulate_grading_score(self)


def calulate_grading_score(grading: GradingRead):
    concept_scores_sum = sum(
        concept_score.coverage * concept_score.concept_importance
        for concept_score in grading.concept_scores
    )

    max_possible_coverage = ConceptScoreRead.max_coverage()

    max_possible_concept_scores_sum = sum(
        concept_score.concept_importance * max_possible_coverage
        for concept_score in grading.concept_scores
    )

    slm_score = 0

    if max_possible_concept_scores_sum > 0:
        slm_score = concept_scores_sum / max_possible_concept_scores_sum

    final_score = (
        slm_score * 0.35701152
        + grading.cosine_similarity * 1.35633295
        - 0.6094303957566415
    )

    return final_score
