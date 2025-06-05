# app/shared/postgres_client.py

import json
import asyncpg
from loguru import logger

from app.config import settings

_CREATE_AUDIT_TABLE_SQL = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint TEXT NOT NULL,
    request_body JSONB,
    response_body JSONB,
    created_on TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT
);
"""

_CREATE_VALIDATION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS pdbe_validation (
    case_id TEXT PRIMARY KEY,
    validation_json JSONB,
    created_on TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

class PostgresClient:
    def __init__(self):
        dsn = settings.get_postgres_dsn()
        if not dsn:
            raise RuntimeError("POSTGRES_DSN not configured.")
        self._dsn = dsn
        self._pool: asyncpg.Pool = None

    async def init(self):
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(dsn=self._dsn, min_size=1, max_size=5)
                async with self._pool.acquire() as conn:
                    await conn.execute(_CREATE_AUDIT_TABLE_SQL)
                    await conn.execute(_CREATE_VALIDATION_TABLE_SQL)
            except Exception as e:
                logger.error(f"[PostgresClient] Error creating tables: {e}")
                raise
        return self._pool

    async def insert_audit_log(self, endpoint: str, request_body: dict, response_body: dict, created_by: str = None):
        if self._pool is None:
            await self.init()
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO audit_logs(endpoint, request_body, response_body, created_by)
                    VALUES($1, $2::jsonb, $3::jsonb, $4)
                    """,
                    endpoint,
                    json.dumps(request_body),
                    json.dumps(response_body),
                    created_by or ""
                )
        except Exception as e:
            logger.error(f"[PostgresClient] Failed to insert audit log: {e}")

    async def insert_pdbe_validation(self, case_id: str, validation_json: dict):
        """
        Inserts or updates a record in pdbe_validation table.
        """
        if self._pool is None:
            await self.init()
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO pdbe_validation(case_id, validation_json)
                    VALUES($1, $2::jsonb)
                    ON CONFLICT (case_id) DO UPDATE 
                      SET validation_json = EXCLUDED.validation_json, created_on = NOW()
                    """,
                    case_id,
                    json.dumps(validation_json)
                )
        except Exception as e:
            logger.error(f"[PostgresClient] Failed to insert pdbe_validation: {e}")

postgres_client = PostgresClient()
