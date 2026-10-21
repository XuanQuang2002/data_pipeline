# E-commerce Data Pipeline

A Python-based data engineering project that builds an end-to-end pipeline for an e-commerce business domain. The project ingests customer, product, order, order-item, and payment data from local files and a mock REST API, normalizes and validates it, loads it into PostgreSQL, and produces data quality and analytics outputs.

This repository is designed for learning and demonstration of ETL/ELT patterns, incremental ingestion, data validation, schema normalization, reject handling, and star-schema reporting in a realistic analytics workflow.

## Overview

The pipeline follows a simple but practical data lifecycle:

1. Extract raw data from source files and/or the mock API
2. Store immutable RAW snapshots
3. Normalize column names and values
4. Validate schema, business rules, and referential integrity
5. Separate valid records from rejects
6. Upsert valid rows into PostgreSQL
7. Generate quality reports and refresh the analytics mart

## Business scope

The model supports an e-commerce platform with the following core entities:

- Customers
- Products and categories
- Orders and order items
- Payments
- KPI and reporting by customer, category, product, and channel

The business rules enforced by the project cover uniqueness, non-negative values, valid statuses, cross-table references, and idempotent ingestion. These rules are aligned with the requirements documented in `docs/business_requirements.md`.

## Architecture

The project implements a layered pipeline:

- Raw layer: stores untouched source snapshots from files or API responses
- Staging/normalized layer: standardizes data types, string casing, timestamps, and column naming
- Validation layer: checks schema quality and business logic
- Reject layer: writes records failed validation to CSV files
- Core database: PostgreSQL stores master and transactional tables
- Reporting layer: generates DQ summaries and refreshes the sales mart

## Key features

- File-based and API-based incremental ingestion
- Daily batch processing with run metadata and checkpoint state
- Duplicate and referential integrity checks
- Data quality reporting and reject tracking
- Idempotent upserts for repeated runs
- PostgreSQL-backed analytics-ready marts
- Dockerized local environment with Postgres and mock API

## Tech stack

- Python 3.x
- Pandas
- SQLAlchemy
- PostgreSQL
- FastAPI mock API
- Docker Compose
- pytest

## Repository structure

```text
.
├── data/
│   ├── dirty/
│   ├── incremental/
│   ├── raw/
│   ├── reject/
│   ├── seed/
│   └── staging/
├── docs/
│   ├── api_docs.md
│   ├── business_requirements.md
│   ├── data_contract.md
│   ├── dataset_summary.json
│   └── ...
├── logs/
├── metadata/
├── mock_api/
├── reports/
├── scripts/
├── sql/
├── src/
├── tests/
├── .env.example
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── README.md
└── ...
```

## Data sources

The project supports two ingestion modes:

### 1. File-based ingestion

Used for daily batch import from local files stored under `data/incremental/`.

Example input directory:

```text
data/incremental/day_2026-07-01/
```

### 2. API-based ingestion

The project can pull incremental records from the mock API service running locally. API documentation is available in `docs/api_docs.md`.

Base URL:

```text
http://localhost:8000
```

Default API key:

```text
training-key
```

## Quick start

### Prerequisites

- Python 3.10+
- Docker Desktop or Docker Engine
- pip

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the sample environment file and adjust values if needed:

```bash
cp .env.example .env
```

The project expects a PostgreSQL connection and the mock API URL, with defaults configured for the local Docker setup.

### 4. Start the services

```bash
docker compose up -d
```

This starts:

- PostgreSQL on port `5433`
- Mock API on port `8000`

## Running the pipeline

### File-based pipeline

Run the pipeline against a local daily dataset:

```bash
python -m src.pipeline --input-dir data/incremental/day_2026-07-01 --source file --refresh-mart
```

### API-based pipeline

Pull the latest data from the mock API:

```bash
python -m src.pipeline --source api --refresh-mart
```

### Mixed mode

Use both local file and API sources together:

```bash
python -m src.pipeline --source both --refresh-mart
```

### Skip already-processed file batches

```bash
python -m src.pipeline --input-dir data/incremental/day_2026-07-01 --source file --skip-processed-file
```

## Pipeline behavior

Each run creates a unique `run_id`, tracks the source, and writes the status into `metadata/pipeline_state.json`.

During each run, the project:

- extracts raw data
- normalizes it
- validates data quality and business rules
- writes rejects to `data/reject/<run_id>/`
- upserts valid records into PostgreSQL
- compiles DQ reports in `reports/`
- optionally refreshes the sales mart

## Validation and data quality

The validation layer checks for:

- duplicate primary keys
- invalid or null values
- invalid categorical status values
- inconsistent monetary values
- invalid dates
- broken foreign keys across tables
- invalid customer/product/order references

The project also generates data quality summaries and reject CSV files so analysts can inspect failed rows without losing the original input.

## Output locations

- Raw source snapshots: `data/raw/`
- Reject records: `data/reject/`
- Clean staging outputs: `data/staging/`
- Pipeline state: `metadata/pipeline_state.json`
- Data quality reports: `reports/`
- Logs: `logs/pipeline.log`

## Testing

Run the automated test suite with:

```bash
pytest
```

The repository includes tests for extraction, profiling, and validation logic under `tests/`.

## Useful commands

```bash
# Start local services
docker compose up -d

# Run file pipeline
python -m src.pipeline --source file --refresh-mart

# Run API pipeline
python -m src.pipeline --source api --refresh-mart

# Run tests
pytest
```

## Project notes

- The project follows an incremental-load pattern with `updated_at` watermarking for API sources.
- Raw data is intentionally preserved and not overwritten during processing.
- Re-running the same file batch should not create duplicate records in the core database due to the upsert logic and checkpoint state.
- The project is primarily a training/reference implementation for data engineering concepts in a realistic retail dataset.

## Documentation

See the `docs/` folder for more detail on requirements, API behavior, data contracts, and project learning materials. The most relevant files are:

- `docs/business_requirements.md`
- `docs/api_docs.md`
- `docs/data_contract.md`
- `docs/dataset_summary.json`
