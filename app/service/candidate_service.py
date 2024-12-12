import datetime

from sqlalchemy.orm import Session

from ..db.models.candidate import Candidate
from ..db.models.candidate_detail import CandidateDetail
from ..db.database import SessionLocal
from ..core.logger_config import logger

def create_candidate(db: Session, offer_id: str, candidate_data: dict):
    """
    Function to create a candidate and associate it with a job offer.
    
    Args:
        db: Database session.
        offer_id: ID of the job offer.
        candidate_data: Candidate data in the form of a dictionary.
        
    Returns:
    """
    #TODO: intentar crear una conexion de base de datos aqui y evitar reciir una
    # print(f"candidate_data: {candidate_data}")
    # print(f"offer_id: {offer_id}")
    
    #crear session
    db = SessionLocal()
    try:
        candidate = Candidate(
            name=candidate_data["name"],
            application_date=candidate_data["applied_date"],
            age=candidate_data["age"],
            education_level=candidate_data["studies"],
            suitability=candidate_data["adequacy"],
            details_link=candidate_data["profile_link"],
            # offer_id="",
            uuid_offer=offer_id,
            uuid_candidate=candidate_data["candidate_id"],
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate
    except Exception as e:
        # Log error if something goes wrong during candidate creation or update
        logger.error(f"Error al crear o actualizar el candidato: {e}")
        return None
    finally:
        db.close()



def save_candidate_details(driver, candidate_details, id_candidate, db: Session):
    """
    Extrae los detalles de un candidato desde un enlace y los guarda en la base de datos.

    :param driver: Instancia activa de Selenium WebDriver.
    :param candidate_details_link: URL con los detalles del candidato.
    :param id_candidate: ID del candidato para asociarlo a los detalles.
    :param db: Sesión activa de la base de datos.
    :return: Objeto de los detalles del candidato guardados en la base de datos.
    """

    # Crear un objeto CandidateDetails
    candidate_details_record = CandidateDetail(
        email=candidate_details.get("email"),
        id_number=candidate_details.get("id_number"),
        mobile_phone=candidate_details.get("mobile_phone"),
        landline_phone=candidate_details.get("landline_phone"),
        location=candidate_details.get("location"),
        marital_status=candidate_details.get("marital_status"),
        availability_to_travel=candidate_details.get("availability_to_travel"),
        availability_to_move=candidate_details.get("availability_to_move"),
        net_monthly_salary=candidate_details.get("net_monthly_salary"),
        resume=None,  # Aquí puedes agregar lógica si quieres extraer el 'resume'
        cv_link=candidate_details.get("cv_link"),
        candidate_id=id_candidate,  # Relacionar con el candidato correcto
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Guardar el registro en la base de datos
    db.add(candidate_details_record)
    db.commit()  # Confirmar los cambios

    print(f"Detalles del candidato con ID {id_candidate} guardados exitosamente.")

    return candidate_details_record

