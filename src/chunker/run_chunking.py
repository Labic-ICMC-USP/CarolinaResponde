"""Orchestrates chunking. Run from project root: python -m chunker.run_chunking extracted_data"""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from tqdm import tqdm

from .chunker import chunk_doc
from shared.utils import load_config, to_output_path


def process_file(in_path: Path, out_path: Path, window_size: int, overlap: int) -> int:
    """Read an extractor JSON, build chunks, and write {doc_name, source_path, chunks}.
    Returns the number of chunks written (0 if the input has no pages).
    """
    with in_path.open("r", encoding="utf-8") as f:
        pages = json.load(f)

    if not pages:
        return 0

    doc_name = pages[0].get("doc_name") or in_path.stem
    source_path = pages[0].get("source_path", "")
    chunks = chunk_doc(pages, doc_name, window_size, overlap)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "doc_name": doc_name,
        "source_path": source_path,
        "chunks": [asdict(c) for c in chunks],
    }
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="File or directory under extracted_data/")
    args = parser.parse_args()

    config = load_config()
    window_size = config["chunking"]["window_size"]
    overlap = config["chunking"]["overlap"]
    chunked_dir = Path(config["paths"]["chunked_dir"])

    in_path: Path = args.input
    if in_path.is_file():
        files = [in_path] if in_path.suffix.lower() == ".json" else []
    else:
        files = sorted(in_path.rglob("*.json"))

    if not files:
        print(f"No .json files found at {in_path}")
        return

    input_root = Path(in_path.parts[0])

    failed: list[str] = []
    total_chunks = 0
    for file in tqdm(files, desc="Chunking", unit="file"):
        out_file = to_output_path(file, input_root, chunked_dir)
        tqdm.write(f"  {file.name} -> {out_file}")
        try:
            n = process_file(file, out_file, window_size, overlap)
            total_chunks += n
            tqdm.write(f"    wrote {n} chunk(s)")
        except Exception as e:
            failed.append(file.name)
            tqdm.write(f"    FAILED: {e}")

    print(f"\nDone. {len(files) - len(failed)} file(s), {total_chunks} chunk(s).")
    if failed:
        print(f"{len(failed)} file(s) failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
