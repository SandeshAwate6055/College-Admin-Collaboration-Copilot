def chunk_documents(documents: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Splits each document's text into smaller chunks with overlap.
    Preserves source and page metadata.
    """
    chunks = []
    for doc in documents:
        text = doc["text"]
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "source": doc["source"],
                "page": doc["page"]
            })
            start += chunk_size - overlap  # overlap ensures no sentence is cut off
    return chunks
