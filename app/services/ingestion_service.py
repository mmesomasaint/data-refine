# app/services/ingestion_service.py
import pandas as pd
import io
import uuid
from typing import List, Dict, Any
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.job import IngestionJobModel
from app.models.employee import EmployeeModel
from app.services.cleaner_service import cleaner_service

class IngestionService:
    @staticmethod
    async def process_csv_file(job_id: str, file_bytes: bytes):
        """Asynchronously cleans, deduplicates, and commits CSV data."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(IngestionJobModel).filter(IngestionJobModel.id == job_id))
            job = result.scalars().first()
            if not job:
                return

            job.status = "PROCESSING"
            await db.commit()

            try:
                # Read CSV into Pandas DataFrame using BytesIO buffer
                df = pd.read_csv(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
                # Normalize column headers: lowercase and strip underscores/spaces
                df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

                job.total_rows = len(df)
                
                # Fetch existing emails from DB to prevent cross-file duplication
                existing_emails_query = await db.execute(select(EmployeeModel.email))
                seen_emails = set(existing_emails_query.scalars().all())

                clean_records: List[Dict[str, Any]] = []
                errors: List[Dict[str, Any]] = []
                duplicates_count = 0

                for idx, row in df.iterrows():
                    row_num = idx + 2  # Accounting for header row in CSV index

                    # 1. Clean and validate email (Primary Identity Anchor)
                    raw_email = row.get("email", "")
                    clean_email = cleaner_service.clean_email(raw_email)
                    
                    if not clean_email:
                        errors.append({"row": row_num, "reason": f"Invalid email format: '{raw_email}'"})
                        continue

                    if clean_email in seen_emails:
                        duplicates_count += 1
                        continue

                    # 2. Clean Dates
                    raw_hire_date = row.get("hire_date") or row.get("start_date") or row.get("date")
                    clean_date = cleaner_service.clean_date(str(raw_hire_date))
                    if not clean_date:
                        errors.append({"row": row_num, "reason": f"Unparseable date: '{raw_hire_date}'"})
                        continue

                    # 3. Clean Names and Phones
                    first_name = cleaner_service.clean_name(row.get("first_name", ""))
                    last_name = cleaner_service.clean_name(row.get("last_name", ""))
                    phone = cleaner_service.clean_phone(row.get("phone", "") or row.get("phone_number", ""))
                    department = cleaner_service.clean_name(row.get("department", "General"))

                    if not first_name or not last_name:
                        errors.append({"row": row_num, "reason": "Missing required First or Last Name"})
                        continue

                    # Mark email as seen and append clean record
                    seen_emails.add(clean_email)
                    clean_records.append({
                        "id": str(uuid.uuid4()),
                        "job_id": job.id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": clean_email,
                        "phone_number": phone,
                        "hire_date": clean_date,
                        "department": department
                    })

                # Bulk insert cleaned records via Core SQLAlchemy
                if clean_records:
                    await db.run_sync(lambda session: session.bulk_insert_mappings(EmployeeModel, clean_records))

                # Update job metrics
                job.imported_rows = len(clean_records)
                job.duplicate_rows = duplicates_count
                job.failed_rows = len(errors)
                job.errors = errors
                job.status = "COMPLETED"

            except Exception as e:
                job.status = "FAILED"
                job.errors = [{"error": f"Fatal processing error: {str(e)}"}]

            await db.commit()

ingestion_service = IngestionService()
