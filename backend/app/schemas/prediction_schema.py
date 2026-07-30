"""Pydantic schemas for the /predict endpoint."""
from typing import List, Optional

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    plant: str = Field(..., examples=["Tomato"])
    disease: str = Field(..., examples=["Late Blight"])
    confidence: float = Field(..., ge=0, le=100, examples=[98.74])
    is_healthy: bool = Field(..., examples=[False])
    description: str
    symptoms: List[str]
    causes: List[str]
    treatment: List[str]
    prevention: List[str]
    history_id: Optional[str] = Field(
        default=None, description="Id of the persisted history record, if saving succeeded."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "plant": "Tomato",
                "disease": "Late Blight",
                "confidence": 98.74,
                "is_healthy": False,
                "description": "Late Blight is caused by Phytophthora infestans.",
                "symptoms": ["Water-soaked lesions on leaves", "White fungal growth on leaf undersides"],
                "causes": ["Cool, moist weather", "Poor air circulation"],
                "treatment": ["Apply copper-based fungicide", "Remove and destroy infected plants"],
                "prevention": ["Use resistant varieties", "Avoid overhead irrigation"],
                "history_id": "65f1c2e4a1b2c3d4e5f6a7b8",
            }
        }
    }
