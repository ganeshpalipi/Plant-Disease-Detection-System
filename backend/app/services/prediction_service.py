"""Loads the trained EfficientNetB0 model and runs inference."""
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

import numpy as np

from app.config import get_settings
from app.utils.exceptions import ModelLoadException, PredictionException

logger = logging.getLogger(__name__)


class PredictionService:
    """Wraps the trained Keras model as a singleton inference engine."""

    def __init__(self, model_path: Path, class_names_path: Path):
        self._model = self._load_model(model_path)
        self._class_names = self._load_class_names(class_names_path)

    @staticmethod
    def _load_model(model_path: Path):
        if not model_path.exists():
            raise ModelLoadException(
                f"Model file not found at '{model_path}'. Train it first via ml_model/train.py."
            )
        try:
            import tensorflow as tf

            model = tf.keras.models.load_model(model_path)
            logger.info("Loaded prediction model from %s", model_path)
            return model
        except Exception as exc:  # noqa: BLE001 - any load failure must map to ModelLoadException
            logger.error("Failed to load model: %s", exc)
            raise ModelLoadException(str(exc)) from exc

    @staticmethod
    def _load_class_names(class_names_path: Path) -> List[str]:
        if not class_names_path.exists():
            raise ModelLoadException(f"class_names.json not found at '{class_names_path}'.")
        with open(class_names_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def predict(self, preprocessed_image: np.ndarray) -> Tuple[str, float]:
        """Runs inference and returns (raw_class_name, confidence_percentage)."""
        try:
            from tensorflow.keras.applications.efficientnet import preprocess_input

            model_input = preprocess_input(preprocessed_image)
            predictions = self._model.predict(model_input, verbose=0)[0]
        except Exception as exc:  # noqa: BLE001
            logger.error("Inference failed: %s", exc)
            raise PredictionException(str(exc)) from exc

        top_index = int(np.argmax(predictions))
        confidence = float(predictions[top_index]) * 100
        raw_class_name = self._class_names[top_index]
        return raw_class_name, round(confidence, 2)

    @staticmethod
    def parse_class_name(raw_class_name: str) -> Tuple[str, str, bool]:
        """Splits a PlantVillage-style label ('Tomato___Late_blight') into (plant, disease, is_healthy)."""
        parts = raw_class_name.split("___")
        plant_raw = parts[0] if len(parts) > 0 else raw_class_name
        disease_raw = parts[1] if len(parts) > 1 else "Unknown"

        plant = plant_raw.replace("_", " ").strip()
        is_healthy = disease_raw.strip().lower() == "healthy"
        disease = "Healthy" if is_healthy else disease_raw.replace("_", " ").strip()

        return plant, disease, is_healthy


@lru_cache
def get_prediction_service() -> PredictionService:
    settings = get_settings()
    return PredictionService(settings.model_path_resolved, settings.class_names_path_resolved)
