import json
from pathlib import Path
from src.models import Question, Answer


class DataLoader:
    def __init__(self, path: str | Path, encoding: str = "utf8"):
        if isinstance(path, str):
            path = Path(path)

        question_file = path / "question.json"
        if not question_file.exists():
            raise FileNotFoundError(f"{str(question_file)} does not exists")

        answers_file = path / "answers.json"
        if not answers_file.exists():
            raise FileNotFoundError(f"{str(answers_file)} does not exists")

        question_text = question_file.read_text(encoding)
        answers_text = answers_file.read_text(encoding)

        question_text = question_file.read_text(encoding)
        question_data = json.loads(question_text)
        self.question = Question.model_validate(question_data)

        answers_text = answers_file.read_text(encoding)
        answers_data = json.loads(answers_text)
        self.answers = [Answer.model_validate(answer) for answer in answers_data]
