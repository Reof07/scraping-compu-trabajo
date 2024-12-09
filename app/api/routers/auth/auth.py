from fastapi import( 
    APIRouter,
    status,
    Depends,
    HTTPException
    )

from sqlalchemy.orm import Session

from ....db.database import get_db
from ....schemas.user_schema import  UserRegister
from ....schemas.generic import GenericResponse
from ....service.user_service import register_user

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],    
    responses={404: {"description": "Not found"}},
)

@auth_router.post(
    "/signin",
    summary="signin",
    description="signin",
)
async def signin():
    return {"message": "Hello, World! Login"}


@auth_router.post(
    "/signup",
    summary="signup",
    description="signup",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: UserRegister,
    db: Session = Depends(get_db)
) -> GenericResponse:
    try:
        user_registered = await register_user(user, db)
        return GenericResponse(
            message="Successfully created the user",
            data={"user_registered": user_registered}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
