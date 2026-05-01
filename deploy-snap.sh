#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-/opt/kernel-registry}"
REPO_URL="${REPO_URL:-https://github.com/AGenNext/kernel-registry.git}"
PUBLIC_HOST="${PUBLIC_HOST:-}"
ADMIN_PASS="${ADMIN_PASS:-}"
DB_PASS="${DB_PASS:-}"
SKIP_FIREWALL="${SKIP_FIREWALL:-false}"

log() { printf '\n==> %s\n' "$*"; }
fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

require_sudo() {
  command -v sudo >/dev/null 2>&1 || fail "sudo is required."
}

install_base_packages() {
  log "Installing base packages"
  sudo apt-get update -y
  sudo apt-get install -y git curl ca-certificates openssl ufw snapd
  sudo systemctl enable --now snapd.socket >/dev/null 2>&1 || true
}

install_snap_docker() {
  log "Installing Docker through Snap"
  if ! snap list docker >/dev/null 2>&1; then
    sudo snap install docker
  fi

  sudo snap start docker >/dev/null 2>&1 || true

  # Snap Docker usually exposes /snap/bin/docker. Make sure non-interactive shells can find it.
  export PATH="/snap/bin:$PATH"

  if ! command -v docker >/dev/null 2>&1; then
    fail "Docker command not found after snap install. Try opening a new shell or check snapd."
  fi

  if ! sudo docker ps >/dev/null 2>&1; then
    echo "Snap Docker failed to start. Snap service status:" >&2
    snap services docker >&2 || true
    fail "Fix Snap Docker first, then rerun this script."
  fi
}

resolve_public_host() {
  if [ -z "$PUBLIC_HOST" ]; then
    PUBLIC_HOST="$(curl -fsS https://api.ipify.org 2>/dev/null || true)"
  fi
  if [ -z "$PUBLIC_HOST" ]; then
    PUBLIC_HOST="$(hostname -I | awk '{print $1}')"
  fi
  [ -n "$PUBLIC_HOST" ] || fail "Could not detect public IP. Rerun with PUBLIC_HOST=your.domain.com bash deploy-snap.sh"
}

clone_or_update_repo() {
  log "Cloning or updating repository"
  sudo mkdir -p "$(dirname "$APP_DIR")"

  if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR"
    git pull --ff-only || sudo git pull --ff-only
  else
    sudo git clone "$REPO_URL" "$APP_DIR"
    sudo chown -R "$USER:$USER" "$APP_DIR" || true
    cd "$APP_DIR"
  fi
}

write_env() {
  log "Writing .env"
  [ -n "$ADMIN_PASS" ] || ADMIN_PASS="$(openssl rand -hex 18)"
  [ -n "$DB_PASS" ] || DB_PASS="$(openssl rand -hex 18)"

  cat > .env <<EOF
KERNEL_MASTER_KEY=$ADMIN_PASS
POSTGRES_PASSWORD=$DB_PASS
DATABASE_URL=postgresql+psycopg2://kernel:$DB_PASS@postgres:5432/kernel

GITHUB_TOKEN=${GITHUB_TOKEN:-}
SLACK_TOKEN=${SLACK_TOKEN:-}
JIRA_API_KEY=${JIRA_API_KEY:-}
JIRA_EMAIL=${JIRA_EMAIL:-}

MOCK_INFERENCE=${MOCK_INFERENCE:-false}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
OPENAI_API_KEY=${OPENAI_API_KEY:-}

AWS_REGION=${AWS_REGION:-us-east-1}
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}
EOF
}

patch_compose_for_vps() {
  log "Patching frontend API URL"
  if [ -f compose.yaml ]; then
    sed -i "s|http://localhost:8000|http://$PUBLIC_HOST:8000|g" compose.yaml || true
  elif [ -f docker-compose.yml ]; then
    sed -i "s|http://localhost:8000|http://$PUBLIC_HOST:8000|g" docker-compose.yml || true
  fi
}

configure_firewall() {
  if [ "$SKIP_FIREWALL" = "true" ]; then
    log "Skipping firewall configuration"
    return 0
  fi

  log "Opening firewall ports"
  sudo ufw allow OpenSSH >/dev/null 2>&1 || true
  sudo ufw allow 3000/tcp >/dev/null 2>&1 || true
  sudo ufw allow 8000/tcp >/dev/null 2>&1 || true
  sudo ufw --force enable >/dev/null 2>&1 || true
}

start_app() {
  log "Building and starting containers with Snap Docker"
  export PATH="/snap/bin:$PATH"
  sudo docker compose up --build -d
}

print_result() {
  cat <<EOF

✅ Snap deployment complete

Dashboard:  http://$PUBLIC_HOST:3000
API:        http://$PUBLIC_HOST:8000
Admin user: admin
Admin pass: $ADMIN_PASS

Useful commands:
  cd $APP_DIR && sudo docker compose ps
  cd $APP_DIR && sudo docker compose logs -f

One-line Snap install:
  curl -fsSL https://raw.githubusercontent.com/AGenNext/kernel-registry/main/deploy-snap.sh | bash
EOF
}

main() {
  require_sudo
  install_base_packages
  install_snap_docker
  resolve_public_host
  clone_or_update_repo
  write_env
  patch_compose_for_vps
  configure_firewall
  start_app
  print_result
}

main "$@"
