import uuid
from contextvars import ContextVar
from fastapi import Request
from typing import Callable
from starlette.responses import Response
from structlog.contextvars import bind_contextvars, clear_contextvars

request_id: ContextVar[str] = ContextVar("request_id")

async def add_correlation_id(request: Request, call_next: Callable) -> Response:
  correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
  request_id.set(correlation_id)
  bind_contextvars(correlation_id=correlation_id)
  try:
    response: Response = await call_next(request)
  finally:
    clear_contextvars()
  response.headers["X-Correlation-ID"] = correlation_id
  return response
