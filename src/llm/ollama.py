from crewai import LLM

from configs.core import settings
from src.utils.logger import LLM_LOGGER

OLLAMA_CONFIG = {
    "name": "ollama",
    "model": settings.llm.OLLAMA_DEFAULT_MODEL,
    "base_url": settings.llm.OLLAMA_BASE_URL,
    "priority": settings.llm.OLLAMA_PRIORITY,
}


def create_ollama_llm():
    llm = LLM(
        model=f"ollama/{OLLAMA_CONFIG['model']}",
        base_url=OLLAMA_CONFIG["base_url"],
    )
    LLM_LOGGER.info("LLM initialized via local Ollama: %s", OLLAMA_CONFIG["model"])
    return llm
