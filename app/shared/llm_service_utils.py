import os
import json
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .exceptions import BadRequestException
from loguru import logger
from app.config import settings


class LLMServiceUtils:
    @staticmethod
    def get_llm_client():
        try:
            llm = AzureChatOpenAI(
                deployment_name=settings.get_azure_openai_deployment(),
                openai_api_base=settings.get_azure_openai_endpoint(),
                openai_api_key=settings.get_azure_openai_key(),
                temperature=settings.get_azure_openai_temperature(),
                max_tokens=1024,
                openai_api_type="azure",
                openai_api_version="2023-05-15",
            )
            return llm
        except Exception as e:
            logger.error(f"Failed to create LLM client: {e}")
            raise BadRequestException("Unable to connect to Azure OpenAI.")

    @staticmethod
    def _load_local_prompt(filename: str) -> str:
        """
        Read a single prompt file under the local prompt directory.
        """
        local_dir = settings.get_local_prompt_dir()
        path = os.path.join(local_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise BadRequestException(f"Local prompt file {path} not found.")
        except Exception as e:
            raise BadRequestException(f"Error reading prompt file {path}: {e}")

    @staticmethod
    def get_prompts_for_aspect(aspect_index: int) -> dict:
        """
        Load the pair (system, user) prompts for the given aspect (1..6)
        from local files:
          - aspect{n}_system.txt
          - aspect{n}_user.txt
        """
        system_file = f"aspect{aspect_index}_system.txt"
        user_file = f"aspect{aspect_index}_user.txt"
        system_txt = LLMServiceUtils._load_local_prompt(system_file)
        user_txt = LLMServiceUtils._load_local_prompt(user_file)
        return {"system": system_txt, "user": user_txt}

    @staticmethod
    def build_aspect_prompt(aspect_index: int, input_json: dict) -> list[dict]:
        """
        Construct system + user messages for checking the given aspect.
        """
        prompts = LLMServiceUtils.get_prompts_for_aspect(aspect_index)
        sys_msg = SystemMessage(content=prompts["system"])
        # We pass the entire input JSON as part of the user message
        usr_content = prompts["user"].format(input=json.dumps(input_json))
        usr_msg = HumanMessage(content=usr_content)
        return [sys_msg, usr_msg]
