import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import search as search_api
from app.datasets.service import search_dataset
from app.database.session import get_db
from app.rag.generator import generate_answer, generate_conversational_response
from app.rag.retriever import retrieve
from app.router.intent import classify_intent
from app.tickets.service import create_ticket

router = APIRouter()
logger = logging.getLogger(__name__)

DATASET_INTENTS = {
    "industry_project_search": ["industry_projects"],
    "academic_project_search": ["academic_projects"],
    "internship_search": ["internships"],
    "hackathon_search": ["hackathons"],
    "certification_search": ["certifications"],
    "research_paper_search": ["research_papers"],
    "paper_search": ["research_papers"],
    "project_search": ["industry_projects", "academic_projects"],
}


class ChatRequest(BaseModel):
    student_id: str
    message: str


def _error_response(response_type: str, message: str) -> dict:
    return {
        "type": response_type,
        "message": message,
        "data": [],
        "answer": "",
        "citations": [],
        "ticket_id": None,
    }


def _dataset_search_response(intent: str, message: str) -> dict:
    dataset_ids = DATASET_INTENTS[intent]
    all_results = []

    for dataset_id in dataset_ids:
        result = search_dataset(dataset_id, message, top_k=5)
        all_results.extend(result.get("results", []))

    if not all_results:
        answer = f"I searched the {intent.replace('_', ' ')} records for '{message}', but couldn't find matching records. Try broader keywords or search the **Talent** / **Research** tabs above."
    else:
        items_summary = []
        for i, item in enumerate(all_results[:5], 1):
            title = (
                item.get("Project_Title") 
                or item.get("Paper_Title") 
                or item.get("Hackathon_Name") 
                or item.get("Certification_Title") 
                or item.get("Internship_Role") 
                or item.get("Title") 
                or "Project/Record"
            )
            student = item.get("Student_Name", "")
            prn = item.get("PRN_or_Roll_No", "")
            org = (
                item.get("Company_Name") 
                or item.get("Internship_Company_Name") 
                or item.get("Platform_or_Provider") 
                or item.get("Venue_Name") 
                or item.get("Team_Name") 
                or ""
            )
            domain = item.get("Project_Domain") or item.get("Paper_Domain") or item.get("Domain") or item.get("Certification_Domain") or ""
            
            line = f"**{i}. {title}**"
            meta = []
            if student: meta.append(f"Student: *{student}* (PRN: {prn})")
            if org: meta.append(f"Org/Venue: *{org}*")
            if domain: meta.append(f"Domain: *{domain}*")
            items_summary.append(f"{line}\n   - " + " | ".join(meta))

        answer = (
            f"Here are the top verified records matching **'{message}'**:\n\n"
            + "\n\n".join(items_summary)
            + f"\n\n*(Showing top {min(len(all_results), 5)} matches. Click the **Student 360 & Portfolio** tab to view complete portfolios.)*"
        )

    return {
        "type": intent,
        "message": "Dataset results matching your query.",
        "data": all_results[:10],
        "answer": answer,
        "citations": [],
        "ticket_id": None,
    }


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        intent = classify_intent(req.message)
    except Exception:
        logger.exception("Intent classification failed")
        intent = "policy_question"

    if intent == "greeting":
        answer = generate_conversational_response(req.message, intent="greeting")
        return {
            "type": "greeting",
            "message": "Welcome to VIT Pune AI Copilot.",
            "data": [],
            "answer": answer,
            "citations": [],
            "ticket_id": None,
        }

    if intent == "policy_question":
        try:
            chunks = retrieve(req.message, top_k=8)
            result = generate_answer(req.message, chunks)
            return {
                "type": "answer",
                "message": "Here is the information from official VIT Pune documents.",
                "data": [],
                "answer": result.get("answer", ""),
                "citations": result.get("citations", []),
                "ticket_id": None,
            }
        except FileNotFoundError:
            return _error_response(
                "answer",
                "Knowledge index not ready; run 'python scripts/ingest_all.py' first.",
            )
        except RuntimeError as exc:
            response = _error_response("answer", "Search model is unavailable.")
            response["answer"] = str(exc)
            return response
        except Exception:
            logger.exception("Policy question failed")
            return _error_response("answer", "Could not answer this question right now.")


    if intent == "complaint":
        try:
            ticket = create_ticket(
                db=db,
                student_id=req.student_id,
                category="general",
                description=req.message,
            )
        except Exception:
            logger.exception("Ticket creation failed")
            raise HTTPException(status_code=500, detail="Could not create ticket")

        return {
            "type": "ticket",
            "message": f"Your complaint has been registered. Ticket ID: #{ticket.id}",
            "data": [],
            "answer": "",
            "citations": [],
            "ticket_id": ticket.id,
        }

    if intent in DATASET_INTENTS:
        try:
            return _dataset_search_response(intent, req.message)
        except FileNotFoundError:
            return _error_response(intent, "Dataset indexes are not ready; run dataset ingestion first.")
        except RuntimeError as exc:
            response = _error_response(intent, "Search model is unavailable.")
            response["answer"] = str(exc)
            return response
        except Exception:
            logger.exception("Dataset search failed")
            return _error_response(intent, "Could not search datasets right now.")

    if intent == "student_match":
        try:
            result = search_api.match_students(req.message, top_k=5)
        except HTTPException as exc:
            return _error_response("student_match", str(exc.detail))

        return {
            "type": "student_match",
            "message": "Student matches for your requirement.",
            "data": result.get("matched_students", []),
            "answer": result.get("recommendation", ""),
            "citations": [],
            "ticket_id": None,
        }

    return _error_response("answer", "Could not classify intent; defaulting to policy question.")
