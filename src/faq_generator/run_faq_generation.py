"""Orchestrates FAQ generation. Run from project root:
    python -m faq_generator.run_faq_generation chunked_data
    python -m faq_generator.run_faq_generation chunked_data --force
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import AuthenticationError, PermissionDeniedError
from tqdm import tqdm

from .client import build_client
from .generator import generate_faq_for_doc
from .prompt import load_prompt
from shared.utils import load_config, to_output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="File or directory under chunked_data/")
    parser.add_argument("--force", action="store_true", help="Overwrite existing FAQ outputs")
    args = parser.parse_args()

    load_dotenv()
    config = load_config()
    llm_cfg = config["llm"]["faq_generator"]
    questions_per_chunk = config["faq_generation"]["questions_per_chunk"]
    faq_dir = Path(config["paths"]["faq_dir"])
    prompts_dir = Path(config["paths"]["prompts_dir"])

    template = load_prompt(prompts_dir)
    client = build_client(llm_cfg["api_key_env"])

    in_path: Path = args.input
    if in_path.is_file():
        files = [in_path] if in_path.suffix.lower() == ".json" else []
    else:
        files = sorted(in_path.rglob("*.json"))

    if not files:
        print(f"No .json files found at {in_path}")
        return

    input_root = Path(in_path.parts[0])

    skipped = 0
    failed_docs: list[str] = []
    failed_chunks_total = 0
    for file in tqdm(files, desc="Generating FAQs", unit="file"):
        out_file = to_output_path(file, input_root, faq_dir)
        if out_file.exists() and not args.force:
            tqdm.write(f"  {file.name} -> SKIP (exists; use --force to overwrite)")
            skipped += 1
            continue

        tqdm.write(f"  {file.name} -> {out_file}")
        try:
            with file.open("r", encoding="utf-8") as f:
                chunked_doc = json.load(f)
            faq_doc, n_failed_chunks = generate_faq_for_doc(
                chunked_doc=chunked_doc,
                template=template,
                client=client,
                model=llm_cfg["model"],
                temperature=llm_cfg["temperature"],
                questions_per_chunk=questions_per_chunk,
            )
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(faq_doc, f, ensure_ascii=False, indent=2)
            failed_chunks_total += n_failed_chunks
            tqdm.write(f"    wrote {len(faq_doc['chunks'])} chunk(s); {n_failed_chunks} failed")
        except (AuthenticationError, PermissionDeniedError):
            # Configuration error — abort the whole run rather than logging it 72 times.
            raise
        except Exception as e:
            failed_docs.append(file.name)
            tqdm.write(f"    FAILED: {e}")

    processed = len(files) - skipped - len(failed_docs)
    print(
        f"\nDone. {processed} processed, {skipped} skipped, "
        f"{len(failed_docs)} doc(s) failed, {failed_chunks_total} chunk(s) failed."
    )
    if failed_docs:
        print(f"Failed docs: {', '.join(failed_docs)}")


if __name__ == "__main__":
    main()
