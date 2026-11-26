from pydantic import Field, model_validator
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict

class EmbeddingSettings(BaseSettings):
    """Embedding model and chunking settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    HUGGINGFACEHUB_API_TOKEN: Annotated[str, Field(validation_alias="HUGGINGFACEHUB_API_TOKEN")]

    EMBEDDING_MODEL: Annotated[str, Field(validation_alias="EMBEDDING_MODEL")]
    EMBEDDING_DIMENSION: Annotated[int, Field(validation_alias="EMBEDDING_DIMENSION")]
    EMBEDDINGS_TABLE_NAME:Annotated[str, Field(..., validation_alias='EMBEDDINGS_TABLE_NAME')]

    CHUNK_SIZE: Annotated[int, Field(..., validation_alias='CHUNK_SIZE')]
    CHUNK_OVERLAP: Annotated[int, Field(..., validation_alias='CHUNK_OVERLAP')]

    @model_validator(mode="after")
    def validate_overlap(self) -> "EmbeddingSettings":
        if self.CHUNK_SIZE <= 0:
            raise ValueError("chunk_size must be > 0")
        if self.CHUNK_OVERLAP < 0:
            raise ValueError("chunk_overlap cannot be < 0")
        if self.CHUNK_OVERLAP >= self.CHUNK_SIZE:
            raise ValueError("chunk_overlap must be < chunk_size.")
        return self
