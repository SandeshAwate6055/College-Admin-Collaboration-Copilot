import json
import os

import faiss
import numpy as np

INDEX_PATH = "data/vector_store/index.faiss"
META_PATH = "data/vector_store/metadata.json"


def save_index(
    embeddings: np.ndarray,
    metadata: list[dict],
    index_path: str = INDEX_PATH,
    meta_path: str = META_PATH,
):
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    print(f"Saved {len(metadata)} chunks to FAISS index at {index_path}.")


def load_index(index_path: str = INDEX_PATH, meta_path: str = META_PATH):
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError(
            "Index or metadata not found. Run 'python scripts/ingest_all.py' first."
        )
    index = faiss.read_index(index_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata
