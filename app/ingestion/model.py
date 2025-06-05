# app/ingestion/model.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class PDBEIngestInput(BaseModel):
    case_id: str = Field(..., description="Unique PDBE Case ID")
    pdbe: Dict[str, Any] = Field(..., description="Raw PDBE JSON payload")

class PromptSetInput(BaseModel):
    question_1_system_prompt: str
    question_1_user_prompt: str
    question_2_system_prompt: str
    question_2_user_prompt: str
    question_3_system_prompt: str
    question_3_user_prompt: str
    question_4_system_prompt: str
    question_4_user_prompt: str
    question_5_system_prompt: str
    question_5_user_prompt: str
    question_6_system_prompt: str
    question_6_user_prompt: str
    created_by: Optional[str] = None
