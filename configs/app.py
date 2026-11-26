from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Core application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    APP_NAME: str = Field(..., validation_alias="APP_NAME")
    APP_VERSION: str = Field(..., validation_alias="APP_VERSION")
    SECRET_KEY: str = Field(..., validation_alias='SECRET_KEY')
    API_TIMEOUT: int = Field(..., validation_alias='API_TIMEOUT')
    
    DB_PATH: str = Field(..., validation_alias="DB_PATH")
    VECTOR_DB_PATH: str = Field(..., validation_alias="VECTOR_DB_PATH")

    AGENTS_CONFIG_PATH: str = Field(..., validation_alias="AGENTS_CONFIG_PATH")
    TASKS_CONFIG_PATH: str = Field(..., validation_alias="TASKS_CONFIG_PATH")

    LANGCHAIN_PROJECT: str = Field(..., validation_alias="LANGCHAIN_PROJECT")