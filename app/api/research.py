import asyncio
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import APIRouter, Request
from schemas.request_schema import ResearchRequest

from src.workflow.crew import MarketResearchCrew

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post('/research')
@limiter.limit("5/hour")
async def research(request: Request, payload: ResearchRequest):
    crew = MarketResearchCrew()
    
    await asyncio.to_thread(
        crew.kickoff_with_state, # type: ignore
        inputs={
            "user_id": payload.user_id,
            "user_input": payload.user_input,
            "product_idea": payload.user_input,
        },
        stream=False,
    )
    
    return crew.app_state.model_dump()
