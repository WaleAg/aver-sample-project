from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ..core.auth import verify_bearer
import random

# Router for tyre degradation endpoints
router = APIRouter()

# Input schema
class TyreRequest(BaseModel):
    model_name: str
    event_name: str
    year: int = Field(gt=2000)
    car_no: int
    n_laps: int = Field(gt=0, description="Number of laps in this stint")
    initial_wear: float = Field(ge=0, le=1, description="Tyre wear at start (0..1)")

# Output schema
class TyrePrediction(BaseModel):
    lap_start: int
    lap_end: int
    wear_after_stint: float
    recommendation: str
    pitstops: list[int]

# In-memory state keyed by request_id
_tyre_state: dict[str, dict] = {}

# Constants for demo simulation
WEAR_RATE = 0.02         # 2% wear per lap (placeholder for real model)
PITSTOP_INTERVAL = 20    # Every 20 laps for demo

@router.post("/tyre_degradation/init")
def init_tyres(req: TyreRequest, _: str = Depends(verify_bearer)):
    """
    Initialize tyre degradation tracking for a car/session.
    Returns request_id for subsequent predictions.
    """
    rid = f"{req.model_name}_{req.event_name}_{req.car_no}_{req.year}"
    _tyre_state[rid] = {"lap_start": 1, "lap_end": 1}
    return {"request_id": rid, "status": "initialized"}

@router.get("/tyre_degradation/predict", response_model=TyrePrediction)
def predict_tyres(request_id: str, laps: int = 5, _: str = Depends(verify_bearer)):
    """
    Simulate tyre wear progression over the next few laps.
    TODO: Replace with real ML model inference and persist to DB.
    """
    if request_id not in _tyre_state:
        raise HTTPException(
        status_code=400,
        detail=f"Invalid request ID '{request_id}'. You must first call POST /v1/tyre_degragation/init to get a request_id.."
    )

    # Update lap range for this request
    state = _tyre_state[request_id]
    state["lap_start"] = state["lap_end"]
    state["lap_end"] += laps

    # Simulated wear progression
    wear = min(1.0, state.get("wear", 0) + WEAR_RATE * laps)
    state["wear"] = wear
    note = "Pit soon" if wear > 0.75 else "OK"

    # Fake pit stops (hardcoded interval for demo purposes)
    pitstops = list(range(PITSTOP_INTERVAL, 100, PITSTOP_INTERVAL))

    return TyrePrediction(
        lap_start=state["lap_start"],
        lap_end=state["lap_end"],
        wear_after_stint=round(wear, 3),
        recommendation=note,
        pitstops=pitstops
    )
