# app/app.py

from datetime import datetime
import yaml
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.openapi.utils import get_openapi

from .config import settings
from .model import CustomException
from .routes import register_routes

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.get_project_name(),
        description=settings.get_project_description(),
        version=settings.get_project_version(),
        docs_url=settings.get_doc_url(),
        redoc_url=settings.get_redoc_url(),
        openapi_url=settings.get_openapi_json_url()
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    register_routes(app)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        host = getattr(getattr(request, "client", None), "host", None)
        port = getattr(getattr(request, "client", None), "port", None)
        url = __get_request_url(request)
        message = str(exc) if isinstance(exc, CustomException) else "Internal Server Error."
        status_code = exc.status_code if isinstance(exc, CustomException) else HTTP_500_INTERNAL_SERVER_ERROR
        log_message = f"{host}:{port} >> {request.method} >> {status_code} >> {url} >> Exception >> {str(exc)}"
        if status_code == HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(log_message)
        else:
            logger.warning(log_message)

        response_content = {
            "status_code": status_code,
            "message": message,
            "path": url,
            "timestamp": datetime.utcnow().isoformat()
        }
        return JSONResponse(content=response_content, status_code=status_code)

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

def __get_request_url(request: Request) -> str:
    return f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
