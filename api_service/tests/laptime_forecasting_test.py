# api_service/tests/test_laptime_forecasting.py
from fastapi.testclient import TestClient
from api_service.app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer mysecrettoken"}

def test_laptime_forecasting_flow():
    # init
    init = client.post("/v1/laptime_forecasting/init", json={
        "model_name": "baseline",
        "event_name": "Toronto",
        "year": 2024,
        "car_no": 28,
        "n_in": 5,
        "n_out": 5
    }, headers=AUTH)
    assert init.status_code == 200
    rid = init.json()["request_id"]

    # predict
    r = client.get(f"/v1/laptime_forecasting/predict?request_id={rid}", headers=AUTH)
    assert r.status_code == 200
    j = r.json()
    assert "predictions" in j and isinstance(j["predictions"], list)
    assert len(j["predictions"]) > 0 
