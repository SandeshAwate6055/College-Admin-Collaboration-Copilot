def chunk_documents(documents: list[dict], chunk_size: int = 1200, overlap: int = 200) -> list[dict]:
    """
    Splits each document's text into meaningful chunks with overlap.
    Keeps entire page together if it fits within chunk_size.
    Preserves source and page metadata.
    """
    chunks = []
    for doc in documents:
        text = doc["text"]
        if not text:
            continue
        if len(text) <= chunk_size:
            chunks.append({
                "text": text,
                "source": doc["source"],
                "page": doc["page"]
            })
            continue

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "source": doc["source"],
                "page": doc["page"]
            })
            start += chunk_size - overlap
    return chunks

