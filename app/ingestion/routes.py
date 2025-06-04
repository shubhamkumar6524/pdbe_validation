from fastapi import FastAPI
from app.config import settings
from .controller import router as ingestion_router

BASE_ROUTE = "ingestion"


def register_routes(app: FastAPI):
    app.include_router(ingestion_router, prefix=f"{settings.get_root_path()}/{BASE_ROUTE}")
