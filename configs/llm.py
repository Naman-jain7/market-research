from pydantic import Field, model_validator
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMSettings(BaseSettings):
    """LLM and Provider Configurations."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GEMINI_DEFAULT_MODEL: Annotated[str, Field(..., validation_alias="GEMINI_DEFAULT_MODEL")]
    GOOGLE_API_KEY: Annotated[str | None, Field(..., validation_alias="GOOGLE_API_KEY")]
    GEMINI_PRIORITY: Annotated[int, Field(..., validation_alias="GEMINI_PRIORITY")]
    GEMINI_TIMEOUT: Annotated[float, Field(default=30.0, validation_alias="GEMINI_TIMEOUT")]

    OPENROUTER_DEFAULT_MODEL: Annotated[str, Field(..., validation_alias="OPENROUTER_DEFAULT_MODEL")]
    OPENROUTER_API_KEY: Annotated[str | None, Field(..., validation_alias="OPENROUTER_API_KEY")]
    OPENROUTER_PRIORITY: Annotated[int, Field(..., validation_alias="OPENROUTER_PRIORITY")]
    OPENROUTER_TIMEOUT: Annotated[float, Field(default=60.0, validation_alias="OPENROUTER_TIMEOUT")]

    OLLAMA_CLOUD_DEFAULT_MODEL: Annotated[str, Field(..., validation_alias="OLLAMA_CLOUD_DEFAULT_MODEL")]
    OLLAMA_CLOUD_API_KEY: Annotated[str | None, Field(..., validation_alias="OLLAMA_CLOUD_API_KEY")]
    OLLAMA_CLOUD_PRIORITY: Annotated[int, Field(..., validation_alias="OLLAMA_CLOUD_PRIORITY")]
    OLLAMA_CLOUD_TIMEOUT: Annotated[float, Field(default=60.0, validation_alias="OLLAMA_CLOUD_TIMEOUT")]

    OLLAMA_DEFAULT_MODEL: str = Field(..., validation_alias="OLLAMA_DEFAULT_MODEL")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    OLLAMA_PRIORITY: Annotated[int, Field(..., validation_alias="OLLAMA_PRIORITY")]

    DEFAULT_MAX_TOKENS: Annotated[int, Field(default=1024, validation_alias="DEFAULT_MAX_TOKENS")]
    DEFAULT_TEMPERATURE: Annotated[float, Field(default=0.3, validation_alias="DEFAULT_TEMPERATURE")]

    MAX_RETRIES: int = Field(default=1, validation_alias="MAX_RETRIES")
    CIRCUIT_BREAKER_THRESHOLD: int = Field(default=3, validation_alias="CIRCUIT_BREAKER_THRESHOLD")
    CIRCUIT_BREAKER_COOLDOWN: int = Field(default=30, validation_alias="CIRCUIT_BREAKER_COOLDOWN")

    @model_validator(mode="after")
    def validate_providers(self)->"LLMSettings":
        """
        Ensures that if a provider is intended to be used, both its API Key
        and Model Name are provided. Also guarantees at least one valid provider exists.
        """

        active_providers = []

        if self.OPENROUTER_API_KEY or self.OPENROUTER_DEFAULT_MODEL:
            if not (self.OPENROUTER_API_KEY and self.OPENROUTER_DEFAULT_MODEL):
                raise ValueError("Both OPENROUTER_API_KEY and OPENROUTER_DEFAULT_MODEL must be provided together.")
            active_providers.append("OpenRouter")

        # 2. Check Gemini
        if self.GOOGLE_API_KEY or self.GEMINI_DEFAULT_MODEL:
            if not (self.GOOGLE_API_KEY and self.GEMINI_DEFAULT_MODEL):
                raise ValueError("Both GOOGLE_API_KEY and GEMINI_DEFAULT_MODEL must be provided together.")
            active_providers.append("Gemini")

        if self.OLLAMA_CLOUD_DEFAULT_MODEL and self.OLLAMA_CLOUD_API_KEY:
            active_providers.append("Ollama Cloud")

        if self.OLLAMA_DEFAULT_MODEL:
            active_providers.append("Ollama Local")

        # 4. Global Check: Ensure at least one provider is configured
        if not active_providers:
            raise ValueError("At least one LLM provider (OpenRouter, Gemini, or Ollama) must be fully configured.")

        return self

