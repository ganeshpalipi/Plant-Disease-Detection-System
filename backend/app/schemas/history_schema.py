"""Pydantic schemas for prediction history endpoints."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class HistoryRecordResponse(BaseModel):
    id: str = Field(..., alias="_id")
    plant: str
    disease: str
    confidence: float
    image_filename: str
    created_at: datetime

    model_config = {"populate_by_name": True}


class HistoryListResponse(BaseModel):
    total: int
    items: List[HistoryRecordResponse]
