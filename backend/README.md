# Backend — Plant Disease Detection System

FastAPI service that serves an EfficientNetB0 model trained on the PlantVillage dataset (38 classes),
returning a disease prediction plus full recommendation content (description, symptoms, causes,
treatment, prevention) in a single response.

## Architecture

```
app/
├── main.py         # App entrypoint: mounts routers, CORS, startup/shutdown lifespan
├── config.py        # Pydantic Settings (reads .env)
├── database.py       # MongoDB (Motor) connection lifecycle
├── routers/          # HTTP endpoints (thin controllers)
├── services/          # Business logic (image processing, inference, recommendations, history)
├── schemas/           # Pydantic request/response models
├── models/             # MongoDB document models
└── utils/               # Image validation, exceptions, logging

ml_model/
├── dataset/            # PlantVillage dataset (not tracked in git)
├── saved_model/         # plant_disease_model.keras, class_names.json, disease_info.json
└── train.py              # EfficientNetB0 training script
```

Routers depend on services; services depend on utils/config. The ML model and MongoDB client
are both loaded once and injected as singletons via FastAPI's `Depends()`, never re-created
per request.

## Local Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # then edit MONGODB_URI, etc.
```

Train the model first (see `ml_model/train.py`, added in Step 4) so that
`ml_model/saved_model/plant_disease_model.keras` and `class_names.json` exist — the API will
fail to start prediction requests without them.

Run the API (added in Step 5):

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger docs: http://localhost:8000/docs

## Status

This README will be expanded with full API usage examples once routers are generated (Step 5)
and again with test/deployment instructions in later steps.
