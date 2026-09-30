from collections import defaultdict

from app.datasets.service import list_datasets, read_dataset_rows, row_to_search_text, row_to_summary, search_dataset
from app.intelligence.student_profile import build_student_360

IMPORTANT_DATASET_WEIGHTS = {
    "industry_projects": 18,
    "academic_projects": 14,
    "internships": 18,
    "hackathons": 12,
    "certifications": 16,
    "research_papers": 14,
}


def _tokens(text: str) -> set[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return {part for part in cleaned.split() if len(part) >= 3}


def _keyword_overlap(requirement: str, evidence_text: str) -> int:
    return len(_tokens(requirement) & _tokens(evidence_text))


def recommend_students(
    requirement: str,
    top_k: int = 5,
    branch: str = "",
    year: str = "",
    min_cgpa: float | None = None,
    domain: str = "",
) -> dict:
    grouped = defaultdict(lambda: {"evidence": [], "raw_score": 0.0})

    # --- Build a set of PRNs that satisfy hard filters from students_master ---
    allowed_prns: set[str] | None = None
    try:
        from app.datasets.service import get_dataset
        master = get_dataset("students_master")
        master_rows = read_dataset_rows(master)
        filtered_rows = []
        for row in master_rows:
            if branch and row.get("branch_code", "").upper() != branch.upper():
                # also try partial match on branch name
                if branch.upper() not in row.get("branch", "").upper():
                    continue
            if year and row.get("year", "").upper() != year.upper():
                continue
            if min_cgpa is not None:
                try:
                    if float(row.get("cgpa", 0)) < min_cgpa:
                        continue
                except (ValueError, TypeError):
                    continue
            if domain and domain.lower() not in row.get("primary_domain", "").lower():
                continue
            filtered_rows.append(row)
        allowed_prns = {r["PRN_or_Roll_No"] for r in filtered_rows}
    except Exception:
        allowed_prns = None  # if master unavailable, don't filter

    for dataset in list_datasets():
        try:
            result = search_dataset(dataset["id"], requirement, top_k=12)
            hits = result.get("results", [])
        except FileNotFoundError:
            hits = []

        rows_by_prn = {
            row.get(dataset.get("student_key", "PRN_or_Roll_No"), ""): row
            for row in read_dataset_rows(dataset)
        }

        for rank, hit in enumerate(hits, start=1):
            prn = hit.get("PRN_or_Roll_No", "")
            if not prn:
                continue
            # Skip students that don't meet hard-filter criteria
            if allowed_prns is not None and prn not in allowed_prns:
                continue

            source_row = rows_by_prn.get(prn, hit)
            text = row_to_search_text(dataset, source_row)
            overlap = _keyword_overlap(requirement, text)
            rank_points = max(0, 13 - rank)
            dataset_points = IMPORTANT_DATASET_WEIGHTS.get(dataset["id"], 10)
            score = dataset_points + rank_points + (overlap * 4)

            grouped[prn]["raw_score"] += score
            grouped[prn]["evidence"].append(
                {
                    "dataset_id": dataset["id"],
                    "dataset_label": dataset["label"],
                    "rank": rank,
                    "matched_terms": overlap,
                    "summary": row_to_summary(dataset, source_row),
                    "reason": _reason_from_row(dataset, source_row),
                }
            )

    recommendations = []
    for prn, data in grouped.items():
        profile = build_student_360(prn)
        breadth_bonus = sum(1 for count in profile["dataset_counts"].values() if count > 0) * 5
        total_score = min(100, round(data["raw_score"] + breadth_bonus))
        evidence = sorted(
            data["evidence"],
            key=lambda item: (item["matched_terms"], -item["rank"]),
            reverse=True,
        )[:6]
        recommendations.append(
            {
                "student_name": profile["student_name"],
                "prn_or_roll_no": prn,
                "branch": profile["branch"],
                "year": profile["year"],
                "cgpa": profile.get("cgpa"),
                "score": total_score,
                "suggested_career_track": profile["suggested_career_track"],
                "strongest_domains": profile["strongest_domains"],
                "evidence": evidence,
                "recommendation_reason": _recommendation_reason(profile, evidence),
            }
        )

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return {
        "requirement": requirement,
        "recommendations": recommendations[:top_k],
        "filters_applied": {
            "branch": branch or None,
            "year": year or None,
            "min_cgpa": min_cgpa,
            "domain": domain or None,
        },
    }


def _reason_from_row(dataset: dict, row: dict) -> str:
    if dataset["id"] in ("industry_projects", "academic_projects"):
        return f"Project evidence: {row.get('Project_Title', '')} in {row.get('Project_Domain', '')}"
    if dataset["id"] == "internships":
        return f"Internship evidence: {row.get('Internship_Role', '')} at {row.get('Internship_Company_Name', '')}"
    if dataset["id"] == "hackathons":
        return f"Hackathon evidence: {row.get('Result_Status', '')} in {row.get('Hackathon_Name', '')}"
    if dataset["id"] == "certifications":
        return f"Certification evidence: {row.get('Certification_Title', '')} from {row.get('Platform_or_Provider', '')}"
    if dataset["id"] == "research_papers":
        return f"Research evidence: {row.get('Paper_Title', '')} in {row.get('Paper_Domain', '')}"
    return dataset["label"]


def _recommendation_reason(profile: dict, evidence: list[dict]) -> str:
    domains = ", ".join(profile["strongest_domains"][:3]) or "multiple activity areas"
    labels = ", ".join(sorted({item["dataset_label"] for item in evidence})) or "student records"
    return (
        f"{profile['student_name'] or profile['prn_or_roll_no']} is a strong fit because their profile "
        f"shows evidence across {labels}, with strongest domains in {domains}."
    )
