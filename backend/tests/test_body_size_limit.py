import os
import sys
import asyncio
import httpx
from pathlib import Path
import types
import pytest

# stub redis module for tests
redis_stub = types.ModuleType("redis")
redis_asyncio_stub = types.ModuleType("redis.asyncio")

def from_url(*args, **kwargs):
  return None

redis_asyncio_stub.from_url = from_url
redis_stub.asyncio = redis_asyncio_stub
sys.modules["redis"] = redis_stub
sys.modules["redis.asyncio"] = redis_asyncio_stub

os.environ["OPENAI_API_KEY"] = "test"
os.environ["CHAT_API_KEY"] = "test-key"

sys.path.append(str(Path(__file__).resolve().parents[2]))

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
        headers={"Content-Type": "application/json"},
      )
    assert resp.status_code == 413

  asyncio.run(_run())
