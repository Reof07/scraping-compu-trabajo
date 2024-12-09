import logging

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware


from .core.config import settings
from .api.routers.base_router import base_router
from .db.database import engine
from .db.database import Base
from .db.models import *


app = FastAPI(
    title="Base FastAPI Project",
    description="""
### Base FastAPI Project

This service provides the following functionalities:
1. **Create new users** – Easily create new users with unique email addresses.
2. **Athentication** – Securely authenticate users with their email address and password.

By following the steps below, you can create a new user and authenticate them.🚀
""",
    version="v0.1.0",
)

# Configuración de CORS: restringir a los orígenes permitidos en producción
origins = [
    "http://127.0.0.1:8000/",
    "http://18.189.100.75",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app.include_router(base_router)

# Endpoint de información general
@app.get("/info")
def read_root():
    return {
        "message": f" Hello, World! the app: {settings.APP_NAME} is Running in {settings.FASTAPI_ENV} mode."}
