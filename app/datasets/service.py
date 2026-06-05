import csv
import json
import os
from collections import Counter
from pathlib import Path

from app.rag.embedder import embed_texts
from app.rag.retriever import retrieve
from app.rag.vector_store import save_index

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "datasets.json"


def _project_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def load_dataset_config(config_path: str | None = None) -> dict:
    path = Path(config_path or os.getenv("DATASETS_CONFIG", DEFAULT_CONFIG_PATH))
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def list_datasets() -> list[dict]:
    return load_dataset_config().get("datasets", [])


def get_dataset(dataset_id: str) -> dict:
    for dataset in list_datasets():
        if dataset["id"] == dataset_id:
            return dataset
    raise KeyError(f"Unknown dataset: {dataset_id}")


def read_dataset_rows(dataset: dict) -> list[dict]:
    csv_path = _project_path(dataset["csv_path"])
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [
            {key: (value.strip() if isinstance(value, str) else value) for key, value in row.items()}
            for row in reader
        ]


def row_to_search_text(dataset: dict, row: dict) -> str:
    parts = []
    for column in dataset.get("searchable_columns", []):
        value = row.get(column, "")
        if value not in ("", None):
            parts.append(f"{column}: {value}")
    return ". ".join(parts)


def row_to_summary(dataset: dict, row: dict) -> dict:
    summary = {column: row.get(column, "") for column in dataset.get("summary_columns", [])}
    summary["dataset_id"] = dataset["id"]
    summary["dataset_label"] = dataset["label"]
    return summary


def ingest_dataset(dataset_id: str) -> dict:
    dataset = get_dataset(dataset_id)
    rows = read_dataset_rows(dataset)
    texts = [row_to_search_text(dataset, row) for row in rows]

    if not rows:
        return {"dataset_id": dataset_id, "indexed": 0}

    metadata = []
    for row, text in zip(rows, texts):
        record = dict(row)
        record["dataset_id"] = dataset["id"]
        record["dataset_label"] = dataset["label"]
        record["source"] = dataset["label"]
        record["page"] = "1"
        record["text"] = text
        metadata.append(record)

    embeddings = embed_texts(texts)
    save_index(
        embeddings,
        metadata,
        index_path=str(_project_path(dataset["index_path"])),
        meta_path=str(_project_path(dataset["metadata_path"])),
    )
    return {"dataset_id": dataset_id, "indexed": len(metadata)}


def ingest_all_datasets() -> list[dict]:
    return [ingest_dataset(dataset["id"]) for dataset in list_datasets()]


def search_dataset(dataset_id: str, query: str, top_k: int = 5) -> dict:
    dataset = get_dataset(dataset_id)
    hits = retrieve(
        query,
        top_k=top_k,
        index_path=str(_project_path(dataset["index_path"])),
        meta_path=str(_project_path(dataset["metadata_path"])),
    )
    return {
        "dataset_id": dataset_id,
        "dataset_label": dataset["label"],
        "query": query,
        "results": [row_to_summary(dataset, hit) | {"score": hit.get("score")} for hit in hits],
    }


def student_profile(prn_or_roll_no: str) -> dict:
    profile = {
        "prn_or_roll_no": prn_or_roll_no,
        "student_name": "",
        "branch": "",
        "year": "",
        "datasets": {},
        "total_records": 0,
    }

    for dataset in list_datasets():
        key = dataset.get("student_key", "PRN_or_Roll_No")
        rows = [row for row in read_dataset_rows(dataset) if row.get(key, "").lower() == prn_or_roll_no.lower()]
        summaries = [row_to_summary(dataset, row) for row in rows]
        profile["datasets"][dataset["id"]] = {
            "label": dataset["label"],
            "count": len(summaries),
            "records": summaries,
        }
        profile["total_records"] += len(summaries)

        if rows and not profile["student_name"]:
            profile["student_name"] = rows[0].get("Student_Name", "")
            profile["branch"] = rows[0].get("Branch", "")
            profile["year"] = rows[0].get("Year", "")

    return profile


def dataset_analytics() -> dict:
    summaries = []
    for dataset in list_datasets():
        rows = read_dataset_rows(dataset)
        branch_counts = Counter(row.get("Branch", "Unknown") or "Unknown" for row in rows)
        year_counts = Counter(row.get("Year", "Unknown") or "Unknown" for row in rows)
        summaries.append(
            {
                "dataset_id": dataset["id"],
                "dataset_label": dataset["label"],
                "total_records": len(rows),
                "branch_counts": dict(branch_counts),
                "year_counts": dict(year_counts),
            }
        )
    return {"datasets": summaries}
