"""FastAPI application for PO Drafter.

This module provides endpoints for health checks and PDF packet generation.
Incoming petition data is validated against a JSON Schema and merged into
AcroForm templates before being returned as a ZIP file.
"""

from __future__ import annotations

import html
import io
import json
import logging
import os
import re
import time
import zipfile
from pathlib import Path
import redis.asyncio as redis

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from jsonschema import ValidationError, validate, FormatChecker
from openai import AsyncOpenAI
from pydantic import BaseModel
from PyPDF2 import PdfReader, PdfWriter
from starlette.middleware.base import BaseHTTPMiddleware
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
RATE_LIMIT = 100
RATE_WINDOW = 60  # seconds

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

fallback_store: dict[str, int] = {}
fallback_last_reset = time.time()
fallback_active = False

def sanitize_string(value: str) -> str:
    cleaned = html.escape(value)
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)

class RateLimitMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    ip = request.client.host if request.client else "anon"
    now = time.time()
    key = f"ratelimit:{ip}"
    global fallback_store, fallback_last_reset, fallback_active
    if fallback_active:
      try:
        await redis_client.ping()
        fallback_active = False
        fallback_store.clear()
        logger.info("Redis connection restored; using Redis store")
      except Exception:
        pass
    if not fallback_active:
      try:
        await redis_client.zremrangebyscore(key, 0, now - RATE_WINDOW)
        count = await redis_client.zcard(key)
        if count >= RATE_LIMIT:
          return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        await redis_client.zadd(key, {str(now): now})
        await redis_client.expire(key, RATE_WINDOW)
        return await call_next(request)
      except Exception as exc:
        fallback_active = True
        fallback_store.clear()
        fallback_last_reset = now
        logger.warning(
          "Rate limiter store error: %s; using in-memory fallback", exc
        )
    if now - fallback_last_reset >= RATE_WINDOW:
      fallback_store.clear()
      fallback_last_reset = now
    count = fallback_store.get(ip, 0)
    if count >= RATE_LIMIT:
      return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    fallback_store[ip] = count + 1
    return await call_next(request)

# OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load JSON schema
with open(SCHEMA_PATH) as f:
    PETITION_SCHEMA = json.load(f)

# CORS config
allowed_origins = [
  o.strip()
  for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
  if o.strip()
]

# FastAPI app
app = FastAPI()
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post("/pdf")
async def generate_pdf(data: dict) -> StreamingResponse:
    """Generate PDF packet from petition data."""
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid request body")

    if len(json.dumps(data).encode("utf-8")) > MAX_REQUEST_SIZE:
        raise HTTPException(status_code=413, detail="Request too large")

    try:
        validate(instance=data, schema=PETITION_SCHEMA, format_checker=FormatChecker())
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    county = data.get("county", "General")
    template_map = {
        "Harris": "harris.pdf",
        "Dallas": "dallas.pdf",
        "Travis": "travis.pdf",
        "General": "tx_general.pdf",
    }
    template_file = FORMS_DIR / template_map.get(county, "tx_general.pdf")

    reader = PdfReader(str(template_file))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    form_values = {}
    for key, field in FIELD_MAP.items():
        try:
            form_values[field] = sanitize_string(str(data[key]))
        except KeyError:
            continue

    try:
        for page in writer.pages:
            writer.update_page_form_field_values(page, form_values)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to populate form fields: {exc}") from exc

    pdf_bytes = io.BytesIO()
    try:
        writer.write(pdf_bytes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to write PDF: {exc}") from exc
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
async def chat(request: ChatRequest):
    payload = request.model_dump()
    if len(json.dumps(payload).encode("utf-8")) > MAX_REQUEST_SIZE:
        raise HTTPException(status_code=413, detail="Request too large")

    messages = [
        {"role": msg.role, "content": sanitize_string(msg.content)}
        for msg in request.messages
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
        raise HTTPException(status_code=500, detail="Internal server error")
