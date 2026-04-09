from pathlib import Path

from .docx import extract_docx
from .pdf import extract_pdf


def extract_file(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(path)
    elif suffix == ".docx":
        return extract_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
