from app.datasets.service import list_datasets, read_dataset_rows
from app.intelligence.portfolio import build_portfolio
from app.intelligence.recommender import recommend_students
from app.intelligence.student_profile import build_student_360


def _sample_prn() -> str:
    dataset = next(item for item in list_datasets() if item["id"] == "certifications")
    return read_dataset_rows(dataset)[0]["PRN_or_Roll_No"]


def test_student_360_adds_strengths_and_track():
    profile = build_student_360(_sample_prn())

    assert profile["prn_or_roll_no"]
    assert "dataset_counts" in profile
    assert "suggested_career_track" in profile
    assert profile["total_records"] >= 1


def test_portfolio_contains_summary_and_sections():
    portfolio = build_portfolio(_sample_prn())

    assert portfolio["portfolio"]["headline"]
    assert portfolio["portfolio"]["summary"]
    assert portfolio["portfolio"]["sections"]


def test_recommend_students_returns_explainable_matches():
    result = recommend_students("Need machine learning NPTEL certified students", top_k=3)

    assert result["recommendations"]
    first = result["recommendations"][0]
    assert first["score"] > 0
    assert first["evidence"]
    assert first["recommendation_reason"]
