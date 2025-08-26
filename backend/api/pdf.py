import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from jsonschema import ValidationError, validate, FormatChecker
from prometheus_client import Counter, Histogram

from ..middleware.auth import verify_api_key
from ..middleware.rate_limit import rate_limit
from ..services.pdf_service import generate_pdf
from ..utils.validation import MAX_REQUEST_SIZE, MAX_FIELD_LENGTH, PETITION_SCHEMA
from ..worker import queue

router = APIRouter()


PDF_REQUESTS = Counter("pdf_requests_total", "Number of PDF requests")
PDF_LATENCY = Histogram(
  "pdf_request_duration_seconds", "Latency of PDF requests"
)


@router.post("/api/pdf")
@rate_limit(limit=5, window=60, key="pdf")
async def pdf(data: dict, request: Request) -> StreamingResponse:
  verify_api_key(request)
  PDF_REQUESTS.inc()
  with PDF_LATENCY.time():
    if not isinstance(data, dict):
      raise HTTPException(status_code=400, detail="Invalid request body")

    if len(json.dumps(data).encode("utf-8")) > MAX_REQUEST_SIZE:
      raise HTTPException(status_code=413, detail="Request too large")

    if any(isinstance(v, str) and len(v) > MAX_FIELD_LENGTH for v in data.values()):
      raise HTTPException(status_code=413, detail="Field too large")

    try:
      validate(instance=data, schema=PETITION_SCHEMA, format_checker=FormatChecker())
    except ValidationError as exc:
      raise HTTPException(status_code=400, detail="Invalid petition data") from exc

    future = await queue.enqueue(generate_pdf, data)
    zip_bytes = await future
    return StreamingResponse(
      zip_bytes,
      media_type="application/zip",
      headers={"Content-Disposition": "attachment; filename=po_packet.zip"},
    )
