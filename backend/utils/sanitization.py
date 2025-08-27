import re
from urllib.parse import urlparse

import bleach
from pydantic import BaseModel, field_validator

from .validation import MAX_FIELD_LENGTH

DISALLOWED_PATTERNS = [
  re.compile(p, re.IGNORECASE)
  for p in ["<script", "javascript:", "data:", "vbscript:", "file:"]
]


def sanitize_string(value: str) -> str:
  cleaned = bleach.clean(value, tags=[], attributes={}, strip=True)
  cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)
  cleaned = re.sub(r"(javascript:|data:)", "", cleaned, flags=re.IGNORECASE)
  return cleaned.strip()[:MAX_FIELD_LENGTH]


def sanitize_url(value: str) -> str:
  cleaned = sanitize_string(value)
  parsed = urlparse(cleaned)
  if parsed.scheme not in {"http", "https"}:
    return ""
  return cleaned


class CoverLetterContext(BaseModel):
  resume_qr_url: str | None = None

  @field_validator("resume_qr_url", mode="before")
  @classmethod
  def validate_resume_qr_url(cls, v: str | None) -> str | None:
    if v is None:
      return None
    sanitized = sanitize_url(v)
    return sanitized or None
