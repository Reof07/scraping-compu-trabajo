from ..database import engine, Base
from ...core.logger_config import logger 
from ..models.user import User
from ..models.offer import Offer
from ..models.candidate import Candidate
from ..models.candidate_detail import CandidateDetail

def init_db():
    """Create the database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
