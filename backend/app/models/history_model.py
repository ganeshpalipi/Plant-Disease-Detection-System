"""MongoDB document model for prediction history records."""
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class PredictionHistory(BaseModel):
    """Represents a single stored prediction, ready for Mongo insertion."""

    plant: str
    disease: str
    confidence: float
    image_filename: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_mongo(self) -> dict:
        return self.model_dump()
