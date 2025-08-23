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
            "petitioner_full_name": "Jane Doe",
            "respondent_full_name": "John Doe",
        }

        class DummyReader:
            pages = []

        monkeypatch.setattr(
            "backend.main.PdfReader", lambda *args, **kwargs: DummyReader()
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            resp = await client.post("/pdf", json=data)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"

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

