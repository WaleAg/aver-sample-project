# api_service/tests/test_tyre_degradation.py
from fastapi.testclient import TestClient
from api_service.app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer mysecrettoken"}

def test_tyre_degradation_flow():
    # init
    init = client.post("/v1/tyre_degradation/init", json={
        "model_name": "baseline",
        "event_name": "Toronto",
        "year": 2024,
        "car_no": 27,
        "n_laps": 10,
        "initial_wear": 0.2
    }, headers=AUTH)
    assert init.status_code == 200
    rid = init.json()["request_id"]

    # predict
    r = client.get(f"/v1/tyre_degradation/predict?request_id={rid}", headers=AUTH)
    assert r.status_code == 200
    j = r.json()

    # validate structure
    assert "wear_after_stint" in j
    assert "recommendation" in j
    assert "pitstops" in j and isinstance(j["pitstops"], list)

    # validate values
    assert 0 <= j["wear_after_stint"] <= 1
    assert j["recommendation"] in ["OK", "Pit soon"]
