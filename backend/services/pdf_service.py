import io
import zipfile
from fastapi import HTTPException

from ..utils.sanitization import sanitize_string
from .template_service import FIELD_MAP, get_template_file, verify_template_integrity


def generate_pdf(data: dict) -> io.BytesIO:
  from backend import main as main_module

  county = data.get("county", "General")
  template_file = get_template_file(county)
  if not template_file.exists():
    raise HTTPException(status_code=404, detail="Template not found")
  verify_template_integrity(template_file)

  reader = main_module.PdfReader(str(template_file))
  writer = main_module.PdfWriter()
  for page in reader.pages:
    writer.add_page(page)

  form_values: dict[str, str] = {}
  for key, field in FIELD_MAP.items():
    value = data.get(key)
    if value is not None:
      form_values[field] = sanitize_string(str(value))

  try:
    for page in writer.pages:
      writer.update_page_form_field_values(page, form_values)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
  except Exception as exc:
    raise HTTPException(status_code=500, detail="Failed to generate PDF") from exc
  pdf_bytes.seek(0)

  zip_bytes = io.BytesIO()
  with zipfile.ZipFile(zip_bytes, "w") as zf:
    zf.writestr("petition.pdf", pdf_bytes.getvalue())
  zip_bytes.seek(0)
  return zip_bytes
