# Data Pipeline (CSV → SQLite with pandas)

Reads `sample_data.csv`, validates required columns, casts types, and loads to SQLite via SQLAlchemy.

## Run

```bash
pip install -r requirements.txt
python -m data_pipeline.pipeline
```

## Test

```bash
PYTHONPATH=. pytest -q
```

## Artifacts

- `data_pipeline/sample_data.csv` → raw input transactions
- `data_pipeline/transactions.db` → SQLite database with cleaned + aggregated results
- Table: `transaction_summary` → total spend per user per day

## Notes

- **Extract**: loads raw transactions from CSV.
- **Transform**: validates schema, drops invalid rows, converts data types, aggregates totals per user/date.
- **Load**: saves the summary into a SQLite table (`transaction_summary`).
- Lightweight demo of ETL (Extract → Transform → Load) workflow.
