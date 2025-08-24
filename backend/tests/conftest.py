import types
import sys

redis_stub = types.ModuleType("redis")
redis_asyncio_stub = types.ModuleType("redis.asyncio")


def from_url(*args, **kwargs):
  return None


redis_asyncio_stub.from_url = from_url
redis_stub.asyncio = redis_asyncio_stub
sys.modules["redis"] = redis_stub
sys.modules["redis.asyncio"] = redis_asyncio_stub
