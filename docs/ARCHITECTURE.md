# System ARchitecture & Security Specification

## System Architecture

```Plaintext
[ HR / Accounting Admin ]
                          │
                          │  Multipart POST /api/v1/imports/csv
                          │  Headers: X-API-Key, Content-Type: multipart/form-data
                          ▼
        ┌────────────────────────────────────────────────────────┐
        │                      Nginx Proxy                       │
        │  - Client Body Limit: 50MB                             │
        │  - TLS Termination & Request Timeout Buffering        │
        └─────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
        ┌────────────────────────────────────────────────────────┐
        │                    FastAPI Gateway                     │
        │  1. API Key Authentication                             │
        │  2. File Magic Byte / MIME Verification (RFC 4180)     │
        │  3. Job Initialization (`PENDING` state in DB)         │
        └─────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
        ┌────────────────────────────────────────────────────────┐
        │             Chunked Stream ETL Pipeline                │
        │                                                        │
        │  ┌──────────────────────────────────────────────────┐  │
        │  │ Layer 1: CSV Formula Injection Neutralization    │  │
        │  │          Prefixes `=, +, -, @` with single quote │  │
        │  └──────────────────────────┬───────────────────────┘  │
        │                             │                          │
        │  ┌──────────────────────────▼───────────────────────┐  │
        │  │ Layer 2: Data Normalization Engine               │  │
        │  │          - Phone Numbers: E.164 conversion       │  │
        │  │          - Dates: Unified ISO-8601 (YYYY-MM-DD)  │  │
        │  │          - Text: Lowercasing, trim whitespace    │  │
        │  └──────────────────────────┬───────────────────────┘  │
        │                             │                          │
        │  ┌──────────────────────────▼───────────────────────┐  │
        │  │ Layer 3: Identity Deduplication & Validation     │  │
        │  │          In-memory set + DB index uniqueness     │  │
        │  └──────────────────────────┬───────────────────────┘  │
        │                             │                          │
        │  ┌──────────────────────────▼───────────────────────┐  │
        │  │ Layer 4: Async Bulk Upsert / Insert              │  │
        │  │          SQLAlchemy Core `bulk_insert_mappings`  │  │
        │  └──────────────────────────────────────────────────┘  │
        └─────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    PostgreSQL Database    │
                    │  - `ingestion_jobs` (Log) │
                    │  - `employee_records` (DB)│
                    └───────────────────────────┘
```

## Threat Model & Defense-In-Depth Protocol

1. **CSV Formula Injection (CWE-1236):** Attackers often weaponize CSV values by injecting `=CMD|' /C calc'!A0` or `@SUM(...)` into names or notes, which execute when opened in Microsoft Excel or LibreOffice Calc. The sanitizer detects cells starting with `=`, `+`, `-`, `@`, `\t`, or `\r` and prepends a safe single quote (`'`).
2. **Memory Exhaustion (OOM Protection):** Instead of using `pd.read_csv()` directly on entire files, the engine streams files via configured chunks (e.g., 5,000 rows per batch) through an asynchronous generator.
3. **MIME Sniffing & Extension Spoofing:** Relies on true file signatures and strict extension enforcement to reject `.exe`, `.sh`, or embedded polyglot files disguised as `.csv`.
