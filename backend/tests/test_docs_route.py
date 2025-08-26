import os
import asyncio
import httpx
import pytest

os.environ["OPENAI_API_KEY"] = "test"
os.environ["CHAT_API_KEY"] = "test-key"

from backend.main import create_app
from backend.middleware.rate_limit import InMemoryRateLimiter


def test_docs_requires_api_key(monkeypatch):
  async def _run():
    monkeypatch.setenv("ENVIRONMENT", "development")
    limiter = InMemoryRateLimiter(100, 60, 300, 1000)
    app = create_app(limiter)
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
      resp = await client.get("/docs")
    assert resp.status_code == 401
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
      resp = await client.get("/docs", headers={"X-API-Key": "test-key"})
    assert resp.status_code == 200
    assert "Swagger UI" in resp.text

  asyncio.run(_run())


def test_docs_not_available_in_production(monkeypatch):
  async def _run():
    monkeypatch.setenv("ENVIRONMENT", "production")
    limiter = InMemoryRateLimiter(100, 60, 300, 1000)
    app = create_app(limiter)
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
      resp = await client.get("/docs", headers={"X-API-Key": "test-key"})
    assert resp.status_code == 404

  asyncio.run(_run())

