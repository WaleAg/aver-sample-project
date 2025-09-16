from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ..core.auth import verify_bearer
import random

# Router for yellow flag probability endpoints
router = APIRouter()

# Input schema
class YellowFlagRequest(BaseModel):
    model_name: str
    event_name: str
    year: int = Field(gt=2000)
    incidents_last_10: int = Field(ge=0, description="Number of incidents in last 10 laps")
    rain_probability: float = Field(ge=0, le=1, description="Probability of rain (0..1)")
    safety_car_history: int = Field(ge=0, description="Number of prior safety car deployments")

# Output schema
class YellowFlagPrediction(BaseModel):
    lap: int
    score: float
    recommendation: str

# In-memory state keyed by request_id
_yellow_flag_state: dict[str, int] = {}

# Weights for the demo scoring model
INCIDENT_WEIGHT = 0.05
RAIN_WEIGHT = 0.6
SAFETY_CAR_WEIGHT = 0.03

@router.post("/yellow_flag/init")
def init_yellow_flag(req: YellowFlagRequest, _: str = Depends(verify_bearer)):
    """
    Initialize yellow flag scoring for a given session.
    Returns a request_id to use for predictions.
    """
    rid = f"{req.model_name}_{req.event_name}_{req.year}"
    _yellow_flag_state[rid] = 1
    return {"request_id": rid, "status": "initialized"}

@router.get("/yellow_flag/predict", response_model=YellowFlagPrediction)
def predict_yellow_flag(
    request_id: str,
    incidents_last_10: int,
    rain_probability: float,
    safety_car_history: int,
    _: str = Depends(verify_bearer)
):
    """
    Compute a simple probability score for a yellow flag event.
    TODO: Replace with ML model inference and persist results.
    """
    if request_id not in _yellow_flag_state:
        raise HTTPException(
        status_code=400,
        detail=f"Invalid request ID '{request_id}'. You must first call POST /v1/yellow_flag/init to get a request_id.."
    )

    # Increment lap counter
    _yellow_flag_state[request_id] += 1
    lap = _yellow_flag_state[request_id]

    # Weighted demo formula
    score = (
        INCIDENT_WEIGHT * incidents_last_10
        + RAIN_WEIGHT * rain_probability
        + SAFETY_CAR_WEIGHT * safety_car_history
    )
    score = min(score, 1.0)

    recommendation = "High risk of yellow flag" if score > 0.7 else "Low risk"

    return YellowFlagPrediction(
        lap=lap,
        score=round(score, 3),
        recommendation=recommendation
    )
