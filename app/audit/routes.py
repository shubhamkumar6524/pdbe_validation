from fastapi import FastAPI
from app.config import settings
from .controller import router as audit_router

BASE_ROUTE = "audit"


def register_routes(app: FastAPI):
    app.include_router(audit_router, prefix=f"{settings.get_root_path()}/{BASE_ROUTE}")
