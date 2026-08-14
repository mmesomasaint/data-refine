# app/schemas/job.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class IngestionJobResponse(BaseModel):
    id: str
    filename: str
    status: str
    total_rows: int
    imported_rows: int
    duplicate_rows: int
    failed_rows: int
    errors: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
