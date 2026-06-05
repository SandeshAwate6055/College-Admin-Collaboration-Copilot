from app.router.intent import classify_intent


def test_classify_intent_uses_keyword_fallback_without_groq_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    assert classify_intent("Find projects on face recognition") == "project_search"
    assert classify_intent("Papers on object detection") == "research_paper_search"
    assert classify_intent("Find NPTEL certifications in AI") == "certification_search"
    assert classify_intent("Show offline internships with stipend") == "internship_search"
    assert classify_intent("National hackathon winners") == "hackathon_search"
    assert classify_intent("Suggest students for computer vision project") == "student_match"
    assert classify_intent("My grade sheet is wrong") == "complaint"
    assert classify_intent("What is CGPA formula?") == "policy_question"
