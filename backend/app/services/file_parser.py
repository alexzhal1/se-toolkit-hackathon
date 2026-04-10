import io


def extract_text_from_file(file_bytes: bytes, ext: str) -> str:
    """Extract text content from PDF or DOCX files."""
    if ext == "pdf":
        text = _parse_pdf(file_bytes)
    elif ext == "docx":
        text = _parse_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")
    return _sanitize(text)


def _sanitize(text: str) -> str:
    """Strip NUL bytes (PostgreSQL TEXT cannot store them) and other
    control chars that have no place in extracted document text."""
    if not text:
        return ""
    # Drop NUL outright; keep \n, \r, \t.
    cleaned = text.replace("\x00", "")
    return "".join(
        ch for ch in cleaned if ch in ("\n", "\r", "\t") or ord(ch) >= 0x20
    )


def _parse_pdf(file_bytes: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _parse_docx(file_bytes: bytes) -> str:
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text)
    return "\n\n".join(paragraphs)
