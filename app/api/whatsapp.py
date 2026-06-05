import logging

from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.orm import Session

from app.api import search as search_api
from app.database.session import get_db
from app.rag.generator import generate_answer
from app.rag.retriever import retrieve
from app.router.intent import classify_intent
from app.tickets.service import create_ticket

router = APIRouter()
logger = logging.getLogger(__name__)


def format_whatsapp_response(chat_result: dict) -> str:
    """Convert the structured chat response into a plain-text WhatsApp message."""
    parts = []

    answer = chat_result.get("answer", "")
    if answer:
        parts.append(answer)

    data = chat_result.get("data", [])
    if data:
        for i, item in enumerate(data[:5], 1):
            if isinstance(item, dict):
                name = item.get("title") or item.get("name") or item.get("project_title", "")
                detail = item.get("description") or item.get("abstract") or item.get("skills", "")
                if name:
                    parts.append(f"{i}. *{name}*")
                    if detail:
                        parts.append(f"   {str(detail)[:150]}")

    citations = chat_result.get("citations", [])
    if citations:
        parts.append("\nCitations:")
        for citation in citations:
            parts.append(f"[{citation['index']}] {citation['source']}")

    ticket_id = chat_result.get("ticket_id")
    if ticket_id:
        parts.append(f"\nTicket ID: #{ticket_id}")

    if not parts:
        return chat_result.get("message", "Sorry, I could not process your request.")

    return "\n".join(parts)


def build_twiml(message: str) -> str:
    """Build a TwiML XML response for Twilio."""
    message = (
        message
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>"""


def _chat_result(answer: str, data=None, citations=None, ticket_id=None) -> dict:
    return {
        "answer": answer,
        "citations": citations or [],
        "data": data or [],
        "ticket_id": ticket_id,
    }


@router.post("/whatsapp")
def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    To: str = Form(""),
    db: Session = Depends(get_db),
):
    message = Body.strip()
    student_id = From.replace("whatsapp:", "").strip()

    if not message:
        twiml = build_twiml(
            "Hi! I'm the College Admin Copilot. Send me a question about policies, "
            "projects, research papers, or anything else."
        )
        return Response(content=twiml, media_type="application/xml")

    try:
        intent = classify_intent(message)
    except Exception:
        logger.exception("WhatsApp intent classification failed")
        intent = "policy_question"

    if intent == "policy_question":
        try:
            chunks = retrieve(message, top_k=3)
            result = generate_answer(message, chunks)
            chat_result = _chat_result(
                result.get("answer", ""),
                citations=result.get("citations", []),
            )
        except FileNotFoundError:
            chat_result = _chat_result("Knowledge index is not ready. Please contact the admin.")
        except RuntimeError as exc:
            chat_result = _chat_result(f"Search model is unavailable: {exc}")
        except Exception:
            logger.exception("WhatsApp policy answer failed")
            chat_result = _chat_result("Could not answer this policy question right now.")

    elif intent == "complaint":
        try:
            ticket = create_ticket(
                db=db,
                student_id=student_id,
                category="general",
                description=message,
            )
            chat_result = _chat_result("Your complaint has been registered.", ticket_id=ticket.id)
        except Exception:
            logger.exception("WhatsApp ticket creation failed")
            chat_result = _chat_result("Could not register your complaint right now.")

    elif intent == "project_search":
        try:
            result = search_api.search_projects(message, top_k=5)
            chat_result = _chat_result(result.get("answer", ""), data=result.get("results", []))
        except Exception:
            logger.exception("WhatsApp project search failed")
            chat_result = _chat_result("Could not search projects right now.")

    elif intent == "paper_search":
        try:
            result = search_api.search_papers(message, top_k=5)
            chat_result = _chat_result(result.get("answer", ""), data=result.get("results", []))
        except Exception:
            logger.exception("WhatsApp paper search failed")
            chat_result = _chat_result("Could not search papers right now.")

    elif intent == "student_match":
        try:
            result = search_api.match_students(message, top_k=5)
            chat_result = _chat_result(
                result.get("recommendation", ""),
                data=result.get("matched_students", []),
            )
        except Exception:
            logger.exception("WhatsApp student match failed")
            chat_result = _chat_result("Could not match students right now.")

    else:
        chat_result = _chat_result(
            "I wasn't sure what you meant. Try asking about policies, projects, "
            "research papers, or report an issue."
        )

    response_text = format_whatsapp_response(chat_result)
    if len(response_text) > 1500:
        response_text = response_text[:1497] + "..."

    twiml = build_twiml(response_text)
    return Response(content=twiml, media_type="application/xml")
