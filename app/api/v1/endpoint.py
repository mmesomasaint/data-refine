# app/api/v1/endpoints.py
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import verify_api_key, validate_csv_file_meta
from app.models.job import IngestionJobModel
from app.models.employee import EmployeeModel
from app.schemas.job import IngestionJobResponse
from app.services.ingestion_service import ingestion_service
from app.config import settings

router = APIRouter()

@router.post("/csv", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(verify_api_key)])
async def upload_csv_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    validate_csv_file_meta(file)
    
    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 50MB system threshold."
        )

    # Initialize Job Record
    job = IngestionJobModel(
        filename=file.filename,
        status="PENDING"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Offload processing to non-blocking background queue
    background_tasks.add_task(
        ingestion_service.process_csv_file,
        job.id,
        file_bytes
    )

    return job

@router.get("/jobs/{job_id}", response_model=IngestionJobResponse, dependencies=[Depends(verify_api_key)])
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IngestionJobModel).filter(IngestionJobModel.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found.")
    return job
