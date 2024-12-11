from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ...db.database import Base

class Candidate(Base):
    """ Candidate model
    
    Args:
        Base (Base): Base clase de SQLAlchemy
        
    Returns:
        class 'models.Candidate': Candidate model
    """
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    application_date = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    education_level = Column(String(255), nullable=True)
    suitability = Column(String(255), nullable=True)
    details_link = Column(String(255), nullable=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=True)
    uuid_offer = Column(String(255), nullable=True)
    offer = relationship("Offer", back_populates="candidates")
    details = relationship('CandidateDetail', back_populates='candidate')

