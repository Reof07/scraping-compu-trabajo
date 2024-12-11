from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
    Header
    )
from fastapi.security import (
    OAuth2PasswordBearer,
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
from ....service.user_service import get_user_by_email

# Esquema de seguridad para Bearer Token
bearer_scheme = HTTPBearer()

scraping_router = APIRouter(
    prefix="/scraping",
    tags=["scraping"],
    responses={404: {"description": "Not found"}},
)


def validate_token(
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


@scraping_router.get(
    "/",
    summary="Scrape job offers",
    description="Scrape job offers from the website.",
    )
async def scrape_job_offers(
    current_user: str = Depends(validate_token),
    db: Session = Depends(get_db)
):
    email = current_user
    user = get_user_by_email(db, email)
    user = UserInfo.model_validate(user)
    password = user.password
    print(user)
    
    try:
        driver.get("https://www.google.com")
        print(driver.title)
        await flujo_principal(db, email, password, user.id)
    except Exception as e:
        print(f"Hubo un error en la ejecución principal: {e}")
    return {"message": "Hello, World! Scrape job offers."}
