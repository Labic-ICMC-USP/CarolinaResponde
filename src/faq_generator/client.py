"""OpenRouter API client for FAQ generation."""

import json
import os
from typing import Optional

from openai import OpenAI
from openai import AuthenticationError, PermissionDeniedError

from .schema import QAPair


def build_client(api_key_env: str) -> OpenAI:
    """Build an OpenAI SDK client pointed at OpenRouter."""
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError(f"Environment variable {api_key_env} is not set")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def _validate_pair(raw: dict, allowed_pages: set[int]) -> Optional[QAPair]:
    """Return a QAPair if raw is a well-shaped dict with non-empty `question` and
    `answer` strings and `source_page` an integer in `allowed_pages`; else None.
    """
    if not isinstance(raw, dict):
        return None
    q = raw.get("question")
    a = raw.get("answer")
    sp = raw.get("source_page")
    if not isinstance(q, str) or not q.strip():
        return None
    if not isinstance(a, str) or not a.strip():
        return None
    if isinstance(sp, bool) or not isinstance(sp, int) or sp not in allowed_pages:
        return None
    return QAPair(question=q.strip(), answer=a.strip(), source_page=sp)


def generate_qa_pairs(client: OpenAI, model: str, temperature: float, prompt: str, allowed_pages: list[int],) -> list[QAPair]:
    """Single sequential call to OpenRouter. Returns [] on any failure."""
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content or ""
        raw_list = json.loads(content)
    except (AuthenticationError, PermissionDeniedError):
        # Configuration errors — abort the run, do not silently produce empty FAQs.
        raise
    except Exception as e:
        print(f"    [client] generation failed: {e}")
        return []

    if not isinstance(raw_list, list):
        print("    [client] response was not a JSON array; skipping")
        return []

    page_set = set(allowed_pages)
    pairs: list[QAPair] = []
    dropped = 0
    for raw in raw_list:
        pair = _validate_pair(raw, page_set)
        if pair is None:
            dropped += 1
            continue
        pairs.append(pair)
    if dropped:
        print(f"    [client] dropped {dropped} invalid pair(s)")
    return pairs
