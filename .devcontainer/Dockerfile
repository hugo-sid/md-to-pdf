FROM python:3.12-slim-bullseye

# Install system deps (WeasyPrint etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user FIRST
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy with proper ownership
COPY --chown=appuser:appuser . .

# Install uv as root, then switch to appuser
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch to appuser BEFORE running uv
USER appuser

ENV PATH="/home/appuser/.local/bin:/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Now install dependencies
RUN uv sync

EXPOSE 5000

CMD ["bash"]