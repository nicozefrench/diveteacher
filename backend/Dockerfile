FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
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

# Expose port
EXPOSE 8000

# Use custom entrypoint with warm-up
ENTRYPOINT ["/app/docker-entrypoint.sh"]

