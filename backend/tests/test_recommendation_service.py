"""Unit tests for RecommendationService, plus a regression guard tying the real
class_names.json and disease_info.json files together (see ml_model/train.py's
generator - a future edit to one file without the other should fail here)."""
import json

import pytest

from app.config import get_settings
from app.services.recommendation_service import RecommendationService
from app.utils.exceptions import DiseaseInfoNotFoundException


@pytest.fixture
def sample_disease_info_path(tmp_path):
    data = {
        "Tomato___Late_blight": {
            "description": "Test description.",
            "symptoms": ["Symptom A"],
            "causes": ["Cause A"],
            "treatment": ["Treatment A"],
            "prevention": ["Prevention A"],
        }
    }
    path = tmp_path / "disease_info.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_get_info_returns_known_class(sample_disease_info_path):
    service = RecommendationService(sample_disease_info_path)
    info = service.get_info("Tomato___Late_blight")
    assert info["description"] == "Test description."


def test_get_info_raises_for_unknown_class(sample_disease_info_path):
    service = RecommendationService(sample_disease_info_path)
    with pytest.raises(DiseaseInfoNotFoundException):
        service.get_info("Not___A_real_class")


def test_missing_file_loads_empty_and_warns(tmp_path):
    service = RecommendationService(tmp_path / "does_not_exist.json")
    with pytest.raises(DiseaseInfoNotFoundException):
        service.get_info("Tomato___Late_blight")


def test_real_disease_info_matches_class_names():
    """Guards against Step 4's data files drifting apart over future edits."""
    settings = get_settings()
    class_names = json.loads(settings.class_names_path_resolved.read_text(encoding="utf-8"))
    disease_info = json.loads(settings.disease_info_path_resolved.read_text(encoding="utf-8"))

    assert len(class_names) == 38
    assert set(class_names) == set(disease_info.keys())

    required_fields = {"description", "symptoms", "causes", "treatment", "prevention"}
    for class_name, info in disease_info.items():
        missing = required_fields - info.keys()
        assert not missing, f"'{class_name}' is missing fields: {missing}"
