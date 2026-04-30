#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

failed=0
while IFS= read -r -d '' f; do
  if ! python3 -m json.tool "$f" >/dev/null; then
    echo "Invalid JSON: $f"
    failed=1
  fi
done < <(find schemas -type f -name "*.json" -print0)

if [[ $failed -ne 0 ]]; then
  exit 1
fi

echo "Schema JSON validation passed."
