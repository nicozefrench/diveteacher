FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (UPGRADED for Docling 2.60 + OpenCV)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --force-reinstall tqdm==4.66.0

# Copy application code (includes app/warmup.py)
COPY app/ ./app/

# Copy entrypoint
COPY docker-entrypoint.sh ./

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh

# Create uploads directory
RUN mkdir -p /uploads

# ✨ NOTE: Build-time Docling warm-up temporarily disabled
# The runtime warm-up (docker-entrypoint.sh) works well and models are cached after first use.
# TODO Phase 3: Add reportlab to requirements.txt and re-enable build-time warm-up for optimal cold-start

# Expose port
EXPOSE 8000

# Use custom entrypoint with warm-up
ENTRYPOINT ["/app/docker-entrypoint.sh"]
