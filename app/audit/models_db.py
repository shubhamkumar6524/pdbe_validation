from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=True)
    path = Column(Text, nullable=False)
    method = Column(String(10), nullable=False)
    request_body = Column(JSON, nullable=True)
    response_body = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
