from typing import Any
from urllib.parse import quote

import httpx
from app.conf import settings


async def call_api(
        method: str,  # "GET", "POST" и т.д.
        endpoint: str,  # "/habits/user/123"
        data: dict | Any = None,
        token: str = None
) -> dict:

    headers = {"accept": "application/json", "Authorization": f"Bearer {token}"} if token else {}

    async with httpx.AsyncClient(base_url=settings.API_URL) as client:
        response = await client.request(
            method,
            endpoint,
            json=data,
            headers=headers
        )
        return response.json()