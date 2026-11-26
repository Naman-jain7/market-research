from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any

class DatabaseConfig(BaseSettings):
    """Database config"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    DB_DSN: str | None = Field("", validation_alias="DB_DSN")

    @model_validator(mode="before")
    @classmethod
    def preprocess_empty_strings(cls, values: Any) -> Any:
        if isinstance(values, dict):
            return {
                k: (None if isinstance(v, str) and v.strip() == "" else v)
                for k, v in values.items()
            }
        return values
