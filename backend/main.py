"""FastAPI application for PO Drafter.

This module provides endpoints for health checks and PDF packet generation.
Incoming petition data is validated against a JSON Schema and merged into
AcroForm templates before being returned as a ZIP file.
"""

from __future__ import annotations

import hashlib
import html
import io
import json
import logging
import os
import re
import time
import zipfile
from pathlib import Path
from urllib.parse import urlparse
import redis.asyncio as redis

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from jsonschema import ValidationError, validate, FormatChecker
from openai import AsyncOpenAI
from pydantic import BaseModel, field_validator
from PyPDF2 import PdfReader, PdfWriter
from starlette.middleware.base import BaseHTTPMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from typing import Literal

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "schema" / "petition.schema.json"
FORMS_DIR = BASE_DIR / "forms" / "standard"

# Mapping of petition data keys to PDF form fields
FIELD_MAP = {
    "case_no": "CaseNumber",
    "hearing_date": "HearingDate",
    "petitioner_full_name": "PetitionerName",
    "petitioner_address": "PetitionerAddress",
    "petitioner_phone": "PetitionerPhone",
    "petitioner_email": "PetitionerEmail",
    "respondent_full_name": "RespondentName",
}

# Limits and sanitization
MAX_REQUEST_SIZE = 10_000  # bytes
MAX_FIELD_LENGTH = 1_000  # characters per field
RATE_LIMIT = 100
RATE_WINDOW = 60  # seconds

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CHAT_API_KEY = os.getenv("CHAT_API_KEY")
SENSITIVE_PATHS = {"/api/chat", "/pdf"}
DISALLOWED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in ["<script", "javascript:", "data:"]]

# SHA256 checksums for standard form templates
TEMPLATE_CHECKSUMS = {
  "dallas.pdf": "fd8584654ccf09fa6b9628fd8fd9859cc6cdc18e566b9a4b3db1f136f821b2c8",
  "harris.pdf": "fd8584654ccf09fa6b9628fd8fd9859cc6cdc18e566b9a4b3db1f136f821b2c8",
  "travis.pdf": "fd8584654ccf09fa6b9628fd8fd9859cc6cdc18e566b9a4b3db1f136f821b2c8",
  "tx_general.pdf": "fd8584654ccf09fa6b9628fd8fd9859cc6cdc18e566b9a4b3db1f136f821b2c8",
}

# In-memory fallback for rate limiting when Redis is unavailable. Mapping of
# IP -> {timestamp_id: request_time}
fallback_store: dict[str, dict[str, float]] = {}
fallback_active = False
FALLBACK_MAX_IPS = 1000
FALLBACK_IP_TTL = RATE_WINDOW * 5

def sanitize_string(value: str) -> str:
  """Basic XSS protection and length enforcement for user-provided strings."""
  cleaned = html.escape(value, quote=True)
  cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)
  cleaned = re.sub(r"(javascript:|data:)", "", cleaned, flags=re.IGNORECASE)
  return cleaned.strip()[:MAX_FIELD_LENGTH]


def sanitize_url(value: str) -> str:
  """Return a sanitized URL if scheme is http/https, else an empty string."""
  cleaned = sanitize_string(value)
  parsed = urlparse(cleaned)
  if parsed.scheme not in {"http", "https"}:
    return ""
  return cleaned


class CoverLetterContext(BaseModel):
  """Context data for cover letter templates."""

  resume_qr_url: str | None = None

  @field_validator("resume_qr_url", mode="before")
  @classmethod
  def validate_resume_qr_url(cls, v: str | None) -> str | None:
    if v is None:
      return None
    sanitized = sanitize_url(v)
    return sanitized or None


def verify_template_integrity(path: Path) -> None:
  expected = TEMPLATE_CHECKSUMS.get(path.name)
  if not expected:
    return
  with open(path, "rb") as f:
    actual = hashlib.sha256(f.read()).hexdigest()
  if actual != expected:
    logger.error("Template checksum mismatch for %s", path.name)
    raise HTTPException(status_code=500, detail="Template integrity check failed")


def get_client_ip(request: Request) -> str:
  """Return the client IP after proxy header resolution."""
  if request.client and request.client.host:
    return request.client.host
  return "anon"

class RateLimitMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    ip = get_client_ip(request)
    now = time.time()
    key = f"ratelimit:{ip}"
    global fallback_store, fallback_active

    if fallback_active:
      try:
        await redis_client.ping()
        fallback_active = False
        fallback_store.clear()
        logger.info("Redis connection restored; using Redis store")
      except Exception as exc:
        logger.debug("Redis ping failed during fallback: %s", exc)

    if not fallback_active:
      try:
        await redis_client.zremrangebyscore(key, 0, now - RATE_WINDOW)
        count = await redis_client.zcard(key)
        if count >= RATE_LIMIT:
          return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        await redis_client.zadd(key, {str(now): now})
        await redis_client.expire(key, RATE_WINDOW)
        response = await call_next(request)
        response.headers["X-RateLimit-Store"] = "redis"
        return response
      except Exception as exc:
        fallback_active = True
        fallback_store.clear()
        logger.warning(
          "Rate limiter store error: %s; using in-memory fallback", exc
        )

    # Fallback in-memory rate limiting
    window_start = now - RATE_WINDOW
    timestamps = fallback_store.setdefault(ip, {})
    for ts_key, ts in list(timestamps.items()):
      if ts < window_start:
        del timestamps[ts_key]
    if len(timestamps) >= RATE_LIMIT:
      return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    timestamps[str(now)] = now
    # Cleanup expired entries and evict stale IPs
    for ip_key, times in list(fallback_store.items()):
      for ts_key, ts in list(times.items()):
        if ts < window_start:
          del times[ts_key]
      last_seen = max(times.values()) if times else 0
      if not times or last_seen < now - FALLBACK_IP_TTL:
        del fallback_store[ip_key]

    # Enforce max IP cache size
    if len(fallback_store) > FALLBACK_MAX_IPS:
      sorted_ips = sorted(
        fallback_store.items(),
        key=lambda item: max(item[1].values()) if item[1] else 0,
      )
      while len(sorted_ips) > FALLBACK_MAX_IPS:
        old_ip, _ = sorted_ips.pop(0)
        fallback_store.pop(old_ip, None)

    response = await call_next(request)
    response.headers["X-RateLimit-Store"] = "memory"
    return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
  """Reject requests over MAX_REQUEST_SIZE."""

  async def dispatch(self, request: Request, call_next):
    cl = request.headers.get("content-length")
    if cl:
      try:
        if int(cl) > MAX_REQUEST_SIZE:
          return JSONResponse(status_code=413, content={"detail": "Request too large"})
      except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Invalid content length"})
    else:
      body = bytearray()
      async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_REQUEST_SIZE:
          return JSONResponse(status_code=413, content={"detail": "Request too large"})
      body_bytes = bytes(body)
      if body_bytes:
        request._body = body_bytes
        consumed = False
        async def receive():
          nonlocal consumed
          if not consumed:
            consumed = True
            return {"type": "http.request", "body": body_bytes, "more_body": False}
          return {"type": "http.disconnect"}
        request._receive = receive
    return await call_next(request)

# OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Environment validation
async def validate_environment() -> None:
  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
    msg = "OPENAI_API_KEY is not set"
    logger.error(msg)
    raise RuntimeError(msg)
  if api_key == "test":
    if ENVIRONMENT == "production":
      msg = "Test API key not allowed in production"
      logger.error(msg)
      raise RuntimeError(msg)
    logger.info("Using test API key; skipping OpenAI connectivity check")
    return
  try:
    await client.models.list()
  except Exception as exc:
    msg = f"OpenAI connectivity check failed: {exc}"
    logger.error(msg)
    raise RuntimeError(msg) from exc

# Load JSON schema with error handling
def load_schema() -> dict:
  try:
    with open(SCHEMA_PATH) as f:
      return json.load(f)
  except FileNotFoundError as exc:
    msg = f"Schema file not found: {SCHEMA_PATH}"
    logger.error(msg)
    raise RuntimeError(msg) from exc
  except json.JSONDecodeError as exc:
    msg = f"Invalid JSON schema: {exc}"
    logger.error(msg)
    raise RuntimeError(msg) from exc


def reload_schema() -> None:
  global PETITION_SCHEMA
  PETITION_SCHEMA = load_schema()


PETITION_SCHEMA: dict = {}
reload_schema()


# CORS config
DEFAULT_ALLOWED_ORIGINS = ["http://localhost:5173"]


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


allowed_origins = get_allowed_origins()

# FastAPI app
app = FastAPI()
app.add_middleware(RateLimitMiddleware)
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_origins,
  allow_methods=["POST", "GET"],
  allow_headers=["*"],
)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["127.0.0.1"])


