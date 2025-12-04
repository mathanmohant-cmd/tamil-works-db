# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy all backend files from current directory
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Start command
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
