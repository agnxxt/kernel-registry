#!/usr/bin/env bash
set -euo pipefail
NS="${1:-agent-kernel}"
OUT_DIR="${2:-/tmp/kernel-perf-baseline}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUT_DIR}/${TS}.txt"
mkdir -p "${OUT_DIR}"
{
  echo "timestamp_utc=${TS}"
  echo "=== nodes ==="
  kubectl get nodes -o wide
  echo "=== pods (${NS}) ==="
  kubectl -n "${NS}" get pods -o wide
  echo "=== services (${NS}) ==="
  kubectl -n "${NS}" get svc
  echo "=== top nodes ==="
  kubectl top nodes || true
  echo "=== top pods (${NS}) ==="
  kubectl -n "${NS}" top pods || true
  echo "=== restart counts (${NS}) ==="
  kubectl -n "${NS}" get pods -o jsonpath="{range .items[*]}{.metadata.name}{'\t'}{range .status.containerStatuses[*]}{.restartCount}{'\t'}{end}{'\n'}{end}"
  echo "=== recent events (${NS}) ==="
  kubectl -n "${NS}" get events --sort-by=.lastTimestamp | tail -n 40
} > "${OUT}"
echo "${OUT}"
