"""FastAPI application for PO Drafter.

This module defines a simple API with a health check and a PDF generation
endpoint. The PDF generation endpoint is currently a placeholder and
should be implemented to merge user data into AcroForm templates and
return a ZIP file containing the completed documents.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


app = FastAPI()

# Configure CORS to allow frontend requests. In production you may want
# to restrict origins and methods for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint.

    Returns a JSON object indicating the status of the service.

    :return: dict containing service status
    """
    return {"status": "ok"}


@app.post("/pdf")
async def generate_pdf(data: dict) -> JSONResponse:
    """Generate PDF packet from petition data.

    This endpoint accepts a JSON body representing petition data and
    returns a placeholder response. In a future iteration it should
    populate Acrobat form fields in the appropriate PDF template and
    return a ZIP archive containing the petition, addendum and any
    accompanying documents.

    :param data: dictionary containing petition information
    :raises HTTPException: if data validation fails
    :return: JSONResponse acknowledging receipt of data
    """
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid request body")

    # Placeholder implementation. In v0.2 this will use the schema to
    # validate input and fill out PDF forms using pdfrw or PyPDF2.
    return JSONResponse(content={"message": "PDF generation not yet implemented", "received": data})