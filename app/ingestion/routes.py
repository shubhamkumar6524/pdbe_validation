# app/ingestion/routes.py

from fastapi import FastAPI
from app.config import settings
from app.ingestion.controller import router as ingestion_router

BASE_ROUTE = "ingestion"

def register_routes(app: FastAPI, root: str = None):
    if not root:
        root = settings.get_root_path()
    app.include_router(ingestion_router, prefix=f"{root}/{BASE_ROUTE}")
