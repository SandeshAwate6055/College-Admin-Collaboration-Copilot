from collections import Counter

from app.datasets.service import list_datasets, read_dataset_rows, row_to_summary

DOMAIN_COLUMNS = (
    "Project_Domain",
    "Certification_Domain",
    "Paper_Domain",
)


def _student_rows(prn_or_roll_no: str) -> list[tuple[dict, dict]]:
    matches = []
    target = prn_or_roll_no.lower()
    for dataset in list_datasets():
        key = dataset.get("student_key", "PRN_or_Roll_No")
        for row in read_dataset_rows(dataset):
            if row.get(key, "").lower() == target:
                matches.append((dataset, row))
    return matches


def _record_domains(row: dict) -> list[str]:
    domains = []
    for column in DOMAIN_COLUMNS:
        value = row.get(column, "")
        if value:
            domains.append(value)
    return domains


def build_student_360(prn_or_roll_no: str) -> dict:
    grouped = {}
    domain_counter = Counter()
    company_counter = Counter()
    platform_counter = Counter()
    achievement_count = 0
    student_name = ""
    branch = ""
    year = ""

    for dataset in list_datasets():
        grouped[dataset["id"]] = {
            "label": dataset["label"],
            "count": 0,
            "records": [],
        }

    for dataset, row in _student_rows(prn_or_roll_no):
        summary = row_to_summary(dataset, row)
        grouped[dataset["id"]]["records"].append(summary)
        grouped[dataset["id"]]["count"] += 1
        achievement_count += 1

        student_name = student_name or row.get("Student_Name", "")
        branch = branch or row.get("Branch", "")
        year = year or row.get("Year", "")

        domain_counter.update(_record_domains(row))
        for column in ("Company_Name", "Internship_Company_Name"):
            if row.get(column):
                company_counter[row[column]] += 1
        if row.get("Platform_or_Provider"):
            platform_counter[row["Platform_or_Provider"]] += 1

    strongest_domains = [item for item, _ in domain_counter.most_common(5)]
    suggested_track = infer_career_track(strongest_domains)

    return {
        "prn_or_roll_no": prn_or_roll_no,
        "student_name": student_name,
        "branch": branch,
        "year": year,
        "total_records": achievement_count,
        "strongest_domains": strongest_domains,
        "top_companies": [item for item, _ in company_counter.most_common(5)],
        "top_platforms": [item for item, _ in platform_counter.most_common(5)],
        "suggested_career_track": suggested_track,
        "dataset_counts": {
            dataset_id: group["count"]
            for dataset_id, group in grouped.items()
        },
        "datasets": grouped,
    }


def infer_career_track(domains: list[str]) -> str:
    text = " ".join(domains).lower()
    if any(term in text for term in ("machine learning", "data science", "nlp", "computer vision")):
        return "AI / Data Science"
    if any(term in text for term in ("cloud", "web", "android")):
        return "Software / Cloud Engineering"
    if "cybersecurity" in text:
        return "Cybersecurity"
    if "iot" in text:
        return "IoT / Embedded Systems"
    if domains:
        return domains[0]
    return "General Engineering"
