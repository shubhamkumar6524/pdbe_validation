from fastapi import APIRouter, Body
from app.ingestion.model import IngestionInput, DocumentUploadResponse, FetchDocumentsResponse
from app.ingestion.service import IngestionService

router = APIRouter()
service = IngestionService()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    tags=["Ingestion"],
    summary="Upload a ServiceMax JSON payload for a given case_id",
)
async def upload_document(request: IngestionInput = Body(...)):
    """
    Ingests a ServiceMax JSON payload under the provided case_id.
    """
    result = service.ingest_document(request.case_id, request.payload)
    return DocumentUploadResponse(case_id=result["case_id"], upload_timestamp=result["timestamp"])


@router.get(
    "/{case_id}",
    response_model=FetchDocumentsResponse,
    tags=["Ingestion"],
    summary="Fetch a document by case_id",
)
async def get_document(case_id: str):
    doc = service.get_document(case_id)
    return FetchDocumentsResponse(documents=[doc])
