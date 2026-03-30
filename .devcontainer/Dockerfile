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

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

WORKDIR /app

# Copy with proper ownership (including .node-version)
COPY --chown=appuser:appuser . .

# Switch to appuser
USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install nvm (Node Version Manager)
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Setup nvm and install Node version from .node-version
ENV NVM_DIR=/home/appuser/.nvm
ENV PATH=$NVM_DIR/versions/node/v24.14.1/bin:$NVM_DIR/bin:$PATH

RUN . $NVM_DIR/nvm.sh && \
    NODE_VERSION=$(cat .node-version) && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION

# Install npm dependencies
RUN . $NVM_DIR/nvm.sh && npm install

# Install Python dependencies
RUN uv sync

EXPOSE 5000

CMD ["sleep", "infinity"]