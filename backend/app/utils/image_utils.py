"""Low-level image validation and preprocessing helpers (Pillow + OpenCV)."""
import io
from pathlib import Path
from typing import List

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

from app.utils.exceptions import CorruptedImageException, InvalidImageException, UnsupportedFormatException


def validate_extension(filename: str, allowed_extensions: List[str]) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise UnsupportedFormatException(
            f"'{suffix or 'unknown'}' is not supported. Allowed formats: {', '.join(allowed_extensions)}."
        )


def validate_size(file_bytes: bytes, max_size_mb: int) -> None:
    if len(file_bytes) == 0:
        raise InvalidImageException("The uploaded file is empty.")
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise InvalidImageException(f"Image size {size_mb:.2f}MB exceeds the {max_size_mb}MB limit.")


def decode_image(file_bytes: bytes) -> Image.Image:
    """Decode raw bytes into a validated, RGB PIL image."""
    try:
        probe = Image.open(io.BytesIO(file_bytes))
        probe.verify()  # Raises if the file is truncated/corrupted
    except (UnidentifiedImageError, OSError) as exc:
        raise CorruptedImageException() from exc

    # verify() invalidates the file object, so it must be reopened before use
    try:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise CorruptedImageException() from exc

    return image


def preprocess_for_model(image: Image.Image, target_size: int) -> np.ndarray:
    """Resize with OpenCV and shape the array into a (1, H, W, 3) float32 batch."""
    image_array = np.array(image)
    resized = cv2.resize(image_array, (target_size, target_size), interpolation=cv2.INTER_AREA)
    batched = np.expand_dims(resized, axis=0).astype(np.float32)
    return batched
