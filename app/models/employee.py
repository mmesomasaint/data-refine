# app/models/employee.py
from sqlalchemy import Column, String, Date, DateTime
from app.core.database import Base
from datetime import datetime, timezone
import uuid

class EmployeeModel(Base):
    __tablename__ = "employee_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone_number = Column(String, nullable=True)
    hire_date = Column(Date, nullable=False)
    department = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
