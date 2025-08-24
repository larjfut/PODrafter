import pytest
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

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

