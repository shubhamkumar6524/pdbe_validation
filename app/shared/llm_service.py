# app/shared/llm_service.py

import asyncio, json
from typing import Dict, Any
from langchain.chat_models import AzureChatOpenAI
from langchain import PromptTemplate, LLMChain
from loguru import logger
from app.config import settings
from app.shared.llm_service_utils import prompt_loader

class LLMService:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name=settings.get_llm_deployment_name(),
            openai_api_key=settings.get_azure_openai_key(),
            openai_api_base=settings.get_azure_openai_endpoint(),
            openai_api_type="azure", openai_api_version="2023-05-15",
            temperature=settings.get_llm_temperature(),
            max_tokens=settings.get_llm_max_tokens()
        )

    async def _run_agent(self, name: str, pdbe_text: str) -> Any:
        prompts = await prompt_loader.load_all_prompts()
        sys_txt = prompts[f"{name}_system_prompt"]
        usr_txt = prompts[f"{name}_user_prompt"]
        chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(input_variables=["pdbe_text"], template=sys_txt+"\n\n"+usr_txt)
        )
        try:
            raw = await chain.arun(pdbe_text=pdbe_text)
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON from {name}: {raw}"}
        except Exception as e:
            return {"error": str(e)}

    async def validate_pdbe_all(self, pdbe_text: str) -> Dict[str,Any]:
        agents = [
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
        ]
        tasks = [self._run_agent(a, pdbe_text) for a in agents]
        results = await asyncio.gather(*tasks)

        out = {
            pdbe_text[:8]: {  # or your pdbe_id
                "case_subject":     results[0],
                "case_description": results[1],
                "PDBE": {f"validation_guideline_{i}": results[1+i] for i in range(1,7)},
                "psa_flag":         results[8],
                "clinical":         results[10].get("validation", False),
                "uuid":             __import__("uuid").uuid4().hex,
                "attachment":       results[9].get("validation", False),
                "overall_llm_summary": results[11].get("summary", ""),
                "overall_quality":     results[12].get("quality", ""),
                "overall_status":      results[13].get("status", "")
            }
        }
        return {"case_id": out}

llm_service = LLMService()
