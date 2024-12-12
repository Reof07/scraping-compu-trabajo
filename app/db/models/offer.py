from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ...db.database import Base

class Offer(Base):
    """ Offer model
    
    Args:
        Base (Base): Base clase de SQLAlchemy
        
    Returns:
        class  'models.Offer': Offer model
    """
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, unique=True)
    offer_id = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    last_update = Column(String(255), nullable=True)
    views = Column(Integer, nullable=True)
    expiration_date = Column(String(255), nullable=True)
    applicants_count = Column(Integer, nullable=True)
    applicants_link = Column(String(255), nullable=True)  
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    user = relationship("User", back_populates="offers")
    candidates = relationship('Candidate', back_populates='offer')
    status = Column(String(255), nullable=True)