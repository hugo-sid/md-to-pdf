# ── STAGE 1: dependency builder ──────────────────────────────────────────────
FROM python:3.12-slim-bullseye AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy only dep files first (layer cache — only re-runs if these change)
COPY pyproject.toml uv.lock ./

# Install deps into /app/.venv, no project itself yet
RUN uv sync --frozen --no-install-project --no-dev

# ── STAGE 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim-bullseye AS runtime

# WeasyPrint needs these system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy venv from builder (no uv, no build tools in final image)
COPY --from=builder /app/.venv /app/.venv

# Copy app files
COPY app.py index.html ./

# Uploads dir — will be overridden by volume mount on EC2
RUN mkdir -p uploads && chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000

# Gunicorn in production, not Flask dev server
CMD ["gunicorn", \
     "--workers", "2", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
