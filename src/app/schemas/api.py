from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    text: str
    reference_answer: str | None = None


class QuestionRead(BaseModel):
    model_config = {"from_attributes": True}

    text: str
    reference_answer: str | None = None
