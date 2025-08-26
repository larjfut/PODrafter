import os
import asyncio
import httpx
import pytest
import redis.asyncio as redis_asyncio

from backend.main import create_app
from backend.middleware.rate_limit import InMemoryRateLimiter, RedisRateLimiter


class DummyRedis:
  async def zremrangebyscore(self, *args, **kwargs):
    raise RuntimeError('down')

  async def zcard(self, *args, **kwargs):
    raise RuntimeError('down')

  async def zadd(self, *args, **kwargs):
    raise RuntimeError('down')

  async def expire(self, *args, **kwargs):
    raise RuntimeError('down')

  async def ping(self, *args, **kwargs):
    raise RuntimeError('down')


def from_url(*args, **kwargs):
  return DummyRedis()


redis_asyncio.from_url = from_url

os.environ['OPENAI_API_KEY'] = 'test'


class TimeStub:
  def __init__(self):
    self.now = 0

  def time(self):
    return self.now


def test_ttl_eviction(monkeypatch):
  async def _run():
    limiter = InMemoryRateLimiter(100, 60, 2, 100)
    app = create_app(limiter)
    ts = TimeStub()
    monkeypatch.setattr('backend.middleware.rate_limit.time.time', ts.time)

    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      resp = await client.get('/health')
    assert resp.status_code == 200
    assert '1.1.1.1' in limiter._store

    ts.now += 3
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('2.2.2.2', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')
    assert '1.1.1.1' not in limiter._store
    assert '2.2.2.2' in limiter._store

  asyncio.run(_run())


def test_lru_eviction(monkeypatch):
  async def _run():
    limiter = InMemoryRateLimiter(100, 60, 100, 2)
    app = create_app(limiter)
    ts = TimeStub()
    monkeypatch.setattr('backend.middleware.rate_limit.time.time', ts.time)

    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')

    ts.now += 1
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('2.2.2.2', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')

    ts.now += 1
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')

    ts.now += 1
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('3.3.3.3', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')

    assert len(limiter._store) == 2
    assert '1.1.1.1' in limiter._store
    assert '2.2.2.2' not in limiter._store
    assert '3.3.3.3' in limiter._store

  asyncio.run(_run())


def test_rate_limit_with_trusted_proxy():
  async def _run():
    limiter = InMemoryRateLimiter(1, 60, 300, 1000)
    app = create_app(limiter)
    headers = {'x-forwarded-for': '5.5.5.5'}
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('127.0.0.1', 0)),
      base_url='http://testserver'
    ) as client:
      resp1 = await client.get('/health', headers=headers)
      resp2 = await client.get('/health', headers=headers)
    assert resp1.status_code == 200
    assert resp2.status_code == 429

  asyncio.run(_run())


def test_spoofed_forwarded_for_ignored():
  async def _run():
    limiter = InMemoryRateLimiter(1, 60, 300, 1000)
    app = create_app(limiter)
    headers1 = {'x-forwarded-for': '5.5.5.5'}
    headers2 = {'x-forwarded-for': '6.6.6.6'}
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      resp1 = await client.get('/health', headers=headers1)
      resp2 = await client.get('/health', headers=headers2)
    assert resp1.status_code == 200
    assert resp2.status_code == 429

  asyncio.run(_run())


def test_timestamp_cleanup(monkeypatch):
  async def _run():
    limiter = InMemoryRateLimiter(10, 2, 100, 100)
    app = create_app(limiter)
    ts = TimeStub()
    monkeypatch.setattr('backend.middleware.rate_limit.time.time', ts.time)

    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')
    assert len(limiter._store['1.1.1.1']) == 1

    ts.now += 1
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')
    assert len(limiter._store['1.1.1.1']) == 2

    ts.now += 3
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')
    assert len(limiter._store['1.1.1.1']) == 1

  asyncio.run(_run())


class FlakyRedis:
  def __init__(self):
    self.fail = True

  async def zremrangebyscore(self, *args, **kwargs):
    if self.fail:
      raise RuntimeError('down')
    return 0

  async def zcard(self, *args, **kwargs):
    if self.fail:
      raise RuntimeError('down')
    return 0

  async def zadd(self, *args, **kwargs):
    if self.fail:
      raise RuntimeError('down')
    return 0

  async def expire(self, *args, **kwargs):
    if self.fail:
      raise RuntimeError('down')
    return True

  async def ping(self, *args, **kwargs):
    if self.fail:
      raise RuntimeError('down')
    return True


def test_fallback_store_cleared_on_recovery(monkeypatch):
  async def _run():
    redis = FlakyRedis()
    limiter = RedisRateLimiter(redis, 100, 60, 300, 100)
    app = create_app(limiter)
    ts = TimeStub()
    monkeypatch.setattr('backend.middleware.rate_limit.time.time', ts.time)

    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')
    assert limiter.fallback_active is True
    assert '1.1.1.1' in limiter.fallback_limiter._store

    redis.fail = False
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('2.2.2.2', 0)),
      base_url='http://testserver'
    ) as client:
      await client.get('/health')
    assert limiter.fallback_active is False
    assert limiter.fallback_limiter._store == {}

  asyncio.run(_run())


def test_concurrent_requests_enforce_limit():
  async def _run():
    limiter = InMemoryRateLimiter(5, 60, 300, 100)
    app = create_app(limiter)
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=app, client=('1.1.1.1', 0)),
      base_url='http://testserver'
    ) as client:
      async def hit():
        return await client.get('/health')
      tasks = [asyncio.create_task(hit()) for _ in range(6)]
      results = await asyncio.gather(*tasks)
    statuses = [r.status_code for r in results]
    assert statuses.count(200) == 5
    assert statuses.count(429) == 1

  asyncio.run(_run())

