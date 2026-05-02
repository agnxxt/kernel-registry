FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    curl \
    gcc \
    libpq-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY persistence/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install -r /app/requirements.txt

COPY . /app

CMD ["uvicorn", "kernel_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
