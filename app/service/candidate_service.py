from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import exc

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

# async def _save_candidates_batch(candidates_batch: list):
#     """
#     Guarda un lote de candidatos en la base de datos.
    
#     Args:
#         db: Sesión de la base de datos.
#         candidates_batch: Lista de candidatos a guardar.
#     """
#     db = SessionLocal()
#     try:
#         db.bulk_insert_mappings(Candidate, candidates_batch)
#         db.commit()
#         logger.info(f"Guardado un lote de {len(candidates_batch)} candidatos.")
#     except exc.SQLAlchemyError as e:
#         db.rollback()
#         logger.error(f"Error al guardar el lote: {e}")
#         db.close()

async def _save_candidates_batch(candidates_batch: list):
    """
    Guarda un lote de candidatos en la base de datos evitando duplicados.
    Actualiza los registros si ya existen, o los crea si no.

    Args:
        candidates_batch: Lista de candidatos a guardar.
    """
    db = SessionLocal()
    try:
        for candidate in candidates_batch:
            existing_candidate = db.query(Candidate).filter(Candidate.uuid_candidate == candidate['uuid_candidate']).first()
            
            if existing_candidate:
                existing_candidate.name = candidate['name']
                existing_candidate.application_date = candidate['application_date']
                existing_candidate.age = candidate['age']
                existing_candidate.education_level = candidate['education_level']
                existing_candidate.suitability = candidate['suitability']
                existing_candidate.details_link = candidate['details_link']
                existing_candidate.uuid_offer = candidate['uuid_offer']
                existing_candidate.updated_at = datetime.now()

                db.commit()
            else:
                new_candidate = Candidate(
                    name=candidate['name'],
                    application_date=candidate['application_date'],
                    age=candidate['age'],
                    education_level=candidate['education_level'],
                    suitability=candidate['suitability'],
                    details_link=candidate['details_link'],
                    uuid_offer=candidate['uuid_offer'],
                    uuid_candidate=candidate['uuid_candidate'],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(new_candidate)
                db.commit()

        logger.info(f"Guardado o actualizado un lote de {len(candidates_batch)} candidatos.")
    except exc.SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al guardar o actualizar el lote: {e}")
    finally:
        db.close()


# async def save_candidate_details(driver, candidate_details, id_candidate, db: Session):
#     """
#     Extrae los detalles de un candidato desde un enlace y los guarda en la base de datos.

#     :param driver: Instancia activa de Selenium WebDriver.
#     :param candidate_details_link: URL con los detalles del candidato.
#     :param id_candidate: ID del candidato para asociarlo a los detalles.
#     :param db: Sesión activa de la base de datos.
#     :return: Objeto de los detalles del candidato guardados en la base de datos.
#     """

#     # Crear un objeto CandidateDetails
#     candidate_details_record = CandidateDetail(
#         email=candidate_details.get("email"),
#         id_number=candidate_details.get("id_number"),
#         mobile_phone=candidate_details.get("mobile_phone"),
#         landline_phone=candidate_details.get("landline_phone"),
#         location=candidate_details.get("location"),
#         marital_status=candidate_details.get("marital_status"),
#         availability_to_travel=candidate_details.get("availability_to_travel"),
#         availability_to_move=candidate_details.get("availability_to_move"),
#         net_monthly_salary=candidate_details.get("net_monthly_salary"),
#         resume=None,  # Aquí puedes agregar lógica si quieres extraer el 'resume'
#         cv_link=candidate_details.get("cv_link"),
#         candidate_id=id_candidate,  # Relacionar con el candidato correcto
#         created_at=datetime.now(),
#         updated_at=datetime.now()
#     )
    
#     # Guardar el registro en la base de datos
#     db.add(candidate_details_record)
#     db.commit()  # Confirmar los cambios

#     print(f"Detalles del candidato con ID {id_candidate} guardados exitosamente.")

#     return candidate_details_record


async def save_candidate_details_batch(candidate_details_batch: list):
    """
    Guarda un lote de detalles de candidatos en la base de datos evitando duplicados.
    Actualiza los registros si ya existen, o los crea si no.

    :param candidate_details_batch: Lista de diccionarios con detalles de candidatos.
    :param db: Sesión activa de la base de datos.
    """
    db = SessionLocal()
    try:
        for details in candidate_details_batch:
            # Verificar si ya existe el registro
            existing_details = db.query(CandidateDetail).filter(
                CandidateDetail.candidate_id == details['candidate_id']
            ).first()

            #get uuid_candidate
            

            if existing_details:
                # Actualizar los campos existentes
                existing_details.email = details.get("email", existing_details.email)
                existing_details.id_number = details.get("id_number", existing_details.id_number)
                existing_details.mobile_phone = details.get("mobile_phone", existing_details.mobile_phone)
                existing_details.landline_phone = details.get("landline_phone", existing_details.landline_phone)
                existing_details.location = details.get("location", existing_details.location)
                existing_details.marital_status = details.get("marital_status", existing_details.marital_status)
                existing_details.availability_to_travel = details.get(
                    "availability_to_travel", existing_details.availability_to_travel
                )
                existing_details.availability_to_move = details.get(
                    "availability_to_move", existing_details.availability_to_move
                )
                existing_details.net_monthly_salary = details.get(
                    "net_monthly_salary", existing_details.net_monthly_salary
                )
                existing_details.cv_link = details.get("cv_link", existing_details.cv_link)
                existing_details.updated_at = datetime.now()
            else:
                # Crear un nuevo registro
                new_details = CandidateDetail(
                    email=details.get("email"),
                    id_number=details.get("id_number"),
                    mobile_phone=details.get("mobile_phone"),
                    landline_phone=details.get("landline_phone"),
                    location=details.get("location"),
                    marital_status=details.get("marital_status"),
                    availability_to_travel=details.get("availability_to_travel"),
                    availability_to_move=details.get("availability_to_move"),
                    net_monthly_salary=details.get("net_monthly_salary"),
                    resume=None,  # Lógica para extraer el resumen, si es necesario
                    cv_link=details.get("cv_link"),
                    uuid_candidate=details["candidate_id"],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                db.add(new_details)

        # Confirmar los cambios en un solo commit para todo el lote
        db.commit()
        print(f"Guardado o actualizado un lote de {len(candidate_details_batch)} detalles de candidatos.")
    except Exception as e:
        db.rollback()
        print(f"Error al guardar o actualizar el lote: {e}")
    finally:
        db.close()
