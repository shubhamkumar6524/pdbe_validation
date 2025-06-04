import json
from datetime import datetime
from fastapi import HTTPException
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from sqlalchemy.orm import Session
from loguru import logger
import asyncio

from app.config import settings
from app.shared.llm_service import LLMService
from app.shared.exceptions import BadRequestException

from app.validate_diagnostics.models_db import ValidationRecord


class ValidationService:
    def __init__(self):
        self.llm = LLMService()
        self.io_container = settings.get_io_container()

    def _get_ingested_payload(self, case_id: str) -> dict:
        try:
            item = self.io_container.read_item(item=case_id, partition_key=case_id)
            return item.get("payload", {})
        except CosmosResourceNotFoundError:
            raise BadRequestException(f"case_id {case_id} not found.")
        except Exception as e:
            logger.error(f"Cosmos read error: {e}")
            raise HTTPException(status_code=500, detail="Error reading ingested payload.")

    async def validate(self, case_id: str) -> dict:
        # 1) Fetch ingested payload
        ingested_data = self._get_ingested_payload(case_id)

        # 2) Launch 6 concurrent LLM calls
        tasks = []
        for aspect_idx in range(1, 7):
            tasks.append(self.llm.validate_aspect(aspect_idx, ingested_data))

        try:
            aspect_responses = await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error during concurrent LLM calls: {e}")
            raise HTTPException(status_code=500, detail="Error validating aspects.")

        # 3) Build the final nested JSON in the requested format
        pdb_key = f"PDBE {case_id}"
        nested = {pdb_key: {}}

        for idx, resp in enumerate(aspect_responses, start=1):
            aspect_key = f"aspect{idx}"
            nested[pdb_key][aspect_key] = {
                "llm_response": resp,
                # extract “comments” field from resp if present; else empty string
                "llm_comment": resp.get("comments", "") if isinstance(resp, dict) else ""
            }

        # Add empty placeholders for overall summary/quality
        nested[pdb_key]["overall_llm_summary"] = {}
        nested[pdb_key]["overall_quality"] = {}

        # 4) Store combined JSON in PostgreSQL
        SessionLocal = settings.get_pg_session()
        db: Session = SessionLocal()
        try:
            new_record = ValidationRecord(
                case_id=case_id,
                all_aspects_json=nested,
            )
            db.add(new_record)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"PostgreSQL insert error: {e}")
        finally:
            db.close()

        return nested
