# JobBot Business Intelligence Engine - Production Dockerfile
# Multi-stage build for optimized production deployment

# ========================================
# Stage 1: Base Python Environment
# ========================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# ========================================
# Stage 2: Dependencies Installation
# ========================================
FROM base as dependencies

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ========================================
# Stage 3: Application Build
# ========================================
FROM dependencies as application

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY pytest.ini .

# Copy additional configuration files
COPY start_server.py .
COPY scraper_config.json .

# Create necessary directories
RUN mkdir -p /app/logs /app/storage /app/scraped_data

# Set proper permissions
RUN chown -R appuser:appuser /app

# ========================================
# Stage 4: Production Image
# ========================================
FROM application as production

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ========================================
# Stage 5: Development Image
# ========================================
FROM application as development

# Install development dependencies
RUN pip install --no-cache-dir pytest-xdist coverage pre-commit

# Switch to non-root user
USER appuser

# Expose application port and debug port
EXPOSE 8000 5678

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ========================================
# Build Arguments and Labels
# ========================================
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=3.0.0

LABEL maintainer="Kaelen Jennings <endersclarity@gmail.com>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="JobBot Business Intelligence Engine" \
      org.label-schema.description="AI-powered business intelligence platform for market creation and automation opportunities" \
      org.label-schema.url="https://github.com/endersclarity/jobbot" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/endersclarity/jobbot" \
      org.label-schema.vendor="Kaelen Jennings" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"