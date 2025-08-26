import time
from PyPDF2 import PdfReader, PdfWriter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from .api import chat, pdf, health
from .middleware.rate_limit import (
  RateLimitMiddleware,
  redis_client,
  fallback_store,
  fallback_active,
  fallback_limiter,
)
from .middleware.security import BodySizeLimitMiddleware, log_requests, set_security_headers
from .utils.sanitization import sanitize_string, CoverLetterContext
from .utils.validation import get_allowed_origins, reload_schema, MAX_REQUEST_SIZE
from .services.openai_client import validate_environment
from .services.template_service import TEMPLATE_CHECKSUMS, FORMS_DIR

RATE_LIMIT = 100
RATE_WINDOW = 60
FALLBACK_MAX_IPS = 1000
FALLBACK_IP_TTL = RATE_WINDOW * 5

app = FastAPI()
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


@app.on_event("startup")
async def startup_event() -> None:
  reload_schema()
  await validate_environment()


app.include_router(chat.router)
app.include_router(pdf.router)
app.include_router(health.router)
