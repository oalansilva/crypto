#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_TEMPLATE="$ROOT_DIR/ops/systemd/crypto-candle-writer.service"
TIMER_TEMPLATE="$ROOT_DIR/ops/systemd/crypto-candle-writer.timer"
USER_SYSTEMD_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_TARGET="$USER_SYSTEMD_DIR/crypto-candle-writer.service"
TIMER_TARGET="$USER_SYSTEMD_DIR/crypto-candle-writer.timer"
CURRENT_USER="$(id -un)"

for template in "$SERVICE_TEMPLATE" "$TIMER_TEMPLATE"; do
  if [[ ! -f "$template" ]]; then
    echo "Missing systemd template: $template" >&2
    exit 1
  fi
done

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl is not available on this host." >&2
  exit 1
fi

if ! systemctl --user show-environment >/dev/null 2>&1; then
  echo "systemd user session is unavailable for $CURRENT_USER." >&2
  exit 1
fi

mkdir -p "$USER_SYSTEMD_DIR"
sed "s|__ROOT_DIR__|$ROOT_DIR|g" "$SERVICE_TEMPLATE" >"$SERVICE_TARGET"
sed "s|__ROOT_DIR__|$ROOT_DIR|g" "$TIMER_TEMPLATE" >"$TIMER_TARGET"

if command -v loginctl >/dev/null 2>&1; then
  if ! loginctl enable-linger "$CURRENT_USER" >/dev/null 2>&1; then
    echo "Warning: could not enable linger for $CURRENT_USER; timer may require an active user session." >&2
  fi
fi

systemctl --user daemon-reload
systemctl --user enable --now crypto-candle-writer.timer
systemctl --user status crypto-candle-writer.timer --no-pager
