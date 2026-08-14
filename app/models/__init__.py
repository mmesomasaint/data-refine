# app/models/__init__.py
from app.models.job import IngestionJobModel
from app.models.employee import EmployeeModel

__all__ = ["IngestionJobModel", "EmployeeModel"]
