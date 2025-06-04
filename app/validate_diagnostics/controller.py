from fastapi import APIRouter, Body
from app.validate_diagnostics.model import ValidationRequest, ValidationResponse
from app.validate_diagnostics.service import ValidationService

router = APIRouter()
service = ValidationService()


@router.post(
    "/validate_diagnostics",
    response_model=ValidationResponse,
    tags=["Validation"],
    summary="Validate six aspects concurrently against the ingested payload",
)
async def validate_diagnostics(request: ValidationRequest = Body(...)):
    """
    Given a case_id, fetch the ingested payload from Cosmos, then launch six
    concurrent LLM calls (one per aspect). Store the combined nested JSON in PostgreSQL
    and return that nested JSON.
    """
    result = await service.validate(request.case_id)
    return ValidationResponse(result=result)
