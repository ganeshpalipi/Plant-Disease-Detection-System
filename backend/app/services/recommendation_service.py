"""Loads and serves static disease recommendation content (disease_info.json)."""
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict

from app.config import get_settings
from app.utils.exceptions import DiseaseInfoNotFoundException

logger = logging.getLogger(__name__)


class RecommendationService:
    """Provides disease description, symptoms, causes, treatment and prevention data."""

    def __init__(self, disease_info_path: Path):
        self._disease_info_path = disease_info_path
        self._data: Dict[str, dict] = self._load()

    def _load(self) -> Dict[str, dict]:
        if not self._disease_info_path.exists():
            logger.warning(
                "disease_info.json not found at %s. Recommendation lookups will fail until it is created.",
                self._disease_info_path,
            )
            return {}
        with open(self._disease_info_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        logger.info("Loaded recommendation data for %d classes", len(data))
        return data

    def get_info(self, class_name: str) -> dict:
        info = self._data.get(class_name)
        if info is None:
            raise DiseaseInfoNotFoundException(class_name)
        return info


@lru_cache
def get_recommendation_service() -> RecommendationService:
    settings = get_settings()
    return RecommendationService(settings.disease_info_path_resolved)
