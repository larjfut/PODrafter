import time
import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars

from .auth import get_client_ip
from ..utils.validation import MAX_REQUEST_SIZE

logger = structlog.get_logger(__name__)
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
  csp = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "font-src 'self'; "
    "frame-ancestors 'none'"
  )
  response.headers["Content-Security-Policy"] = csp
  response.headers["X-Content-Type-Options"] = "nosniff"
  response.headers["X-Frame-Options"] = "DENY"
  response.headers["Referrer-Policy"] = "no-referrer"
  response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
  return response


async def log_requests(request: Request, call_next):
  ip = get_client_ip(request)
  path = request.url.path
  log_ip = "redacted" if path in SENSITIVE_PATHS else ip
  log_path = "redacted" if path in SENSITIVE_PATHS else path
  bind_contextvars(method=request.method, path=log_path, client_ip=log_ip)
  start = time.time()
  try:
    response = await call_next(request)
  except Exception:
    duration = (time.time() - start) * 1000
    logger.exception("request error", duration_ms=duration)
    raise
  duration = (time.time() - start) * 1000
  logger.info(
    "request completed",
    status_code=response.status_code,
    duration_ms=duration,
  )
  return response
