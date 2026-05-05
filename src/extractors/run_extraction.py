"""Orchestrates document extraction. Run from project root: python -m extractors.run_extraction"""

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from tqdm import tqdm
from docling.document_converter import DocumentConverter

from .schema import PageRecord
from .pdf import extract_pdf, pdf_format_option
from .docx import extract_docx
from shared.utils import to_output_path

# Maps file extensions to their extraction functions; add new formats here
EXTRACTORS = {
    ".pdf": extract_pdf,
    ".docx": extract_docx,
}


def build_converter() -> DocumentConverter:
    return DocumentConverter(format_options=pdf_format_option())


def write_json(records: Iterable[PageRecord], out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(r) for r in tqdm(records, desc="  pages", unit="pg", leave=False)]
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="File or directory to extract")
    args = parser.parse_args()

    in_path: Path = args.input
    supported = set(EXTRACTORS.keys())

    # Single file or recursive directory scan, filtering by supported extensions
    if in_path.is_file():
        files = [in_path] if in_path.suffix.lower() in supported else []
    else:
        files = sorted(f for f in in_path.rglob("*") if f.suffix.lower() in supported)

    if not files:
        print(f"No supported files found at {in_path} (supported: {', '.join(supported)})")
        return

    # First path component (e.g. "data") is stripped so extracted_data/ mirrors its structure
    input_root = Path(in_path.parts[0])
    extracted_dir = Path("extracted_data")

    print(f"Found {len(files)} file(s). Loading Docling pipeline...")
    converter = build_converter()

    failed = []
    for file in tqdm(files, desc="Extracting", unit="file"):
        extractor = EXTRACTORS[file.suffix.lower()]
        out_file = to_output_path(file, input_root, extracted_dir).with_suffix(".json")
        tqdm.write(f"  {file.name} -> {out_file}")
        try:
            n = write_json(extractor(file, converter), out_file)
            tqdm.write(f"    wrote {n} page record(s)")
        except Exception as e:
            failed.append(file.name)
            tqdm.write(f"    FAILED: {e}")

    if failed:
        print(f"\n{len(failed)} file(s) failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
