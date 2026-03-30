FROM python:3.12-slim-bullseye

# Install system deps (WeasyPrint etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    fonts-liberation \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally (as root, so it's in /root/.local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Make uv available system-wide by symlinking it
RUN ln -s /root/.local/bin/uv /usr/local/bin/uv && \
    ln -s /root/.local/bin/uvx /usr/local/bin/uvx

# Create non-root user AFTER uv is installed globally
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy with proper ownership
COPY --chown=appuser:appuser . .

# Switch to appuser
USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Now install dependencies as appuser - uv is available via symlink
RUN uv sync

EXPOSE 5000

CMD ["bash"]