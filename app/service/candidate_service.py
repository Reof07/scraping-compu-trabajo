from sqlalchemy.orm import Session

from ..db.models.candidate import Candidate
from ..db.models.candidate_detail import CandidateDetail

async def create_candidate(db: Session, offer_id: str, candidate_data: dict):
    """
    Function to create a candidate and associate it with a job offer.
    
    Args:
        db: Database session.
        offer_id: ID of the job offer.
        candidate_data: Candidate data in the form of a dictionary.
        
    Returns:
    """

    print(f"candidate_data: {candidate_data}")
    print(f"offer_id: {offer_id}")
    candidate = Candidate(
        name=candidate_data["name"],
        application_date=candidate_data["applied_date"],
        age=candidate_data["age"],
        education_level=candidate_data["studies"],
        suitability=candidate_data["adequacy"],
        details_link=candidate_data["profile_link"],
        # offer_id="",
        uuid_offer=offer_id,
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate



async def create_candidate_detail(db: Session, candidate_id: int, detail_data: dict):
    """
    Function to create the details of a candidate.
    
    Args:
        db: Database session.
        candidate_id: ID of the candidate to which the details will be associated.
        detail_data: Data for the details in the form of a dictionary.
        
    Returns:
        CandidateDetail: Instance of the created candidate details.
    """

    candidate_detail = CandidateDetail(
        email=detail_data.get("email", "Correo no encontrado"),
        id_number=detail_data.get("id_number", "Identificación no encontrada"),
        mobile_phone=detail_data.get("mobile_phone", "Teléfono móvil no encontrado"),
        landline_phone=detail_data.get("landline_phone", "Teléfono fijo no encontrado"),
        location=detail_data.get("location", "Ubicación no encontrada"),
        marital_status=detail_data.get("marital_status", "Estado civil no encontrado"),
        availability_to_travel=detail_data.get("availability_to_travel", "Disponibilidad para viajar no encontrada"),
        availability_to_move=detail_data.get("availability_to_move", "Disponibilidad para cambio de residencia no encontrada"),
        net_monthly_salary=detail_data.get("net_monthly_salary", "Salario neto mensual no encontrado"),
        candidate_id=candidate_id,
        # languages=detail_data["languages"],
        # resume=detail_data["resume"]
    )
    
    db.add(candidate_detail)
    db.commit()
    db.refresh(candidate_detail)
    return candidate_detail
