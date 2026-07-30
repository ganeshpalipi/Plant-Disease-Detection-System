"""MongoDB connection lifecycle management using Motor (the async driver)."""
import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.config import get_settings
from app.utils.exceptions import DatabaseConnectionException

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    settings = get_settings()
    try:
        mongodb.client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        await mongodb.client.admin.command("ping")
        mongodb.database = mongodb.client[settings.mongodb_db_name]
        logger.info("Connected to MongoDB database '%s'", settings.mongodb_db_name)
    except PyMongoError as exc:
        logger.error("Failed to connect to MongoDB: %s", exc)
        raise DatabaseConnectionException(f"Could not connect to MongoDB: {exc}") from exc


async def close_mongo_connection() -> None:
    if mongodb.client is not None:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    if mongodb.database is None:
        raise DatabaseConnectionException("Database has not been initialized. Is MongoDB running?")
    return mongodb.database
