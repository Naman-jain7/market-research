from pydantic import BaseModel, Field
from typing import Optional, Annotated


class ProviderConfig(BaseModel):
    name: Annotated[str, Field()]
    model: Annotated[str, Field()]
    api_key: Annotated[str | None, Field()]
    base_url: Annotated[Optional[str], Field(default=None)]
    priority: Annotated[int, Field()]  # lower = tried first
    tier: Annotated[str, Field(default="slow")]


class RetryConfig:
    max_attempts: Annotated[int, Field(default=3)]
    min_wait: Annotated[float, Field(default=1.0)]  # seconds
    max_wait: Annotated[float, Field(default=60.0)]
    jitter: Annotated[float, Field(default=2.0)]


class CircuitBreakerConfig:
    fail_threshold: Annotated[int, Field(default=5)]
    cooldown: Annotated[float, Field(default=30.0)]  # seconds before half-open
