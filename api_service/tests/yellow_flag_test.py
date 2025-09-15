# api_service/tests/test_yellow_flag.py
from fastapi.testclient import TestClient
from api_service.app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer mysecrettoken"}

def test_yellow_flag_flow():
    # init
    init = client.post("/v1/yellow_flag/init", json={
        "model_name": "baseline",
        "event_name": "Toronto",
        "year": 2024,
        "incidents_last_10": 0,
        "rain_probability": 0.0,
        "safety_car_history": 0
    }, headers=AUTH)
    assert init.status_code == 200
    rid = init.json()["request_id"]

    # predict
    r = client.get(
        f"/v1/yellow_flag/predict?request_id={rid}&incidents_last_10=3&rain_probability=0.4&safety_car_history=2",
        headers=AUTH
    )
    assert r.status_code == 200
    j = r.json()

    # validate structure
    assert "score" in j
    assert "recommendation" in j
    assert "lap" in j

    # validate values
    assert isinstance(j["score"], float)
    assert 0 <= j["score"] <= 1
