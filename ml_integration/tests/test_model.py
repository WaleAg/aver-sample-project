from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ml_integration.api import app
from ml_integration.model.predict import predict_sentiment
from ml_integration.model.train import MODEL_PATH

client = TestClient(app)


def test_model_file_exists():
    """Ensure the trained model file exists before predictions."""
    assert MODEL_PATH.exists(), "Model file not found. Run training first."


@pytest.mark.parametrize(
    "text, expected_label",
    [
        ("I absolutely love this!", "positive"),
        ("This is terrible and I hate it.", "negative"),
    ],
)
def test_predict_function(text, expected_label):
    """Directly test the prediction function on known examples."""
    res = predict_sentiment(text)
    assert res["label"] == expected_label
    assert "score" in res and 0.0 <= res["score"] <= 1.0


def test_predict_api_happy_path():
    """Call the API with a valid request and check the response shape and values."""
    resp = client.post("/predict", json={"text": "This is great"})
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {"label", "score"}
    assert body["label"] in {"positive", "negative"}
    assert 0.0 <= body["score"] <= 1.0


def test_predict_api_validation():
    """Ensure invalid input (empty text) is rejected."""
    resp = client.post("/predict", json={"text": ""})
    assert resp.status_code == 422  # Pydantic validation error


def test_health_check():
    """Ensure the /healthz endpoint works as expected."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
