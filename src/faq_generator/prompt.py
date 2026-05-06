"""Load and format the FAQ generation prompt template."""

from pathlib import Path


def load_prompt(prompts_dir: Path) -> str:
    """Read prompts/faq_generation.txt verbatim."""
    path = Path(prompts_dir) / "faq_generation.txt"
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def format_prompt(template: str, chunk_text: str, k: int) -> str:
    """Substitute {k} and {chunk_text} into the template.
    """
    return template.replace("{k}", str(k)).replace("{chunk_text}", chunk_text)
