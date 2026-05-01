FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends bash build-essential && rm -rf /var/lib/apt/lists/*

COPY persistence/requirements.txt /app/persistence/requirements.txt
RUN pip install --no-cache-dir -r /app/persistence/requirements.txt

COPY . /app

# Default command (overridden in compose for consensus)
CMD ["uvicorn", "kernel_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
