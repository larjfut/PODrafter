import json
import os
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCHEMA_PATH = Path(os.getenv("SCHEMA_PATH", BASE_DIR / "schema" / "petition.schema.json"))
MAX_REQUEST_SIZE = 10_000
MAX_FIELD_LENGTH = 1_000
MAX_HISTORY_MESSAGES = 20
DEFAULT_ALLOWED_ORIGINS = ["http://localhost:5173"]


def load_schema() -> dict:
  with open(SCHEMA_PATH) as f:
    return json.load(f)


PETITION_SCHEMA: dict = load_schema()


def reload_schema() -> None:
  global PETITION_SCHEMA
  PETITION_SCHEMA = load_schema()


def get_allowed_origins() -> list[str]:
  raw = os.getenv("ALLOWED_ORIGINS", ",".join(DEFAULT_ALLOWED_ORIGINS))
  origins: list[str] = []
  for origin in (o.strip() for o in raw.split(",")):
    if not origin:
      continue
    if "*" in origin:
      raise RuntimeError(f"Wildcard origin not allowed: {origin}")
    parsed = urlparse(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
      raise RuntimeError(f"Invalid origin URL: {origin}")
    origins.append(origin)
  return origins
