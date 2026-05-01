#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
UI_URL="${UI_URL:-http://localhost:3000}"
MLFLOW_URL="${MLFLOW_URL:-http://localhost:5000}"

check_endpoint() {
  local name="$1"
  local url="$2"
  local expected_code="${3:-200}"

  echo "[e2e] Checking ${name} at ${url}"
  local code
  local body_file
  body_file="$(mktemp)"
  code="$(curl -sS -o "$body_file" -w '%{http_code}' --max-time 10 "$url" || true)"

  if [[ "$code" != "$expected_code" ]]; then
    echo "[e2e] FAIL: ${name} expected HTTP ${expected_code}, got ${code}"
    echo "[e2e] Response preview:"
    head -c 500 "$body_file" || true
    rm -f "$body_file"
    return 1
  fi

  echo "[e2e] PASS: ${name} returned HTTP ${code}"
  rm -f "$body_file"
}

check_endpoint "Kernel API" "${API_URL}/docs" 200
check_endpoint "Kernel UI" "${UI_URL}" 200
check_endpoint "MLflow" "${MLFLOW_URL}" 200

echo "[e2e] All smoke checks passed."
