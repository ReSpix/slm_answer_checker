from pathlib import Path

def write_file(file_path: str, data: str, encoding: str = 'utf8') -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding=encoding)