from app.rag.vector_store import load_index
from app.rag.embedder import embed_query
import numpy as np

def retrieve(query: str, top_k: int = 5, index_path: str = "data/vector_store/index.faiss", meta_path: str = "data/vector_store/metadata.json") -> list[dict]:
    """
    Searches FAISS index for top-k chunks most relevant to the query.
    Returns list of chunk metadata with similarity scores.
    """
    index, metadata = load_index(index_path=index_path, meta_path=meta_path)
    query_embedding = embed_query(query)
    
    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata):
            chunk = metadata[idx].copy()
            chunk["score"] = float(distances[0][i])
            results.append(chunk)
    
    return results
