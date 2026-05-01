#!/usr/bin/env bash
set -euo pipefail

MODE="local"
VALIDATE_ONLY=0
SKIP_MIGRATIONS=0
SKIP_SMOKE=0

usage() {
  cat <<'USAGE'
Agent Kernel guided walkthrough (single command)

Usage:
  ./ops/guided-walkthrough.sh [options]

Options:
  --mode local|k8s      Execution target.
                        local = Docker Compose lifecycle + validations.
                        k8s   = kubectl apply flow for production manifests.
                        Default: local

  --validate-only       Run contract checks only (schemas + proto), skip deploy/start.

  --skip-migrations     Skip Alembic migration upgrade step.

  --skip-smoke          Skip E2E smoke test.

  -h, --help            Show this help.

What this script does:
  1) Explains each step before running it.
  2) Executes the baseline commands for the selected mode.
  3) Keeps the whole flow reproducible via one command.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --validate-only)
      VALIDATE_ONLY=1
      shift
      ;;
    --skip-migrations)
      SKIP_MIGRATIONS=1
      shift
      ;;
    --skip-smoke)
      SKIP_SMOKE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ "$MODE" != "local" && "$MODE" != "k8s" ]]; then
  echo "Invalid --mode '$MODE'. Allowed: local, k8s"
  exit 1
fi

echo "[Step 1] Contract validation: ensure JSON Schemas and Protobuf contracts are syntactically valid."
./scripts/validate_schemas.sh
./scripts/validate_proto.sh

if [[ $VALIDATE_ONLY -eq 1 ]]; then
  echo "--validate-only enabled: stopping after contract checks."
  exit 0
fi

if [[ "$MODE" == "local" ]]; then
  echo "[Step 2] Start local runtime stack with Docker Compose (API/UI/MLflow/tooling)."
  docker compose up --build -d

  if [[ $SKIP_MIGRATIONS -eq 0 ]]; then
    echo "[Step 3] Apply database migrations to align persistence schema with current contracts."
    docker compose exec kernel-tooling alembic -c persistence/alembic.ini upgrade head
  else
    echo "[Step 3] Skipped migrations (--skip-migrations)."
  fi

  if [[ $SKIP_SMOKE -eq 0 ]]; then
    echo "[Step 4] Run E2E smoke checks against API/UI/MLflow endpoints."
    ./ops/e2e-smoke.sh
  else
    echo "[Step 4] Skipped smoke test (--skip-smoke)."
  fi

  echo "[Step 5] Done. To stop local stack later: docker compose down"
else
  echo "[Step 2] Apply core Kubernetes manifests (namespace, API/UI, services, secrets placeholders)."
  kubectl apply -f deploy/k8s/kernel-platform.yaml

  echo "[Step 3] Apply production hardening controls (NetworkPolicies baseline)."
  kubectl apply -f deploy/k8s/production-hardening.yaml

  echo "[Step 4] Apply specialized planes (model-runner, secret-kernel, feast, action-adapters)."
  kubectl apply -f deploy/k8s/model-runner/
  kubectl apply -f deploy/k8s/secret-kernel.yaml
  kubectl apply -f deploy/k8s/feast/
  kubectl apply -f deploy/k8s/action-adapters.yaml

  if [[ $SKIP_SMOKE -eq 0 ]]; then
    echo "[Step 5] Run E2E smoke checks (requires reachable ingress/port-forwarding to localhost endpoints)."
    ./ops/e2e-smoke.sh
  else
    echo "[Step 5] Skipped smoke test (--skip-smoke)."
  fi
fi
