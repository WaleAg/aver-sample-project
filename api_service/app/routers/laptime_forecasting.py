from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel, Field
from ..core.auth import verify_bearer
import random, asyncio

# Router for lap time forecasting endpoints
router = APIRouter()

# Input schema
class LapTimeRequest(BaseModel):
    model_name: str
    event_name: str
    year: int = Field(gt=2000)
    car_no: int
    n_in: int
    n_out: int

# Output schema
class LapTimePrediction(BaseModel):
    lapcount: list[int]
    lapcount_future: list[int]
    predictions: list[float]
    pred_interval_5: list[float]
    pred_interval_95: list[float]

# In-memory store to keep track of request state
_lap_state: dict[str, int] = {}

# Helper function to generate lap time predictions
def _gen(start_lap: int, length: int = 15):
    laps = list(range(start_lap, start_lap + length))
    future = list(range(start_lap + length, start_lap + length + 5))

    # TODO: Replace this random generator with real ML inference,
    preds = [round(random.uniform(70, 120), 2) for _ in laps]

    # Confidence intervals
    pred5 = [p - round(random.uniform(0.5, 1.0), 2) for p in preds]
    pred95 = [p + round(random.uniform(0.5, 1.0), 2) for p in preds]

    return LapTimePrediction(
        lapcount=laps,
        lapcount_future=future,
        predictions=preds,
        pred_interval_5=pred5,
        pred_interval_95=pred95
    )

# Initialize a forecast session
@router.post("/laptime_forecasting/init")
def init_forecast(req: LapTimeRequest, _: str = Depends(verify_bearer)):
    """
    Initialize lap time forecasting for a given model/event/car/year.
    Returns a request_id that must be used in subsequent GET calls.
    """
    rid = f"{req.model_name}_{req.event_name}_{req.car_no}_{req.year}"
    _lap_state[rid] = 1
    return {"request_id": rid, "status": "initialized"}

# Get the next set of predictions
@router.get("/laptime_forecasting/predict", response_model=LapTimePrediction)
def get_forecast(request_id: str, _: str = Depends(verify_bearer)):
    """
    Generate predictions for the next laps. Requires a valid request_id.
    """
    if request_id not in _lap_state:
        raise HTTPException(status_code=404, detail="request_id not initialized")
    _lap_state[request_id] += 1
    return _gen(_lap_state[request_id])

# WebSocket endpoint to stream lap predictions live
@router.websocket("/laptime_forecasting/ws")
async def forecast_ws(ws: WebSocket):
    """
    Send lap predictions over WebSocket every 2s
    """
    await ws.accept()
    lap = 1
    while lap < 100:
        await ws.send_json(_gen(lap).dict())
        await asyncio.sleep(2)
        lap += 5
