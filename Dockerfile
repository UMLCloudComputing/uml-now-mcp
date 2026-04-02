# Use a lightweight Python image
FROM ghcr.io/astral-sh/uv:debian-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some vector math libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY pyproject.toml .
RUN uv sync

# Copy the umlnow code
ADD umlnow/ ./umlnow

# Install Playwright browser and OS-level system dependencies
# Must run as root to install system libraries
RUN uv run playwright install  --with-deps --only-shell chromium

# Copy the server code
COPY server.py .

# Set broadcast address to all since this is runnning within a container
ENV BROADCAST_ADDRESS="0.0.0.0"

# Expose the port for K8s service routing
EXPOSE 8000

# Run the server using Uvicorn
# 0.0.0.0 is mandatory for K8s pod networking
CMD ["uv", "run", "server.py"]
