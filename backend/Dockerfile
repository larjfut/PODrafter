# Use an official Python image
FROM python:3.11-slim

# Improve Python behavior in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app/backend
EXPOSE 8080

# Create non-root user and group
RUN groupadd -g 10001 appgrp && useradd -u 10001 -g appgrp -m appuser

# Install dependencies using root requirements file
COPY --chown=appuser:appgrp requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code and required assets
COPY --chown=appuser:appgrp backend/ /app/backend
COPY --chown=appuser:appgrp forms /app/forms
COPY --chown=appuser:appgrp schema /app/schema

# Drop privileges
USER 10001:10001

# Launch the app with Uvicorn on port 8080
CMD ["uvicorn", "backend.main:app", "--host=0.0.0.0", "--port=8080"]
