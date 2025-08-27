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


def verify_template_integrity(path: Path) -> None:
  expected = TEMPLATE_CHECKSUMS.get(path.name)
  if not expected:
    return
  with open(path, "rb") as f:
    actual = hashlib.sha256(f.read()).hexdigest()
  if actual != expected:
    logger.error("Template checksum mismatch", file=path.name)
    raise HTTPException(status_code=500, detail="Template integrity check failed")


def get_template_file(county: str) -> Path:
  template_map = {
    "Harris": "harris.pdf",
    "Dallas": "dallas.pdf",
    "Travis": "travis.pdf",
    "General": "tx_general.pdf",
  }
  return FORMS_DIR / template_map.get(county, "tx_general.pdf")
