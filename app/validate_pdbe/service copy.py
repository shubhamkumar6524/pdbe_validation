import httpx
from loguru import logger

from app.config import settings
from app.shared.utils import get_dummy_pdbe
from app.shared.cosmos_client import cosmos_client
from app.shared.postgres_client import postgres_client
from app.shared.llm_service import llm_service

class ValidatePDBEService:
    async def fetch_pdbe(self, case_id: str) -> str:
        if settings.use_dummy_pdbe():
            return get_dummy_pdbe()["pdbe"]

        base_url = settings.get_servicemax_base_url().rstrip("/")
        url = f"{base_url}/pdbe/{case_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
        resp.raise_for_status()
        pdbe_obj = resp.json().get("pdbe")

        if settings.is_audit_enabled():
            await cosmos_client.upsert_item(
                settings.get_cosmos_container_raw(),
                {"id": case_id, "pdbe": pdbe_obj}
            )

        if isinstance(pdbe_obj, dict):
            return " ".join(str(v) for v in pdbe_obj.values())
        return pdbe_obj or ""

    async def validate_and_store(self, case_id: str):
        pdbe_text = await self.fetch_pdbe(case_id)
        merged = await llm_service.validate_pdbe_all(pdbe_text)

        if settings.is_audit_enabled():
            raw = await cosmos_client.read_item(settings.get_cosmos_container_raw(), case_id)
            raw["validation"] = merged
            await cosmos_client.upsert_item(settings.get_cosmos_container_raw(), raw)
            await postgres_client.insert_pdbe_validation(case_id, merged)

        return merged
