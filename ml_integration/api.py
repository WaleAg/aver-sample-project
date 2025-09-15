from __future__ import annotations

from typing import Literal
from typing_extensions import Annotated

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, constr

from .model.predict import predict_sentiment

app = FastAPI(
    title="Sentiment Analysis API",
    version="1.0.0",
    description="Simple demo of training + serving an NLP model with FastAPI.",
)

MAX_TEXT_LEN = 10_000  # basic guardrail


class PredictionRequest(BaseModel):
    text: Annotated[
        str,
        Field(..., description="Plain text to analyze", min_length=1, max_length=10000)
    ]


class PredictionResponse(BaseModel):
    label: Literal["positive", "negative"]
    score: float


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    txt = req.text
    if len(txt) > MAX_TEXT_LEN:
        raise HTTPException(status_code=413, detail=f"Text too long (>{MAX_TEXT_LEN} chars).")

    try:
        out = predict_sentiment(txt)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return out
