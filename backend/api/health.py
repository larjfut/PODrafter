import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..middleware.rate_limit import redis_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
  return {"status": "ok"}


@router.get("/redis/health")
async def redis_health():
  try:
    await redis_client.ping()
    return {"status": "ok"}
  except Exception as exc:
    logger.warning("Redis health check failed: %s", exc)
    return JSONResponse(status_code=503, content={"status": "unavailable", "detail": "Redis unavailable"})
