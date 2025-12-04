# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY webapp/backend/ ./webapp/backend/

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Start command
CMD cd webapp/backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
