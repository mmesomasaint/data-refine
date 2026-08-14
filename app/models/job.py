# app/models/job.py
from sqlalchemy import Column, String, Integer, DateTime, JSON
from app.core.database import Base
from datetime import datetime, timezone
import uuid

class IngestionJobModel(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    total_rows = Column(Integer, default=0)
    imported_rows = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)        # [{row: 12, reason: "Invalid Date"}]
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
