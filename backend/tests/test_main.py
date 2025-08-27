import os
import io
import zipfile
import asyncio
import json
import httpx
from openai.resources.chat.completions import AsyncCompletions
from PyPDF2 import PdfReader
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


  def test_health():
    async def _run():
      async with httpx.AsyncClient(
          transport=httpx.ASGITransport(app=app), base_url="http://testserver"
      ) as client:
          resp = await client.get("/health")
      assert resp.status_code == 200
      assert resp.json() == {"status": "ok"}

    asyncio.run(_run())


  def test_correlation_id():
    async def _run():
      async with httpx.AsyncClient(
          transport=httpx.ASGITransport(app=app), base_url="http://testserver"
      ) as client:
          resp = await client.get("/health")
      assert resp.headers.get("X-Correlation-ID")
      correlation = "test-id"
      async with httpx.AsyncClient(
          transport=httpx.ASGITransport(app=app), base_url="http://testserver"
      ) as client:
          resp = await client.get("/health", headers={"X-Correlation-ID": correlation})
      assert resp.headers["X-Correlation-ID"] == correlation

    asyncio.run(_run())


def test_pdf_generation(monkeypatch):
  async def _run():
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

    class DummyPage:
        pass

    class DummyReader:
        def __init__(self, *args, **kwargs):
            self.pages = [DummyPage()]

    class DummyWriter:
        def __init__(self, *args, **kwargs):
            self.pages = []
            self.values = {}

        def add_page(self, page):
            self.pages.append(page)

        def update_page_form_field_values(self, page, data):
            self.values.update(data)

        def write(self, stream):
            from PyPDF2 import PdfWriter
            from PyPDF2.generic import (
                ArrayObject,
                DictionaryObject,
                NameObject,
                NumberObject,
                TextStringObject,
            )

            writer = PdfWriter()
            writer.add_blank_page(width=300, height=400)
            fields_arr = ArrayObject()
            for idx, (name, value) in enumerate(self.values.items()):
                annot = DictionaryObject({
                    NameObject("/T"): TextStringObject(name),
                    NameObject("/FT"): NameObject("/Tx"),
                    NameObject("/Rect"): ArrayObject([
                        NumberObject(0),
                        NumberObject(idx * 20),
                        NumberObject(100),
                        NumberObject(idx * 20 + 20),
                    ]),
                    NameObject("/V"): TextStringObject(value),
                    NameObject("/Ff"): NumberObject(0),
                    NameObject("/Type"): NameObject("/Annot"),
                    NameObject("/Subtype"): NameObject("/Widget"),
                })
                writer.add_annotation(0, annot)
                fields_arr.append(annot)
            writer._root_object.update(
                {
                    NameObject("/AcroForm"): DictionaryObject(
                        {NameObject("/Fields"): fields_arr}
                    )
                }
            )
            writer.write(stream)

    monkeypatch.setattr(
        "backend.services.pdf_service.PdfReader", lambda *args, **kwargs: DummyReader()
    )
    monkeypatch.setattr("backend.services.pdf_service.PdfWriter", DummyWriter)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/pdf", json=data, headers={"X-API-Key": "test-key"}
        )
    assert resp.status_code == 200
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        pdf_bytes = zf.read("petition.pdf")
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = {k: v.get("/V") for k, v in reader.get_fields().items()}
    assert fields == {
        "CaseNumber": "123",
        "HearingDate": "2024-01-01",
        "PetitionerName": "Jane Doe",
        "PetitionerAddress": "1 Main St",
        "PetitionerPhone": "555-0000",
        "PetitionerEmail": "jane@example.com",
        "RespondentName": "John Doe",
    }

  asyncio.run(_run())


def test_pdf_missing_api_key():
  async def _run():
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
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post("/api/pdf", json=data)
    assert resp.status_code == 401

  asyncio.run(_run())


def test_pdf_invalid_api_key():
  async def _run():
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
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/pdf", json=data, headers={"X-API-Key": "wrong"}
        )
    assert resp.status_code == 401

  asyncio.run(_run())


def test_chat_endpoint(monkeypatch):
  async def fake_create(self, *args, **kwargs):
    class FakeMessage:
        role = "assistant"
        content = "hi"

        def model_dump(self):
            return {"role": self.role, "content": self.content}

    class FakeResponse:
        choices = [type("Choice", (), {"message": FakeMessage()})()]

    return FakeResponse()

  async def _run():
    monkeypatch.setattr(AsyncCompletions, "create", fake_create)
    messages = [{"role": "user", "content": "hello"}]
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": messages},
            headers={"X-API-Key": "test-key"},
        )
    assert resp.status_code == 200
    assert resp.json() == {
        "messages": messages + [{"role": "assistant", "content": "hi"}],
        "upserts": [],
    }

  asyncio.run(_run())


