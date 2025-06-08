import os
from typing import Dict
from loguru import logger
from app.config import settings
from app.shared.utils import load_prompt_from_file
from app.shared.cosmos_client import cosmos_client

class PromptLoader:
    def __init__(self):
        self.use_local = settings.use_local_prompt()
        self.base = settings.get_local_prompt_basepath()
        # All 30 prompt keys in snake_case
        self.keys = [
            "alignment_case_subject",
            "alignment_case_subject_user",
            "alignment_case_description",
            "alignment_case_description_user",
            *(f"question_{i}" for i in range(1, 7)),
            *(f"question_{i}_user" for i in range(1, 7)),
            "overall_summary",
            "overall_summary_user",
            "psa_flag",
            "psa_flag_user",
            "pdbe_overall_llm_summary",
            "pdbe_overall_llm_summary_user",
            "pdbe_overall_quality",
            "pdbe_overall_quality_user",
            "pdbe_overall_status",
            "pdbe_overall_status_user",
            "overall_status",
            "overall_status_user",
            "clinical",
            "clinical_user"
        ]

    async def _load_from_cosmos(self) -> Dict[str, str]:
        container = settings.get_cosmos_container_prompts()
        query = "SELECT TOP 1 c.prompts FROM c ORDER BY c.created_on DESC"
        items = cosmos_client.query_items(container, query)
        async for item in items:
            return item.get("prompts", {})
        return {}

    async def load_all_prompts(self) -> Dict[str, str]:
        if not self.use_local:
            return await self._load_from_cosmos()

        prompts: Dict[str, str] = {}
        for key in self.keys:
            sys_fp = os.path.join(self.base, f"{key}_system_prompt.txt")
            usr_fp = os.path.join(self.base, f"{key}_user_prompt.txt")
            try:
                prompts[f"{key}_system_prompt"] = load_prompt_from_file(sys_fp)
                prompts[f"{key}_user_prompt"]   = load_prompt_from_file(usr_fp)
            except FileNotFoundError:
                logger.error(f"Missing prompt file: {key}")
                prompts[f"{key}_system_prompt"] = ""
                prompts[f"{key}_user_prompt"]   = ""
        return prompts

prompt_loader = PromptLoader()
