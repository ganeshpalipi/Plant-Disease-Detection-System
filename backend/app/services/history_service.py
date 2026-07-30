"""Persists and retrieves prediction history records from MongoDB."""
import logging
from typing import List, Tuple

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.database import get_database
from app.models.history_model import PredictionHistory
from app.utils.exceptions import DatabaseConnectionException, HistoryNotFoundException

logger = logging.getLogger(__name__)

COLLECTION_NAME = "prediction_history"


class HistoryService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self._collection = database[COLLECTION_NAME]

    async def save(self, record: PredictionHistory) -> str:
        try:
            result = await self._collection.insert_one(record.to_mongo())
            return str(result.inserted_id)
        except PyMongoError as exc:
            logger.error("Failed to save prediction history: %s", exc)
            raise DatabaseConnectionException("Could not save prediction to history.") from exc

    async def list_recent(self, limit: int = 20, skip: int = 0) -> Tuple[List[dict], int]:
        try:
            total = await self._collection.count_documents({})
            cursor = self._collection.find().sort("created_at", -1).skip(skip).limit(limit)
            items = [self._serialize(doc) async for doc in cursor]
            return items, total
        except PyMongoError as exc:
            logger.error("Failed to fetch prediction history: %s", exc)
            raise DatabaseConnectionException("Could not fetch prediction history.") from exc

    async def get_by_id(self, record_id: str) -> dict:
        try:
            object_id = ObjectId(record_id)
        except InvalidId as exc:
            raise HistoryNotFoundException(record_id) from exc

        document = await self._collection.find_one({"_id": object_id})
        if document is None:
            raise HistoryNotFoundException(record_id)
        return self._serialize(document)

    @staticmethod
    def _serialize(document: dict) -> dict:
        document["_id"] = str(document["_id"])
        return document


def get_history_service() -> HistoryService:
    return HistoryService(get_database())
