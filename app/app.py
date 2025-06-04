import yaml
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.openapi.utils import get_openapi
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from loguru import logger
from datetime import datetime

from .config import settings
from .model import CustomException
from .routes import register_routes
from .validate_diagnostics.models_db import Base as ValidationBase
from .audit.models_db import Base as AuditBase
from sqlalchemy.exc import OperationalError

from .audit.service import AuditService
from typing import Callable


def create_app():
    app = FastAPI(
        title=settings.get_project_name(),
        description=settings.get_project_description(),
        version=settings.get_project_version(),
        docs_url=settings.get_doc_url(),
        redoc_url=settings.get_redoc_url(),
        openapi_url=settings.get_openapi_json_url(),
    )

    # CORS (allow all for now; lock down in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    # Azure AD JWT authentication
    from .shared.authentication import AzureBearerAuthentication

    app.add_middleware(AuthenticationMiddleware, backend=AzureBearerAuthentication())

    # On startup: create PostgreSQL tables if they don't exist
    try:
        engine = settings._get_pg_engine()
        ValidationBase.metadata.create_all(bind=engine)
        AuditBase.metadata.create_all(bind=engine)
    except OperationalError as e:
        logger.error(f"Failed to create tables on startup: {e}")

    # Register all routes (Ingestion, Validation, Audit, Health)
    register_routes(app)

    # Audit middleware: logs every request/response into PostgreSQL
    @app.middleware("http")
    async def audit_middleware(request: Request, call_next: Callable):
        response: Response = await call_next(request)

        # Extract authenticated username if available
        username = None
        try:
            user = request.state.user
            if user and hasattr(user, "preferred_username"):
                username = user.preferred_username
            elif user and hasattr(user, "display_name"):
                username = user.display_name
        except Exception:
            username = None

        try:
            await AuditService().from_request_response(request, response, username)
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")

        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        status_code = exc.status_code if isinstance(exc, CustomException) else HTTP_500_INTERNAL_SERVER_ERROR
        detail = exc.detail if isinstance(exc, CustomException) else "Internal Server Error."
        if status_code == HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(f"{request.client.host}:{request.client.port} >> {request.method} >> {request.url.path} >> 500 >> {str(exc)}")
        else:
            logger.warning(f"{request.client.host}:{request.client.port} >> {request.method} >> {request.url.path} >> {status_code} >> {str(exc)}")
        return JSONResponse(
            status_code=status_code,
            content={
                "status_code": status_code,
                "message": detail,
                "path": request.url.path,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @app.get("/openapi.yaml", include_in_schema=False)
    async def get_openapi_yaml():
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        yaml_content = yaml.dump(openapi_schema, sort_keys=False)
        return PlainTextResponse(content=yaml_content)

    return app


app = create_app()
