import os
import hashlib

os.environ["OPENAI_API_KEY"] = "test"

from backend.main import TEMPLATE_CHECKSUMS, FORMS_DIR


def test_template_checksums():
  expected: dict[str, str] = {}
  for path in FORMS_DIR.glob("*.pdf"):
    with open(path, "rb") as f:
      expected[path.name] = hashlib.sha256(f.read()).hexdigest()
  assert TEMPLATE_CHECKSUMS == expected
