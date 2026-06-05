import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

VALID_INTENTS = {
    "policy_question",
    "project_search",
    "paper_search",
    "academic_project_search",
    "industry_project_search",
    "internship_search",
    "hackathon_search",
    "certification_search",
    "research_paper_search",
    "student_match",
    "complaint",
}


def _keyword_intent(message: str) -> str:
    text = message.lower()

    complaint_terms = ("wrong", "issue", "problem", "not working", "complaint", "error", "broken")
    student_terms = ("suggest students", "find students", "student who", "students who", "match students")
    certification_terms = ("certification", "certificate", "nptel", "coursera", "edx", "score", "grade")
    hackathon_terms = ("hackathon", "winner", "finalist", "team", "runner up", "shortlisted")
    internship_terms = ("internship", "intern", "stipend", "online", "offline", "hybrid")
    research_paper_terms = ("paper", "research", "journal", "publication", "doi")
    academic_project_terms = ("academic project", "mini project", "major project", "proposed", "ongoing", "completed")
    industry_project_terms = ("industry project", "company project", "company", "worked on", "similar project")

    if any(term in text for term in complaint_terms):
        return "complaint"
    if any(term in text for term in student_terms):
        return "student_match"
    if any(term in text for term in certification_terms):
        return "certification_search"
    if any(term in text for term in hackathon_terms):
        return "hackathon_search"
    if any(term in text for term in internship_terms):
        return "internship_search"
    if any(term in text for term in research_paper_terms):
        return "research_paper_search"
    if any(term in text for term in academic_project_terms):
        return "academic_project_search"
    if any(term in text for term in industry_project_terms):
        return "industry_project_search"
    if "project" in text:
        return "project_search"
    return "policy_question"


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def classify_intent(message: str) -> str:
    """Classify a user message into one supported chat intent."""
    client = _get_client()
    if client is None:
        return _keyword_intent(message)

    prompt = f"""Classify this student/admin message into exactly one intent value.

Intent values:
1. policy_question - questions about exam rules, CGPA, fees, certificates, admin policies
2. industry_project_search - looking for company or industry projects
3. academic_project_search - looking for mini/major academic projects
4. internship_search - looking for internships, roles, modes, stipends, companies
5. hackathon_search - looking for hackathons, teams, winners, finalists
6. certification_search - looking for certifications, platforms, scores, providers
7. research_paper_search - looking for research papers, publications, DOI, venues
8. project_search - generic project search when project type is unclear
9. paper_search - legacy research paper search
10. student_match - teacher/admin finding students for a requirement
11. complaint - reporting a problem or issue

Examples:
"What is CGPA formula?" -> policy_question
"Find industry projects on face recognition" -> industry_project_search
"Find mini projects on IoT" -> academic_project_search
"Show offline internships with stipend" -> internship_search
"National hackathon winners" -> hackathon_search
"Find NPTEL certifications in AI" -> certification_search
"Research papers on transformer models" -> research_paper_search
"Suggest students for computer vision project" -> student_match
"My grade sheet is wrong" -> complaint

Message: "{message}"
Reply with only one token from: policy_question | industry_project_search | academic_project_search | internship_search | hackathon_search | certification_search | research_paper_search | project_search | paper_search | student_match | complaint"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    except Exception:
        return _keyword_intent(message)

    intent = response.choices[0].message.content.strip().lower()
    if intent not in VALID_INTENTS:
        return _keyword_intent(message)
    return intent
