"""Prediction endpoint: image upload -> preprocessing -> inference -> recommendation lookup."""
import logging

from fastapi import APIRouter, Depends, File, UploadFile

from app.models.history_model import PredictionHistory
from app.schemas.prediction_schema import PredictionResponse
from app.services.history_service import HistoryService, get_history_service
from app.services.image_service import ImageProcessingService, get_image_processing_service
from app.services.prediction_service import PredictionService, get_prediction_service
from app.services.recommendation_service import RecommendationService, get_recommendation_service
from app.utils.exceptions import DatabaseConnectionException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("", response_model=PredictionResponse, summary="Predict plant disease from a leaf image")
async def predict_disease(
    file: UploadFile = File(..., description="Leaf image (JPG/JPEG/PNG)"),
    image_service: ImageProcessingService = Depends(get_image_processing_service),
    prediction_service: PredictionService = Depends(get_prediction_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    history_service: HistoryService = Depends(get_history_service),
) -> PredictionResponse:
    image, file_bytes = await image_service.load_and_validate(file)
    preprocessed = image_service.preprocess(image)

    raw_class_name, confidence = prediction_service.predict(preprocessed)
    plant, disease, is_healthy = prediction_service.parse_class_name(raw_class_name)
    info = recommendation_service.get_info(raw_class_name)

    image_filename = await image_service.save_upload(file_bytes, file.filename or "upload.jpg")

    # A history-persistence failure should not fail the prediction itself - the user
    # still gets their result, they just won't see this one in /history.
    history_id = None
    try:
        record = PredictionHistory(
            plant=plant,
            disease=disease,
            confidence=confidence,
            image_filename=image_filename,
        )
        history_id = await history_service.save(record)
    except DatabaseConnectionException as exc:
        logger.warning("Prediction succeeded but history could not be saved: %s", exc.message)

    return PredictionResponse(
        plant=plant,
        disease=disease,
        confidence=confidence,
        is_healthy=is_healthy,
        description=info["description"],
        symptoms=info["symptoms"],
        causes=info["causes"],
        treatment=info["treatment"],
        prevention=info["prevention"],
        history_id=history_id,
    )
