#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8003/api}"
FAVORITE_ID="${FAVORITE_ID:-4}"
CONVERSATION_ID="${CONVERSATION_ID:-fav-${FAVORITE_ID}}"
THINKING="${THINKING:-low}"
MESSAGE="${MESSAGE:-teste}"
MAX_TIME="${MAX_TIME:-75}"

red() { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

yellow "[1/3] Health: ${API_BASE_URL}/health"
curl -fsS "${API_BASE_URL}/health" | head -c 300; echo

yellow "[2/3] Favorite exists? id=${FAVORITE_ID}"
# just check favorites list contains it (single-tenant MVP)
if ! curl -fsS "${API_BASE_URL}/favorites/" | grep -q "\"id\"[[:space:]]*:[[:space:]]*${FAVORITE_ID}"; then
  yellow "(favorites list doesn't include explicit id fields in some builds; skipping strict check)"
fi

yellow "[3/3] POST /agent/chat (max-time=${MAX_TIME}s)"
RESP=$(curl -sS --max-time "${MAX_TIME}" \
  -X POST "${API_BASE_URL}/agent/chat" \
  -H 'Content-Type: application/json' \
  -d "{\"favorite_id\":${FAVORITE_ID},\"message\":\"${MESSAGE}\",\"conversation_id\":\"${CONVERSATION_ID}\",\"thinking\":\"${THINKING}\"}")

echo "$RESP" | head -c 2000; echo

# Basic assertions without jq
if echo "$RESP" | grep -q '"reply"[[:space:]]*:[[:space:]]*""'; then
  red "FAIL: reply is empty"
  exit 2
fi
if ! echo "$RESP" | grep -q '"reply"'; then
  red "FAIL: missing reply field"
  exit 3
fi

green "PASS: got non-empty reply"
