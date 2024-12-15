from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
    Header
    )
from fastapi.responses import FileResponse

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
    )
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
    "/export-cv-excel",
    summary="Export candidates information to Excel",
    description="Export list the curriculum vitae of the candidates.",
    )
async def export_cv_excel(
    current_user: str = Depends(validate_token),
    db: Session = Depends(get_db)
):
    return FileResponse(
        path="file_path",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="candidates_export.xlsx",
    )