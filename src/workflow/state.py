from typing import Annotated
from pydantic import BaseModel, Field

class Citation(BaseModel):
    title: str=""
    url: str

class AgentOutput(BaseModel):
    text: Annotated[str, Field(default="", description="Detailed analysis, findings, recommendations, and reasoning produced by the agent.")]
    score: Annotated[float, Field(default=0.0, ge=0.0, le=10.0, description="Overall evaluation score assigned by the agent on a scale from 0 to 10, where 10 is the strongest assessment.")]

    sources: list[Citation] = Field(default_factory=list, description="a list of Citation objects referencing evidence used during validation")


class AppState(BaseModel):
    user_id: int | str = Field(default=0)

    user_input: str = Field(default="", description="Original user request or product idea submitted for analysis.")
    product_idea: str = Field(default="", description="Product or business idea being evaluated by the research workflow.")

    market_research: AgentOutput = Field(default_factory=AgentOutput, description="Market size, trends, demand, opportunities, and industry analysis.") # type: ignore

    competitive_intelligence: AgentOutput = Field(default_factory=AgentOutput, description="Competitor landscape, differentiation opportunities, and market positioning analysis.") # type: ignore

    customer_insights: AgentOutput = Field(default_factory=AgentOutput, description="Target audience analysis, customer needs, pain points, and behavioral insights.") # type: ignore

    product_strategy: AgentOutput = Field(default_factory=AgentOutput, description="Product strategy, feature recommendations, roadmap suggestions, and go-to-market considerations.") # type: ignore

    business_analyst: AgentOutput = Field(default_factory=AgentOutput, description="Final business assessment, viability analysis, risks, opportunities, and overall recommendation.") # type: ignore
    