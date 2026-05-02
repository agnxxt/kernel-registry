FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip (important for newer packages)
RUN pip install --upgrade pip

# Copy and install dependencies
COPY persistence/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire kernel
COPY . /app

# Start API server
CMD ["uvicorn", "kernel_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
