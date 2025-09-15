# API Service (FastAPI)

Demo FastAPI service exposing token-protected race strategy endpoints.  
Endpoints are stubbed with random/demo values

## Endpoints

- `POST /v1/laptime_forecasting/init` → start a session, get `request_id`
- `GET /v1/laptime_forecasting/predict?request_id=...` → fetch next lap predictions
- `POST /v1/tyre_degradation/init` → start tyre degradation tracking
- `GET /v1/tyre_degradation/predict?request_id=...` → fetch tyre wear predictions
- `POST /v1/yellow_flag/init` → start yellow flag scoring
- `GET /v1/yellow_flag/predict?request_id=...` → fetch yellow flag probability
- `GET /healthz` and `GET /readyz` → liveness/readiness probes

## Run locally

```bash
# from project root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# set demo auth token
export DEMO_BEARER_TOKEN=mysecrettoken

# start API
uvicorn api_service.app.main:app --reload
```

### Interactive Docs

Browse interactive docs at http://127.0.0.1:8000/docs

## Auth

- In Swagger UI (`http://127.0.0.1:8000/docs`), click **Authorize** (green lock icon).
- Enter: `Bearer mysecrettoken`

## Example calls

### Laptime Forecasting

```bash
# init laptime forecasting
curl -X POST http://127.0.0.1:8000/v1/laptime_forecasting/init   -H "Authorization: Bearer mysecrettoken"   -H "Content-Type: application/json"   -d '{"model_name":"baseline","event_name":"Toronto","year":2024,"car_no":28,"n_in":5,"n_out":5}'

# get predictions
curl -X GET "http://127.0.0.1:8000/v1/laptime_forecasting/predict?request_id=baseline_Toronto_28_2024"   -H "Authorization: Bearer mysecrettoken"
```

### Tyre Degradation

```bash
# init tyre degradation
curl -X POST http://127.0.0.1:8000/v1/tyre_degradation/init   -H "Authorization: Bearer mysecrettoken"   -H "Content-Type: application/json"   -d '{"model_name":"tyre_model","event_name":"TorontoGP","year":2024,"car_no":27,"n_laps":10,"initial_wear":0.2}'

# get predictions
curl -X GET "http://127.0.0.1:8000/v1/tyre_degradation/predict?request_id=tyre_model_TorontoGP_27_2024"   -H "Authorization: Bearer mysecrettoken"
```

### Yellow Flag

```bash
# init yellow flag scoring
curl -X POST http://127.0.0.1:8000/v1/yellow_flag/init   -H "Authorization: Bearer mysecrettoken"   -H "Content-Type: application/json"   -d '{"model_name":"yellow_model","event_name":"Indy500","year":2024,"incidents_last_10":3,"rain_probability":0.4,"safety_car_history":2}'

# get predictions
curl -X GET "http://127.0.0.1:8000/v1/yellow_flag/predict?request_id=yellow_model_Indy500_2024&incidents_last_10=3&rain_probability=0.4&safety_car_history=2"   -H "Authorization: Bearer mysecrettoken"
```

## Test

```bash
PYTHONPATH=. pytest -q
```

## Notes

- All outputs are simulated with random values for demo purposes.
