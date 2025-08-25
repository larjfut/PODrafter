import asyncio
import httpx
import importlib
import pytest
from openai.resources.chat.completions import AsyncCompletions


class DummyRedis:
  async def zremrangebyscore(self, *args, **kwargs):
    pass

  async def zcard(self, *args, **kwargs):
    return 0

  async def zadd(self, *args, **kwargs):
    pass

  async def expire(self, *args, **kwargs):
    pass


@pytest.fixture
def app(monkeypatch):
  monkeypatch.setenv("OPENAI_API_KEY", "test")
  monkeypatch.delenv("CHAT_API_KEY", raising=False)
  monkeypatch.setenv("PUBLIC_CHAT_API_KEY", "test-key")
  import backend.main as main
  importlib.reload(main)
  monkeypatch.setattr("backend.main.redis_client", DummyRedis())
  return main.app


def test_public_key_fallback(monkeypatch, app):
  async def fake_create(self, *args, **kwargs):
    class Msg:
      role = "assistant"
      content = "hi"
      tool_calls = []

      def model_dump(self):
        return {"role": self.role, "content": self.content}

    class Choice:
      message = Msg()

    class Resp:
      choices = [Choice()]

    return Resp()

  async def _run():
    monkeypatch.setattr(AsyncCompletions, "create", fake_create)
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
      resp = await client.post(
        "/api/chat", json={"messages": []}, headers={"X-API-Key": "test-key"}
      )
    assert resp.status_code == 200

  asyncio.run(_run())

