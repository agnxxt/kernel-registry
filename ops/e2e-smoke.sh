#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
UI_URL="${UI_URL:-http://localhost:3000}"
MLFLOW_URL="${MLFLOW_URL:-http://localhost:5000}"

check_endpoint() {
  local name="$1"
  local url="$2"
  local expected_code="${3:-200}"
  local max_attempts="${4:-3}"
  local retry_delay="${5:-2}"

  echo "[e2e] Checking ${name} at ${url}"
  local code
  local body_file
  body_file="$(mktemp)"

  for ((attempt=1; attempt<=max_attempts; attempt++)); do
    code="$(curl -sS -o "$body_file" -w '%{http_code}' --max-time 10 "$url" || true)"
    
    if [[ "$code" == "$expected_code" ]]; then
      echo "[e2e] PASS: ${name} returned HTTP ${code}"
      rm -f "$body_file"
      return 0
    fi
    
    if [[ $attempt -lt $max_attempts ]]; then
      echo "[e2e] Attempt $attempt/$max_attempts failed for ${name}: expected HTTP ${expected_code}, got ${code}. Retrying in ${retry_delay}s..."
      sleep "$retry_delay"
    fi
  done

  echo "[e2e] FAIL: ${name} expected HTTP ${expected_code}, got ${code} after ${max_attempts} attempts"
  echo "[e2e] Response preview:"
  head -c 500 "$body_file" || true
  rm -f "$body_file"
  return 1
}

check_endpoint "Kernel API" "${API_URL}/docs" 200
check_endpoint "Kernel UI" "${UI_URL}" 200
check_endpoint "MLflow" "${MLFLOW_URL}" 200

echo "[e2e] All smoke checks passed."
