"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Plant Disease Detection System"
    app_version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "plant_disease_db"

    # ML Model
    model_path: str = "ml_model/saved_model/plant_disease_model.keras"
    class_names_path: str = "ml_model/saved_model/class_names.json"
    disease_info_path: str = "ml_model/saved_model/disease_info.json"
    image_size: int = 224
    confidence_threshold: float = 40.0

    # Uploads
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10
    allowed_image_extensions: str = ".jpg,.jpeg,.png"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.allowed_image_extensions.split(",") if ext.strip()]

    @property
    def base_dir(self) -> Path:
        """Resolves to the backend/ directory regardless of the process's working directory."""
        return Path(__file__).resolve().parent.parent

    @property
    def model_path_resolved(self) -> Path:
        return self.base_dir / self.model_path

    @property
    def class_names_path_resolved(self) -> Path:
        return self.base_dir / self.class_names_path

    @property
    def disease_info_path_resolved(self) -> Path:
        return self.base_dir / self.disease_info_path

    @property
    def upload_dir_resolved(self) -> Path:
        return self.base_dir / self.upload_dir


@lru_cache
def get_settings() -> Settings:
    return Settings()
