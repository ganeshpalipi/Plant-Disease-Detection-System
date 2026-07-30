"""FastAPI application entrypoint: wires together config, database, routers and error handling."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import close_mongo_connection, connect_to_mongo
from app.routers import health, history, predict
from app.utils.exceptions import DatabaseConnectionException, register_exception_handlers
from app.utils.logger import setup_logging

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    # MongoDB is required for /history but not for /predict, so a failed connection
    # here is logged rather than treated as fatal - it keeps the rest of the API usable
    # and turns into a clear 503 DatabaseConnectionException the moment /history is hit.
    try:
        await connect_to_mongo()
    except DatabaseConnectionException as exc:
        logger.warning(
            "MongoDB unavailable at startup (%s). History endpoints will return 503 "
            "until MONGODB_URI is configured and reachable.",
            exc.message,
        )

    # The EfficientNetB0 model is loaded lazily on the first /predict request (see
    # app/services/prediction_service.py) rather than eagerly here, for the same reason:
    # the API, Swagger docs, and /history remain usable before the model is trained.
    logger.info("%s v%s ready.", settings.app_name, settings.app_version)

    yield

    await close_mongo_connection()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Deep learning-powered plant disease detection with actionable treatment recommendations.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(predict.router, prefix=settings.api_v1_prefix)
app.include_router(history.router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["Root"])
async def root() -> dict:
    return {
        "message": f"{settings.app_name} API",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
