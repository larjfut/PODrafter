"""FastAPI application for PO Drafter.

This module provides endpoints for health checks and PDF packet generation.
Incoming petition data is validated against a JSON Schema and merged into
AcroForm templates before being returned as a ZIP file.
"""

from __future__ import annotations

import io
import json
import os
import zipfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from jsonschema import ValidationError, validate
from PyPDF2 import PdfReader, PdfWriter

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "schema" / "petition.schema.json"
FORMS_DIR = BASE_DIR / "forms" / "standard"

with open(SCHEMA_PATH) as f:
    PETITION_SCHEMA = json.load(f)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post("/pdf")
async def generate_pdf(data: dict) -> StreamingResponse:
    """Generate PDF packet from petition data."""
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid request body")

    try:
        validate(instance=data, schema=PETITION_SCHEMA)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    county = data.get("county", "General")
    template_map = {
        "Harris": "harris.pdf",
        "Dallas": "dallas.pdf",
        "Travis": "travis.pdf",
        "General": "tx_general.pdf",
    }
    template_file = FORMS_DIR / template_map.get(county, "tx_general.pdf")

    reader = PdfReader(str(template_file))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as zf:
        zf.writestr("petition.pdf", pdf_bytes.getvalue())
    zip_bytes.seek(0)

    return StreamingResponse(
        zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=po_packet.zip"},
    )
