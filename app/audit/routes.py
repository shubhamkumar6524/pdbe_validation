# app/audit/routes.py

from fastapi import FastAPI
from app.config import settings
from app.audit.controller import router as audit_router

BASE_ROUTE = "audit"

def register_routes(app: FastAPI, root: str = None):
    if not root:
        root = settings.get_root_path()
    app.include_router(audit_router, prefix=f"{root}/{BASE_ROUTE}")
