# DataRefine - Bulk CSV Sanitization & Database Ingestion Engine

An asynchronous, high-throughput ETL microservice built with **FastAPI**, **Pandas**, **SQLAlchemy**, and **Pydantic**. DataRefine enables HR and accounting departments to bulk-upload unstructured CSV files, sanitize formulas against spreadsheet security vulnerabilities, normalize heterogeneous phone and date formats, filter duplicates, and commit verified records into relational storage.

---

## Key Architectural Features

* **CWE-1236 Formula Neutralization:** Automatically sanitizes cells beginning with `=`, `+`, `-`, or `@` to prevent CSV formula exploitation when spreadsheets are exported.
* **Smart Heterogeneous Date Parsing:** Normalizes inconsistent date inputs (`MM/DD/YYYY`, `YYYY-MM-DD`, `Month DD, YYYY`) into uniform ISO-8601 database records (`YYYY-MM-DD`).
* **E.164 International Phone Standardization:** Formats international telephone numbers via Google's `libphonenumber` integration.
* **Deduplication Engine:** Employs an in-memory hash set matched with database-level uniqueness constraints to drop duplicate records across batch operations.
* **Non-Blocking Background Tasks:** Returns an immediate `202 Accepted` job status token for real-time progress polling.

---

## Local Quick Start

### 1. Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Start Application Server
```bash
uvicorn app.main:app --reload --port 8000
```


## Interactive Testing via Swagger UI
1. Open `http://localhost:8000/docs` in your browser.
2. Click the green `Authorize` button at the top right, enter `dev_secret_api_key_12345`, and confirm.
3. Prepare a local test file named `test_dirty.csv`:
   ```csv
   first_name,last_name,email,hire_date,phone,department
   =cmd|'calc'!A0,Doe,john.doe@company.com,04/12/2021,555-0199,Finance
   Jane,Smith,jane.smith@company.com,August 15 2022,+1-555-0122,HR
   Jane,Duplicate,jane.smith@company.com,2022-08-15,555-0122,HR
   Bob,Johnson,bob@invalid-email,2020-01-01,555-0133,Engineering
   ```
4. Expand `POST /api/v1/imports/csv`, select the file, and click `Execute`.
5. Copy the returned `id` token (e.g. `e5a953cf-...`) and poll `GET /api/v1/imports/jobs/{job_id}` to view detailed import metrics:
   - `imported_rows`: `2` (John and Jane)
   - `duplicate_rows`: `1` (Jane's duplicate record filtered)
   - `failed_rows`: `1` (Bob's invalid email dropped with reason)


---


## Automated Testing

```bash
pytest -v
```


---
