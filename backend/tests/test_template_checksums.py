import os
import sys
import types
from pathlib import Path
import hashlib

# stub redis module for import side effects
redis_stub = types.ModuleType("redis")
redis_asyncio_stub = types.ModuleType("redis.asyncio")

def from_url(*args, **kwargs):
  return None

redis_asyncio_stub.from_url = from_url
redis_stub.asyncio = redis_asyncio_stub
sys.modules["redis"] = redis_stub
sys.modules["redis.asyncio"] = redis_asyncio_stub

os.environ["OPENAI_API_KEY"] = "test"

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.main import TEMPLATE_CHECKSUMS, FORMS_DIR


def test_template_checksums():
  for path in FORMS_DIR.glob("*.pdf"):
    with open(path, "rb") as f:
      actual = hashlib.sha256(f.read()).hexdigest()
    expected = TEMPLATE_CHECKSUMS.get(path.name)
    assert expected == actual, f"{path.name} checksum mismatch"
