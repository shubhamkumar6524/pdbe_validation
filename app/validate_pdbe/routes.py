# app/validate_pdbe/routes.py

from fastapi import FastAPI
from app.config import settings
from app.validate_pdbe.controller import router as validate_pdbe_router

BASE_ROUTE = "validate_pdbe"

def register_routes(app: FastAPI, root: str = None):
    if not root:
        root = settings.get_root_path()
    app.include_router(
        validate_pdbe_router, prefix=f"{root}/{BASE_ROUTE}")
