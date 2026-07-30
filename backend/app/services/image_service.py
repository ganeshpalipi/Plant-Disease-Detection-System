"""Validates and preprocesses uploaded images before they reach the ML model."""
import logging
from functools import lru_cache
from pathlib import Path
from typing import Tuple
from uuid import uuid4

import aiofiles
import numpy as np
from fastapi import UploadFile
from PIL import Image

from app.config import Settings, get_settings
from app.utils import image_utils

logger = logging.getLogger(__name__)


class ImageProcessingService:
    def __init__(self, settings: Settings):
        self._allowed_extensions = settings.allowed_extensions_list
        self._max_size_mb = settings.max_upload_size_mb
        self._target_size = settings.image_size
        self._upload_dir = settings.upload_dir_resolved
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    async def load_and_validate(self, file: UploadFile) -> Tuple[Image.Image, bytes]:
        """Runs all validation steps and returns the decoded PIL image plus raw bytes."""
        image_utils.validate_extension(file.filename or "", self._allowed_extensions)

        file_bytes = await file.read()
        image_utils.validate_size(file_bytes, self._max_size_mb)

        image = image_utils.decode_image(file_bytes)
        logger.debug("Validated image '%s' (%d bytes)", file.filename, len(file_bytes))
        return image, file_bytes

    def preprocess(self, image: Image.Image) -> np.ndarray:
        return image_utils.preprocess_for_model(image, self._target_size)

    async def save_upload(self, file_bytes: bytes, original_filename: str) -> str:
        """Persists the raw upload under a random filename and returns it (never trusts
        the client-supplied filename, avoiding path traversal)."""
        extension = Path(original_filename).suffix.lower() or ".jpg"
        unique_name = f"{uuid4().hex}{extension}"
        destination = self._upload_dir / unique_name

        async with aiofiles.open(destination, "wb") as out_file:
            await out_file.write(file_bytes)

        return unique_name


@lru_cache
def get_image_processing_service() -> ImageProcessingService:
    return ImageProcessingService(get_settings())
