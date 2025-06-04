from fastapi import APIRouter
from loguru import logger
from .config import settings

from .validate_diagnostics.routes import register_routes as rdv_routes
from .ingestion.routes import register_routes as ing_routes
from .audit.routes import register_routes as audit_routes

router = APIRouter()


@router.get("/", tags=["Health"])
async def root_healthcheck():
    return {"healthcheck": True}


@router.get("/readyz", tags=["Health"])
async def readyz():
    return {"status": "ok"}


def register_app_routes(app, root=settings.get_root_path()):
    app.include_router(router, prefix="", tags=["Health"])
    rdv_routes(app)
    ing_routes(app)
    audit_routes(app)


def register_routes(app):
    logger.info("Registering all routes")
    register_app_routes(app)
