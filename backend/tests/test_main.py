import os
import httpx
import asyncio

os.environ["OPENAI_API_KEY"] = "test"

from backend.main import app


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
            "county": "Harris",
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

        captured = {}

        class DummyWriter:
            def __init__(self, *args, **kwargs):
                self.pages = []

            def add_page(self, page):
                self.pages.append(page)

            def update_page_form_field_values(self, page, data):
                captured.update(data)

            def write(self, stream):
                pass

        monkeypatch.setattr(
            "backend.main.PdfReader", lambda *args, **kwargs: DummyReader()
        )
        monkeypatch.setattr("backend.main.PdfWriter", DummyWriter)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            resp = await client.post("/pdf", json=data)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"
        assert captured == {
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
    async def fake_create(*args, **kwargs):
        class FakeMessage:
            role = "assistant"
            content = "hi"

            def model_dump(self):
                return {"role": self.role, "content": self.content}

        class FakeResponse:
            choices = [type("Choice", (), {"message": FakeMessage()})()]

        return FakeResponse()

    async def _run():
        monkeypatch.setattr(
            "backend.main.client.chat.completions.create", fake_create
        )
        messages = [{"role": "user", "content": "hello"}]
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            resp = await client.post("/api/chat", json={"messages": messages})
        assert resp.status_code == 200
        assert resp.json() == {"role": "assistant", "content": "hi"}

    asyncio.run(_run())

