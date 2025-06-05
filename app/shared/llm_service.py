# app/shared/llm_service.py

import asyncio
import json
from typing import Any, Dict

from langchain.chat_models import AzureChatOpenAI
from langchain import PromptTemplate, LLMChain
from loguru import logger

from app.config import settings
from app.shared.llm_service_utils import prompt_loader

class LLMService:
    def __init__(self):
        endpoint = settings.get_azure_openai_endpoint()
        key = settings.get_azure_openai_key()
        deployment = settings.get_llm_deployment_name()
        if not (endpoint and key and deployment):
            raise RuntimeError("Azure OpenAI configuration missing.")

        self.llm = AzureChatOpenAI(
            deployment_name=deployment,
            openai_api_key=key,
            openai_api_base=endpoint,
            openai_api_type="azure",
            openai_api_version="2023-05-15",
            temperature=settings.get_llm_temperature(),
            max_tokens=settings.get_llm_max_tokens(),
        )

    async def _build_chain(self, system_txt: str, user_txt: str) -> LLMChain:
        prompt = PromptTemplate(
            input_variables=["pdbe_text"],
            template=system_txt.strip() + "\n\n" + user_txt.strip()
        )
        return LLMChain(llm=self.llm, prompt=prompt, output_key="text")

    async def _run_question(self, idx: int, pdbe_text: str) -> Dict[str, Any]:
        prompts = await prompt_loader.load_all_prompts()
        sys_key = f"question_{idx}_system_prompt"
        usr_key = f"question_{idx}_user_prompt"
        system_txt = prompts.get(sys_key, "")
        user_txt = prompts.get(usr_key, "")
        if not system_txt or not user_txt:
            msg = f"Prompts not found for question {idx}"
            logger.error(msg)
            return {"error": msg}

        chain = await self._build_chain(system_txt, user_txt)
        logger.info(f"[LLMService] Running question {idx}")
        try:
            raw_resp = await chain.arun(pdbe_text=pdbe_text)
            try:
                return json.loads(raw_resp)
            except json.JSONDecodeError:
                return {"error": f"Invalid JSON from LLM Q{idx}: {raw_resp}"}
        except Exception as e:
            logger.error(f"[LLMService] Error Q{idx}: {e}")
            return {"error": str(e)}

    async def validate_pdbe_all(self, pdbe_text: str) -> Dict[str, Any]:
        tasks = [self._run_question(i, pdbe_text) for i in range(1, 7)]
        results = await asyncio.gather(*tasks)

        merged: Dict[str, Any] = {}
        pdbekey = "PDBE 1"
        merged[pdbekey] = {}

        # 1) case subject (Q1)
        merged[pdbekey]["case subject"] = results[0]
        # 2) case description (Q2)
        merged[pdbekey]["case description"] = results[1]

        # 3) aspect validation: Q3→"question 1", Q4→"question 2", Q5→"question 3", Q6→"question 4"
        aspect_validation = {}
        for i in range(3, 7):
            qlabel = f"question {i-2}"
            aspect_validation[qlabel] = results[i - 1]
        merged[pdbekey]["aspect validation"] = aspect_validation

        # 4) overall summary & quality
        missing_indices = []
        errors = []
        for idx, res in enumerate(results):
            if isinstance(res, dict):
                val = res.get("validation", "")
                if "not aligned" in val:
                    missing_indices.append(idx + 1)
                if "error" in res:
                    errors.append(res["error"])

        overall_summary = {"missing_parameters": missing_indices, "errors": errors}
        merged[pdbekey]["overall_llm_summary"] = overall_summary
        merged[pdbekey]["overall_quality"] = "Poor" if (missing_indices or errors) else "Good"

        return merged

llm_service = LLMService()
