import os
import asyncio
import httpx
import pytest

os.environ["OPENAI_API_KEY"] = "test"
os.environ["CHAT_API_KEY"] = "test-key"

from backend.main import MAX_REQUEST_SIZE, app


class DummyRedis:
  async def zremrangebyscore(self, *args, **kwargs):
    pass

  async def zcard(self, *args, **kwargs):
    return 0

  async def zadd(self, *args, **kwargs):
    pass

  async def expire(self, *args, **kwargs):
    pass


@pytest.fixture(autouse=True)
def _fake_redis(monkeypatch):
  monkeypatch.setattr("backend.main.redis_client", DummyRedis())


def test_chunked_request_too_large():
  async def _run():
    async def gen():
      chunk = b"x" * 1024
      for _ in range((MAX_REQUEST_SIZE // 1024) + 2):
        yield chunk
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
      resp = await client.post(
        "/pdf",
        content=gen(),
        headers={
          "Content-Type": "application/json",
          "X-API-Key": "test-key",
        },
      )
    assert resp.status_code == 413

  asyncio.run(_run())
