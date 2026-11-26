from crewai import LLM

from configs.core import settings
from src.utils.logger import LLM_LOGGER

GEMINI_CONFIG = {
    "model": settings.llm.GEMINI_DEFAULT_MODEL,
    "api_key": settings.llm.GOOGLE_API_KEY,
    "priority": settings.llm.GEMINI_PRIORITY,
}


def create_gemini_llm():
    llm = LLM(model=GEMINI_CONFIG["model"], api_key=GEMINI_CONFIG["api_key"])
    LLM_LOGGER.info("LLM initialized via Gemini: %s", GEMINI_CONFIG["model"])
    return llm
