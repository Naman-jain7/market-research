from typing import Annotated
from pydantic import BaseModel, Field, field_validator

class Citation(BaseModel):
    title: str=""
    url: str

class AgentOutput(BaseModel):
    text: Annotated[str, Field(default="", description="Detailed analysis, findings, recommendations, and reasoning produced by the agent.")]
    score: Annotated[float, Field(default=0.0, ge=0.0, le=10.0, description="Overall evaluation score assigned by the agent on a scale from 0 to 10, where 10 is the strongest assessment.")]

    sources: list[Citation] = Field(default_factory=list, description="a list of Citation objects referencing evidence used during validation")

    @field_validator('sources', mode='before')
    @classmethod
    def clean_sources(cls, v):
        if not isinstance(v, list):
            return []
        cleaned = []
        for item in v:
            if isinstance(item, dict):
                cleaned.append(item)
            elif isinstance(item, str) and item.strip():
                # If the LLM returns a raw string (e.g., a URL) instead of a dict
                cleaned.append({"title": "Source", "url": item})
            # Empty strings (like the one that caused the error) are simply ignored
        return cleaned


class AppState(BaseModel):
    user_id: int | str = Field(default=0)

    user_input: str = Field(default="", description="Original user request or product idea submitted for analysis.")
    product_idea: str = Field(default="", description="Product or business idea being evaluated by the research workflow.")

    market_research: AgentOutput = Field(default_factory=AgentOutput, description="Market size, trends, demand, opportunities, and industry analysis.") # type: ignore

    competitive_intelligence: AgentOutput = Field(default_factory=AgentOutput, description="Competitor landscape, differentiation opportunities, and market positioning analysis.") # type: ignore

    customer_insights: AgentOutput = Field(default_factory=AgentOutput, description="Target audience analysis, customer needs, pain points, and behavioral insights.") # type: ignore

    research_manager_review: AgentOutput = Field(default_factory=AgentOutput, description="Review of all collected research.") # type: ignore

    manager_synthesis: AgentOutput = Field(default_factory=AgentOutput, description="Final synthesis of the research and findings.") # type: ignore