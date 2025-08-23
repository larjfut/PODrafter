# Use an official Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app
EXPOSE 8080

# Install dependencies using root requirements file
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ /app

# Launch the app with Uvicorn on port 8080
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8080"]
