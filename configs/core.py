from pathlib import Path
from typing import Annotated, Any

from dotenv import load_dotenv
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore

from configs.app import AppConfig
from configs.db import DatabaseConfig
from configs.embeddings import EmbeddingSettings
from configs.llm import LLMSettings
from configs.services import ServicesSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    """Master Settings Object."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm: LLMSettings = Field(default_factory=lambda: LLMSettings())  # type: ignore
    embedding: EmbeddingSettings = Field(default_factory=lambda: EmbeddingSettings())  # type: ignore
    db: DatabaseConfig = Field(default_factory=lambda: DatabaseConfig())  # type: ignore
    services: ServicesSettings = Field(default_factory=lambda: ServicesSettings())  # type: ignore
    app: AppConfig = Field(default_factory=lambda: AppConfig())  # type: ignore


settings = Settings()

RAW_DB_PATH = BASE_DIR / settings.app.DB_PATH
VECTOR_DB_PATH = BASE_DIR / settings.app.VECTOR_DB_PATH

AGENTS_CONFIG_PATH = str(BASE_DIR / settings.app.AGENTS_CONFIG_PATH)
TASKS_CONFIG_PATH = str(BASE_DIR / settings.app.TASKS_CONFIG_PATH)

SUPPORTED_TEXT_SUFFIXES = frozenset({".md", ".markdown", ".txt", ".csv", ".json"})