from datetime import datetime
from fastapi import HTTPException
from loguru import logger

from app.shared.exceptions import BadRequestException
from app.config import settings

from azure.cosmos.exceptions import CosmosResourceNotFoundError


class IngestionService:
    """
    Stores incoming ServiceMax JSON payloads into Cosmos DB container "inputs_outputs".
    """

    def __init__(self):
        self.container = settings.get_io_container()

    def ingest_document(self, case_id: str, payload: dict) -> dict:
        # Upsert item into Cosmos DB
        item = {
            "id": case_id,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
        try:
            self.container.upsert_item(item)
        except Exception as e:
            logger.error(f"Cosmos DB upsert failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to store document.")
        return {"case_id": case_id, "timestamp": item["timestamp"]}

    def get_document(self, case_id: str) -> dict:
        try:
            resp = self.container.read_item(item=case_id, partition_key=case_id)
            return {"case_id": resp["id"], "payload": resp["payload"], "timestamp": resp["timestamp"]}
        except CosmosResourceNotFoundError:
            raise BadRequestException(f"No document found for case_id {case_id}")
        except Exception as e:
            logger.error(f"Cosmos DB read failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch document.")
