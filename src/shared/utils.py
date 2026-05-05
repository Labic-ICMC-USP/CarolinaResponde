"""Shared utilities used across pipeline stages."""

import yaml
from pathlib import Path

def load_config(path: Path = Path("config.yaml")) -> dict:
    """Load the project YAML config from the given path."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def to_output_path(source: Path, input_dir: Path, output_dir: Path) -> Path:
    """Mirror the source path structure under output_dir.
    Example: source=data/PPC/file.pdf, input_dir=data/
          -> output_dir/PPC/file.pdf
    """
    relative = source.relative_to(input_dir)
    return output_dir / relative
