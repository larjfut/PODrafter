import asyncio
import pytest
from fastapi import HTTPException

from backend.worker import WorkerQueue


def test_excessive_enqueues_rejected():
  queue = WorkerQueue()
  queue._queue = asyncio.Queue(maxsize=1)
  queue._worker_started = True

  async def dummy():
    return None

  async def run():
    await queue.enqueue(dummy)
    with pytest.raises(HTTPException) as exc:
      await queue.enqueue(dummy)
    assert exc.value.status_code == 503

  asyncio.run(run())
