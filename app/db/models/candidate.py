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

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    application_date = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    education_level = Column(String(255), nullable=True)
    suitability = Column(String(255), nullable=True)
    details_link = Column(String(255), nullable=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), index=True, nullable=True)
    uuid_offer = Column(String(255), nullable=True, index=True)
    uuid_candidate = Column(String(255), index=True, nullable=True)

    offer = relationship("Offer", back_populates="candidates")
    
    details = relationship('CandidateDetail', back_populates='candidate')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    

