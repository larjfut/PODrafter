import pytest
from fastapi import HTTPException

from backend.services.template_service import verify_template_integrity

def test_verify_template_integrity_rejects_outside_dir(tmp_path):
  outside = tmp_path / "evil.pdf"
  outside.write_text("data")
  with pytest.raises(HTTPException) as exc:
    verify_template_integrity(outside)
  assert exc.value.status_code == 400
