FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY persistence/requirements.txt /app/persistence/requirements.txt
RUN pip install --no-cache-dir -r /app/persistence/requirements.txt

COPY . /app

# Default command: validate contracts and print migration status.
CMD ["bash", "-lc", "./scripts/validate_schemas.sh && ./scripts/validate_proto.sh && alembic -c persistence/alembic.ini current || true"]
