from app.intelligence.student_profile import build_student_360


def build_portfolio(prn_or_roll_no: str) -> dict:
    profile = build_student_360(prn_or_roll_no)
    name = profile["student_name"] or "Student"
    domains = profile["strongest_domains"]
    domain_text = ", ".join(domains[:3]) if domains else "engineering fundamentals"

    summary = (
        f"{name} is a {profile['branch'] or 'college'} student with activity across "
        f"{profile['total_records']} recorded academic and co-curricular records. "
        f"The profile indicates strengths in {domain_text} and a suggested track of "
        f"{profile['suggested_career_track']}."
    )

    highlights = []
    for dataset_id, group in profile["datasets"].items():
        if group["count"]:
            highlights.append(f"{group['count']} {group['label'].lower()} record(s)")

    return {
        "profile": profile,
        "portfolio": {
            "headline": f"{name} - {profile['suggested_career_track']} Portfolio",
            "summary": summary,
            "highlights": highlights,
            "skills_or_domains": domains,
            "sections": profile["datasets"],
        },
    }
