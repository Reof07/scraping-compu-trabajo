import os
import tempfile
from datetime import datetime

from fastapi.responses import FileResponse
from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import exc

from openpyxl import Workbook

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

async def _save_candidates_batch(candidates_batch: list):
    """
    
    Save a batch of candidates to the database avoiding duplicates.
    Updates existing records if they exist, or creates them if they don't.
    

    Args: 
        candidates_batch: List of candidate dictionaries.
        db: Active database session.
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


async def save_candidate_details_batch(candidate_details_batch: list):
    """
    Save a batch of candidate details to the database avoiding duplicates.
    Updates existing records if they exist, or creates them if they don't.
    
    Args:
        candidate_details_batch: List of candidate details dictionaries.
        db: Active database session.
    """
    db = SessionLocal()
    try:
        for details in candidate_details_batch:
            # Verificar si ya existe el registro
            existing_details = db.query(CandidateDetail).filter(
                CandidateDetail.uuid_candidate == details['uuid_candidate']
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
                    uuid_candidate=details["uuid_candidate"],
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


async def get_candidates_by_offer(
    uuid_offer: str,
    db: Session,
    page: int = 1,
    page_size: int = 10,
    ):
    """ Get all candidates of an offer with pagination, along with their details. """
    
    offset = (page - 1) * page_size
    candidates = (
            db.query(Candidate)
            .filter(Candidate.uuid_offer == uuid_offer)
            .offset(offset)
            .limit(page_size)
            .all()
        )

    if not candidates:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron candidatos para esta oferta."
        )

    total_candidates = (
            db.query(Candidate)
            .filter(Candidate.uuid_offer == uuid_offer)
            .count()
        )

    response = []
    for candidate in candidates:
        candidate_details = (
            db.query(CandidateDetail)
            .filter(CandidateDetail.uuid_candidate == candidate.uuid_candidate)
            .first()
        )

        candidate_data = {
                "id": candidate.id,
                "name": candidate.name,
                "application_date": candidate.application_date,
                "age": candidate.age,
                "education_level": candidate.education_level,
                "suitability": candidate.suitability,
                "details_link": candidate.details_link,
                "uuid_offer": candidate.uuid_offer,
                "uuid_candidate": candidate.uuid_candidate,
                "details": {
                    "email": candidate_details.email if candidate_details else None,
                    "id_number": candidate_details.id_number if candidate_details else None,
                    "mobile_phone": candidate_details.mobile_phone if candidate_details else None,
                    "landline_phone": candidate_details.landline_phone if candidate_details else None,
                    "location": candidate_details.location if candidate_details else None,
                    "marital_status": candidate_details.marital_status if candidate_details else None,
                    "availability_to_travel": candidate_details.availability_to_travel if candidate_details else None,
                    "availability_to_move": candidate_details.availability_to_move if candidate_details else None,
                    "net_monthly_salary": candidate_details.net_monthly_salary if candidate_details else None,
                    "languages": candidate_details.languages if candidate_details else None,
                    "resume": candidate_details.resume if candidate_details else None,
                    "cv_link": candidate_details.cv_link if candidate_details else None,
                },
            }
        response.append(candidate_data)

    return {
            "page": page,
            "page_size": page_size,
            "total_candidates": total_candidates,
            "total_pages": (total_candidates + page_size - 1) // page_size,
            "candidates": response,
        }
