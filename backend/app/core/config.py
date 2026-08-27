from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Intelligent Customer Signal Detector"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    frontend_origins: str = "http://localhost:3000"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout_seconds: float = Field(default=15, ge=1, le=60)
    customer_data_source: str = "sample"
    sample_data_path: str = "sample_data/hf_banking77_customers.json"
    hf_dataset_id: str = "PolyAI/banking77"
    hf_split: str = "test"
    hf_max_rows: int = Field(default=100, ge=1, le=5000)
    hf_trust_remote_code: bool = False
    database_url: str | None = None
    max_batch_size: int = Field(default=500, ge=1, le=5000)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [value.strip() for value in self.frontend_origins.split(",") if value.strip()]

    def local_data_file(self) -> Path:
        return Path(__file__).resolve().parents[2] / self.sample_data_path


@lru_cache
def get_settings() -> Settings:
    return Settings()
