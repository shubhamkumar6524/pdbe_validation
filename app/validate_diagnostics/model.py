from typing import Any, Dict
from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    case_id: str = Field(..., description="Unique case ID referencing ingested payload")


class ValidationResponse(BaseModel):
    result: Dict[str, Any]  # The final nested JSON keyed by "PDBE <case_id>"
