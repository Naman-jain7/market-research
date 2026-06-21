from fastapi import APIRouter, Request
from schemas.request_schema import ResearchRequest

from src.workflow.flow import MarketResearchFlow

router = APIRouter()

@router.post('/research')
async def research(request: Request, payload: ResearchRequest):
    flow = MarketResearchFlow()
    
    result = flow.kickoff(
        inputs={
            "user_id": payload.user_id,
            "user_input": payload.user_input,
            "product_idea": payload.user_input,
        }
    )
    
    return result
