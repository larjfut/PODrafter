import asyncio
import os
import time
from collections import OrderedDict
from functools import wraps
from typing import Dict, Protocol, Tuple

import redis.asyncio as redis
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from .auth import get_client_ip

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class RateLimiterProtocol(Protocol):
  async def record_request(self, ip: str, now: float) -> Tuple[bool, str, int]:
    ...

  async def clear(self) -> None:
    ...


class InMemoryRateLimiter:
  def __init__(
    self,
    rate_limit: int,
    rate_window: int,
    fallback_ip_ttl: int,
    fallback_max_ips: int,
  ) -> None:
    self.rate_limit = rate_limit
    self.rate_window = rate_window
    self.fallback_ip_ttl = fallback_ip_ttl
    self.fallback_max_ips = fallback_max_ips
    self._store: OrderedDict[str, Dict[str, float]] = OrderedDict()
    self._lock = asyncio.Lock()

  async def record_request(self, ip: str, now: float) -> Tuple[bool, str, int]:
    async with self._lock:
      allowed, remaining = self._record_request_unsafe(ip, now)
    return allowed, "memory", remaining

  async def clear(self) -> None:
    async with self._lock:
      self._store.clear()

  def _record_request_unsafe(self, ip: str, now: float) -> Tuple[bool, int]:
    window_start = now - self.rate_window
    for ip_key, times in list(self._store.items()):
      for ts_key, ts in list(times.items()):
        if ts < window_start:
          del times[ts_key]
      last_seen = max(times.values()) if times else 0
      if not times or last_seen < now - self.fallback_ip_ttl:
        self._store.pop(ip_key, None)

    timestamps = self._store.setdefault(ip, {})
    if len(timestamps) >= self.rate_limit:
      return False, 0
    timestamps[str(now)] = now
    self._store.move_to_end(ip)
    while len(self._store) > self.fallback_max_ips:
      self._store.popitem(last=False)
    remaining = self.rate_limit - len(timestamps)
    return True, remaining


class RedisRateLimiter:
  def __init__(
    self,
    redis_cli,
    rate_limit: int,
    rate_window: int,
    fallback_ip_ttl: int,
    fallback_max_ips: int,
  ) -> None:
    self.redis_cli = redis_cli
    self.rate_limit = rate_limit
    self.rate_window = rate_window
    self.fallback_ip_ttl = fallback_ip_ttl
    self.fallback_max_ips = fallback_max_ips
    self.fallback_limiter = InMemoryRateLimiter(
      rate_limit, rate_window, fallback_ip_ttl, fallback_max_ips
    )
    self.fallback_active = False

  async def record_request(self, ip: str, now: float) -> Tuple[bool, str, int]:
    if self.fallback_active:
      try:
        await self.redis_cli.ping()
        self.fallback_active = False
        await self.fallback_limiter.clear()
      except Exception:
        pass

    if not self.fallback_active:
      try:
        key = f"ratelimit:{ip}"
        await self.redis_cli.zremrangebyscore(key, 0, now - self.rate_window)
        count = await self.redis_cli.zcard(key)
        if count >= self.rate_limit:
          return False, "redis", 0
        await self.redis_cli.zadd(key, {str(now): now})
        await self.redis_cli.expire(key, self.rate_window)
        remaining = self.rate_limit - (count + 1)
        return True, "redis", remaining
      except Exception:
        self.fallback_active = True
        await self.fallback_limiter.clear()

    allowed, _, remaining = await self.fallback_limiter.record_request(ip, now)
    return allowed, "memory", remaining

  async def clear(self) -> None:
    self.fallback_active = False
    await self.fallback_limiter.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    rate_limiter = request.app.state.rate_limiter
    ip = get_client_ip(request)
    now = time.time()
    allowed, store, remaining = await rate_limiter.record_request(ip, now)
    if not allowed:
      return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    response = await call_next(request)
    response.headers["X-RateLimit-Store"] = store
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response


def rate_limit(limit: int, window: int, key: str | None = None):
  limiter = RedisRateLimiter(redis_client, limit, window, window * 5, 1000)

  def decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
      request: Request = kwargs.get("request")
      if request is None:
        for arg in args:
          if isinstance(arg, Request):
            request = arg
            break
      if request is None:
        raise RuntimeError("Request object required for rate limiting")
      ip = get_client_ip(request)
      route_key = key or request.url.path
      composite = f"{route_key}:{ip}"
      allowed, store, remaining = await limiter.record_request(composite, time.time())
      if not allowed:
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})
      response = await func(*args, **kwargs)
      response.headers["X-RateLimit-Store"] = store
      response.headers["X-Route-RateLimit-Remaining"] = str(remaining)
      return response

    return wrapper

  return decorator
