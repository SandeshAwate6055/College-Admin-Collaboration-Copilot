import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

VALID_INTENTS = {
    "greeting",
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
    text = message.lower().strip()

    # Friendly greeting / small-talk patterns — the ONLY thing that bypasses RAG
    clean_words = text.replace("!", " ").replace("?", " ").replace(",", " ").split()
    first_word = clean_words[0] if clean_words else ""
    first_two = " ".join(clean_words[:2]) if len(clean_words) >= 2 else ""

    greeting_terms = (
        "hi", "hello", "hey", "hola", "namaste", "good morning", "good afternoon",
        "good evening", "how are you", "who are you", "what can you do",
        "what is your name", "introduce yourself", "thanks", "thank you"
    )
    if (
        first_word in ("hi", "hello", "hey", "namaste")
        or first_two in ("good morning", "good afternoon", "good evening", "how are", "who are", "what can")
        or any(text == g for g in greeting_terms)
    ):
        return "greeting"

    # Dataset-specific intents
    complaint_terms = ("wrong grade", "is wrong", "grade is wrong", "grade sheet is wrong", "issue with", "problem with", "not working", "complaint", "broken", "error in", "error", "grievance")
    student_terms = ("suggest students", "find students", "student who", "students who", "match students", "who can work")
    certification_terms = ("certification", "certificate", "nptel", "coursera", "edx")
    hackathon_terms = ("hackathon", "winner", "finalist", "runner up", "shortlisted")
    internship_terms = ("internship", "intern at", "stipend", "internship company", "intern")
    research_paper_terms = ("paper", "papers", "paper on", "papers on", "research on", "research paper", "journal", "publication", "doi", "ieee", "springer")
    academic_project_terms = ("academic project", "mini project", "major project", "proposed project", "ongoing project")
    industry_project_terms = ("industry project", "company project", "project at company", "worked on project")

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

    # Everything else → policy_question (search official PDFs first)
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
1. greeting - ONLY for friendly greetings like "hi", "hello", "good morning", "how are you", "thank you" — nothing else
2. policy_question - ANY question about VIT Pune college: departments, syllabus, faculty, fees, CGPA, exams, admissions, placements, labs, courses, rules, regulations, scholarships, hostel — basically everything that needs an official answer
3. industry_project_search - looking for company or industry projects
4. academic_project_search - looking for mini/major academic projects
5. internship_search - looking for internships, roles, modes, stipends, companies
6. hackathon_search - looking for hackathons, teams, winners, finalists
7. certification_search - looking for certifications, platforms, scores, providers
8. research_paper_search - looking for research papers, publications, DOI, venues
9. project_search - generic project search when project type is unclear
10. student_match - teacher/admin finding students for a requirement
11. complaint - reporting a specific problem or issue with a grade/document

IMPORTANT: When in doubt, always use policy_question. Do NOT use greeting unless it's purely a greeting with no question content.

Examples:
"Hello!" -> greeting
"Hi there" -> greeting
"Tell me about AIDS department" -> policy_question
"What is the syllabus for Computer Engineering?" -> policy_question
"What is CGPA formula?" -> policy_question
"What are the fees?" -> policy_question
"Who is the HOD of CS department?" -> policy_question
"What labs does VIT have?" -> policy_question
"Tell me about placements at VIT" -> policy_question
"Find industry projects on face recognition" -> industry_project_search
"Find mini projects on IoT" -> academic_project_search
"Show offline internships with stipend" -> internship_search
"National hackathon winners" -> hackathon_search
"Find NPTEL certifications in AI" -> certification_search
"Research papers on transformer models" -> research_paper_search
"Suggest students for computer vision project" -> student_match
"My grade sheet has wrong marks" -> complaint

Message: "{message}"
Reply with only one token from: greeting | policy_question | industry_project_search | academic_project_search | internship_search | hackathon_search | certification_search | research_paper_search | project_search | paper_search | student_match | complaint"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    except Exception:
        return _keyword_intent(message)

    intent = response.choices[0].message.content.strip().lower()
    if intent not in VALID_INTENTS:
        return "policy_question"  # Safe fallback — always search PDFs
    return intent
