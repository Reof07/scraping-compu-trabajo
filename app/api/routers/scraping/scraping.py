import os
import tempfile
from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
    Header,
    Query
    )
from fastapi.responses import FileResponse
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
    )

from openpyxl import Workbook
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ....core.selenium import driver
from ....core.config import settings
from ....service.selenium_service import (
    flujo_principal
)
from ....db.database import get_db
from ....schemas.user_schema import UserInfo
from ....schemas.generic import OffersList
from ....service.user_service import get_user_by_email
from ....core.logger_config import logger
from ....db.models.candidate import Candidate
from ....db.models.candidate_detail import CandidateDetail
from ....service.candidate_service import get_candidates_by_offer


bearer_scheme = HTTPBearer()

scraping_router = APIRouter(
    prefix="/scraping",
    tags=["scraping"],
    responses={404: {"description": "Not found"}},
)

#ESTO ES UNA DEPENDENCIA
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> str:
    """Valida el token."""
    
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided."
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: email not found.",
            )

        return email
    except JWTError as e:
        print(f"Error durante la validación del token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
        )
        
@scraping_router.post(
    "/",
    operation_id="scrape_job_offers",
    summary="Scrape job offers",
    description="Scrape job offers from the website.",
    )
async def scrape_job_offers(
    list_offers: OffersList,
    current_user: str = Depends(validate_token),
    db: Session = Depends(get_db)
):
    email = current_user
    user = get_user_by_email(db, email)
    user = UserInfo.model_validate(user)
    password = user.password
    
    try:
        
        await flujo_principal(db, email, password, list_offers)

    except Exception as e:
        logger.error(f"Hubo un error en la ejecución principal: {e}")
    return {"message": "Hello, World! Scrape job offers."}

    
@scraping_router.get(
    "/offers/{uuid_offer}/candidates",
    operation_id="get_candidates_by_offer_paginated",
    summary="Get candidates by offer",
    description="Get all candidates of an offer with pagination, along with their details.",
    response_model=dict)
async def get_candidates_by_offer_paginated(
    uuid_offer: str,
    current_user: str = Depends(validate_token),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all candidates of an offer with pagination, along with their details.
    
    :param uuid_offer: UUID of the offer to search for candidates.
    :param page: Page number (default: 1).
    :param page_size: Number of records per page (default: 10, max. 100).
    :param db: Database session.
    :return: Paginated list of candidates and their details.
    """
    try:
        candidates = await get_candidates_by_offer(uuid_offer, db, page, page_size)        
        return {
            "data": candidates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@scraping_router.get(
    "/offers/{uuid_offer}/candidates/export", 
    operation_id="export_candidates_to_excel",
    summary="Export candidates to Excel",
    description="Export list the curriculum vitae of the candidates.",
    response_description="file Excel with candidates")
async def export_candidates_to_excel(
    uuid_offer: str,
    current_user: str = Depends(validate_token),
    db: Session = Depends(get_db)
):

    try:
        candidates = (
            db.query(Candidate)
            .filter(Candidate.uuid_offer == uuid_offer)
            .all()
        )

        if not candidates:
            raise HTTPException(status_code=404, detail="No se encontraron candidatos para esta oferta.")

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Candidatos"

        headers = [
            "Nombre", "Fecha de Aplicación", "Edad", "Nivel Educativo", "Adecuación",
            "Email", "ID Número", "Teléfono Móvil", "Teléfono Fijo", "Ubicación",
            "Estado Civil", "Disponibilidad para Viajar", "Disponibilidad para Mudarse",
            "Salario Mensual Neto", "Idiomas", "CV Link"
        ]
        sheet.append(headers)

        for candidate in candidates:
            candidate_details = (
                db.query(CandidateDetail)
                .filter(CandidateDetail.uuid_candidate == candidate.uuid_candidate)
                .first()
            )

            row = [
                candidate.name,
                candidate.application_date,
                candidate.age,
                candidate.education_level,
                candidate.suitability,
                candidate_details.email if candidate_details else None,
                candidate_details.id_number if candidate_details else None,
                candidate_details.mobile_phone if candidate_details else None,
                candidate_details.landline_phone if candidate_details else None,
                candidate_details.location if candidate_details else None,
                candidate_details.marital_status if candidate_details else None,
                candidate_details.availability_to_travel if candidate_details else None,
                candidate_details.availability_to_move if candidate_details else None,
                candidate_details.net_monthly_salary if candidate_details else None,
                candidate_details.languages if candidate_details else None,
                candidate_details.cv_link if candidate_details else None,
            ]
            sheet.append(row)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            file_path = temp_file.name
            workbook.save(file_path)

        return FileResponse(
            path=file_path,
            filename=f"candidatos_{uuid_offer}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