def test_chat_returns_upserts(monkeypatch):
  async def fake_create(self, *args, **kwargs):
    class FakeCall:
      function = type(
        "Func",
        (),
        {
          "name": "upsert_petition",
          "arguments": json.dumps(
            {
              "county": "Harris",
              "source_msg_id": "m1",
              "confidence": 0.9,
            }
          ),
        },
      )

    class FakeMessage:
      role = "assistant"
      content = "hi"
      tool_calls = [FakeCall()]

      def model_dump(self):
        return {"role": self.role, "content": self.content}

    class FakeResponse:
      choices = [type("Choice", (), {"message": FakeMessage()})()]

    return FakeResponse()

  async def _run():
    monkeypatch.setattr(AsyncCompletions, "create", fake_create)
    messages = [{"role": "user", "content": "hello"}]
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
      resp = await client.post(
        "/api/chat",
        json={"messages": messages},
        headers={"X-API-Key": "test-key"},
      )
    assert resp.status_code == 200
    assert resp.json() == {
      "messages": messages + [{"role": "assistant", "content": "hi"}],
      "upserts": [
        {
          "county": "Harris",
          "source_msg_id": "m1",
          "confidence": 0.9,
        }
      ],
    }

  asyncio.run(_run())


def test_chat_openai_failure(monkeypatch):
  async def fake_create(self, *args, **kwargs):
    raise RuntimeError("boom")

  async def _run():
    monkeypatch.setattr(AsyncCompletions, "create", fake_create)
    messages = [{"role": "user", "content": "hello"}]
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": messages},
            headers={"X-API-Key": "test-key"},
        )
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"

  asyncio.run(_run())


def test_chat_auth_required(monkeypatch):
  called = False

  async def fake_create(self, *args, **kwargs):
    nonlocal called
    called = True
    return None

  async def _run():
    monkeypatch.setattr(AsyncCompletions, "create", fake_create)
    messages = [{"role": "user", "content": "hello"}]
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post("/api/chat", json={"messages": messages})
    assert resp.status_code == 401
    assert called is False

  asyncio.run(_run())


def test_invalid_allowed_origin(monkeypatch):
  from backend import main

  monkeypatch.setenv("ALLOWED_ORIGINS", "not-a-url")
  with pytest.raises(RuntimeError):
    main.get_allowed_origins()


def test_wildcard_allowed_origin(monkeypatch):
  from backend import main

  monkeypatch.setenv("ALLOWED_ORIGINS", "http://example.com,*")
  with pytest.raises(RuntimeError):
    main.get_allowed_origins()


def test_chat_rejects_bad_content():
  async def _run():
    messages = [{"role": "user", "content": "<script>bad()</script>"}]
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": messages},
            headers={"X-API-Key": "test-key"},
        )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid content"

  asyncio.run(_run())


def test_chat_request_too_large():
  async def _run():
    big_content = "a" * (MAX_REQUEST_SIZE + 1)
    messages = [{"role": "user", "content": big_content}]
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": messages},
            headers={"X-API-Key": "test-key"},
        )
    assert resp.status_code == 413

  asyncio.run(_run())


def test_chat_truncates_history(monkeypatch):
  called = {}

  async def fake_create(self, *args, **kwargs):
    called["messages"] = kwargs["messages"]
    class FakeMessage:
      role = "assistant"
      content = "ok"
    class FakeResponse:
      choices = [type("Choice", (), {"message": FakeMessage()})()]
    return FakeResponse()

  async def _run():
    monkeypatch.setattr(AsyncCompletions, "create", fake_create)
    long = "a" * 299
    messages = [{"role": "user", "content": long}] * 30
    payload = {"messages": messages[-20:]}
    assert len(json.dumps(payload).encode("utf-8")) <= MAX_REQUEST_SIZE
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/chat",
            json={"messages": messages},
            headers={"X-API-Key": "test-key"},
        )
    assert resp.status_code == 200
    assert len(called["messages"]) == 21

  asyncio.run(_run())


def test_pdf_invalid_schema():
  async def _run():
    data = {"county": "Harris"}
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/pdf", json=data, headers={"X-API-Key": "test-key"}
        )
    assert resp.status_code == 400

  asyncio.run(_run())

