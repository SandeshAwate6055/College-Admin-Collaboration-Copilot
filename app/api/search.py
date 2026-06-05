import logging

from fastapi import APIRouter, HTTPException, Query
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer

router = APIRouter()
logger = logging.getLogger(__name__)

STUDENTS_INDEX = "data/vector_store/students_index.faiss"
STUDENTS_META = "data/vector_store/students_metadata.json"
PAPERS_INDEX = "data/vector_store/papers_index.faiss"
PAPERS_META = "data/vector_store/papers_metadata.json"


def _student_chunk(record: dict) -> dict:
    summary = (
        f"Student: {record.get('student_name','')} / "
        f"Project: {record.get('project_title','')} / "
        f"Company: {record.get('company','')} / "
        f"Technologies: {record.get('technologies','')} / "
        f"Domain: {record.get('domain','')}"
    )
    return {"source": "students", "page": "1", "text": summary}


def _paper_chunk(record: dict) -> dict:
    summary = (
        f"Title: {record.get('paper_title','')} / "
        f"Authors: {record.get('authors','')} / "
        f"Year: {record.get('year','')} / "
        f"Conference: {record.get('conference_journal','')} / "
        f"Domain: {record.get('domain','')}"
    )
    return {"source": "papers", "page": "1", "text": summary}


def _safe_year(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return value or 0


def _answer_from_chunks(query: str, chunks: list[dict]) -> str:
    try:
        return generate_answer(query, chunks).get("answer", "")
    except Exception:
        logger.exception("Answer generation failed")
        return "Results were found, but answer generation is temporarily unavailable."


@router.get("/search/projects")
def search_projects(q: str = Query(..., min_length=1), top_k: int = Query(5, ge=1)):
    try:
        hits = retrieve(q, top_k=top_k, index_path=STUDENTS_INDEX, meta_path=STUDENTS_META)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Search model unavailable: {exc}")
    except Exception:
        logger.exception("Project search failed")
        raise HTTPException(status_code=500, detail="Project search failed")

    chunks = [_student_chunk(r) for r in hits]
    answer = _answer_from_chunks(q, chunks)

    results = []
    for idx, hit in enumerate(hits, start=1):
        results.append({
            "student_name": hit.get("student_name", ""),
            "project_title": hit.get("project_title", ""),
            "company": hit.get("company", ""),
            "technologies": hit.get("technologies", ""),
            "domain": hit.get("domain", ""),
            "similarity_rank": idx,
        })

    return {
        "query": q,
        "answer": answer,
        "results": results,
    }


@router.get("/search/papers")
def search_papers(q: str = Query(..., min_length=1), top_k: int = Query(5, ge=1)):
    try:
        hits = retrieve(q, top_k=top_k, index_path=PAPERS_INDEX, meta_path=PAPERS_META)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Search model unavailable: {exc}")
    except Exception:
        logger.exception("Paper search failed")
        raise HTTPException(status_code=500, detail="Paper search failed")

    chunks = [_paper_chunk(r) for r in hits]
    answer = _answer_from_chunks(q, chunks)

    results = []
    for idx, hit in enumerate(hits, start=1):
        results.append({
            "paper_title": hit.get("paper_title", ""),
            "authors": hit.get("authors", ""),
            "year": _safe_year(hit.get("year", 0)),
            "conference_journal": hit.get("conference_journal", ""),
            "abstract": hit.get("abstract", ""),
            "keywords": hit.get("keywords", ""),
            "domain": hit.get("domain", ""),
            "similarity_rank": idx,
        })

    return {
        "query": q,
        "answer": answer,
        "results": results,
    }


@router.get("/match/students")
def match_students(requirement: str = Query(..., min_length=1), top_k: int = Query(5, ge=1)):
    try:
        hits = retrieve(requirement, top_k=top_k, index_path=STUDENTS_INDEX, meta_path=STUDENTS_META)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Search model unavailable: {exc}")
    except Exception:
        logger.exception("Student match failed")
        raise HTTPException(status_code=500, detail="Student match failed")

    chunks = [_student_chunk(r) for r in hits]
    recommendation = _answer_from_chunks(requirement, chunks)

    matched_students = []
    for idx, hit in enumerate(hits, start=1):
        matched_students.append({
            "student_name": hit.get("student_name", ""),
            "project_title": hit.get("project_title", ""),
            "technologies": hit.get("technologies", ""),
            "company": hit.get("company", ""),
            "domain": hit.get("domain", ""),
            "match_rank": idx,
        })

    return {
        "requirement": requirement,
        "recommendation": recommendation,
        "matched_students": matched_students,
    }
