"""Sliding-window chunker over extracted page records."""

from .schema import Chunk

def _window_indices(n_pages: int, window_size: int, overlap: int) -> list[list[int]]:
    """Return list of 0-based page-index windows.

    Examples:
      n=5, window=2, overlap=1 -> [[0,1],[1,2],[2,3],[3,4]]
      n=1, window=2, overlap=1 -> [[0]]                 # single-page doc
      n=2, window=3, overlap=1 -> [[0,1]]               # doc shorter than window
    """
    if window_size < 1:
        raise ValueError("window_size must be >= 1")
    if overlap < 0 or overlap >= window_size:
        raise ValueError("overlap must be in [0, window_size)")

    if n_pages == 0:
        return []
    if n_pages <= window_size:
        return [list(range(n_pages))]

    step = window_size - overlap
    windows: list[list[int]] = []
    start = 0
    while start < n_pages:
        end = min(start + window_size, n_pages)
        windows.append(list(range(start, end)))
        if end == n_pages:
            break
        start += step
    return windows


def chunk_doc(pages: list[dict], doc_name: str, window_size: int, overlap: int,) -> list[Chunk]:
    """Build Chunks from a list of PageRecord-shaped dicts (as loaded from extractor JSON).

    Each chunk_text embeds page markers: '[Página N]\n<text>' joined by '\n\n'.
    """
    if not pages:
        return []

    # Sort defensively in case the JSON is not in page order.
    sorted_pages = sorted(pages, key=lambda p: p["page"])
    n = len(sorted_pages)

    chunks: list[Chunk] = []
    for idx, win in enumerate(_window_indices(n, window_size, overlap)):
        page_numbers = [sorted_pages[i]["page"] for i in win]
        parts = [f"[Página {sorted_pages[i]['page']}]\n{sorted_pages[i]['text']}" for i in win]
        chunks.append(
            Chunk(
                chunk_id=f"{doc_name}__c{idx}",
                pages=page_numbers,
                chunk_text="\n\n".join(parts),
            )
        )
    return chunks
