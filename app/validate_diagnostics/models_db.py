from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    JSON,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ValidationRecord(Base):
    __tablename__ = "validation_records"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(100), nullable=False, index=True)
    run_timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    all_aspects_json = Column(JSON, nullable=False)
