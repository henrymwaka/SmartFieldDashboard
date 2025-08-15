#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pull() {
  echo "[pull] copying live configs into deploy/"
  sudo cp /etc/nginx/sites-available/host-8080 "$REPO_ROOT/deploy/nginx_host-8080.conf"
  sudo cp /etc/systemd/system/djangoapp@SmartFieldDashboard.service "$REPO_ROOT/deploy/gunicorn_sfdash.service"
  sudo chown $USER:$USER "$REPO_ROOT/deploy/nginx_host-8080.conf" "$REPO_ROOT/deploy/gunicorn_sfdash.service"
  echo "[pull] done"
}

push() {
  echo "[push] copying deploy configs back to system locations"
  sudo cp "$REPO_ROOT/deploy/nginx_host-8080.conf" /etc/nginx/sites-available/host-8080
  sudo cp "$REPO_ROOT/deploy/gunicorn_sfdash.service" /etc/systemd/system/djangoapp@SmartFieldDashboard.service
  echo "[push] reloading services"
  sudo nginx -t && sudo systemctl reload nginx
  sudo systemctl daemon-reload
  sudo systemctl restart djangoapp@SmartFieldDashboard
  echo "[push] done"
}

case "${1:-}" in
  pull) pull ;;
  push) push ;;
  *) echo "Usage: $0 [pull|push]"; exit 2 ;;
esac
