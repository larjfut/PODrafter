import hashlib
import os
from pathlib import Path

import structlog
from fastapi import HTTPException

logger = structlog.get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FORMS_DIR = Path(os.getenv("FORMS_DIR", BASE_DIR / "forms" / "standard"))

FIELD_MAP = {
  "case_no": "CaseNumber",
  "hearing_date": "HearingDate",
  "petitioner_full_name": "PetitionerName",
  "petitioner_address": "PetitionerAddress",
  "petitioner_phone": "PetitionerPhone",
  "petitioner_email": "PetitionerEmail",
  "respondent_full_name": "RespondentName",
}

# Pre-computed SHA-256 checksums for the standard PDF templates.
# These values are used to verify the integrity of form templates at runtime.
TEMPLATE_CHECKSUMS: dict[str, str] = {
  "dallas.pdf": "fd8584654ccf09fa6b9628fd8fd9859cc6cdc18e566b9a4b3db1f136f821b2c8",
  "harris.pdf": "fd8584654ccf09fa6b9628fd8fd9859cc6cdc18e566b9a4b3db1f136f821b2c8",
  "travis.pdf": "fd8584654ccf09fa6b9628fd8fd9859cc6cdc18e566b9a4b3db1f136f821b2c8",
  "tx_general.pdf": "fd8584654ccf09fa6b9628fd8fd9859cc6cdc18e566b9a4b3db1f136f821b2c8",
}


def _resolve_template(path: Path) -> Path:
  resolved = path.resolve()
  forms_root = FORMS_DIR.resolve()
  if not resolved.is_relative_to(forms_root):
    logger.warning("Template path traversal attempt", path=str(resolved))
    raise HTTPException(status_code=400, detail="Invalid template path")
  return resolved


def verify_template_integrity(path: Path) -> None:
  resolved = _resolve_template(path)
  expected = TEMPLATE_CHECKSUMS.get(resolved.name)
  if not expected:
    return
  with open(resolved, "rb") as f:
    actual = hashlib.sha256(f.read()).hexdigest()
  if actual != expected:
    logger.error("Template checksum mismatch", file=resolved.name)
    raise HTTPException(status_code=500, detail="Template integrity check failed")


def get_template_file(county: str) -> Path:
  template_map = {
    "Harris": "harris.pdf",
    "Dallas": "dallas.pdf",
    "Travis": "travis.pdf",
    "General": "tx_general.pdf",
  }
  candidate = FORMS_DIR / template_map.get(county, "tx_general.pdf")
  return _resolve_template(candidate)
