from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class ServicesSettings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ALPHAVANTAGE_STOCK_API_KEY: str = Field(..., validation_alias="ALPHAVANTAGE_STOCK_API_KEY")

    CURRENCY_EXCHANGE_URL: str = Field(..., validation_alias="CURRENCY_EXCHANGE_URL")
    CURRENCY_EXCHANGE_API_KEY: str = Field(..., validation_alias="CURRENCY_EXCHANGE_API_KEY")

    TAVILY_API_KEY: str = Field(..., validation_alias="TAVILY_API_KEY")

