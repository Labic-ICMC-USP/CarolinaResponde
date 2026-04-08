import re

def _clean_text(text: str) -> str:
    """
    Clean extracted text from PDFs and DOCX files.
    """
    if not text:
        return ""

    # Normalize line endings and special whitespace characters
    text = text.replace("\r\n", "\n")
    text = text.replace("\xa0", " ")  # non-breaking space
    text = text.replace("\x00", " ")  # null bytes

    # Fix hyphenation across line breaks (e.g. "exam-\nple" or "exam- \nple" → "example")
    text = re.sub(r'(\w+)-\s*\n(\w+)', r'\1\2', text)

    # Replace single line breaks (line wrapping) with a space, preserve paragraph breaks
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    # Collapse multiple spaces and tabs
    text = re.sub(r'[ \t]+', ' ', text)

    # Normalize excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()