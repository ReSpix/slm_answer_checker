from pydantic import BaseModel, Field


class RagAnswer(BaseModel):
    success: bool = Field(description="Успешно ли найден и сгенерирован ответ")
    message: str = Field(description="Содержание ответа на вопрос")