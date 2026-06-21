from collections.abc import Iterator
from typing import Any
import requests


API_BASE_URL = "http://127.0.0.1:8000/api/v1"
TIMEOUT_SECONDS = 60

class APIError(RuntimeError):
    pass

def _detail(response: requests.Response) -> str:
    try:
        body = response.json()
        return str(body.get("detail") or body.get("message") or response.text)

    except ValueError:
        return response.text or f"Request failed with status {response.status_code}"


def _raise_for_status(response: requests.Response) -> None:
    if not response.ok:
        raise APIError(_detail(response))


def signup(full_name: str, email: str, password: str, age: int | None) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/auth/signup",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
            "age": age,
        },
        timeout=TIMEOUT_SECONDS,
    )
    _raise_for_status(response)
    return response.json()


def login(email: str, password: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={"username": email, "password": password},
        timeout=TIMEOUT_SECONDS,
    )
    _raise_for_status(response)
    return response.json()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def run_research(user_id: int, token: str, query: str) -> Iterator[str]:
    payload = {"user_id": user_id, "query": query}

    with requests.post(
        f"{API_BASE_URL}/research",
        headers={**_auth_headers(token), "Content-Type": "application/json"},
        json=payload,
        stream=True,
        timeout=None,
    ) as response:
        _raise_for_status(response)
        
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk # type: ignore