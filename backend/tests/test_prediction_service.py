"""Unit tests for PredictionService.parse_class_name - pure string logic, no model needed.

Regression-tests the exact PlantVillage label formats stored in class_names.json, since a
parsing mistake here would silently mislabel real predictions.
"""
import pytest

from app.services.prediction_service import PredictionService


@pytest.mark.parametrize(
    "raw_class_name, expected_plant, expected_disease, expected_is_healthy",
    [
        ("Tomato___Late_blight", "Tomato", "Late blight", False),
        ("Apple___healthy", "Apple", "Healthy", True),
        ("Corn_(maize)___Common_rust_", "Corn (maize)", "Common rust", False),
        ("Pepper,_bell___Bacterial_spot", "Pepper, bell", "Bacterial spot", False),
        (
            "Tomato___Spider_mites Two-spotted_spider_mite",
            "Tomato",
            "Spider mites Two-spotted spider mite",
            False,
        ),
        ("Grape___Esca_(Black_Measles)", "Grape", "Esca (Black Measles)", False),
    ],
)
def test_parse_class_name(raw_class_name, expected_plant, expected_disease, expected_is_healthy):
    plant, disease, is_healthy = PredictionService.parse_class_name(raw_class_name)
    assert plant == expected_plant
    assert disease == expected_disease
    assert is_healthy is expected_is_healthy
