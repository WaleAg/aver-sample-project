# ML Integration (FastAPI)

Demo project showing how to train a simple NLP model (sentiment analysis) and expose it as a FastAPI service.

## Run locally

```bash
# from project root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Train the model

```bash
# run training (loads data/sentiment.csv if present, else uses fallback dataset)
python -m ml_integration.model.train
```

Artifacts:

- `ml_integration/model/sentiment_model.joblib` → trained pipeline (TF-IDF + Logistic Regression)
- `ml_integration/model/metrics.json` → training metrics (accuracy, precision, recall, f1)

## Start API

```bash
uvicorn ml_integration.api:app --reload
```

### Interactive Docs

Browse interactive docs at http://127.0.0.1:8000/docs

## Health Check

```bash
curl http://127.0.0.1:8000/healthz
# -> {"status":"ok"}
```

## Example calls

### Predict sentiment

```bash
curl -s http://127.0.0.1:8000/predict   -H "Content-Type: application/json"   -d '{"text":"I really enjoyed this service"}'
```

Response:

```json
{ "label": "positive", "score": 0.91 }
```

```bash
curl -s http://127.0.0.1:8000/predict   -H "Content-Type: application/json"   -d '{"text":"This is the worst experience"}'
```

Response:

```json
{ "label": "negative", "score": 0.88 }
```

## Test

```bash
PYTHONPATH=. pytest -q
```

## Notes

- The sample dataset is in data/sentiment.csv. Expand it with more examples for better accuracy.
- The model pipeline uses: TF-IDF for feature extraction and Logistic Regression for classification.
- Predictions return both a discrete label (positive/negative) and a probability score.
- This is a lightweight demo for showcasing ML integration and API design.
