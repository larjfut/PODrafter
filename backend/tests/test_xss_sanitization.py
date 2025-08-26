import os
import asyncio
import httpx
import pytest

os.environ["OPENAI_API_KEY"] = "test"
os.environ["CHAT_API_KEY"] = "test-key"

from backend.main import sanitize_string, app


@pytest.mark.parametrize(
  "payload,expected",
  [
    ("<script>alert('x')</script>", "alert('x')"),
    ("<img src=x onerror=alert(1)>", ""),
    ("javascript:alert(1)", "alert(1)"),
    ("data:text/html,<script>alert(1)</script>", "text/html,alert(1)"),
  ],
)
def test_sanitize_string(payload, expected):
  assert sanitize_string(payload) == expected


@pytest.mark.parametrize(
  "payload",
  [
    "vbscript:alert(1)",
    "file://etc/passwd",
  ],
)
def test_chat_rejects_disallowed_schemes(payload):
  async def _run():
    messages = [{"role": "user", "content": payload}]
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
      resp = await client.post(
        "/api/chat",
        json={"messages": messages},
        headers={"X-API-Key": "test-key"},
      )
    assert resp.status_code == 400

  asyncio.run(_run())
