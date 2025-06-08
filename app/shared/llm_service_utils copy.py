# app/shared/llm_service_utils.py

import asyncio
from typing import Dict
from uuid import uuid4

from app.config import settings
from app.shared.utils import load_prompt_from_file
from app.shared.cosmos_client import cosmos_client
from loguru import logger

class PromptLoader:
    def __init__(self):
        self.use_local = settings.use_local_prompt()

    async def _load_from_cosmos(self) -> Dict[str, str]:
        container = settings.get_cosmos_container_prompts()
        query = "SELECT TOP 1 c.prompts FROM c ORDER BY c.created_on DESC"
        items = cosmos_client.query_items(container, query)
        async for item in items:
            return item.get("prompts", {})
        return {}

    async def load_all_prompts(self) -> Dict[str, str]:
        if self.use_local:
            base = settings.get_local_prompt_basepath()
            prompts = {}
            for i in range(1, 7):
                sys_file = f"question_{i}_system_prompt.txt"
                usr_file = f"question_{i}_user_prompt.txt"
                prompts[f"question_{i}_system_prompt"] = load_prompt_from_file(sys_file)
                prompts[f"question_{i}_user_prompt"] = load_prompt_from_file(usr_file)
            return prompts
        else:
            return await self._load_from_cosmos()

prompt_loader = PromptLoader()
