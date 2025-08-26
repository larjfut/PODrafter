import logging
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .auth import get_client_ip
from ..utils.validation import MAX_REQUEST_SIZE

logger = logging.getLogger(__name__)
SENSITIVE_PATHS = {"/api/chat", "/pdf"}


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
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


async def set_security_headers(request: Request, call_next):
  response = await call_next(request)
  response.headers["Content-Security-Policy"] = "default-src 'self'"
  response.headers["X-Content-Type-Options"] = "nosniff"
  return response


async def log_requests(request: Request, call_next):
  ip = get_client_ip(request)
  start = time.time()
  try:
    response = await call_next(request)
  except Exception:
    duration = (time.time() - start) * 1000
    path = request.url.path
    log_ip = "redacted" if path in SENSITIVE_PATHS else ip
    log_path = "redacted" if path in SENSITIVE_PATHS else path
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
  log_ip = "redacted" if path in SENSITIVE_PATHS else ip
  log_path = "redacted" if path in SENSITIVE_PATHS else path
  logger.info(
    "%s %s from %s -> %s in %.2fms",
    request.method,
    log_path,
    log_ip,
    response.status_code,
    duration,
  )
  return response
