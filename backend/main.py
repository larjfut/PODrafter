import time
from PyPDF2 import PdfReader, PdfWriter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from .api import chat, pdf, health
from .middleware.rate_limit import (
  RateLimitMiddleware,
  redis_client,
  RedisRateLimiter,
  InMemoryRateLimiter,
  RateLimiterProtocol,
)
from .middleware.security import BodySizeLimitMiddleware, log_requests, set_security_headers
from .middleware.correlation import add_correlation_id
from .utils.sanitization import sanitize_string, CoverLetterContext
from .utils.validation import get_allowed_origins, reload_schema, MAX_REQUEST_SIZE
from .services.openai_client import validate_environment
from .services.template_service import TEMPLATE_CHECKSUMS, FORMS_DIR
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


RATE_LIMIT = 100
RATE_WINDOW = 60
FALLBACK_MAX_IPS = 1000
FALLBACK_IP_TTL = RATE_WINDOW * 5


def create_app(rate_limiter: RateLimiterProtocol) -> FastAPI:
  app = FastAPI()
  app.state.rate_limiter = rate_limiter
  app.add_middleware(RateLimitMiddleware)
  app.add_middleware(BodySizeLimitMiddleware)
  app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
  )
  app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["127.0.0.1"])
  app.middleware("http")(set_security_headers)
  app.middleware("http")(log_requests)
  app.middleware("http")(add_correlation_id)

  @app.on_event("startup")
  async def startup_event() -> None:
    reload_schema()
    await validate_environment()

  app.include_router(chat.router)
  app.include_router(pdf.router)
  app.include_router(health.router)

  @app.get("/metrics")
  async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
  return app


rate_limiter = RedisRateLimiter(
  redis_client, RATE_LIMIT, RATE_WINDOW, FALLBACK_IP_TTL, FALLBACK_MAX_IPS
)
app = create_app(rate_limiter)

