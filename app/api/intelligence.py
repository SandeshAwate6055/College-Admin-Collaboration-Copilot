from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.intelligence.portfolio import build_portfolio
from app.intelligence.recommender import recommend_students
from app.intelligence.student_profile import build_student_360

router = APIRouter()


class RecommendationRequest(BaseModel):
    requirement: str
    top_k: int = 5
    # Optional hard filters — AI results will only include students matching these
    branch: str = ""
    year: str = ""
    min_cgpa: float | None = None
    domain: str = ""


@router.get("/intelligence/student/{prn_or_roll_no}")
def student_360(prn_or_roll_no: str):
    return build_student_360(prn_or_roll_no)


@router.post("/intelligence/recommend")
def recommend(req: RecommendationRequest):
    if not req.requirement.strip():
        raise HTTPException(status_code=400, detail="Requirement cannot be empty")
    return recommend_students(
        req.requirement,
        top_k=req.top_k,
        branch=req.branch,
        year=req.year,
        min_cgpa=req.min_cgpa,
        domain=req.domain,
    )


@router.get("/intelligence/portfolio/{prn_or_roll_no}")
def portfolio(prn_or_roll_no: str):
    return build_portfolio(prn_or_roll_no)
