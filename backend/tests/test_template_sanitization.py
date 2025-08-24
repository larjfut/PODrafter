import pytest
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from backend.main import CoverLetterContext

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)
env.filters["date"] = lambda value, fmt: value.strftime(fmt)


@pytest.mark.parametrize(
  "template,context",
  [
    (
      "cover_letter.html",
      {
        "county": "Test",
        "today": datetime(2024, 1, 1),
        "petitioner_full_name": "Jane",
        "respondent_full_name": "John",
      },
    ),
    (
      "filing_guide.html",
      {"county": "Test", "petitioner_address": "123 Main"},
    ),
  ],
)
def test_county_clerk_address_escaped(template, context):
  malicious = "<script>alert(1)</script>\n123 Main"
  context["county_clerk_address"] = malicious
  rendered = env.get_template(template).render(**context)
  assert "<script>" not in rendered
  assert "&lt;script&gt;alert(1)&lt;/script&gt;<br>123 Main" in rendered


def test_resume_qr_url_rejects_javascript():
  model = CoverLetterContext(resume_qr_url="javascript:alert(1)")
  context = {
    "county": "Test",
    "today": datetime(2024, 1, 1),
    "petitioner_full_name": "Jane",
    "respondent_full_name": "John",
    "resume_qr_url": model.resume_qr_url,
  }
  rendered = env.get_template("cover_letter.html").render(**context)
  assert "javascript:" not in rendered
  assert "<img" not in rendered


def test_resume_qr_url_allows_http():
  model = CoverLetterContext(resume_qr_url="https://example.com/qr.png")
  context = {
    "county": "Test",
    "today": datetime(2024, 1, 1),
    "petitioner_full_name": "Jane",
    "respondent_full_name": "John",
    "resume_qr_url": model.resume_qr_url,
  }
  rendered = env.get_template("cover_letter.html").render(**context)
  assert 'src="https://example.com/qr.png"' in rendered

