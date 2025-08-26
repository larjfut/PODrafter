import logging
import sys

import structlog


def configure_logging() -> None:
  timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
  structlog.configure(
    processors=[
      structlog.contextvars.merge_contextvars,
      structlog.processors.add_log_level,
      timestamper,
      structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
  )
  logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
