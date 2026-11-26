from crewai import LLM

from configs.core import settings
from src.utils.logger import LLM_LOGGER

OPENROUTER_CONFIG = {
    "model": settings.llm.OPENROUTER_DEFAULT_MODEL,
    "api_key": settings.llm.OPENROUTER_API_KEY,
    "priority": settings.llm.OPENROUTER_PRIORITY,
}


def create_openrouter_llm():
    llm = LLM(
        model=f"openrouter/{OPENROUTER_CONFIG['model']}",
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_CONFIG["api_key"],
    )
    LLM_LOGGER.info("LLM initialized via OpenRouter: %s", OPENROUTER_CONFIG["model"])
    return llm
