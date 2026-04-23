#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_PATH="$ROOT_DIR/ops/systemd/crypto-stack.service"
USER_SYSTEMD_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
TARGET_PATH="$USER_SYSTEMD_DIR/crypto-stack.service"
SERVICE_NAME="crypto-stack.service"
CURRENT_USER="$(id -un)"

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "Missing service template: $TEMPLATE_PATH" >&2
  exit 1
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl is not available on this host." >&2
  exit 1
fi

if ! systemctl --user show-environment >/dev/null 2>&1; then
  echo "systemd user session is unavailable for $CURRENT_USER." >&2
  exit 1
fi

mkdir -p "$USER_SYSTEMD_DIR"
sed "s|__ROOT_DIR__|$ROOT_DIR|g" "$TEMPLATE_PATH" >"$TARGET_PATH"

if command -v loginctl >/dev/null 2>&1; then
  loginctl enable-linger "$CURRENT_USER" >/dev/null 2>&1 || true
fi

systemctl --user daemon-reload
"$ROOT_DIR/stop.sh" >/dev/null 2>&1 || true
systemctl --user enable --now "$SERVICE_NAME"
systemctl --user status "$SERVICE_NAME" --no-pager
