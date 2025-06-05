# app/config.py

import json
import os

from enum import Enum
from typing import Dict

import boto3
from dotenv import dotenv_values
from loguru import logger

class Environment(str, Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    ST2 = "ST2"
    PROD = "PROD"

class AppSettings:
    """
    Reads configuration from environment variables or .env file. Optionally loads from AWS Secrets Manager.
    """

    def __init__(self) -> None:
        self.env_values: Dict[str, str] = dotenv_values()
        self.resolved_values: Dict[str, str] = {}

        if self.enable_aws_secrets():
            logger.info("Applying AWS secrets from Secrets Manager")
            secret = self.get_secret()
            for key, value in secret.items():
                self.env_values[key.upper()] = value
        else:
            logger.info("Skipping AWS Secrets Manager")

    def get_config(self, key: str, default: str = None) -> str:
        if key in self.resolved_values:
            return self.resolved_values[key]

        os_val = os.getenv(key)
        env_val = self.env_values.get(key)
        resolved = os_val if os_val is not None else (env_val if env_val is not None else default)
        self.resolved_values[key] = resolved
        return resolved

    # ----------------------------
    # AWS Secrets Manager
    # ----------------------------
    def enable_aws_secrets(self) -> bool:
        return self.get_config("ENABLE_AWS_SECRETS", "True").lower() == "false"

    def get_secret_id(self) -> str:
        return self.get_config("SECRET_ID", "")

    def get_secrets_manager(self) -> str:
        return self.get_config("SECRETS_MANAGER", "secretsmanager")

    def get_aws_region(self) -> str:
        return self.get_config("AWS_REGION", "us-east-1")

    def get_secret(self) -> Dict[str, str]:
        client = boto3.client(
            service_name=self.get_secrets_manager(),
            region_name=self.get_aws_region(),
            verify=False
        )
        secret_id = self.get_secret_id()
        if not secret_id:
            raise ValueError("SECRET_ID must be set")

        try:
            response = client.get_secret_value(SecretId=secret_id)
            logger.info(f"Fetched secret {secret_id} from AWS Secrets Manager")
        except Exception as e:
            raise RuntimeError(f"Error fetching AWS secret: {e}")

        secret_string = response.get("SecretString", "{}")
        parsed = json.loads(secret_string)
        # If the secret wraps a JSON under "password", unwrap it:
        if "password" in parsed:
            return json.loads(parsed["password"])
        return parsed

    # ----------------------------
    # Environment
    # ----------------------------
    def get_environment(self) -> Environment:
        val = self.get_config("ENV_TYPE", Environment.DEV.value)
        try:
            return Environment(val)
        except ValueError:
            return Environment.DEV

    def is_prod_environment(self) -> bool:
        return self.get_environment() == Environment.PROD

    def is_local_environment(self) -> bool:
        return self.get_environment() == Environment.LOCAL

    # ----------------------------
    # Project Metadata & Paths
    # ----------------------------
    def get_project_name(self) -> str:
        return self.get_config("PROJECT_NAME", "PDBE Validation API")

    def get_project_description(self) -> str:
        return self.get_config("PROJECT_DESCRIPTION", "Validate PDBE using Azure OpenAI")

    def get_project_version(self) -> str:
        return self.get_config("VERSION", "1.0.0")

    def get_root_path(self) -> str:
        return self.get_config("DEFAULT_ROOT_PATH", "/api/pdbe")

    def get_doc_url(self) -> str:
        return None if self.is_prod_environment() else self.get_config("DOC_URL", "/api/pdbe/docs")

    def get_redoc_url(self) -> str:
        return None if self.is_prod_environment() else self.get_config("REDOC_URL", "/api/pdbe/redoc")

    def get_openapi_json_url(self) -> str:
        return None if self.is_prod_environment() else self.get_config("OPENAPI_JSON_URL", "/api/pdbe/openapi.json")

    # ----------------------------
    # Host / Port
    # ----------------------------
    def get_host(self) -> str:
        return self.get_config("APP_HOST", "0.0.0.0")

    def get_port(self) -> int:
        return int(self.get_config("APP_PORT", "8080"))

    def get_reload(self) -> bool:
        return self.get_config("RELOAD", "True").lower() == "false"

    def get_uvicorn_workers(self) -> int:
        return int(self.get_config("UVICORN_WORKERS", "1"))

    # ----------------------------
    # Azure OpenAI
    # ----------------------------
    def get_azure_openai_endpoint(self) -> str:
        return self.get_config("AZURE_OPENAI_ENDPOINT", "")

    def get_azure_openai_key(self) -> str:
        return self.get_config("AZURE_OPENAI_KEY", "")

    def get_llm_deployment_name(self) -> str:
        return self.get_config("LLM_DEPLOYMENT_NAME", "")

    def get_llm_temperature(self) -> float:
        return float(self.get_config("LLM_TEMPERATURE", "0.0"))

    def get_llm_max_tokens(self) -> int:
        return int(self.get_config("LLM_MAX_TOKENS", "1024"))

    # ----------------------------
    # ServiceMax Middleware
    # ----------------------------
    def get_servicemax_base_url(self) -> str:
        return self.get_config("SERVICEMAX_BASE_URL", "")

    # ----------------------------
    # CosmosDB Config
    # ----------------------------
    def get_cosmos_endpoint(self) -> str:
        return self.get_config("COSMOS_ENDPOINT", "")

    def get_cosmos_key(self) -> str:
        return self.get_config("COSMOS_KEY", "")

    def get_cosmos_database(self) -> str:
        return self.get_config("COSMOS_DATABASE", "pdbe_db")

    def get_cosmos_container_raw(self) -> str:
        return self.get_config("COSMOS_CONTAINER_RAW", "raw_pdbe")

    def get_cosmos_container_prompts(self) -> str:
        return self.get_config("COSMOS_CONTAINER_PROMPTS", "llm_prompts")

    def get_cosmos_container_outputs(self) -> str:
        return self.get_config("COSMOS_CONTAINER_OUTPUTS", "llm_outputs")

    def get_cosmos_container_configs(self) -> str:
        return self.get_config("COSMOS_CONTAINER_CONFIGS", "configs")

    def get_cosmos_container_validation(self) -> str:
        return self.get_config("COSMOS_CONTAINER_VALIDATION", "pdbe_validation")

    def get_cosmos_container_audit(self) -> str:
        return self.get_config("COSMOS_CONTAINER_AUDIT", "audit")

    # ----------------------------
    # PostgreSQL Config
    # ----------------------------
    def get_postgres_dsn(self) -> str:
        return self.get_config("POSTGRES_DSN", "")

    # ----------------------------
    # Feature Flags
    # ----------------------------
    def is_audit_enabled(self) -> bool:
        return self.get_config("IS_AUDIT_ENABLED", "True").lower() == "false"

    def use_dummy_pdbe(self) -> bool:
        return self.get_config("USE_DUMMY_PDBE_RESPONSE", "True").lower() == "true"

    def use_local_prompt(self) -> bool:
        return self.get_config("USE_LOCAL_PROMPT", "True").lower() == "true"

    # ----------------------------
    # Prompt File Paths
    # ----------------------------
    def get_local_prompt_basepath(self) -> str:
        return self.get_config("LOCAL_PROMPT_BASEPATH", "app/prompts/local/validate_pdbe_prompts")
    

settings = AppSettings()
