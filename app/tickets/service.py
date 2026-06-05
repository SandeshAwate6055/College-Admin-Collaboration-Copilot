from sqlalchemy.orm import Session
from app.tickets.models import Ticket

def create_ticket(db: Session, student_id: str, category: str, description: str):
    ticket = Ticket(
        student_id=student_id,
        category=category,
        description=description
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_tickets(db: Session, student_id: str):
    return db.query(Ticket).filter(Ticket.student_id == student_id).all()
