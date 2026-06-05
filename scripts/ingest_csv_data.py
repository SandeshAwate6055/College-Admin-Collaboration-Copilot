import csv
from pathlib import Path
from app.rag.embedder import embed_texts
from app.rag.vector_store import save_index


def _resolve_csv_path(csv_path: str, candidates: list[str]) -> str:
    path = Path(csv_path)
    if path.exists():
        return str(path)

    for candidate in candidates:
        candidate_path = Path(candidate)
        if candidate_path.exists():
            return str(candidate_path)

    expected = ", ".join([csv_path, *candidates])
    raise FileNotFoundError(f"CSV file not found. Tried: {expected}")


def ingest_students(csv_path: str = "data/csv/industry project students.csv"):
    csv_path = _resolve_csv_path(
        csv_path,
        ["data/csv/industry-project-students.csv"],
    )
    students = []
    student_texts = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            text = (
                f"Student: {row.get('student_name','')}. "
                f"Department: {row.get('department','')}. "
                f"Company: {row.get('company','')}. "
                f"Project: {row.get('project_title','')}. "
                f"Domain: {row.get('domain','')}. "
                f"Technologies: {row.get('technologies','')}. "
                f"Role: {row.get('role','')}. "
                f"Year: {row.get('academic_year','')}.")

            students.append(row)
            student_texts.append(text)

    if not students:
        print("⚠️ No students found in CSV")
        return

    embeddings = embed_texts(student_texts)
    save_index(
        embeddings,
        students,
        index_path="data/vector_store/students_index.faiss",
        meta_path="data/vector_store/students_metadata.json"
    )
    print(f"✅ Indexed {len(students)} students")


def ingest_papers(csv_path: str = "data/csv/research papers dataset.csv"):
    csv_path = _resolve_csv_path(
        csv_path,
        ["data/csv/research-papers-dataset-2.csv", "data/csv/research-papers-dataset.csv"],
    )
    papers = []
    paper_texts = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            text = (
                f"Title: {row.get('paper_title','')}. "
                f"Authors: {row.get('authors','')}. "
                f"Year: {row.get('year','')}. "
                f"Published in: {row.get('conference_journal','')}. "
                f"Abstract: {row.get('abstract','')}. "
                f"Keywords: {row.get('keywords','')}. "
                f"Domain: {row.get('domain','')}.")

            papers.append(row)
            paper_texts.append(text)

    if not papers:
        print("⚠️ No papers found in CSV")
        return

    embeddings = embed_texts(paper_texts)
    save_index(
        embeddings,
        papers,
        index_path="data/vector_store/papers_index.faiss",
        meta_path="data/vector_store/papers_metadata.json"
    )
    print(f"✅ Indexed {len(papers)} papers")


if __name__ == "__main__":
    ingest_students()
    ingest_papers()
