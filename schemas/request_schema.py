from pydantic import BaseModel


class ResearchRequest(BaseModel):
    user_id: int
    user_input: str
