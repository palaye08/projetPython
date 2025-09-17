# Use Python 3.9 slim image
FROM python:3.9-slim

# Set environment variables pour optimiser Python et pip
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies (ajout de plus de packages pour compilation)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first (for better Docker caching)
COPY requirements.txt .

# Install Python dependencies with error handling
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "❌ Error installing requirements. Content of requirements.txt:" && \
     cat requirements.txt && \
     echo "Available Python packages:" && \
     pip list && \
     exit 1)

# Copy the rest of the application
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Switch to non-root user
USER app

# Expose port (fix: use fixed port instead of variable)
EXPOSE 5000

# Use Gunicorn for production (fix: use PORT environment variable properly)
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 --access-logfile - --error-logfile - main:app