from pathlib import Path
import pandas as pd
import pytest
from sqlalchemy import create_engine

from data_pipeline import pipeline

DB_PATH = Path(__file__).resolve().parents[1] / "data_pipeline" / "transactions.db"


def test_extract_loads_csv(tmp_path):
    """Ensure extract reads CSV into a DataFrame."""
    # Write a minimal CSV to temp path
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("user_id,date,amount\nu1,2025-09-01,100\n")
    df = pipeline.extract(csv_path)
    assert not df.empty
    assert list(df.columns) == ["user_id", "date", "amount"]


@pytest.mark.parametrize(
    "rows, expected_total",
    [
        # multiple rows for u1 → should sum to 150
        (
            [
                {"user_id": "u1", "date": "2025-09-01", "amount": 100},
                {"user_id": "u1", "date": "2025-09-01", "amount": 50},
            ],
            150,
        ),
        # single row for u2 → should remain unchanged
        (
            [
                {"user_id": "u2", "date": "2025-09-02", "amount": 20},
            ],
            20,
        ),
    ],
)
def test_transform_aggregates(rows, expected_total):
    """Ensure transform aggregates correctly by user/date."""
    df = pd.DataFrame(rows)
    summary = pipeline.transform(df)
    assert not summary.empty
    total = summary["total_amount"].iloc[0]
    assert total == expected_total
    # column type should remain numeric
    assert pd.api.types.is_numeric_dtype(summary["total_amount"])


def test_run_pipeline_creates_db(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("user_id,date,amount\nu1,2025-09-01,100\n")
    db_path = tmp_path / "transactions.db"

    pipeline.run_pipeline(data_path=csv_path, db_path=db_path)

    engine = create_engine(f"sqlite:///{db_path}")
    rows = pd.read_sql("SELECT * FROM transaction_summary", engine)
    assert not rows.empty
    assert set(rows.columns) == {"user_id", "date", "total_amount"}