@app.middleware("http")
async def log_requests(request: Request, call_next):
  ip = get_client_ip(request)
  start = time.time()
  try:
    response = await call_next(request)
  except Exception as exc:
    duration = (time.time() - start) * 1000
    path = request.url.path
    log_ip = ip
    log_path = path
    if path in SENSITIVE_PATHS:
      log_ip = "redacted"
      log_path = "redacted"
    logger.exception(
      "Error processing %s %s from %s in %.2fms",
      request.method,
      log_path,
      log_ip,
      duration,
    )
    raise
  duration = (time.time() - start) * 1000
  path = request.url.path
  log_ip = ip
  log_path = path
  if path in SENSITIVE_PATHS:
    log_ip = "redacted"
    log_path = "redacted"
  logger.info(
    "%s %s from %s -> %s in %.2fms",
    request.method,
    log_path,
    log_ip,
    response.status_code,
    duration,
  )
  return response


@app.on_event("startup")
async def startup_event() -> None:
  """Reload schema and validate environment at startup."""
  reload_schema()
  await validate_environment()

@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/redis/health")
async def redis_health():
  try:
    await redis_client.ping()
    return {"status": "ok"}
  except Exception as exc:
    logger.warning("Redis health check failed: %s", exc)
    return JSONResponse(
      status_code=503,
      content={"status": "unavailable", "detail": "Redis unavailable"},
    )


@app.post("/pdf")
async def generate_pdf(data: dict) -> StreamingResponse:
    """Generate PDF packet from petition data."""
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid request body")

    if len(json.dumps(data).encode("utf-8")) > MAX_REQUEST_SIZE:
        raise HTTPException(status_code=413, detail="Request too large")

    if any(isinstance(v, str) and len(v) > MAX_FIELD_LENGTH for v in data.values()):
        raise HTTPException(status_code=413, detail="Field too large")

    try:
        validate(instance=data, schema=PETITION_SCHEMA, format_checker=FormatChecker())
    except ValidationError as exc:
        logger.warning("Petition validation failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid petition data") from exc

    county = data.get("county", "General")
    logger.info("PDF requested for county %s", county)
    template_map = {
        "Harris": "harris.pdf",
        "Dallas": "dallas.pdf",
        "Travis": "travis.pdf",
        "General": "tx_general.pdf",
    }
    template_file = FORMS_DIR / template_map.get(county, "tx_general.pdf")

    if not template_file.exists():
        logger.warning("Template not found for county %s", county)
        raise HTTPException(status_code=404, detail="Template not found")
    verify_template_integrity(template_file)

    reader = PdfReader(str(template_file))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    form_values: dict[str, str] = {}
    for key, field in FIELD_MAP.items():
        value = data.get(key)
        if value is not None:
            form_values[field] = sanitize_string(str(value))

    try:
        for page in writer.pages:
            writer.update_page_form_field_values(page, form_values)
        pdf_bytes = io.BytesIO()
        writer.write(pdf_bytes)
    except Exception as exc:
        logger.exception("PDF generation failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to generate PDF") from exc
    pdf_bytes.seek(0)

    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as zf:
        zf.writestr("petition.pdf", pdf_bytes.getvalue())
    zip_bytes.seek(0)

    return StreamingResponse(
        zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=po_packet.zip"},
    )


# ✅ Add your OpenAI chat endpoint below

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]

@app.post("/api/chat")
async def chat(chat_request: ChatRequest, request: Request):
  provided = request.headers.get("X-API-Key")
  if CHAT_API_KEY is None:
    logger.error("CHAT_API_KEY is not set")
    raise HTTPException(status_code=500, detail="Server misconfiguration")
  if not provided or provided != CHAT_API_KEY:
    raise HTTPException(status_code=401, detail="Unauthorized")

  payload = chat_request.model_dump()
  if len(json.dumps(payload).encode("utf-8")) > MAX_REQUEST_SIZE:
    raise HTTPException(status_code=413, detail="Request too large")

  for msg in chat_request.messages:
    if len(msg.content) > MAX_FIELD_LENGTH:
      raise HTTPException(status_code=413, detail="Field too large")
    for pattern in DISALLOWED_PATTERNS:
      if pattern.search(msg.content):
        raise HTTPException(status_code=400, detail="Invalid content")

  messages = [
    {"role": msg.role, "content": sanitize_string(msg.content)}
    for msg in chat_request.messages
  ]

  try:
    response = await client.chat.completions.create(
      model="gpt-4o",
      messages=messages,
      temperature=0.7,
    )
    return response.choices[0].message.model_dump()
  except Exception as e:
    logger.exception("chat endpoint failed", exc_info=e)
    raise HTTPException(status_code=500, detail="Internal server error") from e
