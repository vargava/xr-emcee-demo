# Use Python 3.11 slim image for M1 compatibility
FROM --platform=linux/arm64 python:3.11-slim

# Install system dependencies for audio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    build-essential \
    gcc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["python", "api_server.py"]