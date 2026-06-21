from crewai.flow import Flow, start
from src.workflow.crew import MarketResearchCrew
from src.workflow.state import AppState

class MarketResearchFlow(Flow[AppState]):

    @start()
    def run_crew(self):
        result = MarketResearchCrew().crew().kickoff(
            inputs=self.state.model_dump()
        )
        
        outputs = result.tasks_output  # type: ignore[attr-defined]

        self.state.market_research = outputs[0].pydantic
        self.state.competitive_intelligence = outputs[1].pydantic
        self.state.customer_insights = outputs[2].pydantic
        self.state.product_strategy = outputs[3].pydantic
        self.state.business_analyst = outputs[4].pydantic

        return self.state