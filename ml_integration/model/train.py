from __future__ import annotations

from pathlib import Path
import json
from typing import Tuple, List

import joblib
import numpy as np

try:
    import pandas as pd  # optional, only needed if you use a CSV dataset
except Exception:  # pragma: no cover
    pd = None

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Paths
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sentiment.csv"       # optional dataset
MODEL_DIR = Path(__file__).parent
MODEL_PATH = MODEL_DIR / "sentiment_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

LABEL_MAP = {0: "negative", 1: "positive"}  # keep it simple & explicit


def _load_dataset() -> Tuple[List[str], List[int]]:
    """
    Load dataset from data/sentiment.csv if present (expects columns: text,label).
    Otherwise fall back to a small, built-in sample so the project runs out of the box.
    """
    if DATA_PATH.exists():
        if pd is None:
            raise RuntimeError("pandas is required to read data/sentiment.csv")
        df = pd.read_csv(DATA_PATH)
        if not {"text", "label"}.issubset(df.columns):
            raise ValueError("sentiment.csv must have columns: text,label")
        X = df["text"].astype(str).tolist()
        y = df["label"].astype(int).tolist()
        return X, y

    # Minimal fallback dataset (small but works for demo)
    X = [
        "I love this product, it is fantastic!",
        "Absolutely wonderful experience. Highly recommend.",
        "This is the best thing I've bought this year.",
        "Terrible quality and awful support.",
        "I hate it. Waste of money.",
        "Not good at all, very disappointed.",
        "Great value and works perfectly.",
        "Really happy with the performance.",
        "Awful packaging and broken on arrival.",
        "Brilliant! Exceeded my expectations.",
        "Mediocre at best, would not buy again.",
        "Pretty decent overall, satisfied with it.",
    ]
    y = [1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1]
    return X, y


def build_pipeline() -> Pipeline:
    """
    Text -> TF-IDF -> Logistic Regression (binary).
    """
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95)),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )


def main() -> None:
    X, y = _load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, target_names=list(LABEL_MAP.values()), zero_division=0)

    # Save the whole pipeline (vectorizer + classifier)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)

    # Save basic metrics for transparency
    METRICS_PATH.write_text(json.dumps({"accuracy": acc, "report": report}, indent=2))

    print(f"Saved model -> {MODEL_PATH}")
    print(f"Accuracy: {acc:.3f}")
    print(report)


if __name__ == "__main__":
    main()
