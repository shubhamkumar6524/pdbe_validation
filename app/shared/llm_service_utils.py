# app/shared/llm_service_utils.py

import os, asyncio
from typing import Dict
from app.config import settings
from app.shared.utils import load_prompt_from_file
from app.shared.cosmos_client import cosmos_client

class PromptLoader:
    def __init__(self):
        self.use_local = settings.use_local_prompt()

    async def _load_from_cosmos(self) -> Dict[str,str]:
        query = "SELECT TOP 1 c.prompts FROM c ORDER BY c.created_on DESC"
        async for item in cosmos_client.query_items(settings.get_cosmos_container_prompts(), query):
            return item.get("prompts", {})
        return {}

    async def load_all_prompts(self) -> Dict[str,str]:
        if not self.use_local:
            return await self._load_from_cosmos()

        base = settings.get_local_prompt_basepath().rstrip("/")
        prompts = {}
        for name in [
            "alignment_case_subject",
            "alignment_case_description",
            *[f"question_{i}" for i in range(1,7)],
            "psa_flag_check",
            "attachments_check",
            "clinical_check",
            "overall_status",
            "overall_summary",
            "overall_quality",
            "pdbe_overall_status",
            "pdbe_overall_llm_summary",
            "pdbe_overall_quality"
        ]:
            prompts[f"{name}_system_prompt"] = load_prompt_from_file(f"{name}_system_prompt.txt")
            prompts[f"{name}_user_prompt"]   = load_prompt_from_file(f"{name}_user_prompt.txt")
        return prompts

prompt_loader = PromptLoader()
