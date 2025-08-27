import os
import hashlib
import pytest
from fastapi import HTTPException

os.environ["OPENAI_API_KEY"] = "test"

from backend.services.template_service import (
  TEMPLATE_CHECKSUMS,
  FORMS_DIR,
  verify_template_integrity,
)


def test_template_checksums():
  expected: dict[str, str] = {}
  for path in FORMS_DIR.glob("*.pdf"):
    with open(path, "rb") as f:
      expected[path.name] = hashlib.sha256(f.read()).hexdigest()
  assert TEMPLATE_CHECKSUMS == expected


def test_verify_template_integrity_raises_on_mismatch(monkeypatch):
  path = next(FORMS_DIR.glob("*.pdf"))
  monkeypatch.setitem(TEMPLATE_CHECKSUMS, path.name, "badchecksum")
  with pytest.raises(HTTPException):
    verify_template_integrity(path)
