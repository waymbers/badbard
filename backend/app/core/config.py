from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration pulled from environment variables."""

    api_v1_prefix: str = "/api/v1"
    project_name: str = "Form a Pauper API"
    database_url: str = f"sqlite:///{Path(__file__).resolve().parents[2] / 'formapauper.db'}"
    allowed_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(env_prefix="FORMAPauper_", env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
