from dataclasses import dataclass, field

@dataclass
class QAPair:
    question: str
    answer: str
    source_page: int

@dataclass
class ChunkWithFAQs:
    chunk_id: str
    pages: list[int]
    chunk_text: str
    qa_pairs: list[QAPair] = field(default_factory=list)
