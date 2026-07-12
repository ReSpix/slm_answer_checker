from pydantic import BaseModel
from app.schemas import Concept


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
