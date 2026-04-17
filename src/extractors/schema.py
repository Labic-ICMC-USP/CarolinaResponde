from dataclasses import dataclass

@dataclass
class PageRecord:
    doc_name: str
    source_path: str
    page: int
    page_count: int
    text: str
