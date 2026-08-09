import asyncio
import importlib
import sys
from types import ModuleType

import httpx
from fastapi import FastAPI


class _FakeAppState:
    def model_dump(self):
        return {
            "user_id": 42,
            "user_input": "sanitized",
            "product_idea": "sanitized",
            "market_research": {"text": "ok", "score": 7.0, "sources": []},
            "competitive_intelligence": {"text": "", "score": 0.0, "sources": []},
            "customer_insights": {"text": "", "score": 0.0, "sources": []},
            "research_manager_review": {"text": "", "score": 0.0, "sources": []},
            "manager_synthesis": {"text": "", "score": 0.0, "sources": []},
        }


class _FakeMarketResearchCrew:
    last_instance = None

    def __init__(self):
        self.app_state = _FakeAppState()
        self.kickoff_inputs = None
        self.stream = None
        _FakeMarketResearchCrew.last_instance = self

    def kickoff_with_state(self, inputs, stream=True):
        self.kickoff_inputs = inputs
        self.stream = stream


def import_research_router_with_fake_crew(monkeypatch):
    crew_module = ModuleType("src.workflow.crew")
    crew_module.MarketResearchCrew = _FakeMarketResearchCrew # type: ignore

    monkeypatch.setitem(sys.modules, "src.workflow.crew", crew_module)
    sys.modules.pop("app.api.research", None)

    return importlib.import_module("app.api.research")


def test_research_endpoint_invokes_crew_with_payload_and_returns_state(monkeypatch):
    research_module = import_research_router_with_fake_crew(monkeypatch)
    app = FastAPI()
    app.state.limiter = research_module.limiter
    app.include_router(research_module.router)

    async def call_endpoint():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/research",
                json={"user_id": 42, "user_input": "AI market research app"},
            )

    response = asyncio.run(call_endpoint())

    assert response.status_code == 200
    assert response.json()["market_research"]["text"] == "ok"
    assert _FakeMarketResearchCrew.last_instance.kickoff_inputs == { # type: ignore
        "user_id": 42,
        "user_input": "AI market research app",
        "product_idea": "AI market research app",
    }
    assert _FakeMarketResearchCrew.last_instance.stream is False # type: ignore
