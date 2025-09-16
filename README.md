# Wale's Sample Project — Python Backend, ML Integration, and Data Pipelines

This repository contains three small, production-style Python projects showcasing backend APIs, ML integration, and data pipelines.

## Projects

1. **`api_service/`** — FastAPI service with validated endpoints, token-based authentication, health checks, and tests.
2. **`ml_integration/`** — Minimal ML model (sentiment analysis with scikit-learn) wrapped in FastAPI for inference.
3. **`data_pipeline/`** — CSV → SQLite ETL pipeline using pandas + SQLAlchemy with validation and tests.

## Key Practices Demonstrated

These projects highlight production-style practices such as:

- Modular project structure
- Token-based authentication & input validation (FastAPI)
- Automated tests with pytest
- Logging and error handling
- Clear READMEs for setup and usage

## How to Run

Each project has its own README with detailed instructions, but here are quick-start commands:

### API Service

```bash
cd api_service
pip install -r requirements.txt
uvicorn main:app --reload
```

### ML Integration

```bash
cd ml_integration
pip install -r requirements.txt
uvicorn app:app --reload
```

### Data Pipeline

```bash
cd data_pipeline
pip install -r requirements.txt
python pipeline.py --input sample.csv --output transactions.db
```

---

Each project is intentionally small in scope but structured to resemble production patterns.
They are designed to be easily extended and demonstrate secure, testable, and maintainable code.
