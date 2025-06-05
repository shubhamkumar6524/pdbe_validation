# app/validate_pdbe/controller.py

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from app.validate_pdbe.model import ValidatePDBERequest, ValidatePDBEResponse
from app.validate_pdbe.service import ValidatePDBEService

router = APIRouter()

@router.post("", response_model=ValidatePDBEResponse, tags=["ValidatePDBE"])
async def validate_pdbe_endpoint(
    payload: ValidatePDBERequest,
    service: ValidatePDBEService = Depends()
):
    try:
        merged = await service.validate_and_store(payload.case_id)
        return ValidatePDBEResponse(data=merged)
    except ValueError as ve:
        logger.error(f"[ValidatePDBE] Not found: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"[ValidatePDBE] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
