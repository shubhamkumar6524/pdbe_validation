import asyncio
import re
import json
from typing import Dict, Any
from loguru import logger
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import AzureChatOpenAI

from app.config import settings
from app.shared.llm_service_utils import prompt_loader

class LLMService:
    def __init__(self):
        endpoint   = settings.get_azure_openai_endpoint()
        api_key    = settings.get_azure_openai_key()
        deployment = settings.get_llm_deployment_name()
        if not (endpoint and api_key and deployment):
            raise RuntimeError("Azure OpenAI not configured.")
        self.llm = AzureChatOpenAI(
            deployment_name=deployment,
            openai_api_base=endpoint,
            openai_api_key=api_key,
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

    def _clean_json(self, raw: str) -> str:
        raw = re.sub(r"```(?:json)?", "", raw).replace("```", "")
        raw = re.sub(r"[‘’“”]", '"', raw)
        m = re.search(r"(\{.*\})", raw, re.DOTALL)
        if not m:
            raise ValueError("No JSON object found")
        js = m.group(1)
        js = re.sub(r",\s*}", "}", js)
        js = re.sub(r",\s*\]", "]", js)
        return js

    async def _run_key(self, key: str, pdbe_text: str) -> Dict[str, Any]:
        prompts = await prompt_loader.load_all_prompts()
        sys_txt = prompts.get(f"{key}_system_prompt", "")
        usr_txt = prompts.get(f"{key}_user_prompt", "")
        if not sys_txt or not usr_txt:
            msg = f"Prompts missing for {key}"
            logger.error(msg)
            return {"error": msg}

        chain = await self._build_chain(sys_txt, usr_txt)
        try:
            raw = await chain.arun(pdbe_text=pdbe_text)
            cleaned = self._clean_json(raw)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON from LLM {key}: {raw}"}
        except Exception as e:
            return {"error": str(e)}

    async def validate_pdbe_all(self, pdbe_text: str) -> Dict[str, Any]:
        keys = prompt_loader.keys
        tasks = [self._run_key(key, pdbe_text) for key in keys]
        results = await asyncio.gather(*tasks)

        # Extract pieces
        case_subject     = results[keys.index("alignment_case_subject")]
        case_description = results[keys.index("alignment_case_description")]

        questions = {
            i: results[keys.index(f"question_{i}")] for i in range(1,7)
        }

        overall_summary = results[keys.index("overall_summary")]
        psa_flag        = results[keys.index("psa_flag")]
        pdbe_llm        = results[keys.index("pdbe_overall_llm_summary")]
        pdbe_quality    = results[keys.index("pdbe_overall_quality")]
        pdbe_status     = results[keys.index("pdbe_overall_status")]
        overall_status  = results[keys.index("overall_status")]
        clinical        = results[keys.index("clinical")]

        pdbe = {
            **{f"validation_guideline_{i}": questions[i] for i in range(1,7)},
            "pdbe_overall_llm_summary": pdbe_llm.get("overall_summary"),
            "pdbe_overall_quality":     pdbe_quality.get("overall_quality"),
            "pdbe_overall_status":      pdbe_status.get("overall_status")
        }

        return {
            "case_subject":     case_subject,
            "case_description": case_description,
            "pdbe":             pdbe,
            "psa_flag": {
                "psa_flag_validation":  psa_flag.get("psa_flag_validation"),
                "psa_flag_description": psa_flag.get("psa_flag_description")
            },
            "clinical":          clinical.get("clinical"),
            "unique_uuid":       psa_flag.get("unique_run_id"),
            "attachment":        psa_flag.get("attachment_present"),
            "overall_llm_summary": overall_summary.get("overall_summary"),
            "overall_quality":     overall_summary.get("overall_quality"),
            "overall_status":      overall_status.get("overall_status")
        }

llm_service = LLMService()
