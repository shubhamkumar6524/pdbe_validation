-- scripts/create_postgres_schema.sql

-- Enable pgcrypto to allow gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1) audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint TEXT NOT NULL,
    request_body JSONB,
    response_body JSONB,
    created_on TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT
);

-- 2) pdbe_validation table
CREATE TABLE IF NOT EXISTS pdbe_validation (
    case_id TEXT PRIMARY KEY,
    validation_json JSONB,
    created_on TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
