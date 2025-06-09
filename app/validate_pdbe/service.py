# app/validate_pdbe/service.py

import json
import httpx
from datetime import datetime
from loguru import logger

from app.config import settings
from app.shared.utils import get_dummy_pdbe
from app.shared.cosmos_client import cosmos_client
from app.shared.llm_service import llm_service
from app.shared.postgres_client import postgres_client

class ValidatePDBEService:
    """
    1) Fetch PDBE from ServiceMax (or dummy).
    2) If audit enabled, store raw PDBE in Cosmos.
    3) Run all 14 LLM agents.
    4) If audit enabled, update raw Cosmos doc with 'validation' and insert into Postgres.
    5) Return the merged JSON.
    """

    async def fetch_pdbe_from_servicemax(self, case_id: str) -> dict:
        base = settings.get_servicemax_base_url().rstrip("/")
        if not base:
            raise RuntimeError("SERVICEMAX_BASE_URL not configured.")
        url = f"{base}/pdbe/{case_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
            else:
                raise RuntimeError(f"ServiceMax returned {resp.status_code}: {resp.text}")

    async def fetch_pdbe(self, case_id: str) -> str:
        # 1) Dummy override?
        if settings.use_dummy_pdbe():
            return get_dummy_pdbe()["pdbe"]

        # 2) Real fetch
        pdbe_obj = await self.fetch_pdbe_from_servicemax(case_id)
        pdbe_payload = pdbe_obj.get("pdbe")
        if pdbe_payload is None:
            raise ValueError(f"No 'pdbe' in ServiceMax response for {case_id}")

        # 3) Audit: store raw PDBE JSON
        if settings.is_audit_enabled():
            try:
                await cosmos_client.upsert_item(
                    settings.get_cosmos_container_raw(),
                    {
                        "id": case_id,
                        "pdbe": pdbe_payload,
                        "created_on": datetime.utcnow().isoformat()
                    }
                )
            except Exception as e:
                logger.error(f"[ValidatePDBEService] Cosmos upsert raw failed: {e}")

        # 4) Flatten dict→string or return string
        if isinstance(pdbe_payload, dict):
            # join all values
            return " ".join(str(v) for v in pdbe_payload.values())
        elif isinstance(pdbe_payload, str):
            return pdbe_payload
        else:
            return str(pdbe_payload)

    async def validate_and_store(self, case_id: str) -> dict:
        # Fetch and normalize PDBE text
        pdbe_text = await self.fetch_pdbe(case_id)

        # Run the 14 LLM agents concurrently
        merged = await llm_service.validate_pdbe_all(pdbe_text)

        # If auditing, write 'validation' back to Cosmos and to Postgres
        if settings.is_audit_enabled():
            raw_container = settings.get_cosmos_container_raw()
            try:
                raw_doc = await cosmos_client.read_item(raw_container, case_id)
                if raw_doc:
                    raw_doc["validation"] = merged
                    await cosmos_client.upsert_item(raw_container, raw_doc)
                else:
                    logger.warning(f"[ValidatePDBEService] No raw doc found for {case_id}")
                # Postgres insert/update
                await postgres_client.insert_pdbe_validation(case_id, merged)
            except Exception as e:
                logger.error(f"[ValidatePDBEService] DB write error: {e}")
        else:
            logger.info("[ValidatePDBEService] Skipping DB writes (audit disabled)")

        return merged
