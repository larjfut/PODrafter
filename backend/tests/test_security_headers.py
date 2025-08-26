import os
import asyncio
import httpx
import pytest

os.environ["OPENAI_API_KEY"] = "test"
os.environ["CHAT_API_KEY"] = "test-key"

from backend.main import app


class DummyRedis:
  async def zremrangebyscore(self, *args, **kwargs):
    pass

  async def zcard(self, *args, **kwargs):
    return 0

  async def zadd(self, *args, **kwargs):
    pass

  async def expire(self, *args, **kwargs):
    pass

  async def ping(self, *args, **kwargs):
    return True


@pytest.fixture(autouse=True)
def _fake_redis(monkeypatch):
  monkeypatch.setattr("backend.main.redis_client", DummyRedis())


@pytest.mark.parametrize("path", ["/health", "/redis/health"])
def test_security_headers(path):
  async def _run():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.get(path)
    expected_csp = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "frame-ancestors 'none'"
    )
    assert resp.headers["content-security-policy"] == expected_csp
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers["referrer-policy"] == "no-referrer"
    assert (
        resp.headers["permissions-policy"]
        == "geolocation=(), microphone=(), camera=()"
    )

  asyncio.run(_run())

