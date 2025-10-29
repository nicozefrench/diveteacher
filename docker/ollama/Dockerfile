# Custom Ollama image with curl for proper healthcheck
# Based on: ollama/ollama:latest
# Purpose: Enable functional Docker healthcheck monitoring

FROM ollama/ollama:latest

# Install curl for healthcheck
# Using apt-get instead of apk because Ollama base is Debian-based
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Verify curl installation
RUN curl --version

# No need to change ENTRYPOINT or CMD - inherit from base image
# The base image already sets up Ollama properly

LABEL maintainer="DiveTeacher"
LABEL description="Ollama with curl for healthcheck support"
LABEL version="1.0"

