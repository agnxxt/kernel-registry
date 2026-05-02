#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
BACKEND_SERVICE="${BACKEND_SERVICE:-kernel-registry-api}"
UI_SERVICE="${UI_SERVICE:-kernel-registry-ui}"
BACKEND_IMAGE="${BACKEND_IMAGE:-ghcr.io/AGenNext/kernel-registry-backend:latest}"
UI_IMAGE="${UI_IMAGE:-ghcr.io/AGenNext/kernel-registry-ui:latest}"
DB_URL="${DATABASE_URL:-}"
KERNEL_MASTER_KEY="${KERNEL_MASTER_KEY:-}"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-true}"

log() { printf '\n==> %s\n' "$*"; }
fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

require_gcloud() {
  command -v gcloud >/dev/null 2>&1 || fail "gcloud CLI is required. Install it, authenticate, then rerun."
}

resolve_project() {
  if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
  fi
  [ -n "$PROJECT_ID" ] || fail "Set PROJECT_ID or run: gcloud config set project YOUR_PROJECT_ID"
}

enable_apis() {
  log "Enabling required Google Cloud APIs"
  gcloud services enable run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com --project "$PROJECT_ID"
}

prepare_env() {
  [ -n "$KERNEL_MASTER_KEY" ] || KERNEL_MASTER_KEY="$(openssl rand -hex 18)"

  if [ -z "$DB_URL" ]; then
    cat >&2 <<EOF

No DATABASE_URL was provided.
Cloud Run does not include Postgres/Redpanda/Vault/Temporal/MLflow from docker-compose.
For production, provide a managed Postgres URL, for example:

  DATABASE_URL='postgresql+psycopg2://USER:PASS@HOST:5432/kernel' PROJECT_ID=$PROJECT_ID bash deploy-cloud-run.sh

EOF
    fail "DATABASE_URL is required for Cloud Run API deployment."
  fi
}

deploy_api() {
  log "Deploying API to Cloud Run"
  local auth_flag="--allow-unauthenticated"
  if [ "$ALLOW_UNAUTHENTICATED" != "true" ]; then
    auth_flag="--no-allow-unauthenticated"
  fi

  gcloud run deploy "$BACKEND_SERVICE" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --image "$BACKEND_IMAGE" \
    --port 8000 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 3 \
    $auth_flag \
    --set-env-vars "DATABASE_URL=$DB_URL,KERNEL_MASTER_KEY=$KERNEL_MASTER_KEY,MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-},KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS:-},VAULT_ADDR=${VAULT_ADDR:-},FGA_API_URL=${FGA_API_URL:-},AWS_REGION=${AWS_REGION:-us-east-1},AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1},ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-},OPENAI_API_KEY=${OPENAI_API_KEY:-}"
}

get_api_url() {
  gcloud run services describe "$BACKEND_SERVICE" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --format='value(status.url)'
}

deploy_ui() {
  local api_url="$1"
  log "Deploying UI to Cloud Run"
  local auth_flag="--allow-unauthenticated"
  if [ "$ALLOW_UNAUTHENTICATED" != "true" ]; then
    auth_flag="--no-allow-unauthenticated"
  fi

  gcloud run deploy "$UI_SERVICE" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --image "$UI_IMAGE" \
    --port 3000 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    $auth_flag \
    --set-env-vars "NEXT_PUBLIC_API_URL=$api_url"
}

print_result() {
  local api_url="$1"
  local ui_url="$2"
  cat <<EOF

✅ Cloud Run deployment complete

Project: $PROJECT_ID
Region:  $REGION
API:     $api_url
UI:      $ui_url

Admin user: admin
Admin pass: $KERNEL_MASTER_KEY

Notes:
- This deploys the API/UI containers only.
- Use managed services for Postgres and any required external dependencies.
- GHCR images must be public or accessible to Cloud Run.

One-line Cloud Run deploy example:
  curl -fsSL https://raw.githubusercontent.com/AGenNext/kernel-registry/main/deploy-cloud-run.sh | DATABASE_URL='postgresql+psycopg2://USER:PASS@HOST:5432/kernel' PROJECT_ID='$PROJECT_ID' bash
EOF
}

main() {
  require_gcloud
  resolve_project
  enable_apis
  prepare_env
  deploy_api
  API_URL="$(get_api_url)"
  deploy_ui "$API_URL"
  UI_URL="$(gcloud run services describe "$UI_SERVICE" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)')"
  print_result "$API_URL" "$UI_URL"
}

main "$@"
