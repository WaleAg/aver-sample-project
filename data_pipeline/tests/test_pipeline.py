from pathlib import Path
import pandas as pd
import pytest
from sqlalchemy import create_engine
from data_pipeline import pipeline


def test_extract_loads_csv(tmp_path):
    """Ensure extract reads CSV into a DataFrame."""
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("user_id,date,amount\nu1,2025-09-01,100\n")
    df = pipeline.extract(csv_path)
    assert not df.empty
    assert list(df.columns) == ["user_id", "date", "amount"]


def test_validate_passes_on_good_data():
    df = pd.DataFrame([{"user_id": "u1", "date": "2025-09-01", "amount": 100}])
    validated = pipeline.validate(df)
    assert not validated.empty


def test_validate_fails_on_missing_column():
    df = pd.DataFrame([{"user_id": "u1", "date": "2025-09-01"}])  # no 'amount'
    with pytest.raises(ValueError, match="required columns"):
        pipeline.validate(df)


def test_validate_drops_null_user_id(caplog):
    """Validate should drop rows with null user_id and log a warning."""
    df = pd.DataFrame([
        {"user_id": None, "date": "2025-09-01", "amount": 10},
        {"user_id": "u1", "date": "2025-09-01", "amount": 20},
    ])
    with caplog.at_level("WARNING"):
        validated = pipeline.validate(df)

    # Assert a warning was logged
    assert "dropping" in caplog.text

    # Assert the valid row remains
    assert "u1" in validated["user_id"].values
    assert validated["user_id"].isnull().sum() == 0



@pytest.mark.parametrize(
    "rows, expected_total",
    [
        (
            [  # multiple rows → should sum
                {"user_id": "u1", "date": "2025-09-01", "amount": 100},
                {"user_id": "u1", "date": "2025-09-01", "amount": 50},
            ],
            150,
        ),
        (
            [  # single row → unchanged
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
    assert summary["total_amount"].iloc[0] == expected_total
    assert pd.api.types.is_numeric_dtype(summary["total_amount"])


def test_load_writes_to_database(tmp_path):
    db_path = tmp_path / "transactions.db"
    db_url = f"sqlite:///{db_path}"
    df = pd.DataFrame(
        [{"user_id": "u1", "date": "2025-09-01", "total_amount": 100}]
    )

    pipeline.load(df, db_url)

    engine = create_engine(db_url)
    rows = pd.read_sql("SELECT * FROM transaction_summary", engine)
    assert not rows.empty
    assert set(rows.columns) == {"user_id", "date", "total_amount"}


def test_run_pipeline_end_to_end(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("user_id,date,amount\nu1,2025-09-01,100\n")
    db_path = tmp_path / "transactions.db"

    # Override globals for test
    pipeline.DATA_FILE = str(csv_path)
    pipeline.DB_URL = f"sqlite:///{db_path}"

    pipeline.run_pipeline()

    engine = create_engine(pipeline.DB_URL)
    rows = pd.read_sql("SELECT * FROM transaction_summary", engine)
    assert not rows.empty
    assert set(rows.columns) == {"user_id", "date", "total_amount"}
