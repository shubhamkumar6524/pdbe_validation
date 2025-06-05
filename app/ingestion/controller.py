# app/ingestion/controller.py

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from app.ingestion.model import PDBEIngestInput, PromptSetInput
from app.ingestion.service import IngestionService
from app.model import BaseResponseModel

router = APIRouter()

@router.post("/pdbe", response_model=BaseResponseModel, tags=["Ingestion"])
async def ingest_pdbe(data: PDBEIngestInput, svc: IngestionService = Depends()):
    success = await svc.ingest_pdbe(case_id=data.case_id, pdbe_payload=data.pdbe)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest PDBE")
    return BaseResponseModel(message="PDBE ingested successfully")

@router.post("/prompts", response_model=BaseResponseModel, tags=["Ingestion"])
async def ingest_prompts(data: PromptSetInput, svc: IngestionService = Depends()):
    prompt_dict = data.dict(exclude={"created_by"})
    success = await svc.ingest_prompts(prompt_dict, created_by=data.created_by)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest prompts")
    return BaseResponseModel(message="Prompts ingested successfully")
