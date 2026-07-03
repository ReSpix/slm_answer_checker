import json
from pathlib import Path
from app.schemas import TestCase
from pydantic import ValidationError
from logging import getLogger

logger = getLogger(__name__)


class DataLoader:
    def __init__(self, path: str | Path, encoding: str = "utf8"):
        if isinstance(path, str):
            path = Path(path)

        self.test_cases: dict[str, TestCase] = {}

        for file in path.iterdir():
            if file.is_dir():
                continue

            data = file.read_text(encoding)

            try:
                test_case = TestCase.model_validate(json.loads(data))
                self.test_cases[file.stem] = test_case
            except ValidationError as e:
                logger.warning(f"Cannot validate {str(file)}: {e}")
