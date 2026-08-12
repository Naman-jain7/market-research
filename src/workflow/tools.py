from crewai.tools import tool
from crewai_tools import (
    ScrapeWebsiteTool,
    SeleniumScrapingTool,
    SerperDevTool,
    TavilyResearchTool,
    TavilySearchTool,
)
from langchain_community.tools import DuckDuckGoSearchRun  # type:ignore
from langsmith import traceable

from src.utils.logger import LLM_LOGGER

# @tool("Get Stock Price")
# def get_stock_price(symbol: str) -> str:
#     """Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') using Alpha Vantage."""
#     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={settings.services.ALPHAVANTAGE_STOCK_API_KEY}"
#     return str(requests.get(url).json())

# @tool("Get Currency Exchange Rate")
# def get_currency_exchange_rate(from_currency: str, to_currency: str) -> str:
#     """Fetch latest currency exchange rate for a given currency pair (e.g. 'USD', 'EUR')."""
#     url = f"https://v6.exchangerate-api.com/v6/{settings.services.CURRENCY_EXCHANGE_API_KEY}/latest/{from_currency}"
#     data = requests.get(url).json()
#     rate = data["conversion_rates"][to_currency.upper()]
#     return f"1 {from_currency.upper()} = {rate} {to_currency.upper()}"

class TracedSerperDevTool(SerperDevTool):
    @traceable(run_type="tool", name="SerperDevTool")
    def _run(self, *args, **kwargs):
        LLM_LOGGER.info("Executing SerperDevTool: args=%s, kwargs=%s", args, kwargs)
        try:
            result = super()._run(*args, **kwargs)
            LLM_LOGGER.info("SerperDevTool completed successfully")
            return result
        except Exception as e:
            LLM_LOGGER.error("SerperDevTool failed: %s", e)
            raise

class TracedScrapeWebsiteTool(ScrapeWebsiteTool):
    @traceable(run_type="tool", name="ScrapeWebsiteTool")
    def _run(self, *args, **kwargs):
        LLM_LOGGER.info("Executing ScrapeWebsiteTool: args=%s, kwargs=%s", args, kwargs)
        try:
            result = super()._run(*args, **kwargs)
            LLM_LOGGER.info("ScrapeWebsiteTool completed successfully")
            return result
        except Exception as e:
            LLM_LOGGER.error("ScrapeWebsiteTool failed: %s", e)
            raise

class TracedSeleniumScrapingTool(SeleniumScrapingTool):
    @traceable(run_type="tool", name="SeleniumScrapingTool")
    def _run(self, *args, **kwargs):
        LLM_LOGGER.info("Executing SeleniumScrapingTool: args=%s, kwargs=%s", args, kwargs)
        try:
            result = super()._run(*args, **kwargs)
            LLM_LOGGER.info("SeleniumScrapingTool completed successfully")
            return result
        except Exception as e:
            LLM_LOGGER.error("SeleniumScrapingTool failed: %s", e)
            raise

class TracedTavilySearchTool(TavilySearchTool):
    @traceable(run_type='tool', name="TavilySearchTool")
    def _run(self, *args, **kwargs):
        LLM_LOGGER.info("Executing TavilySearchTool: args=%s, kwargs=%s", args, kwargs)
        try:
            result = super()._run(*args, **kwargs)
            LLM_LOGGER.info("TavilySearchTool completed successfully")
            return result
        except Exception as e:
            LLM_LOGGER.error("TavilySearchTool failed: %s", e)
            raise

class TracedTavilyResearchTool(TavilyResearchTool):
    @traceable(run_type='tool', name="TavilyResearchTool")
    def _run(self, *args, **kwargs):
        LLM_LOGGER.info("Executing TavilyResearchTool: args=%s, kwargs=%s", args, kwargs)
        try:
            result = super()._run(*args, **kwargs)
            LLM_LOGGER.info("TavilyResearchTool completed successfully")
            return result
        except Exception as e:
            LLM_LOGGER.error("TavilyResearchTool failed: %s", e)
            raise

_ddg = DuckDuckGoSearchRun()

@tool("DuckDuckGo Search")
def duckduckgo_search(query: str) -> str:
    """Search the web using DuckDuckGo for current information."""
    return _ddg.run(query)


tavily_search_tool = TracedTavilySearchTool()
tavily_research_tool = TracedTavilyResearchTool()



tools = [
    # serper_web_search_tool,

    # web_scraping_tool,
    # selenium_scraping_tool,

    tavily_search_tool,
    tavily_research_tool,

    # duckduckgo_search,
]
