import json
import os
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from app.datasets.service import list_datasets, read_dataset_rows, student_profile
from app.intelligence.student_profile import build_student_360
from app.intelligence.portfolio import build_portfolio
from app.intelligence.recommender import recommend_students
from app.rag.retriever import retrieve

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[2]

@router.get("/platform/knowledge/overview")
def get_knowledge_overview():
    pdfs_dir = PROJECT_ROOT / "data" / "pdfs"
    pdf_files = []
    if pdfs_dir.exists():
        for f in pdfs_dir.glob("*.pdf"):
            pdf_files.append({
                "filename": f.name,
                "size_kb": round(f.stat().st_size / 1024, 1)
            })

    departments = [
        {"name": "Computer Engineering", "code": "CS", "focus": "AI, Cloud, Distributed Systems, Cybersecurity"},
        {"name": "Information Technology", "code": "IT", "focus": "Cloud Architecture, DevOps, Web Engineering, Big Data"},
        {"name": "Artificial Intelligence & Data Science", "code": "AIDS", "focus": "Deep Learning, Generative AI, Computer Vision, NLP"},
        {"name": "Electronics & Telecommunication", "code": "E&TC", "focus": "Embedded Systems, IoT, Edge AI, 5G & VLSI"},
        {"name": "Mechanical Engineering", "code": "MECH", "focus": "Robotics, EV Powertrain, Automation, CAD/CFD"},
        {"name": "Chemical Engineering", "code": "CHEM", "focus": "Process Automation, Green Energy, Biofuels"},
        {"name": "Instrumentation Engineering", "code": "INSTRU", "focus": "Industrial Automation (PLC/SCADA), Biomedical, Smart Sensors"}
    ]

    placement_highlights = [
        {"company": "Nvidia", "role": "AI / System Software Intern", "stipend": "₹50,000 / month", "location": "Pune / Bangalore"},
        {"company": "Barclays", "role": "Software Developer Intern", "stipend": "₹40,000 / month", "location": "Pune"},
        {"company": "Persistent Systems", "role": "Cloud Engineering Intern", "stipend": "₹30,000 / month", "location": "Pune"},
        {"company": "Veritas Technologies", "role": "Systems / Storage Intern", "stipend": "₹35,000 / month", "location": "Pune"},
        {"company": "Eaton Corporation", "role": "Mechatronics / Power Intern", "stipend": "₹30,000 / month", "location": "Pune"}
    ]

    return {
        "institution": "Vishwakarma Institute of Technology (VIT), Pune",
        "tagline": "Autonomous Institute Affiliated to SPPU | NAAC A++ Grade",
        "total_policy_docs": len(pdf_files),
        "policy_documents": sorted(pdf_files, key=lambda x: x["filename"]),
        "departments": departments,
        "placement_highlights": placement_highlights
    }


