import asyncio
import importlib

import httpx
from fastapi import FastAPI

from app.main import app_exception_handler
from src.utils.exception import AppException


class _FakeDbManager:
    async def get_user_by_email(self, email):
        return None


def test_login_invalid_credentials_returns_user_facing_error(monkeypatch):
    auth_module = importlib.import_module("app.api.auth")
    monkeypatch.setattr(auth_module, "db_manager", _FakeDbManager())

    app = FastAPI()
    app.add_exception_handler(AppException, app_exception_handler)
    app.include_router(auth_module.router)

    async def call_endpoint():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/login",
                data={"username": "missing@example.com", "password": "wrong-password"},
            )

    response = asyncio.run(call_endpoint())

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
