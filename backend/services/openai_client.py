import os

import structlog
from openai import AsyncOpenAI

logger = structlog.get_logger(__name__)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


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
    logger.error("OpenAI connectivity check failed", error=str(exc))
    raise RuntimeError(f"OpenAI connectivity check failed: {exc}") from exc
