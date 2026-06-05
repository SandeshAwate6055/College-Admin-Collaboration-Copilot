from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database.session import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id          = Column(Integer, primary_key=True, index=True)
    student_id  = Column(String, nullable=False)
    category    = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status      = Column(String, default="open")
    created_at  = Column(DateTime, default=datetime.utcnow)
