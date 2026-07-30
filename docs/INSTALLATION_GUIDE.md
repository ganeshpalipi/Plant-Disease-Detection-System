# Installation Guide

Complete local setup instructions for the Plant Disease Detection System: backend, frontend,
database, and the ML model.

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11.x | Backend + model training |
| Node.js | 18+ | Frontend (tested with 20+) |
| MongoDB | Local install or [Atlas](https://www.mongodb.com/cloud/atlas) free tier | Prediction history storage |
| Git | any | |
pip list
GPU is optional but strongly recommended for training (Step 4's `train.py`) — CPU training on
the full PlantVillage dataset will be very slow.

## 1. Clone and Enter the Project

```bash
git clone <your-repo-url>
cd Plant-Disease-Detection-System
```

## 2. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
```

Edit `backend/.env`:
- `MONGODB_URI` — a local `mongodb://localhost:27017` or an Atlas connection string
- `ALLOWED_ORIGINS` — leave as `http://localhost:5173,http://localhost:3000` for local dev

The API will start even without a valid `MONGODB_URI` or a trained model — see
[backend/README.md](../backend/README.md) for why (`/predict` and `/history` degrade to a clean
503 instead of crashing the server). To actually get predictions and history working, see steps
3 and 4 below.

Run it:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify: open http://localhost:8000/docs (Swagger UI) or http://localhost:8000/api/v1/health.

## 3. Train the Model (Required for Real Predictions)

1. Download the PlantVillage dataset (color images, 38 classes). The "New Plant Diseases Dataset
   (Augmented)" on Kaggle is a common source and already ships in `train/` / `valid/` folders per
   class.
2. Place it at `backend/ml_model/dataset/` so the layout is:
   ```
   backend/ml_model/dataset/
     train/
       Apple___Apple_scab/*.jpg
       ...
     valid/
       Apple___Apple_scab/*.jpg
       ...
   ```
3. From `backend/`, run:
   ```bash
   python ml_model/train.py --epochs 15 --fine-tune-epochs 10
   ```
   This produces `backend/ml_model/saved_model/plant_disease_model.keras`,
   `classification_report.txt`, and `confusion_matrix.png`. It also overwrites
   `class_names.json` with the class order actually discovered on disk, so it always matches the
   trained weights.
4. Restart the backend (or just wait — the model loads lazily on the first `/predict` request).

## 4. MongoDB (for Prediction History)

**Option A — Local MongoDB**: install MongoDB Community Server, run it, and use
`MONGODB_URI=mongodb://localhost:27017` in `backend/.env`.

**Option B — MongoDB Atlas (recommended, free tier available)**:
1. Create a free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas).
2. Create a database user (Database Access) with a username/password.
3. Under Network Access, allow your current IP (or `0.0.0.0/0` for simplicity in development).
4. Copy the connection string from "Connect" → "Drivers", replace `<username>`/`<password>`, and
   set it as `MONGODB_URI` in `backend/.env`.

## 5. Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
npm run dev
```

Verify: open http://localhost:5173.

`frontend/.env`'s `VITE_API_BASE_URL` should point at wherever the backend is running
(`http://localhost:8000` by default).

## 6. Run the Test Suite

```bash
cd backend
pip install -r requirements.txt   # if not already done
pytest -v
```

The 30-test suite runs without TensorFlow or a live MongoDB connection (see
[backend/tests/conftest.py](../backend/tests/conftest.py) — the ML model and database are swapped
for lightweight fakes via FastAPI's dependency overrides).

## Troubleshooting

| Symptom | Likely Cause |
|---|---|
| `/predict` returns 503 `ModelLoadException` | Model not trained yet — see step 3 |
| `/history` returns 503 `DatabaseConnectionException` | `MONGODB_URI` unset/unreachable — see step 4 |
| Frontend shows "Cannot reach the server" | Backend isn't running, or `VITE_API_BASE_URL` is wrong |
| CORS error in browser console | Frontend's origin isn't in the backend's `ALLOWED_ORIGINS` |
