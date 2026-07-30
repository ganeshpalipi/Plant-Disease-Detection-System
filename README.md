# Plant Disease Detection System

AI-powered web application that detects plant diseases from leaf images and returns not just a
label, but full actionable guidance: plant name, disease, confidence score, description, symptoms,
causes, treatment, and prevention. Built as a B.Tech CSE (AI & ML) minor project.

## Architecture

```
┌──────────────────┐   REST / multipart   ┌───────────────────┐   Motor/PyMongo   ┌────────────────┐
│  React Frontend   │ ───────────────────▶ │  FastAPI Backend   │ ─────────────────▶│  MongoDB Atlas  │
│  (Vite + Tailwind)│ ◀─────────────────── │  (Clean Architecture)│◀────────────────│ (History)       │
└──────────────────┘        JSON           └───────────────────┘                   └────────────────┘
                                                     │
                                                     │ lazy-loads on first /predict call
                                                     ▼
                                          ┌───────────────────────┐
                                          │ EfficientNetB0 (.keras) │
                                          │ 38 PlantVillage classes │
                                          └───────────────────────┘
```

See [backend/README.md](backend/README.md) for the backend's internal layering.

## Project Structure

```
Plant-Disease-Detection-System/
├── backend/         FastAPI app, ML training pipeline, saved model artifacts
├── frontend/        React + Vite + Tailwind UI
└── docs/            API, installation and deployment documentation
```

## Running Locally (Both Servers)

**1. Backend** — http://localhost:8000

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Swagger docs: http://localhost:8000/docs

**2. Frontend** — http://localhost:5173

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The frontend's `.env` points `VITE_API_BASE_URL` at `http://localhost:8000`; the backend's `.env`
lists `http://localhost:5173` in `ALLOWED_ORIGINS` for CORS. Both are pre-wired to work together
out of the box — no extra configuration needed for local development.

## Testing

```bash
cd backend
pytest -v
```

30 tests, all passing in under a second — no TensorFlow or live MongoDB required (the ML model
and database are swapped for fakes via FastAPI's `dependency_overrides`; see
[backend/tests/conftest.py](backend/tests/conftest.py)). Two tests deliberately use the real,
un-mocked providers to lock in the graceful-degradation behavior described below.

## Deployment

Frontend → Vercel, Backend → Render, Database → MongoDB Atlas. Full walkthrough — including how
to get the gitignored trained model onto Render — in
[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md).

## Current Status

- **Backend**: fully functional — routes, services, error handling, MongoDB integration all built
  and verified against a live server.
- **Frontend**: fully functional — all 5 pages built and verified in a real browser (build, lint,
  full upload→result flow, mobile layout, error states).
- **Integration**: verified live — CORS confirmed working via a real cross-origin `fetch` from the
  frontend origin, and a real (unmocked) `/predict` request correctly returns a graceful 503 with
  a clear message, since no trained model exists yet.
- **ML model**: `train.py` is complete and ready to run, but requires the PlantVillage dataset
  (not included — download separately) and real training time. Until `plant_disease_model.keras`
  exists at `backend/ml_model/saved_model/`, `/predict` returns `503 ModelLoadException` by design
  rather than crashing the server.
- **MongoDB**: requires a real `MONGODB_URI` in `backend/.env` (e.g. MongoDB Atlas). Until then,
  `/history` returns `503 DatabaseConnectionException`; predictions still succeed without it.

## Documentation

- [backend/README.md](backend/README.md) — backend architecture and setup
- [docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) — full local setup, including model
  training and MongoDB
- [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) — every endpoint, request/response
  examples, error codes
- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) — Vercel + Render + MongoDB Atlas deployment
