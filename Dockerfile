FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies if any are needed (like curl for uvicorn etc, but keeping it minimal)
RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*

COPY persistence/requirements.txt /app/persistence/requirements.txt
RUN pip install --no-cache-dir -r /app/persistence/requirements.txt uvicorn fastapi pydantic

COPY . /app

# Start the API server using Uvicorn
CMD ["uvicorn", "kernel_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
