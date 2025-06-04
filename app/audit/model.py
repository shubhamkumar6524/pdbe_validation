from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any


class AuditLogInput(BaseModel):
    username: Optional[str] = Field(None, description="Authenticated username")
    path: str = Field(..., description="API path")
    method: str = Field(..., description="HTTP method")
    request_body: Optional[Any] = Field(None, description="Parsed request JSON body")
    response_body: Optional[Any] = Field(None, description="Parsed response JSON body")
    status_code: int = Field(..., description="HTTP status code of response")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.utcnow(), description="Timestamp")
