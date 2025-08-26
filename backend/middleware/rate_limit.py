import asyncio
import os
import time
from collections import OrderedDict

import redis.asyncio as redis
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from .auth import get_client_ip

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

fallback_store: OrderedDict[str, dict[str, float]] = OrderedDict()
fallback_active = False
fallback_lock = asyncio.Lock()


def record_fallback_request(ip: str, now: float, rate_limit: int, rate_window: int,
                            fallback_ip_ttl: int, fallback_max_ips: int) -> bool:
  window_start = now - rate_window
  for ip_key, times in list(fallback_store.items()):
    for ts_key, ts in list(times.items()):
      if ts < window_start:
        del times[ts_key]
    last_seen = max(times.values()) if times else 0
    if not times or last_seen < now - fallback_ip_ttl:
      fallback_store.pop(ip_key, None)

  timestamps = fallback_store.setdefault(ip, {})
  if len(timestamps) >= rate_limit:
    return False
  timestamps[str(now)] = now
  fallback_store.move_to_end(ip)
  while len(fallback_store) > fallback_max_ips:
    fallback_store.popitem(last=False)
  return True


class RateLimitMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    from backend import main as main_module

    rate_limit = main_module.RATE_LIMIT
    rate_window = main_module.RATE_WINDOW
    fallback_ip_ttl = main_module.FALLBACK_IP_TTL
    redis_cli = main_module.redis_client
    fallback_max_ips = main_module.FALLBACK_MAX_IPS

    ip = get_client_ip(request)
    now = time.time()
    key = f"ratelimit:{ip}"
    global fallback_store, fallback_active

    if fallback_active:
      try:
        await redis_cli.ping()
        fallback_active = False
        main_module.fallback_active = False
        async with fallback_lock:
          fallback_store.clear()
      except Exception:
        pass

    if not fallback_active:
      try:
        await redis_cli.zremrangebyscore(key, 0, now - rate_window)
        count = await redis_cli.zcard(key)
        if count >= rate_limit:
          return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        await redis_cli.zadd(key, {str(now): now})
        await redis_cli.expire(key, rate_window)
        response = await call_next(request)
        response.headers["X-RateLimit-Store"] = "redis"
        return response
      except Exception:
        fallback_active = True
        main_module.fallback_active = True
        async with fallback_lock:
          fallback_store.clear()

    async with fallback_lock:
      allowed = record_fallback_request(ip, now, rate_limit, rate_window,
                                        fallback_ip_ttl, fallback_max_ips)
    main_module.fallback_active = fallback_active
    if not allowed:
      return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    response = await call_next(request)
    response.headers["X-RateLimit-Store"] = "memory"
    return response
