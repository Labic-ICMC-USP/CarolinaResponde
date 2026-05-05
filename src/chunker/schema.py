from dataclasses import dataclass

@dataclass
class Chunk:
    chunk_id: str
    pages: list[int]
    chunk_text: str
