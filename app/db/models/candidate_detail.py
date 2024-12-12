from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ...db.database import Base

class CandidateDetail(Base):
    """ Candidate Detail model
    
    Args:
        Base (Base): Base clase de SQLAlchemy
        
    Returns:
        class 'models.CandidateDetail': CandidateDetail model
    """
    __tablename__ = "candidate_details"

    id = Column(Integer, index=True, primary_key=True)
    email = Column(String(255), index=True, nullable=True)
    id_number = Column(String(255), nullable=True)
    mobile_phone = Column(String(255), nullable=True)
    landline_phone = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    marital_status = Column(String(255), nullable=True)
    availability_to_travel = Column(String(255), nullable=True)
    availability_to_move = Column(String(255), nullable=True)
    net_monthly_salary = Column(String(255), nullable=True)
    languages = Column(String(255), nullable=True)  
    resume = Column(String(255), nullable=True)
    cv_link = Column(String(255), nullable=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), index=True, nullable=False)

    candidate = relationship("Candidate", back_populates="details")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


