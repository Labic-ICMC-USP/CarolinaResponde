"""Iterate chunks of a single doc, call OpenRouter, build the enriched output dict."""

from dataclasses import asdict
from typing import Any

from openai import OpenAI
from tqdm import tqdm

from .client import generate_qa_pairs
from .prompt import format_prompt


def generate_faq_for_doc(chunked_doc: dict, template: str, client: OpenAI, model: str, temperature: float, questions_per_chunk: int) -> tuple[dict, int]:
    """Return (faq_doc, failed_chunk_count)."""
    chunks_with_qa: list[dict[str, Any]] = []
    failed = 0

    for chunk in tqdm(chunked_doc.get("chunks", []), desc="  chunks", unit="chunk", leave=False):
        prompt = format_prompt(template, chunk["chunk_text"], questions_per_chunk)
        try:
            qa_pairs = generate_qa_pairs(
                client=client,
                model=model,
                temperature=temperature,
                prompt=prompt,
                allowed_pages=chunk["pages"],
            )
        except Exception as e:
            tqdm.write(f"    chunk {chunk.get('chunk_id')} FAILED: {e}")
            qa_pairs = []

        if not qa_pairs:
            failed += 1

        chunks_with_qa.append({
            **chunk,
            "qa_pairs": [asdict(p) for p in qa_pairs],
        })

    return (
        {
            "doc_name": chunked_doc.get("doc_name", ""),
            "source_path": chunked_doc.get("source_path", ""),
            "chunks": chunks_with_qa,
        },
        failed,
    )
