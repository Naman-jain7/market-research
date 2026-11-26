import asyncio
from typing import Protocol, cast

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Request
from schemas.request_schema import ResearchRequest

from src.workflow.crew import MarketResearchCrew
from src.workflow.state import AppState

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


class _ResearchCrew(Protocol):
    @property
    def app_state(self) -> AppState: ...

    def kickoff_with_state(self, inputs: dict, stream: bool = True) -> object: ...


@router.post('/research')
@limiter.limit("5/hour")
async def research(request: Request, payload: ResearchRequest):
    # CrewBase preserves these members at runtime but omits them from its type.
    crew = cast(_ResearchCrew, MarketResearchCrew())
    
    await asyncio.to_thread(
        crew.kickoff_with_state,
        inputs={
            "user_id": payload.user_id,
            "user_input": payload.user_input,
            "product_idea": payload.user_input,
        },
        stream=False,
    )
    
    return crew.app_state.model_dump()
