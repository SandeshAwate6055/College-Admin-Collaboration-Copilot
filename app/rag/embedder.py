from sentence_transformers import SentenceTransformer
import numpy as np
import warnings

# Suppress version warnings
warnings.filterwarnings("ignore")

try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    model = None

def embed_texts(texts: list[str]) -> np.ndarray:
    if model is None:
        raise RuntimeError("Model not loaded")
    return model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

def embed_query(query: str) -> np.ndarray:
    if model is None:
        raise RuntimeError("Model not loaded")
    return model.encode([query], convert_to_numpy=True)
