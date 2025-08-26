import pytest

from backend.main import sanitize_string


@pytest.mark.parametrize(
  "payload,expected",
  [
    ("<script>alert('x')</script>", "alert('x')"),
    ("<img src=x onerror=alert(1)>", ""),
    ("javascript:alert(1)", "alert(1)"),
    ("data:text/html,<script>alert(1)</script>", "text/html,alert(1)"),
  ],
)
def test_sanitize_string(payload, expected):
  assert sanitize_string(payload) == expected
