"""Tests for POST /api/v1/predict.

Most tests use the `client` fixture (fake model/DB) to test request handling in
isolation. `test_predict_real_model_not_trained_returns_503` deliberately uses the real,
un-mocked PredictionService to prove the exact graceful-degradation behavior verified
manually in Step 7: no model file yet -> a clean 503, not a crash.
"""


def test_predict_success(client, sample_image_bytes, fake_history_service):
    files = {"file": ("leaf.jpg", sample_image_bytes, "image/jpeg")}
    response = client.post("/api/v1/predict", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["plant"] == "Tomato"
    assert body["disease"] == "Late Blight"
    assert body["confidence"] == 98.74
    assert body["is_healthy"] is False
    assert body["description"] == "Test description."
    assert body["history_id"] == "fake_history_id"
    assert len(fake_history_service.saved_records) == 1
    assert fake_history_service.saved_records[0].plant == "Tomato"


def test_predict_rejects_unsupported_format(client, sample_image_bytes):
    files = {"file": ("leaf.gif", sample_image_bytes, "image/gif")}
    response = client.post("/api/v1/predict", files=files)

    assert response.status_code == 415
    assert response.json()["error"] == "UnsupportedFormatException"


def test_predict_rejects_corrupted_image(client):
    files = {"file": ("leaf.jpg", b"this is not a real image file", "image/jpeg")}
    response = client.post("/api/v1/predict", files=files)

    assert response.status_code == 422
    assert response.json()["error"] == "CorruptedImageException"


def test_predict_rejects_oversized_image(client):
    huge_bytes = b"\xff" * (11 * 1024 * 1024)
    files = {"file": ("leaf.jpg", huge_bytes, "image/jpeg")}
    response = client.post("/api/v1/predict", files=files)

    assert response.status_code == 400
    assert response.json()["error"] == "InvalidImageException"


def test_predict_missing_file_returns_422(client):
    response = client.post("/api/v1/predict")
    assert response.status_code == 422


def test_predict_real_model_not_trained_returns_503(real_dependencies_client, sample_image_bytes):
    files = {"file": ("leaf.jpg", sample_image_bytes, "image/jpeg")}
    response = real_dependencies_client.post("/api/v1/predict", files=files)

    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "ModelLoadException"
    assert "train it first" in body["message"].lower()
