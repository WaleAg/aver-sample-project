# Data Pipeline (CSV → SQLite with pandas)

A lightweight but **robust ETL pipeline** that demonstrates real-world data processing patterns:

- Extracts transaction data from CSV.
- Validates schema and handles dirty rows.
- Transforms by casting types and aggregating totals.
- Loads results into a SQLite database with SQLAlchemy.

---

## 🚀 Run the Pipeline

Install dependencies and run:

```bash
pip install -r requirements.txt
python -m data_pipeline.pipeline
```

By default, config is read from `.env`:

```env
DB_URL=sqlite:///data_pipeline/transactions.db
DATA_FILE=data_pipeline/sample_data.csv
```

You can copy defaults with:

```bash
cp data_pipeline/.env.example data_pipeline/.env
```

---

## ✅ Example Output

Running the pipeline produces logs and loads results into SQLite:

```
INFO - Pipeline started
INFO - Extracting data from data_pipeline/sample_data.csv
WARNING - Found 1 rows with null 'user_id' — dropping them
INFO - Transforming data
INFO - Loading data into database
INFO - Loaded 6 rows into sqlite:///data_pipeline/transactions.db
INFO - Pipeline completed successfully
```

Sample query result (`SELECT * FROM transaction_summary LIMIT 5`):

| user_id | date       | total_amount |
| ------- | ---------- | ------------ |
| u1      | 2025-09-01 | 250.0        |
| u2      | 2025-09-01 | 180.5        |
| u2      | 2025-09-02 | 20.0         |
| u3      | 2025-09-01 | 75.0         |
| u3      | 2025-09-02 | 75.0         |

---

## 🧪 Run Tests

```bash
PYTHONPATH=. pytest -q
```

All steps are covered:

- Extract (CSV → DataFrame)
- Validate (schema enforcement, null handling with warnings)
- Transform (aggregation per user/date)
- Load (writes to SQLite, queryable via SQL)
- End-to-end integration

---

## 📂 Artifacts

- `data_pipeline/sample_data.csv` → raw input transactions (includes valid + invalid rows for testing).
- `data_pipeline/transactions.db` → SQLite database with cleaned + aggregated results.
- Table: `transaction_summary` → total spend per user per day.

---

## 📝 Notes

- **Extract** → loads raw transactions from CSV.
- **Validate** → enforces schema, drops invalid rows with warnings.
- **Transform** → converts types and aggregates totals per user/date.
- **Load** → saves results into SQLite with SQLAlchemy.
