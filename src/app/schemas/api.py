from pydantic import BaseModel, Field


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

class DocumentRead(BaseModel):
    id: int
    name: str


class QuestionDocumentLink(BaseModel):
    question_id: int
    document_id: int