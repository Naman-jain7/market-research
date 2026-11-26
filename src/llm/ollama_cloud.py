from crewai import LLM

from configs.core import settings
from src.utils.logger import LLM_LOGGER

OLLAMA_CLOUD_CONFIG = {
    "name": "ollama_cloud",
    "model": settings.llm.OLLAMA_CLOUD_DEFAULT_MODEL,
    "api_key": settings.llm.OLLAMA_CLOUD_API_KEY,
    "priority": settings.llm.OLLAMA_CLOUD_PRIORITY,
}


def create_ollama_cloud_llm(*, critic=False):
    llm = LLM(
        model=f"openai/{OLLAMA_CLOUD_CONFIG['model']}",
        base_url="https://ollama.com/v1",
        api_key=OLLAMA_CLOUD_CONFIG["api_key"],
    )
    label = "Critic LLM" if critic else "LLM"
    LLM_LOGGER.info("%s initialized via Ollama Cloud: %s", label, OLLAMA_CLOUD_CONFIG["model"])
    return llm
