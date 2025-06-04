from fastapi import FastAPI
from app.config import settings
from .controller import router as vd_router

BASE_ROUTE = "validate"


def register_routes(app: FastAPI):
    app.include_router(vd_router, prefix=f"{settings.get_root_path()}/{BASE_ROUTE}")
