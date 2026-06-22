from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from configs.core_config import AGENTS_CONFIG_PATH, TASKS_CONFIG_PATH
from src.workflow.state import AgentOutput, AppState
from src.workflow.guardrails import sanitize_input, validate_agent_output
from src.workflow.tools import tools
from src.utils.logger import APP_LOGGER, LLM_LOGGER
from src.llm.providers import create_llm, create_ollama_llm

load_dotenv()

default_llm = create_llm()

critic_llm = create_ollama_llm() or create_llm()

@CrewBase
class MarketResearchCrew():
    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self) -> None:
        self.app_state = AppState()

    def _make_callback(self, agent_field: str):
        def callback(output):
            agent_output = validate_agent_output(output)
            setattr(self.app_state, agent_field, agent_output)

            score_str = f"{agent_output.score:.1f}"
            
            APP_LOGGER.info("Task complete [%s] — score: %s, output length: %d chars", agent_field, score_str, len(agent_output.text))
            LLM_LOGGER.info("LLM call finished [%s] — score: %s", agent_field, score_str)
        
        return callback

    # Use absolute paths for configs so crewai can find them
    agents_config = AGENTS_CONFIG_PATH
    tasks_config = TASKS_CONFIG_PATH

    # ================ Agents ======================
    @agent
    def market_research_specialist(self) -> Agent:
        return Agent(
            llm=default_llm, config=self.agents_config["market_research_specialist"], tools=tools   # type: ignore
        )

    @agent
    def competitive_intelligence_analyst(self) -> Agent:
        return Agent(
            llm=default_llm, config=self.agents_config["competitive_intelligence_analyst"], tools=tools   # type: ignore
        )
        
    @agent
    def customer_insights_researcher(self) -> Agent:
        return Agent(
            llm=default_llm, config=self.agents_config["customer_insights_researcher"], tools=tools     # type:ignore
        )
    
    @agent
    def research_manager(self) -> Agent:
        return Agent(
            llm=critic_llm, config=self.agents_config["research_manager"], tools=tools     # type:ignore
        )

    @agent
    def strategy_manager(self)->Agent:
        return Agent(
            llm=default_llm, config=self.agents_config["strategy_manager"], tools=tools  #type: ignore
        )

    # ================ Tasks ======================
    def kickoff_with_state(self, inputs: dict, stream: bool = True):
        """Initialize state from inputs and run the crew."""
        # Sanitize inputs
        sanitized_user_input = sanitize_input(inputs.get("user_input", ""))
        sanitized_product_idea = sanitize_input(inputs.get("product_idea", ""))
        inputs["user_input"] = sanitized_user_input
        inputs["product_idea"] = sanitized_product_idea
        
        self.app_state.user_id = inputs.get("user_id", 0)
        self.app_state.user_input = sanitized_user_input
        self.app_state.product_idea = sanitized_product_idea
        APP_LOGGER.info(
            "Crew kickoff — user_id: %s, product: %.60s",
            self.app_state.user_id, self.app_state.product_idea
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
            
            callback=self._make_callback("market_research"),
            output_pydantic=AgentOutput
        ) # type: ignore
        

    @task
    def competitive_intelligence_task(self) -> Task:
        return Task(
            config=self.tasks_config["competitive_intelligence_task"],  # type: ignore
            
            context=[
                self.market_research_task(),  # type: ignore
            ],

            callback=self._make_callback("competitive_intelligence"),
            output_pydantic=AgentOutput,
        ) # type: ignore


    @task
    def customer_insights_task(self) -> Task:
        return Task(
            config=self.tasks_config["customer_insights_task"], # type: ignore
            
            context=[
                self.market_research_task(), # type: ignore
                self.competitive_intelligence_task() # type: ignore
            ],
            
            callback=self._make_callback("customer_insights"),
            output_pydantic=AgentOutput
        ) # type: ignore
        
    # @task
    # def product_strategy_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["product_strategy_task"], # type: ignore
            
    #         context=[self.market_research_task(), # type: ignore
    #                  self.competitive_intelligence_task(), # pyright: ignore[reportCallIssue]
    #                  self.customer_insights_task()], # type: ignore
            
    #         callback=self._make_callback("product_strategy"),
    #         output_pydantic=AgentOutput
    #     ) # type: ignore
        
    # @task
    # def business_analyst_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["business_analyst_task"], # type: ignore
            
    #         context=[self.market_research_task(), # type: ignore
    #                  self.competitive_intelligence_task(), # type: ignore
    #                  self.customer_insights_task(), # type: ignore
    #                  self.product_strategy_task()], # type: ignore
            
    #         callback=self._make_callback("business_analyst"),
    #         output_pydantic=AgentOutput,
            
    #         output_file="reports/report.md"
    #     ) # type:ignore

    @task
    def research_manager_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_manager_review_task"],  # type: ignore
            context=[
                self.market_research_task(),  # type: ignore
                self.competitive_intelligence_task(),  # type: ignore
                self.customer_insights_task(),  # type: ignore
            ],
            callback=self._make_callback("research_manager_review"),
            output_pydantic=AgentOutput,
        )  # type: ignore

    @task
    def manager_synthesis_task(self) -> Task:
        return Task(
            config=self.tasks_config["manager_synthesis_task"],  # type: ignore
            context=[
                self.market_research_task(),  # type: ignore
                self.competitive_intelligence_task(),  # type: ignore
                self.customer_insights_task(),  # type: ignore
            ],
            callback=self._make_callback("manager_synthesis"),
            output_pydantic=AgentOutput,
        )  # type: ignore
    
    # ================= Crew ===========================
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
    )