import os
import asyncio
import httpx
import pytest
import redis.asyncio as redis_asyncio

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

import backend.main as main

@pytest.fixture(autouse=True)
def _setup(monkeypatch):
  monkeypatch.setattr(main, 'redis_client', DummyRedis())
  main.fallback_store.clear()
  main.fallback_active = False

class TimeStub:
  def __init__(self):
    self.now = 0

  def time(self):
    return self.now


def test_ttl_eviction(monkeypatch):
  async def _run():
    monkeypatch.setattr(main, 'FALLBACK_IP_TTL', 2)
    monkeypatch.setattr(main, 'FALLBACK_MAX_IPS', 100)
    ts = TimeStub()
    monkeypatch.setattr(main.time, 'time', ts.time)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('1.1.1.1', 0)), base_url='http://testserver') as client:
      resp = await client.get('/health')
    assert resp.status_code == 200
    assert '1.1.1.1' in main.fallback_store

    ts.now += 3
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('2.2.2.2', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert '1.1.1.1' not in main.fallback_store
    assert '2.2.2.2' in main.fallback_store

  asyncio.run(_run())


def test_store_size_pruning(monkeypatch):
  async def _run():
    monkeypatch.setattr(main, 'FALLBACK_IP_TTL', 100)
    monkeypatch.setattr(main, 'FALLBACK_MAX_IPS', 2)
    ts = TimeStub()
    monkeypatch.setattr(main.time, 'time', ts.time)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('1.1.1.1', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert len(main.fallback_store) == 1

    ts.now += 1
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('2.2.2.2', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert len(main.fallback_store) == 2

    ts.now += 1
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('3.3.3.3', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert len(main.fallback_store) == 2
    assert '1.1.1.1' not in main.fallback_store

  asyncio.run(_run())


def test_rate_limit_with_trusted_proxy(monkeypatch):
  async def _run():
    monkeypatch.setattr(main, 'RATE_LIMIT', 1)
    headers = {'x-forwarded-for': '5.5.5.5'}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('127.0.0.1', 0)), base_url='http://testserver') as client:
      resp1 = await client.get('/health', headers=headers)
      resp2 = await client.get('/health', headers=headers)
    assert resp1.status_code == 200
    assert resp2.status_code == 429

  asyncio.run(_run())


def test_spoofed_forwarded_for_ignored(monkeypatch):
  async def _run():
    monkeypatch.setattr(main, 'RATE_LIMIT', 1)
    headers1 = {'x-forwarded-for': '5.5.5.5'}
    headers2 = {'x-forwarded-for': '6.6.6.6'}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('1.1.1.1', 0)), base_url='http://testserver') as client:
      resp1 = await client.get('/health', headers=headers1)
      resp2 = await client.get('/health', headers=headers2)
    assert resp1.status_code == 200
    assert resp2.status_code == 429

  asyncio.run(_run())


def test_timestamp_cleanup(monkeypatch):
  async def _run():
    monkeypatch.setattr(main, 'FALLBACK_IP_TTL', 100)
    monkeypatch.setattr(main, 'RATE_WINDOW', 2)
    monkeypatch.setattr(main, 'RATE_LIMIT', 10)
    ts = TimeStub()
    monkeypatch.setattr(main.time, 'time', ts.time)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('1.1.1.1', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert len(main.fallback_store['1.1.1.1']) == 1

    ts.now += 1
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('1.1.1.1', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert len(main.fallback_store['1.1.1.1']) == 2

    ts.now += 3
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('1.1.1.1', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert len(main.fallback_store['1.1.1.1']) == 1

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
    monkeypatch.setattr(main, 'redis_client', redis)
    ts = TimeStub()
    monkeypatch.setattr(main.time, 'time', ts.time)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('1.1.1.1', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert main.fallback_active is True
    assert '1.1.1.1' in main.fallback_store

    redis.fail = False
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app, client=('2.2.2.2', 0)), base_url='http://testserver') as client:
      await client.get('/health')
    assert main.fallback_active is False
    assert main.fallback_store == {}

  asyncio.run(_run())


def test_concurrent_requests_enforce_limit(monkeypatch):
  async def _run():
    monkeypatch.setattr(main, 'RATE_LIMIT', 5)
    main.fallback_active = True
    async with httpx.AsyncClient(
      transport=httpx.ASGITransport(app=main.app, client=('1.1.1.1', 0)),
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
