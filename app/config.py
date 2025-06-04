import os
import json
from enum import Enum
from typing import Optional

from dotenv import dotenv_values
from azure.cosmos import CosmosClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger


class Environment(str, Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    ST2 = "ST2"
    PROD = "PROD"


class AppSettings:
    def __init__(self):
        self.env_values = dotenv_values()
        self.resolved_values: dict[str, str] = {}

        # Cosmos DB
        self._cosmos_client = None
        self._cosmos_database = None

        # PostgreSQL
        self._pg_engine = None
        self._pg_SessionLocal = None

    def _get_from_env(self, key: str, default: Optional[str] = None) -> str:
        if key in self.resolved_values:
            return self.resolved_values[key]
        env_val = os.getenv(key, None)
        file_val = self.env_values.get(key, None)
        resolved = env_val if env_val else (file_val if file_val else default)
        self.resolved_values[key] = resolved
        return resolved

    # --- Original‐style getters (matching your previous code) ---

    # Host/Port/Reload/Workers
    def get_host(self) -> str:
        return self._get_from_env("APP_HOST", "0.0.0.0")

    def get_port(self) -> int:
        return int(self._get_from_env("APP_PORT", "8000"))

    def get_reload(self) -> bool:
        return self._get_from_env("RELOAD", "False").lower() == "true"

    def get_uvicorn_workers(self) -> int:
        return int(self._get_from_env("UVICORN_WORKERS", "1"))

    # Project metadata
    def get_project_name(self) -> str:
        return self._get_from_env("PROJECT_NAME", "Diagnostic Validation API")

    def get_project_description(self) -> str:
        return self._get_from_env("PROJECT_DESCRIPTION", "Validates diagnostic checklists via GPT-4o")

    def get_project_version(self) -> str:
        return self._get_from_env("VERSION", "1.0.0")

    def get_root_path(self) -> str:
        return self._get_from_env("DEFAULT_ROOT_PATH", "/api/diag")

    def get_doc_url(self) -> Optional[str]:
        if self.is_prod_environment():
            return None
        return self._get_from_env("DOC_URL", "/api/diag/docs")

    def get_redoc_url(self) -> Optional[str]:
        if self.is_prod_environment():
            return None
        return self._get_from_env("REDOC_URL", "/api/diag/redoc")

    def get_openapi_json_url(self) -> Optional[str]:
        if self.is_prod_environment():
            return None
        return self._get_from_env("OPENAPI_JSON_URL", "/api/diag/openapi.json")

    # Environment flags
    def get_environment(self) -> Environment:
        env = self._get_from_env("ENV_TYPE", Environment.DEV.value)
        return Environment(env)

    def is_prod_environment(self) -> bool:
        return self.get_environment() == Environment.PROD

    def is_local_environment(self) -> bool:
        return self.get_environment() == Environment.LOCAL

    # Azure OpenAI
    def get_azure_openai_endpoint(self) -> str:
        return self._get_from_env("AZURE_OPENAI_ENDPOINT", None)

    def get_azure_openai_key(self) -> str:
        return self._get_from_env("AZURE_OPENAI_KEY", None)

    def get_azure_openai_deployment(self) -> str:
        return self._get_from_env("AZURE_OPENAI_DEPLOYMENT_GPT4O", None)

    def get_azure_openai_temperature(self) -> float:
        return float(self._get_from_env("AZURE_OPENAI_TEMPERATURE", "0.0"))

    # Cosmos DB
    def _initialize_cosmos(self):
        if self._cosmos_client is None:
            endpoint = self._get_from_env("COSMOS_ENDPOINT", None)
            key = self._get_from_env("COSMOS_KEY", None)
            self._cosmos_client = CosmosClient(endpoint, credential=key)
        return self._cosmos_client

    def get_cosmos_database(self):
        if self._cosmos_database is None:
            db_name = self._get_from_env("COSMOS_DATABASE", "diagValidationDb")
            self._cosmos_database = self._initialize_cosmos().get_database_client(db_name)
        return self._cosmos_database

    def get_cosmos_container(self, container_name: str):
        return self.get_cosmos_database().get_container_client(container_name)

    def get_prompts_container(self):
        return self.get_cosmos_container(self._get_from_env("COSMOS_CONTAINER_PROMPTS", "prompts"))

    def get_io_container(self):
        return self.get_cosmos_container(self._get_from_env("COSMOS_CONTAINER_IO", "inputs_outputs"))

    def get_configs_container(self):
        return self.get_cosmos_container(self._get_from_env("COSMOS_CONTAINER_CONFIGS", "configs"))

    # PostgreSQL (SQLAlchemy)
    def _get_pg_engine(self):
        if self._pg_engine is None:
            user = self._get_from_env("POSTGRES_USER", None)
            pwd = self._get_from_env("POSTGRES_PASSWORD", None)
            host = self._get_from_env("POSTGRES_HOST", None)
            port = self._get_from_env("POSTGRES_PORT", "5432")
            db = self._get_from_env("POSTGRES_DB", "diag_validation")
            url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
            self._pg_engine = create_engine(url, pool_pre_ping=True)
        return self._pg_engine

    def get_pg_session(self):
        if self._pg_SessionLocal is None:
            engine = self._get_pg_engine()
            self._pg_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return self._pg_SessionLocal

    # Azure AD
    def get_azure_ad_tenant(self) -> str:
        return self._get_from_env("AZURE_AD_TENANT_ID", None)

    def get_azure_ad_client_id(self) -> str:
        return self._get_from_env("AZURE_AD_CLIENT_ID", None)

    def get_azure_ad_issuer(self) -> str:
        return self._get_from_env("AZURE_AD_ISSUER", None)

    def get_azure_ad_audience(self) -> str:
        return self._get_from_env("AZURE_AD_AUDIENCE", None)

    def get_validation_ad_group(self) -> str:
        return self._get_from_env("AZURE_AD_VALIDATION_GROUP", None)

    # Checklist template middleware
    def get_template_middleware_url(self) -> str:
        return self._get_from_env("TEMPLATE_MIDDLEWARE_URL", None)

    # Logging settings
    def is_audit_enabled(self) -> bool:
        return self._get_from_env("ENABLE_AUDIT", "True").lower() == "true"

    def is_debug(self) -> bool:
        return self._get_from_env("DEBUG", "False").lower() == "true"

    def get_local_prompt_dir(self) -> str:
        return self._get_from_env("LOCAL_PROMPT_DIR", "app/prompts/local/validation")
    
settings = AppSettings()
