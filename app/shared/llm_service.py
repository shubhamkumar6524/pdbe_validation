import json
from loguru import logger
from fastapi import HTTPException
from .llm_service_utils import LLMServiceUtils
from .exceptions import BadRequestException


class LLMService:
    """
    Wrapper around LangChain AzureChatOpenAI for validating individual aspects.
    """

    def __init__(self):
        self.client = LLMServiceUtils.get_llm_client()

    async def validate_aspect(self, aspect_index: int, input_json: dict) -> dict:
        """
        Calls Azure GPT-4o with the prompt for the given aspect, passing input_json.
        Returns the parsed JSON output.
        """
        messages = LLMServiceUtils.build_aspect_prompt(aspect_index, input_json)
        try:
            resp = await self.client.apredict(messages=messages)
            text = resp.content
            try:
                result_json = json.loads(text)
                return result_json
            except json.JSONDecodeError as e:
                logger.error(f"Aspect {aspect_index}: JSON parse error: {e} - Response: {text}")
                raise BadRequestException(f"LLM returned invalid JSON for aspect {aspect_index}.")
        except Exception as e:
            logger.error(f"Aspect {aspect_index}: LLM call failed: {e}")
            raise HTTPException(status_code=500, detail=f"LLM call failed for aspect {aspect_index}.")
