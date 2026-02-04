#!/usr/bin/env bash
set -euo pipefail

SESSION_ID="${SESSION_ID:-smoketest-$(date +%s)}"
THINKING="${THINKING:-low}"
TIMEOUT="${TIMEOUT:-60}"
MESSAGE="${MESSAGE:-Você é um analista. Responda apenas com 'ok'.}"

echo "Running: openclaw agent --agent main --session-id ${SESSION_ID} --thinking ${THINKING} --timeout ${TIMEOUT} --json"

# Note: openclaw may output JSON to stdout. We just print first chunk.
openclaw agent \
  --agent main \
  --session-id "${SESSION_ID}" \
  --message "${MESSAGE}" \
  --thinking "${THINKING}" \
  --json \
  --timeout "${TIMEOUT}" \
  | head -c 4000

echo
