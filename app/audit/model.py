# app/audit/model.py

from pydantic import BaseModel
from typing import Optional, Dict, Any

class AuditInput(BaseModel):
    endpoint: str
    request_body: Dict[str, Any]
    response_body: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
