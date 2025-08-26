import asyncio
from typing import Any, Awaitable, Callable

class WorkerQueue:
  def __init__(self) -> None:
    self._queue: asyncio.Queue[tuple[Callable[..., Awaitable[Any]], tuple, dict, asyncio.Future]] = asyncio.Queue()
    self._worker_started = False

  async def _start_worker(self) -> None:
    if not self._worker_started:
      asyncio.create_task(self._worker())
      self._worker_started = True

  async def _worker(self) -> None:
    while True:
      func, args, kwargs, future = await self._queue.get()
      try:
        result = await func(*args, **kwargs)
        future.set_result(result)
      except Exception as exc:
        future.set_exception(exc)
      self._queue.task_done()

  async def enqueue(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> asyncio.Future:
    await self._start_worker()
    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()
    await self._queue.put((func, args, kwargs, future))
    return future

queue = WorkerQueue()
