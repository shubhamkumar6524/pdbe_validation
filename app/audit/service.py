import json
from fastapi import Request, Response
from sqlalchemy.orm import Session
from loguru import logger

from app.config import settings
from .models_db import AuditLog
from .model import AuditLogInput


class AuditService:
    """
    Writes incoming request/response details into the `audit_logs` table in PostgreSQL.
    """

    def __init__(self):
        self.SessionLocal = settings.get_pg_session()

    def log(self, audit_input: AuditLogInput):
        db: Session = self.SessionLocal()
        try:
            record = AuditLog(
                username=audit_input.username,
                path=audit_input.path,
                method=audit_input.method,
                request_body=audit_input.request_body,
                response_body=audit_input.response_body,
                status_code=audit_input.status_code,
                timestamp=audit_input.timestamp,
            )
            db.add(record)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to insert audit log: {e}")
        finally:
            db.close()

    async def from_request_response(self, request: Request, response: Response, username: str):
        path = request.url.path
        method = request.method

        # Extract request body JSON
        request_body = None
        try:
            if request.headers.get("content-type", "").lower().startswith("application/json"):
                body_bytes = await request.body()
                if body_bytes:
                    request_body = json.loads(body_bytes)
        except Exception:
            request_body = None

        # Extract response body JSON
        response_body = None
        try:
            if response.media_type and "application/json" in response.media_type:
                if isinstance(response.body, (bytes, str)):
                    body_bytes = response.body if isinstance(response.body, bytes) else response.body.encode()
                    if body_bytes:
                        response_body = json.loads(body_bytes)
        except Exception:
            response_body = None

        status_code = response.status_code

        audit_input = AuditLogInput(
            username=username,
            path=path,
            method=method,
            request_body=request_body,
            response_body=response_body,
            status_code=status_code,
        )
        self.log(audit_input)
