"""PDF extraction using Docling."""

from pathlib import Path
from typing import Iterator, Optional

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    PdfPipelineOptions,
    TableFormerMode,
    TableStructureOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

from .schema import PageRecord


def pdf_format_option() -> dict:
    pipeline_options = PdfPipelineOptions(
        do_ocr=True,
        do_table_structure=True,
        ocr_options=EasyOcrOptions(lang=["pt", "en"]),
        table_structure_options=TableStructureOptions(
            mode=TableFormerMode.ACCURATE,
            do_cell_matching=True,
        ),
    )
    return {
        # pypdfium backend: docling-parse (default) crashes with std::bad_alloc on dense PDFs
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
            backend=PyPdfiumDocumentBackend,
        ),
    }


def extract_pdf(path: Path, converter: Optional[DocumentConverter] = None) -> Iterator[PageRecord]:
    if converter is None:
        converter = DocumentConverter(format_options=pdf_format_option())
    result = converter.convert(str(path))
    doc = result.document

    pages = getattr(doc, "pages", None) or {}

    if not pages:
        yield PageRecord(
            doc_name=path.stem,
            source_path=str(path),
            page=1,
            page_count=1,
            text=doc.export_to_markdown(),
        )
        return

    page_numbers = sorted(pages.keys())
    page_count = len(page_numbers)

    for page_no in page_numbers:
        yield PageRecord(
            doc_name=path.stem,
            source_path=str(path),
            page=page_no,
            page_count=page_count,
            text=doc.export_to_markdown(page_no=page_no),
        )
