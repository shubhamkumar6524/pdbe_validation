# app/validate_pdbe/service.py

import asyncio
import logging
import json

import httpx
from loguru import logger

from app.config import settings
from app.shared.utils import get_dummy_pdbe
from app.shared.cosmos_client import cosmos_client
from app.shared.llm_service import llm_service
from app.shared.postgres_client import postgres_client

class ValidatePDBEService:
    """
    1) Fetch PDBE from ServiceMax middleware (or dummy).
    2) If IS_AUDIT_ENABLED=True, store raw PDBE in Cosmos 'raw_pdbe'.
    3) Run concurrent LLM calls to validate.
    4) If IS_AUDIT_ENABLED=True, update 'raw_pdbe' document to include 'validation' JSON and insert into Postgres.
    5) Return the merged JSON.
    """

    async def fetch_pdbe_from_servicemax(self, case_id: str) -> dict:
        """
        Calls GET {SERVICEMAX_BASE_URL}/pdbe/{case_id} and returns the JSON.
        Adjust if your actual endpoint differs.
        """
        base_url = settings.get_servicemax_base_url().rstrip("/")
        if not base_url:
            raise RuntimeError("SERVICEMAX_BASE_URL not configured.")

        url = f"{base_url}/pdbe/{case_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
            else:
                raise RuntimeError(f"ServiceMax returned {resp.status_code}: {resp.text}")

    async def fetch_pdbe(self, case_id: str) -> str:
        """
        Returns the PDBE text. If USE_DUMMY_PDBE_RESPONSE=True, return dummy.
        Otherwise, fetch from ServiceMax middleware and (optionally) store raw in Cosmos.
        """
        if settings.use_dummy_pdbe():
            obj = get_dummy_pdbe()
            return obj["pdbe"]
        else:
            # Fetch from ServiceMax
            pdbe_obj = await self.fetch_pdbe_from_servicemax(case_id)
            pdbe_payload = pdbe_obj.get("pdbe")
            if pdbe_payload is None:
                raise ValueError(f"No 'pdbe' field in ServiceMax response for case_id={case_id}")

            # If auditing, store raw in Cosmos under container raw_pdbe
            if settings.is_audit_enabled():
                container = settings.get_cosmos_container_raw()
                item = {
                    "id": case_id,
                    "pdbe": pdbe_payload,
                    "created_on": __import__("datetime").datetime.utcnow().isoformat()
                }
                try:
                    await cosmos_client.upsert_item(container, item)
                except Exception as e:
                    logger.error(f"[ValidatePDBEService] Failed to store raw PDBE in Cosmos: {e}")

            # Extract text (if pdbe_payload is dict, flatten; if string, return it)
            if isinstance(pdbe_payload, dict):
                return " ".join(str(v) for v in pdbe_payload.values())
            elif isinstance(pdbe_payload, str):
                return pdbe_payload
            else:
                return str(pdbe_payload)

    async def validate_and_store(self, case_id: str):
        # 1) Fetch PDBE text
        pdbe_text = await self.fetch_pdbe(case_id)

        # 2) Run LLM validations
        merged = await llm_service.validate_pdbe_all(pdbe_text)

        # 3) If auditing, update Cosmos and insert into PostgreSQL
        if settings.is_audit_enabled():
            # 3a) Update raw PDBE doc: add "validation" field
            container = settings.get_cosmos_container_raw()
            try:
                existing = await cosmos_client.read_item(container, case_id)
                if existing:
                    existing["validation"] = merged
                    # Upsert back
                    await cosmos_client.upsert_item(container, existing)
                else:
                    logger.warning(f"[ValidatePDBEService] Raw PDBE not found for case_id={case_id}, cannot update validation")
                # 3b) Insert into Postgres pdbe_validation table
                await postgres_client.insert_pdbe_validation(case_id, merged)
            except Exception as e:
                logger.error(f"[ValidatePDBEService] Error writing validation to DBs: {e}")
        else:
            logger.info(f"[ValidatePDBEService] Skipping Cosmos/Postgres writes because IS_AUDIT_ENABLED=False")

        # 4) Return merged JSON
        return merged
