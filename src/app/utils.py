from pathlib import Path
import uuid


def write_file(file_path: str, data: str, encoding: str = "utf8") -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding=encoding)


def write_file_with_uuid(dir: str, content: str | bytes, suffix=".json", encoding="utf-8"):
    path = Path(dir)

    path.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}{suffix}"
    unique_path = path / unique_name

    if isinstance(content, str):
        unique_path.write_text(content, encoding)
    else:
        unique_path.write_bytes(content)

    return str(unique_path)
