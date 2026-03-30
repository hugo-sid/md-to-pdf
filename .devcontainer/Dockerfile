FROM python:3.12-slim-bullseye

# Install system deps (WeasyPrint etc.) + git
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    fonts-liberation \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx

# Install fnm (Fast Node Manager) to manage Node versions
RUN curl -fsSL https://fnm.io/install | bash -s -- --install-dir /usr/local/bin && \
    chmod +x /usr/local/bin/fnm

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

WORKDIR /app

# Copy with proper ownership
COPY --chown=appuser:appuser . .

# Switch to appuser
USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/share/fnm:$PATH"

# Read .node-version and install that Node version
RUN if [ -f .node-version ]; then \
      NODE_VERSION=$(cat .node-version) && \
      fnm install $NODE_VERSION && \
      fnm use $NODE_VERSION; \
    fi

# Now install Python dependencies
RUN uv sync

# Install npm dependencies
RUN npm install

EXPOSE 5000

CMD ["sleep", "infinity"]