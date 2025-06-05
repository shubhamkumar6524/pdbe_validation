# app/routes.py

import asyncio
from fastapi.routing import APIRoute
from fastapi import APIRouter, FastAPI
from starlette.requests import Request
from fastapi.responses import Response
from time import time
from loguru import logger

from app.config import settings
from app.audit.service import AuditService

from app.config import settings

# Health‐check router
router = APIRouter()

@router.get("/", tags=["Health"])
async def root_health():
    return {"healthcheck": "PDBE Validation API is up"}

@router.get("/readyz", tags=["Health"])
async def ready_health():
    return {"status": "ready"}

@router.get("/healthcheck", tags=["Health"])
async def health_check():
    return {"status": "ok"}

def register_app_routes(app: FastAPI, root: str = None):
    if not root:
        root = settings.get_root_path()
    app.include_router(router, prefix="")  # health routes at root

def register_routes(app: FastAPI):
    logger.info("Registering all app & module routes.")
    register_app_routes(app)

    from app.audit.routes import register_routes as register_audit_routes
    from app.ingestion.routes import register_routes as register_ingestion_routes
    from app.validate_pdbe.routes import register_routes as register_validate_pdbe_routes

    register_ingestion_routes(app)      # /api/pdbe/ingestion/...
    register_validate_pdbe_routes(app)  # /api/pdbe/validate_pdbe
    register_audit_routes(app)          # /api/pdbe/audit


class CustomRoute(APIRoute):
    def get_route_handler(self):
        original_route = super().get_route_handler()
        async def audited_route(request: Request):
            start_time = time()
            response = await original_route(request)
            if settings.is_audit_enabled():
                try:
                    asyncio.create_task(AuditService().audit(request=request, response=response))
                except Exception as e:
                    logger.error(f"[CustomRoute] Error scheduling audit: {e}")
            end_time = time()
            logger.info(f"Processed {request.method} {request.url.path} in {(end_time - start_time):.3f}s")
            return response
        return audited_route
