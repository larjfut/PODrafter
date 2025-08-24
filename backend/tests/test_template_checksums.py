import os
import sys
from pathlib import Path
import hashlib

os.environ["OPENAI_API_KEY"] = "test"

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.main import TEMPLATE_CHECKSUMS, FORMS_DIR


def test_template_checksums():
  for path in FORMS_DIR.glob("*.pdf"):
    with open(path, "rb") as f:
      actual = hashlib.sha256(f.read()).hexdigest()
    expected = TEMPLATE_CHECKSUMS.get(path.name)
    assert expected == actual, f"{path.name} checksum mismatch"
