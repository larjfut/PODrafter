import importlib
import pytest
from fastapi import HTTPException


def test_public_key_without_chat_key_fails(monkeypatch):
  monkeypatch.setenv("OPENAI_API_KEY", "test")
  monkeypatch.delenv("CHAT_API_KEY", raising=False)
  monkeypatch.setenv("PUBLIC_CHAT_API_KEY", "test-key")
  with pytest.raises(HTTPException) as exc:
    import backend.main as main
    importlib.reload(main)
  assert exc.value.status_code == 500
  assert exc.value.detail == "Server misconfiguration"
