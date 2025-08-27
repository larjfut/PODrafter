import importlib
import pytest
from fastapi import HTTPException


def test_public_key_without_chat_key_fails(monkeypatch):
  monkeypatch.setenv("OPENAI_API_KEY", "test")
  monkeypatch.delenv("CHAT_API_KEY", raising=False)
  monkeypatch.setenv("PUBLIC_CHAT_API_KEY", "test-key")
  import backend.middleware.auth as auth
  with pytest.raises(HTTPException) as exc:
    importlib.reload(auth)
  assert exc.value.status_code == 500
  assert exc.value.detail == "Server misconfiguration"
  monkeypatch.setenv("CHAT_API_KEY", "test-key")
  importlib.reload(auth)
