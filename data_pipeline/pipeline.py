import os
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load config
load_dotenv()
DB_URL = os.getenv("DB_URL", "sqlite:///transactions.db")
DATA_FILE = os.getenv("DATA_FILE", "sample_data.csv")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"user_id", "date", "amount"}

def extract(file_path: str = DATA_FILE) -> pd.DataFrame:
    """Extract data from CSV into a DataFrame."""
    try:
        logger.info(f"Extracting data from {file_path}")
        return pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Failed to extract data: {e}")
        raise

def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Validate schema and critical fields."""
    logger.info("Validating data schema")
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise ValueError(f"CSV must contain required columns: {REQUIRED_COLUMNS}")
    
    # Handle null user_id
    if df["user_id"].isnull().any():
        null_count = df["user_id"].isnull().sum()
        logger.warning(f"Found {null_count} rows with null 'user_id' — dropping them")
        df = df.dropna(subset=["user_id"])
    
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and aggregate transaction data."""
    logger.info("Transforming data")
    df = df.dropna(subset=REQUIRED_COLUMNS)
    df["user_id"] = df["user_id"].astype(str)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount"])

    # Aggregate
    summary = (
        df.groupby(["user_id", df["date"].dt.date])["amount"]
        .sum()
        .reset_index()
        .rename(columns={"date": "date", "amount": "total_amount"})
    )
    return summary

def load(df: pd.DataFrame, db_url: str = DB_URL):
    """Load data into target database."""
    try:
        logger.info("Loading data into database")
        engine = create_engine(db_url)
        df.to_sql("transaction_summary", con=engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df)} rows into {db_url}")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise

def run_pipeline():
    """Main pipeline entry point."""
    logger.info("Pipeline started")
    df = extract(DATA_FILE)
    df = validate(df)
    df = transform(df)
    load(df, DB_URL)
    logger.info("Pipeline completed successfully")

if __name__ == "__main__":
    run_pipeline()
