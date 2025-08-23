import os
import io
import zipfile
import asyncio
import httpx
from openai.resources.chat.completions import AsyncCompletions
from PyPDF2 import PdfReader
import sys
from pathlib import Path
import pytest
import fakeredis.aioredis as fakeredis

os.environ["OPENAI_API_KEY"] = "test"

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.main import MAX_REQUEST_SIZE, app


@pytest.fixture(autouse=True)
def _fake_redis(monkeypatch):
  monkeypatch.setattr("backend.main.redis_client", fakeredis.FakeRedis())


def test_health():
  async def _run():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

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
        "backend.main.PdfReader", lambda *args, **kwargs: DummyReader()
    )
    monkeypatch.setattr("backend.main.PdfWriter", DummyWriter)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post("/pdf", json=data)
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
        resp = await client.post("/api/chat", json={"messages": messages})
    assert resp.status_code == 200
    assert resp.json() == {"role": "assistant", "content": "hi"}

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
        resp = await client.post("/api/chat", json={"messages": messages})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Internal server error"

  asyncio.run(_run())


def test_chat_request_too_large():
  async def _run():
    big_content = "a" * (MAX_REQUEST_SIZE + 1)
    messages = [{"role": "user", "content": big_content}]
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post("/api/chat", json={"messages": messages})
    assert resp.status_code == 413

  asyncio.run(_run())


def test_pdf_invalid_schema():
  async def _run():
    data = {"county": "Harris"}
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        resp = await client.post("/pdf", json=data)
    assert resp.status_code == 400

  asyncio.run(_run())

