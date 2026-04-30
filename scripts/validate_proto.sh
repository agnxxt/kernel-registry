#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Basic structural validation: ensure syntax/package declarations exist.
failed=0
while IFS= read -r -d '' f; do
  grep -q '^syntax = "proto3";' "$f" || { echo "Missing proto3 syntax in $f"; failed=1; }
  grep -q '^package ' "$f" || { echo "Missing package in $f"; failed=1; }
done < <(find schemas -type f -name "*.proto" -print0)

if [[ $failed -ne 0 ]]; then
  exit 1
fi

echo "Proto structural validation passed."
