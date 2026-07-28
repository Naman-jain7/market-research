from crewai import LLM

from configs.core_config import LLM_PROVIDERS, settings
from src.utils.logger import LLM_LOGGER


def get_active_provider():

    for provider in sorted(LLM_PROVIDERS, key=lambda p: p["priority"]):
        if provider["api_key"] and provider["model"]:
            return provider

    raise ValueError("No valid LLM provider configured")


def create_llm():
    provider = get_active_provider()

    if provider["name"] == "gemini":
        default_llm = LLM(model=provider["model"], api_key=provider["api_key"])
        LLM_LOGGER.info("LLM initialized via Gemini: %s", provider["model"])
    
    elif provider["name"] == "openrouter":
        default_llm = LLM(
            model=f"openrouter/{provider['model']}",
            base_url="https://openrouter.ai/api/v1",
            api_key=provider["api_key"],
        )
        LLM_LOGGER.info("LLM initialized via OpenRouter: %s", provider["model"])
    
    elif provider["name"] == "ollama":
        default_llm = LLM(
            model=f"openai/{provider['model']}",
            base_url="https://ollama.com/v1",
            api_key=provider["api_key"],
        )
        LLM_LOGGER.info("LLM initialized via Ollama: %s", provider["model"])
    
    return default_llm

def create_ollama_llm():
    ollama_llm = LLM(
        model=f"openai/{settings.llm.OLLAMA_MODEL_NAME}",
        base_url="https://ollama.com/v1",
        api_key=settings.llm.OLLAMA_API_KEY,
    )

    LLM_LOGGER.info("Critic LLM initialized via Ollama: %s", settings.llm.OLLAMA_MODEL_NAME)

    return ollama_llm