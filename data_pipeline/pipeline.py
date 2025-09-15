from __future__ import annotations

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

try:
    from tabulate import tabulate
except ImportError:  # fallback
    tabulate = None


# Paths
ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "sample_data.csv"
DB_PATH = ROOT / "transactions.db"

REQUIRED_COLUMNS = {"user_id", "date", "amount"}


def extract(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load raw CSV into a DataFrame."""
    return pd.read_csv(path)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and aggregate transaction data."""
    # Validate schema
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {REQUIRED_COLUMNS}")

    # Handle missing/invalid values
    df = df.dropna(subset=REQUIRED_COLUMNS)
    df["user_id"] = df["user_id"].astype(str)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount"])

    # Aggregate transactions per user per day
    summary = (
        df.groupby(["user_id", df["date"].dt.date])["amount"]
        .sum()
        .reset_index()
        .rename(columns={"date": "date", "amount": "total_amount"})
    )
    return summary



def load(df: pd.DataFrame, db_path: Path = DB_PATH) -> None:
    """Load the cleaned summary into SQLite (creates empty table if no rows)."""
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        df.head(0).to_sql("transaction_summary", conn, if_exists="replace", index=False)
        if not df.empty:
            df.to_sql("transaction_summary", conn, if_exists="append", index=False)



def run_pipeline(data_path: Path = DATA_PATH, db_path: Path = DB_PATH):
    """End-to-end pipeline: extract → transform → load."""
    raw = extract(data_path)
    summary = transform(raw)
    load(summary, db_path)
    print(f"Pipeline complete. Loaded {len(summary)} rows into {db_path}")
    return summary



def get_summary(limit: int = 10) -> pd.DataFrame:
    """Helper to fetch a few rows from the summary table."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    query = f"SELECT * FROM transaction_summary LIMIT {limit}"
    return pd.read_sql(query, engine)


if __name__ == "__main__":
    df_summary = run_pipeline()
    sample = get_summary()

    if tabulate:
        print("\nSample summary:")
        print(tabulate(sample, headers="keys", tablefmt="psql", showindex=False))
    else:
        print("\nSample summary:")
        print(sample)
