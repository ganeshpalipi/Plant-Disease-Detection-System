# API Documentation

Base URL (local): `http://localhost:8000/api/v1`

Interactive Swagger UI is auto-generated at `/docs` (and ReDoc at `/redoc`) whenever the backend
is running — this document is a static reference alongside it.

All error responses share one shape:

```json
{
  "error": "ExceptionClassName",
  "message": "Human-readable explanation."
}
```

---

## `GET /health`

Service health check.

**Response `200`**
```json
{
  "status": "ok",
  "app_name": "Plant Disease Detection System",
  "version": "1.0.0"
}
```

---

## `POST /predict`

Uploads a leaf image and returns the predicted plant/disease plus full recommendation content.

**Request**: `multipart/form-data`

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | file | yes | JPG/JPEG/PNG, up to 10MB |

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -F "file=@leaf.jpg"
```

**Response `200`**
```json
{
  "plant": "Tomato",
  "disease": "Late Blight",
  "confidence": 98.74,
  "is_healthy": false,
  "description": "Late Blight is a highly destructive disease caused by Phytophthora infestans...",
  "symptoms": ["Water-soaked, dark green to black lesions on leaves", "..."],
  "causes": ["Infection by the oomycete Phytophthora infestans", "..."],
  "treatment": ["Apply fungicides containing chlorothalonil or copper compounds immediately", "..."],
  "prevention": ["Use resistant tomato varieties", "..."],
  "history_id": "65f1c2e4a1b2c3d4e5f6a7b8"
}
```

`history_id` is `null` if the prediction succeeded but saving to MongoDB failed — the prediction
itself is never blocked by a history-persistence failure.

**Error responses**

| Status | `error` | Cause |
|---|---|---|
| 400 | `InvalidImageException` | Empty file, or exceeds `MAX_UPLOAD_SIZE_MB` |
| 415 | `UnsupportedFormatException` | Extension not in `.jpg`/`.jpeg`/`.png` |
| 422 | `CorruptedImageException` | File extension is valid but the image data can't be decoded |
| 422 | (FastAPI validation error) | `file` field missing from the request |
| 503 | `ModelLoadException` | Model not trained yet (`plant_disease_model.keras` missing) |
| 500 | `PredictionException` | Inference itself raised an unexpected error |

---

## `GET /history`

Lists recent predictions, newest first.

**Query parameters**

| Param | Type | Default | Notes |
|---|---|---|---|
| `limit` | int | 20 | 1–100 |
| `skip` | int | 0 | for pagination |

```bash
curl "http://localhost:8000/api/v1/history?limit=10&skip=0"
```

**Response `200`**
```json
{
  "total": 42,
  "items": [
    {
      "_id": "65f1c2e4a1b2c3d4e5f6a7b8",
      "plant": "Tomato",
      "disease": "Late Blight",
      "confidence": 98.74,
      "image_filename": "3f2a1b9c8d7e6f5a4b3c2d1e.jpg",
      "created_at": "2026-07-28T10:15:30.123Z"
    }
  ]
}
```

**Error responses**

| Status | `error` | Cause |
|---|---|---|
| 503 | `DatabaseConnectionException` | MongoDB unreachable/not configured |

---

## `GET /history/{record_id}`

Fetches a single history record by its MongoDB ObjectId.

```bash
curl http://localhost:8000/api/v1/history/65f1c2e4a1b2c3d4e5f6a7b8
```

**Response `200`** — same shape as one item in `GET /history`.

**Error responses**

| Status | `error` | Cause |
|---|---|---|
| 404 | `HistoryNotFoundException` | No record with that id (or id isn't a valid ObjectId) |
| 503 | `DatabaseConnectionException` | MongoDB unreachable/not configured |
