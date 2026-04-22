"""DOCX extraction: convert to PDF via pandoc, then extract with the PDF pipeline."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterator, Optional

from docling.document_converter import DocumentConverter

from .pdf import extract_pdf, pdf_format_option
from .schema import PageRecord


def _check_pandoc() -> None:
    if shutil.which("pandoc") is None:
        raise RuntimeError(
            "pandoc not found. Install it from https://pandoc.org/installing.html"
        )


def extract_docx(path: Path, converter: Optional[DocumentConverter] = None) -> Iterator[PageRecord]:
    _check_pandoc()

    if converter is None:
        converter = DocumentConverter(format_options=pdf_format_option())

    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / f"{path.stem}.pdf"
        subprocess.run(
            ["pandoc", str(path), "-o", str(pdf_path), "--pdf-engine=lualatex"],
            check=True,
            capture_output=True,
        )

        for record in extract_pdf(pdf_path, converter):
            record.source_path = str(path)
            yield record
