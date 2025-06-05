# app/shared/audit_dto.py

import json
from datetime import datetime
from uuid import uuid4
from loguru import logger

from app.config import settings
from app.shared.cosmos_client import cosmos_client
from app.shared.postgres_client import postgres_client

class AuditDto:
    def __init__(self):
        self._container = settings.get_cosmos_container_audit()

    async def insert_event(self, endpoint: str, request_payload: dict, response_payload: dict, created_by: str = None):
        event_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat()

        cosmos_item = {
            "id": event_id,
            "endpoint": endpoint,
            "request": request_payload,
            "response": response_payload,
            "created_on": timestamp,
            "created_by": created_by or ""
        }
        try:
            await cosmos_client.upsert_item(self._container, cosmos_item)
        except Exception as e:
            logger.error(f"[AuditDto][Cosmos] Failed to write audit event: {e}")

        if settings.is_audit_enabled():
            try:
                await postgres_client.insert_audit_log(
                    endpoint=endpoint,
                    request_body=request_payload,
                    response_body=response_payload,
                    created_by=created_by
                )
            except Exception as e:
                logger.error(f"[AuditDto][Postgres] Failed to write audit event: {e}")

audit_dto = AuditDto()
