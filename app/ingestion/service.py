# app/ingestion/service.py

from datetime import datetime
from loguru import logger

from app.shared.cosmos_client import cosmos_client
from app.config import settings

class IngestionService:
    async def ingest_pdbe(self, case_id: str, pdbe_payload: dict) -> bool:
        container = settings.get_cosmos_container_raw()
        item = {
            "id": case_id,
            "pdbe": pdbe_payload,
            "created_on": datetime.utcnow().isoformat()
        }
        try:
            await cosmos_client.upsert_item(container, item)
            return True
        except Exception as e:
            logger.error(f"[IngestionService] Failed to ingest PDBE {case_id}: {e}")
            return False

    async def ingest_prompts(self, prompt_dict: dict, created_by: str = None) -> bool:
        container = settings.get_cosmos_container_prompts()
        from uuid import uuid4
        item = {
            "id": str(uuid4()),
            "prompts": prompt_dict,
            "created_on": datetime.utcnow().isoformat(),
            "created_by": created_by or ""
        }
        try:
            await cosmos_client.upsert_item(container, item)
            return True
        except Exception as e:
            logger.error(f"[IngestionService] Failed to ingest prompts: {e}")
            return False