@router.get("/platform/talent/filter")
def filter_talent(
    q: Optional[str] = Query(None, description="Free text query"),
    branch: Optional[str] = Query(None, description="Filter by branch code or name"),
    year: Optional[str] = Query(None, description="Filter by academic year: FY, SY, TY, BTECH"),
    min_cgpa: Optional[float] = Query(None, ge=0.0, le=10.0),
    domain: Optional[str] = Query(None, description="Filter by primary domain"),
    has_hackathon: Optional[bool] = Query(None),
    has_internship: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    q_val = str(q) if q and not hasattr(q, "default") else ""
    branch_val = str(branch) if branch and not hasattr(branch, "default") else ""
    year_val = str(year) if year and not hasattr(year, "default") else ""
    domain_val = str(domain) if domain and not hasattr(domain, "default") else ""
    min_cgpa_val = float(min_cgpa) if min_cgpa is not None and not hasattr(min_cgpa, "default") else None
    has_hack_val = bool(has_hackathon) if has_hackathon is not None and not hasattr(has_hackathon, "default") else None
    has_intern_val = bool(has_internship) if has_internship is not None and not hasattr(has_internship, "default") else None
    
    try:
        page_val = int(page) if not hasattr(page, "default") else int(page.default)
    except Exception:
        page_val = 1

    try:
        page_size_val = int(page_size) if not hasattr(page_size, "default") else int(page_size.default)
    except Exception:
        page_size_val = 20

    master_dataset = next((d for d in list_datasets() if d["id"] == "students_master"), None)
    if not master_dataset:
        raise HTTPException(status_code=500, detail="students_master dataset not found")

    students = read_dataset_rows(master_dataset)

    # Optional lookup maps for fast boolean checks
    hackathon_prns = set()
    if has_hack_val is not None:
        try:
            hack_ds = next(d for d in list_datasets() if d["id"] == "hackathons")
            hackathon_prns = {r["PRN_or_Roll_No"] for r in read_dataset_rows(hack_ds)}
        except Exception:
            pass

    internship_prns = set()
    if has_intern_val is not None:
        try:
            intern_ds = next(d for d in list_datasets() if d["id"] == "internships")
            internship_prns = {r["PRN_or_Roll_No"] for r in read_dataset_rows(intern_ds)}
        except Exception:
            pass

    filtered = []
    q_lower = q_val.lower().strip()

    for s in students:
        if branch_val:
            b = branch_val.lower()
            if b not in s.get("branch", "").lower() and b != s.get("branch_code", "").lower():
                continue

        if year_val:
            if s.get("year", "").upper() != year_val.upper():
                continue

        if min_cgpa_val is not None:
            try:
                if float(s.get("cgpa", 0)) < min_cgpa_val:
                    continue
            except (ValueError, TypeError):
                continue

        if domain_val:
            if domain_val.lower() not in s.get("primary_domain", "").lower():
                continue

        if has_hack_val is True and s["PRN_or_Roll_No"] not in hackathon_prns:
            continue
        if has_hack_val is False and s["PRN_or_Roll_No"] in hackathon_prns:
            continue

        if has_intern_val is True and s["PRN_or_Roll_No"] not in internship_prns:
            continue
        if has_intern_val is False and s["PRN_or_Roll_No"] in internship_prns:
            continue

        if q_lower:
            searchable = f"{s.get('student_name', '')} {s.get('PRN_or_Roll_No', '')} {s.get('primary_domain', '')} {s.get('technologies', '')} {s.get('branch', '')}".lower()
            if q_lower not in searchable:
                q_tokens = [w for w in re.findall(r'[a-zA-Z0-9]+', q_lower) if w not in {"student", "students", "who", "with", "have", "in", "and", "or", "for", "the"}]
                if not q_tokens or not all(w in searchable for w in q_tokens):
                    continue

        filtered.append(s)

    total = len(filtered)
    start_idx = (page_val - 1) * page_size_val
    end_idx = start_idx + page_size_val
    paginated = filtered[start_idx:end_idx]

    return {
        "total": total,
        "page": page_val,
        "page_size": page_size_val,
        "results": paginated
    }


RESEARCH_STOPWORDS = {
    "i", "want", "need", "find", "show", "get", "give", "me", "papers", "paper",
    "research", "patent", "patents", "copyright", "copyrights", "related", "to",
    "in", "the", "on", "about", "for", "with", "published", "filed", "year", "years",
    "all", "please", "can", "you", "tell", "any", "some", "from", "of", "and", "a", "an",
    "reseach", "reserch", "reaserch", "papres", "pappers", "papper", "artical", "articals"
}


def _parse_research_query(query: str, explicit_year: Optional[int] = None):
    q_str = (query or "").strip()
    if not q_str:
        return "", [], explicit_year, None

    year_val = explicit_year
    year_match = re.search(r'\b(20[12][0-9])\b', q_str)
    if year_match and year_val is None:
        year_val = int(year_match.group(1))

    q_lower = q_str.lower()
    suggested_type = None
    if any(p in q_lower for p in ["patent", "patents", "copyright", "copyrights", "ipr"]):
        suggested_type = "patents"
    elif any(p in q_lower for p in ["paper", "papers", "publication", "journal", "conference"]):
        suggested_type = "papers"

    clean_q = re.sub(r'\b(20[12][0-9])\b', ' ', q_lower)
    words = [w for w in re.findall(r'[a-zA-Z0-9]+', clean_q) if w not in RESEARCH_STOPWORDS]
    clean_query = " ".join(words)

    return clean_query, words, year_val, suggested_type


def _score_research_item(item_text: str, domain: str, raw_query: str, clean_query: str, words: list[str]) -> int:
    text_lower = item_text.lower()
    dom_lower = domain.lower()
    score = 0

    # 1. Exact raw or clean query phrase match
    if clean_query and clean_query in text_lower:
        score += 120
    elif raw_query and raw_query.lower() in text_lower:
        score += 100

    # 2. Domain matching
    if clean_query and (clean_query in dom_lower or dom_lower in clean_query):
        score += 80

    # 3. Individual token matches
    matched_words = 0
    for w in words:
        if w in text_lower or w in dom_lower:
            matched_words += 1
            score += 25
            if w in dom_lower:
                score += 15

    # Bonus if all core keywords match
    if words and matched_words == len(words):
        score += 60

    return score


@router.get("/platform/research/search")
def search_research(
    q: Optional[str] = Query(None, description="Search query across papers and patents"),
    domain: Optional[str] = Query(None, description="Domain filter"),
    item_type: Optional[str] = Query("all", description="all | papers | patents"),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)
):
    q_str = str(q) if q and not hasattr(q, "default") else ""
    dom_str = str(domain) if domain and not hasattr(domain, "default") else ""
    dom_lower = dom_str.lower().strip()
    type_str = str(item_type) if item_type and not hasattr(item_type, "default") else "all"

    explicit_year = None
    if year is not None and not hasattr(year, "default"):
        try:
            explicit_year = int(year)
        except Exception:
            explicit_year = None

    # Parse natural language query (extracts year, cleans conversational filler)
    clean_q, words, detected_year, suggested_type = _parse_research_query(q_str, explicit_year)
    effective_year = explicit_year if explicit_year is not None else detected_year

    # If user's prompt explicitly asks for patents/papers and no manual filter was selected:
    effective_type = type_str
    if type_str == "all" and suggested_type:
        effective_type = suggested_type

    all_domains = set()
    total_papers_count = 0
    total_patents_count = 0
    scored_results = []

    # 1. Search Research Papers
    try:
        ds_papers = next(d for d in list_datasets() if d["id"] == "research_papers")
        paper_rows = read_dataset_rows(ds_papers)
        total_papers_count = len(paper_rows)

        for row in paper_rows:
            p_domain = row.get("Paper_Domain", "")
            if p_domain:
                all_domains.add(p_domain)

            if effective_type not in ("all", "papers"):
                continue

            if dom_lower and dom_lower not in p_domain.lower():
                continue

            pub_year = None
            try:
                pub_year = int(row.get("Publication_Year", 0))
            except Exception:
                pass

            if effective_year is not None and pub_year != effective_year:
                continue

            searchable = f"{row.get('Paper_Title','')} {row.get('Authors','')} {row.get('Venue_Name','')} {p_domain} {row.get('Student_Name','')}".lower()
            
            relevance = 10  # base score
            if q_str.strip():
                relevance = _score_research_item(searchable, p_domain, q_str, clean_q, words)
                if relevance <= 0:
                    continue

            scored_results.append((
                relevance,
                {
                    "type": "Research Paper",
                    "title": row.get("Paper_Title"),
                    "domain": p_domain,
                    "venue_or_status": row.get("Venue_Name"),
                    "publication_type": row.get("Publication_Type"),
                    "year": row.get("Publication_Year"),
                    "authors": row.get("Authors"),
                    "email": row.get("Author_Email"),
                    "url_or_no": row.get("DOI_or_Paper_URL"),
                    "student_name": row.get("Student_Name"),
                    "prn": row.get("PRN_or_Roll_No")
                }
            ))
    except Exception as e:
        logger = getattr(router, "logger", None)
        if logger: logger.error(f"Error loading research papers: {e}")

    # 2. Search Patents & Copyrights
    try:
        ds_patents = next(d for d in list_datasets() if d["id"] == "patents_and_copyrights")
        patent_rows = read_dataset_rows(ds_patents)
        total_patents_count = len(patent_rows)

        for row in patent_rows:
            pat_domain = row.get("Domain", "")
            if pat_domain:
                all_domains.add(pat_domain)

            if effective_type not in ("all", "patents"):
                continue

            if dom_lower and dom_lower not in pat_domain.lower():
                continue

            filing_year = None
            try:
                filing_year = int(row.get("Filing_Year", 0))
            except Exception:
                pass

            if effective_year is not None and filing_year != effective_year:
                continue

            searchable = f"{row.get('Title','')} {row.get('Student_Name','')} {pat_domain} {row.get('Application_or_Registration_No','')} {row.get('IP_Type','')}".lower()
            
            relevance = 10  # base score
            if q_str.strip():
                relevance = _score_research_item(searchable, pat_domain, q_str, clean_q, words)
                if relevance <= 0:
                    continue

            scored_results.append((
                relevance,
                {
                    "type": row.get("IP_Type", "Patent"),
                    "title": row.get("Title"),
                    "domain": pat_domain,
                    "venue_or_status": row.get("Filing_Status"),
                    "publication_type": row.get("IP_Type"),
                    "year": row.get("Filing_Year"),
                    "authors": row.get("Student_Name"),
                    "email": "",
                    "url_or_no": row.get("Application_or_Registration_No"),
                    "student_name": row.get("Student_Name"),
                    "prn": row.get("PRN_or_Roll_No")
                }
            ))
    except Exception as e:
        logger = getattr(router, "logger", None)
        if logger: logger.error(f"Error loading patents: {e}")

    # Sort results by relevance score descending
    scored_results.sort(key=lambda x: x[0], reverse=True)
    results = [item for _, item in scored_results]

    try:
        page_val = int(page) if not hasattr(page, "default") else int(page.default)
    except Exception:
        page_val = 1

    try:
        page_size_val = int(page_size) if not hasattr(page_size, "default") else int(page_size.default)
    except Exception:
        page_size_val = 50

    total = len(results)
    start_idx = (page_val - 1) * page_size_val
    end_idx = start_idx + page_size_val
    paginated = results[start_idx:end_idx]

    return {
        "total": total,
        "total_papers": total_papers_count,
        "total_patents": total_patents_count,
        "available_domains": sorted(list(all_domains)),
        "detected_year": effective_year,
        "page": page_val,
        "page_size": page_size_val,
        "results": paginated
    }

