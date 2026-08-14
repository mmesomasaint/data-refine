# tests/test_api.py
import pytest
import io
from app.config import settings

@pytest.mark.asyncio
async def test_csv_upload_pipeline(client):
    headers = {"X-API-Key": settings.API_KEY.get_secret_value()}
    
    # Construct a dirty CSV payload
    dirty_csv_content = (
        "first_name,last_name,email,hire_date,phone,department\n"
        "John,Doe,john.doe@company.com,2023-01-15,415-555-0100,Engineering\n"
        "John,Duplicate,john.doe@company.com,01/15/2023,415-555-0100,Engineering\n" # Duplicate email
        "Jane,Smith,jane.smith@company.com,Invalid Date,415-555-0199,HR\n"         # Corrupt Date
        "Alice,Walker,alice@company.com,2021-08-01,202-555-0188,Finance\n"
    ).encode("utf-8")

    files = {"file": ("dirty_records.csv", io.BytesIO(dirty_csv_content), "text/csv")}
    
    # 1. Trigger Async Upload
    res = await client.post("/api/v1/imports/csv", headers=headers, files=files)
    assert res.status_code == 202
    job_data = res.json()
    job_id = job_data["id"]
    assert job_data["status"] == "PENDING"

    # 2. Inquire Job Status
    status_res = await client.get(f"/api/v1/imports/jobs/{job_id}", headers=headers)
    assert status_res.status_code == 200
    report = status_res.json()
    assert report["id"] == job_id
