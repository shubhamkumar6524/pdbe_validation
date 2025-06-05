# app/validate_pdbe/model.py

from pydantic import BaseModel, Field
from typing import Dict, Any

class ValidatePDBERequest(BaseModel):
    case_id: str = Field(..., description="Case ID to validate")

class ValidatePDBEResponse(BaseModel):
    data: Dict[str, Any]
    message: str = "Validation complete"
    status_code: int = 200
