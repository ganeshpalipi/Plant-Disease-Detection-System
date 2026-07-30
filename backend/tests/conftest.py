"""Shared pytest fixtures.

Design goal: the test suite must run without TensorFlow installed and without a live
MongoDB connection. Heavy/external dependencies (the ML model, the database) are swapped
for lightweight fakes via FastAPI's `dependency_overrides`, while everything else (image
validation/preprocessing, the real disease_info.json data, routing, error handling) is
exercised for real through the actual HTTP layer.
"""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import get_settings
from app.main import app
from app.services.history_service import get_history_service
from app.services.prediction_service import get_prediction_service
from app.services.recommendation_service import get_recommendation_service
from app.utils.exceptions import HistoryNotFoundException


class FakePredictionService:
    """Stands in for the real EfficientNetB0-backed PredictionService in tests."""

    def predict(self, preprocessed_image):
        return "Tomato___Late_blight", 98.74

    def parse_class_name(self, raw_class_name):
        return "Tomato", "Late Blight", False


class FakeRecommendationService:
    def get_info(self, class_name):
        return {
            "description": "Test description.",
            "symptoms": ["Symptom A"],
            "causes": ["Cause A"],
            "treatment": ["Treatment A"],
            "prevention": ["Prevention A"],
        }


class FakeHistoryService:
    """In-memory stand-in for MongoDB-backed HistoryService."""

    def __init__(self):
        self.saved_records = []

    async def save(self, record):
        self.saved_records.append(record)
        return "fake_history_id"

    async def list_recent(self, limit=20, skip=0):
        return [], 0

    async def get_by_id(self, record_id):
        raise HistoryNotFoundException(record_id)


@pytest.fixture
def fake_prediction_service():
    return FakePredictionService()


@pytest.fixture
def fake_recommendation_service():
    return FakeRecommendationService()


@pytest.fixture
def fake_history_service():
    return FakeHistoryService()


@pytest.fixture(scope="session")
def _session_client():
    """One TestClient (and one lifespan startup/shutdown cycle) for the whole session,
    so a slow/unreachable MongoDB URI only costs time once, not per test."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client(_session_client, fake_prediction_service, fake_recommendation_service, fake_history_service):
    """A client with the ML model and database swapped for fakes - the default for
    tests that only care about request/response behavior, not external dependencies."""
    app.dependency_overrides[get_prediction_service] = lambda: fake_prediction_service
    app.dependency_overrides[get_recommendation_service] = lambda: fake_recommendation_service
    app.dependency_overrides[get_history_service] = lambda: fake_history_service
    yield _session_client
    app.dependency_overrides.clear()


@pytest.fixture
def real_dependencies_client(_session_client):
    """A client with NO dependency overrides - exercises the real
    get_prediction_service()/get_history_service() providers, for tests that verify
    graceful degradation when the model isn't trained yet or MongoDB isn't reachable."""
    app.dependency_overrides.clear()
    yield _session_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_image_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (256, 256), color=(34, 139, 34)).save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture(autouse=True, scope="session")
def _cleanup_uploads_dir():
    """Successful /predict tests write real files to backend/uploads/ via the real
    ImageProcessingService - clean them up after the test session."""
    yield
    upload_dir = get_settings().upload_dir_resolved
    if upload_dir.exists():
        for item in upload_dir.iterdir():
            if item.name != ".gitkeep":
                item.unlink(missing_ok=True)
