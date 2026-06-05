from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.tickets.service import get_tickets
from app.database.session import get_db

router = APIRouter()  # ← REQUIRED!

@router.get("/tickets/{student_id}")
def fetch_tickets(student_id: str, db: Session = Depends(get_db)):
    tickets = get_tickets(db, student_id)
    return [
        {
            "ticket_id": t.id,
            "category": t.category,
            "description": t.description,
            "status": t.status,
            "created_at": str(t.created_at)
        }
        for t in tickets
    ]
