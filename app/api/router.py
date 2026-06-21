from fastapi import APIRouter

from app.api import research, auth

api_router = APIRouter()

api_router.include_router(research.router, tags=["Research"])
api_router.include_router(auth.router, tags=["Auth"], prefix='/auth')
