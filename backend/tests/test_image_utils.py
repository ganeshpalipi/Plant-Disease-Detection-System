"""Unit tests for image validation/preprocessing - no FastAPI or model required."""
import io

import pytest
from PIL import Image

from app.utils import image_utils
from app.utils.exceptions import CorruptedImageException, InvalidImageException, UnsupportedFormatException


def make_jpeg_bytes(size=(64, 64), color=(10, 200, 10)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color=color).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_validate_extension_accepts_allowed():
    image_utils.validate_extension("leaf.jpg", [".jpg", ".jpeg", ".png"])


def test_validate_extension_rejects_disallowed():
    with pytest.raises(UnsupportedFormatException):
        image_utils.validate_extension("leaf.gif", [".jpg", ".jpeg", ".png"])


def test_validate_extension_rejects_missing_extension():
    with pytest.raises(UnsupportedFormatException):
        image_utils.validate_extension("leaf", [".jpg", ".jpeg", ".png"])


def test_validate_size_rejects_empty():
    with pytest.raises(InvalidImageException):
        image_utils.validate_size(b"", max_size_mb=10)


def test_validate_size_rejects_too_large():
    with pytest.raises(InvalidImageException):
        image_utils.validate_size(b"x" * (11 * 1024 * 1024), max_size_mb=10)


def test_validate_size_accepts_within_limit():
    image_utils.validate_size(b"x" * 1024, max_size_mb=10)


def test_decode_image_returns_rgb_image():
    image = image_utils.decode_image(make_jpeg_bytes())
    assert image.mode == "RGB"


def test_decode_image_rejects_corrupted_bytes():
    with pytest.raises(CorruptedImageException):
        image_utils.decode_image(b"this is not a real image file")


def test_preprocess_for_model_shapes_batch():
    image = image_utils.decode_image(make_jpeg_bytes(size=(100, 100)))
    batch = image_utils.preprocess_for_model(image, target_size=224)
    assert batch.shape == (1, 224, 224, 3)
    assert batch.dtype.name == "float32"
