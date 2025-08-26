import logging
import os

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

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
    msg = f"OpenAI connectivity check failed: {exc}"
    logger.error(msg)
    raise RuntimeError(msg) from exc
