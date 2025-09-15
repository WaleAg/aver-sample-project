from __future__ import annotations

from pathlib import Path
import threading
from typing import Dict
import sys

import joblib
import numpy as np

# Path to the trained model
MODEL_PATH = Path(__file__).with_name("sentiment_model.joblib")
LABEL_MAP = {0: "negative", 1: "positive"}

_model = None
_lock = threading.Lock()


def _load_model():
    """Lazy-load the model once, thread-safe."""
    global _model
    with _lock:
        if _model is None:
            if not MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Model not found at {MODEL_PATH}. Run `python -m ml_integration.model.train` first."
                )
            _model = joblib.load(MODEL_PATH)
    return _model


def predict_sentiment(text: str) -> Dict[str, float | str]:
    """
    Predict the sentiment of a given text string.

    Args:
        text (str): Input sentence to analyze.

    Returns:
        dict: {
            "label": "positive" | "negative",
            "score": float probability of the predicted label
        }
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("`text` must be a non-empty string.")

    model = _load_model()
    probs = model.predict_proba([text])[0]
    idx = int(np.argmax(probs))
    return {
        "label": LABEL_MAP.get(idx, str(idx)),
        "score": float(probs[idx]),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m ml_integration.model.predict 'Your text here'")
        sys.exit(1)

    input_text = " ".join(sys.argv[1:])
    try:
        result = predict_sentiment(input_text)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
