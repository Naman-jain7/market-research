import os
from typing import List, Optional

from crewai import LLM, Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import re

from configs.core_config import LLM_PROVIDERS, settings, AGENTS_CONFIG_PATH, TASKS_CONFIG_PATH
from src.workflow.state import AgentOutput, AppState
from src.workflow.tools import tools
from src.utils.logger import APP_LOGGER, LLM_LOGGER

app_state: AppState = AppState(user_id=0)


load_dotenv()

# Determine active LLM based on priority
active_provider = None
for p in sorted(LLM_PROVIDERS, key=lambda x: x["priority"]):
    if p["api_key"] and p["model"]:
        active_provider = p
        break

if not active_provider:
    active_provider = [p for p in LLM_PROVIDERS if p["name"] == "gemini"][0]

APP_LOGGER.info(
    "Active LLM provider: %s, model: %s, priority: %s",
    active_provider["name"], active_provider["model"],
    active_provider.get("priority", "N/A")
)

if active_provider and active_provider["name"] == "gemini":
    os.environ["GEMINI_API_KEY"] = active_provider["api_key"]
    os.environ["MODEL_NAME"] = active_provider["model"]
    default_llm = LLM(model=active_provider["model"], api_key=active_provider["api_key"])
    LLM_LOGGER.info("LLM initialized via Gemini: %s", active_provider["model"])
elif active_provider and active_provider["name"] == "openrouter":
    os.environ["OPENAI_API_KEY"] = active_provider["api_key"]
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_MODEL_NAME"] = f"openrouter/{active_provider['model']}"
    default_llm = LLM(model=f"openrouter/{active_provider['model']}", base_url="https://openrouter.ai/api/v1", api_key=active_provider["api_key"])
    LLM_LOGGER.info("LLM initialized via OpenRouter: %s", active_provider["model"])
else:
    # Ollama Cloud via OpenAI Endpoint
    ollama_base_url = "https://ollama.com/v1"
    os.environ["OPENAI_API_KEY"] = settings.llm.OLLAMA_API_KEY or "NA"
    os.environ["OPENAI_API_BASE"] = ollama_base_url
    os.environ["OPENAI_MODEL_NAME"] = f"openai/{settings.llm.OLLAMA_MODEL_NAME}"
    # Use openai/ prefix so LiteLLM treats it as an OpenAI-compatible endpoint
    default_llm = LLM(
        model=f"openai/{settings.llm.OLLAMA_MODEL_NAME}",
        base_url=ollama_base_url,
        api_key=settings.llm.OLLAMA_API_KEY
    )
    LLM_LOGGER.info("LLM initialized via Ollama: %s", settings.llm.OLLAMA_MODEL_NAME)

def _extract_score(text: str) -> Optional[float]:
    match = re.search(r'(?:Score|score|SCORE)\s*[:：]\s*(\d+(?:\.\d+)?)', text)
    return float(match.group(1)) if match else None


def _make_callback(agent_field: str):
    def callback(output):
        score = None
        text = str(output)
        if hasattr(output, 'pydantic') and output.pydantic:
            parsed = output.pydantic
            text = parsed.text
            score = parsed.score
        
        # Regex fallback to extract score from raw text if not parsed by Pydantic
        if score is None:
            match = re.search(r'(?:[Ss]core(?:\s*field)?[:\s\*\*]+)(\d+(?:\.\d+)?)', text)
            if match:
                try:
                    score = float(match.group(1))
                except ValueError:
                    pass

        agent_output = AgentOutput(text=text, score=score) # type: ignore
        setattr(app_state, agent_field, agent_output)

        score_str = f"{score:.1f}" if score is not None else "N/A"
        APP_LOGGER.info("Task complete [%s] — score: %s, output length: %d chars",
                        agent_field, score_str, len(text))
        LLM_LOGGER.info("LLM call finished [%s] — score: %s", agent_field, score_str)
    return callback


@CrewBase
class MarketResearchCrew():
    agents: List[BaseAgent]
    tasks: List[Task]

    # Use absolute paths for configs so crewai can find them
    agents_config = AGENTS_CONFIG_PATH
    tasks_config = TASKS_CONFIG_PATH

    # ================ Agents ======================
    @agent
    def market_research_specialist(self) -> Agent:
        return Agent(
            llm=default_llm,
            config=self.agents_config["market_research_specialist"], # type: ignore
            tools=tools,
        )

    @agent
    def competitive_intelligence_analyst(self) -> Agent:
        return Agent(
            llm=default_llm,
            config=self.agents_config["competitive_intelligence_analyst"], # type: ignore
            tools=tools
        )
        
    @agent
    def customer_insights_researcher(self) -> Agent:
        return Agent(
            llm=default_llm,
            config=self.agents_config["customer_insights_researcher"], # type: ignore
            tools=tools
        )

    @agent
    def product_strategy_advisor(self) -> Agent:
        return Agent(
            llm=default_llm,
            config=self.agents_config["product_strategy_advisor"], # type: ignore
            tools=tools
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            llm=default_llm,
            config=self.agents_config["business_analyst"], # type: ignore
            tools=tools,
        )

    # ================ Tasks ======================
    
    def kickoff_with_state(self, inputs: dict, stream: bool = True):
        """Initialize state from inputs and run the crew."""
        global app_state
        app_state.user_id = inputs.get("user_id", 0)
        app_state.user_input = inputs.get("user_input", "")
        app_state.product_idea = inputs.get("product_idea", "")
        APP_LOGGER.info(
            "Crew kickoff — user_id: %s, product: %.60s",
            app_state.user_id, app_state.product_idea
        )
        LLM_LOGGER.info("Sequential crew execution started — 5 tasks: market_research, competitive_intelligence, customer_insights, product_strategy, business_analyst")
        c = self.crew()
        c.stream = stream
        result = c.kickoff(inputs=inputs)
        LLM_LOGGER.info("Sequential crew execution finished")
        return result

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["market_research_task"], # type: ignore
            callback=_make_callback("market_research"),
        ) # type: ignore
        
    @task
    def competitive_intelligence_task(self) -> Task:
        return Task(
            config=self.tasks_config["competitive_intelligence_task"], # type: ignore
            context=[self.market_research_task()], # type: ignore
            callback=_make_callback("competitive_intelligence"),
        ) # type: ignore
        
    @task
    def customer_insights_task(self) -> Task:
        return Task(
        config=self.tasks_config["customer_insights_task"], # type: ignore
        context=[
            self.market_research_task(), # type: ignore
            self.competitive_intelligence_task() # type: ignore
        ],
        callback=_make_callback("customer_insights"),
    ) # type: ignore
        
    @task
    def product_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config["product_strategy_task"], # type: ignore
            context=[self.market_research_task(), # type: ignore
                     self.competitive_intelligence_task(), # pyright: ignore[reportCallIssue]
                     self.customer_insights_task()], # type: ignore
            callback=_make_callback("product_strategy"),
        ) # type: ignore
        
    @task
    def business_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config["business_analyst_task"], # type: ignore
            
            context=[self.market_research_task(), # type: ignore
                     self.competitive_intelligence_task(), # type: ignore
                     self.customer_insights_task(), # type: ignore
                     self.product_strategy_task()], # type: ignore
            
            callback=_make_callback("business_analyst"),
            
            output_file="reports/report.md"
        ) # type:ignore

    # ================= Crew ===========================
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )