#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/dev-via-acpx.sh <change|story|bug> <id> <prompt...>
  scripts/dev-via-acpx.sh exec <change|story|bug> <id> <prompt...>
  scripts/dev-via-acpx.sh status <change|story|bug> <id>
  scripts/dev-via-acpx.sh history <change|story|bug> <id>
  scripts/dev-via-acpx.sh cancel <change|story|bug> <id>
  scripts/dev-via-acpx.sh ensure <change|story|bug> <id>
  scripts/dev-via-acpx.sh set <change|story|bug> <id> <key> <value>
  scripts/dev-via-acpx.sh set-mode <change|story|bug> <id> <mode>

Examples:
  scripts/dev-via-acpx.sh story STR-142 "implemente os criterios de aceite"
  scripts/dev-via-acpx.sh bug BUG-77 "corrija a regressao e rode testes"
  scripts/dev-via-acpx.sh exec story STR-142 "resuma riscos antes de codar"
USAGE
}

require_acpx() {
  if ! command -v acpx >/dev/null 2>&1; then
    echo "acpx nao encontrado no PATH" >&2
    exit 1
  fi
}

session_name() {
  local item_type="$1"
  local item_id="$2"
  printf 'dev-%s-%s' "$item_type" "$item_id"
}

require_scope() {
  if [[ $# -lt 2 ]]; then
    usage >&2
    exit 1
  fi
}

run_prompt() {
  local mode="$1"
  local item_type="$2"
  local item_id="$3"
  shift 3

  local session
  session="$(session_name "$item_type" "$item_id")"

  if [[ $# -lt 1 ]]; then
    usage >&2
    exit 1
  fi

  if [[ "$mode" == "exec" ]]; then
    exec acpx codex exec "$@"
  fi

  acpx codex sessions ensure --name "$session" >/dev/null
  exec acpx codex -s "$session" "$@"
}

run_session_command() {
  local command="$1"
  local item_type="$2"
  local item_id="$3"
  shift 3

  local session
  session="$(session_name "$item_type" "$item_id")"

  case "$command" in
    ensure)
      exec acpx codex sessions ensure --name "$session"
      ;;
    status)
      exec acpx codex status -s "$session"
      ;;
    history)
      exec acpx codex sessions history "$session"
      ;;
    cancel)
      exec acpx codex cancel -s "$session"
      ;;
    set)
      if [[ $# -ne 2 ]]; then
        usage >&2
        exit 1
      fi
      exec acpx codex set "$1" "$2" -s "$session"
      ;;
    set-mode)
      if [[ $# -ne 1 ]]; then
        usage >&2
        exit 1
      fi
      exec acpx codex set-mode "$1" -s "$session"
      ;;
    *)
      usage >&2
      exit 1
      ;;
  esac
}

main() {
  require_acpx

  if [[ $# -lt 1 ]]; then
    usage >&2
    exit 1
  fi

  local command="$1"
  shift

  case "$command" in
    exec)
      require_scope "$@"
      run_prompt "exec" "$@"
      ;;
    status|history|cancel|ensure|set|set-mode)
      require_scope "$@"
      run_session_command "$command" "$@"
      ;;
    change|story|bug)
      run_prompt "prompt" "$command" "$@"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      usage >&2
      exit 1
      ;;
  esac
}

main "$@"
