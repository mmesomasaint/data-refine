# Repository Directory Structure

## Directory map

```Plaintext
data-refine/
├── app/
│   ├── __init__.py
│   ├── main.py                   # Lifespan startup, middleware, and route mounting
│   ├── config.py                 # Pydantic Settings & ETL boundary rules
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py         # V1 API router aggregation
│   │       └── endpoints.py      # Multipart upload, job status, & export endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py       # Async SQLAlchemy connection & session factory
│   │   ├── security.py       # API Key auth, MIME validation, & CSV formula neutralization
│   │   └── exceptions.py     # Custom ETL & validation exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py                # Ingestion batch tracking model
│   │   └── employee.py           # Clean normalized relational destination entity
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── job.py                # Job status, audit metrics, & error payload schemas
│   │   └── record.py             # Strict row-level data validation schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cleaner_service.py    # Regex cleaning, date unification, phone/email parsing
│   │   ├── ingestion_service.py  # Chunked pipeline, deduplication, & database bulk insert
│   │   └── export_service.py     # Cleaned data export generator
│   └── templates/                # (Optional documentation/audit report templates)
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Async Pytest fixtures, mock CSVs, & test database
│   ├── test_cleaner.py           # Unit tests for date parsing, phone cleanup, & sanitization
│   ├── test_security.py          # CSV injection defense & MIME sniffing tests
│   └── test_api.py               # Multipart upload & ingestion pipeline integration tests
├── devops/
│   ├── docker-compose.yml        # Multi-container stack (API, PostgreSQL, Redis, Worker)
│   ├── Dockerfile                # Multi-stage production container build
│   └── nginx.conf                # Reverse proxy with strict client upload body limits
├── docs/
│   └── ARCHITECTURE.md           # ETL pipeline architecture, threat model, & schema specs
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md                     # Enterprise handover & operational guide
└── requirements.txt              # Locked application dependencies
```
