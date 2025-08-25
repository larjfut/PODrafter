import importlib
import sys
import pytest


def test_missing_key_raises(monkeypatch):
  monkeypatch.delenv("CHAT_API_KEY", raising=False)
  monkeypatch.setenv("ENVIRONMENT", "production")
  monkeypatch.setenv("OPENAI_API_KEY", "test")
  sys.modules.pop("backend.main", None)
  with pytest.raises(RuntimeError):
    importlib.import_module("backend.main")
  sys.modules.pop("backend.main", None)

