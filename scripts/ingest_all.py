#!/usr/bin/env python3
"""Build FAISS indexes for policy PDFs and configured CSV datasets."""

from app.datasets.service import ingest_all_datasets
from app.rag.chunker import chunk_documents
from app.rag.embedder import embed_texts
from app.rag.loader import load_pdfs
from app.rag.vector_store import save_index


def ingest_policy_pdfs():
    print("Loading policy PDFs...")
    documents = load_pdfs("data/pdfs")
    print(f"Found {len(documents)} pages across {len(set(d['source'] for d in documents))} files")

    print("Chunking policy text...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    texts = [chunk["text"] for chunk in chunks]
    metadata = [
        {"text": chunk["text"], "source": chunk["source"], "page": chunk["page"]}
        for chunk in chunks
    ]

    print("Generating policy embeddings...")
    embeddings = embed_texts(texts)
    print(f"Embeddings shape: {embeddings.shape}")

    print("Saving policy FAISS index...")
    save_index(embeddings, metadata)


def main():
    ingest_policy_pdfs()

    print("Indexing configured CSV datasets...")
    for result in ingest_all_datasets():
        print(f"Indexed {result['indexed']} records for {result['dataset_id']}")

    print("Done. Ready for questions.")


if __name__ == "__main__":
    main()
