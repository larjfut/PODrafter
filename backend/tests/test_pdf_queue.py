import asyncio
import io
import zipfile

import httpx
import os
import pytest

os.environ["OPENAI_API_KEY"] = "test"
os.environ["CHAT_API_KEY"] = "test-key"

from backend.main import app
from backend.services.pdf_service import generate_pdf

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


def test_route_enqueues_and_returns_zip(monkeypatch):
  called = {}

  async def fake_enqueue(func, *args, **kwargs):
    called["func"] = func
    called["args"] = args
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as zf:
      zf.writestr("petition.pdf", b"dummy")
    zip_bytes.seek(0)
    future.set_result(zip_bytes)
    return future

  monkeypatch.setattr("backend.api.pdf.queue.enqueue", fake_enqueue)

  data = {
    "county": "General",
    "case_no": "123",
    "hearing_date": "2024-01-01",
    "petitioner_full_name": "Jane Doe",
    "petitioner_address": "1 Main St",
    "petitioner_phone": "555-0000",
    "petitioner_email": "jane@example.com",
    "respondent_full_name": "John Doe",
  }

  async def _run():
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
      return await client.post("/api/pdf", json=data, headers={"X-API-Key": "test-key"})

  resp = asyncio.run(_run())
  assert resp.status_code == 200
  assert called["func"] is generate_pdf
  with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
    assert zf.read("petition.pdf") == b"dummy"
