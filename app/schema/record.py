# app/schemas/record.py
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class CleanEmployeeRecord(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    phone_number: Optional[str] = None
    hire_date: date
    department: str = Field(default="Unassigned")
