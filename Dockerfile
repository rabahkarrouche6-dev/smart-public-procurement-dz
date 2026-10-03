# Dockerfile for Smart Public Procurement Platform (Algeria)
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package resolution
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy requirements and install
COPY pyproject.toml* requirements.txt* /app/
RUN pip install --no-cache-dir \
    django>=5.0 \
    djangorestframework \
    django-cors-headers \
    django-filter \
    drf-spectacular \
    python-dotenv \
    pydantic \
    psycopg[binary] \
    celery \
    redis \
    gunicorn

# Copy application source code
COPY . /app/

# Create unprivileged user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/schema/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--chdir", "/app/backend", "config.wsgi:application"]
