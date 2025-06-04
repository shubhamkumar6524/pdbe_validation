from typing import Any, Dict, List
from pydantic import BaseModel, Field


class IngestionInput(BaseModel):
    case_id: str = Field(..., description="Unique case ID")
    payload: Dict[str, Any] = Field(
        ..., description="Full ServiceMax JSON payload representing checklist data"
    )


class DocumentUploadResponse(BaseModel):
    case_id: str
    upload_timestamp: str


class DocumentRecord(BaseModel):
    case_id: str
    payload: Dict[str, Any]
    timestamp: str


class FetchDocumentsResponse(BaseModel):
    documents: List[DocumentRecord]
