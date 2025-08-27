import importlib
import pytest


def test_public_key_without_chat_key_fails(monkeypatch):
  monkeypatch.setenv("OPENAI_API_KEY", "test")
  monkeypatch.delenv("CHAT_API_KEY", raising=False)
  monkeypatch.setenv("PUBLIC_CHAT_API_KEY", "test-key")
  import backend.middleware.auth as auth
  importlib.reload(auth)
  with pytest.raises(RuntimeError):
    auth.validate_api_key()
  monkeypatch.setenv("CHAT_API_KEY", "test-key")
  importlib.reload(auth)
  auth.validate_api_key()
