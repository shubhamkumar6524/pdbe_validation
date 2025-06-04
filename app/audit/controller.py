from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session

from app.shared.authentication import AzureBearerAuthentication
from app.config import settings
from app.model import CustomException
from .models_db import AuditLog
from .service import AuditService

router = APIRouter()

# Dependency to get a DB session (for querying logs)
def get_db():
    db = settings.get_pg_session()()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/logs",
    tags=["Audit"],
    summary="Fetch audit logs (paginated)",
    dependencies=[Depends(AzureBearerAuthentication())],
)
def get_audit_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of audit logs, ordered by timestamp descending.
    """
    try:
        query = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)
        logs = query.all()
        result = []
        for log in logs:
            result.append(
                {
                    "id": log.id,
                    "username": log.username,
                    "path": log.path,
                    "method": log.method,
                    "request_body": log.request_body,
                    "response_body": log.response_body,
                    "status_code": log.status_code,
                    "timestamp": log.timestamp.isoformat(),
                }
            )
        return {"logs": result, "offset": offset, "limit": limit}
    except Exception as e:
        raise CustomException(f"Failed to fetch audit logs: {e}")
