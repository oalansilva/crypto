#!/bin/sh
# Emit allowlisted routing metadata from one exact native Codex rollout.

set -eu

usage() {
  cat <<'EOF'
Usage: inspect-agent-runtime.sh [--sessions-dir DIR] THREAD_ID

Read the single rollout whose filename ends with THREAD_ID and emit only safe
routing metadata. The default sessions root is "$CODEX_HOME/sessions" when
CODEX_HOME is set, otherwise "$HOME/.codex/sessions".
EOF
}

fail() {
  printf '%s\n' "ERROR: $*" >&2
  exit 1
}

sessions_dir=''
case "$#" in
  1) thread_id=$1 ;;
  3)
    [ "$1" = "--sessions-dir" ] || { usage >&2; exit 2; }
    [ -n "$2" ] || fail "--sessions-dir requires a non-empty directory."
    sessions_dir=$2
    thread_id=$3
    ;;
  *) usage >&2; exit 2 ;;
esac

if ! printf '%s\n' "$thread_id" | LC_ALL=C grep -Eq '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'; then
  fail "THREAD_ID must be a lowercase UUID."
fi

if [ -z "$sessions_dir" ]; then
  if [ -n "${CODEX_HOME-}" ]; then
    sessions_dir=$CODEX_HOME/sessions
  else
    [ -n "${HOME-}" ] || fail "HOME is unset; pass --sessions-dir explicitly."
    sessions_dir=$HOME/.codex/sessions
  fi
fi

[ -d "$sessions_dir" ] || fail "sessions directory is unavailable."

tmp_base=${TMPDIR:-/tmp}
case "$tmp_base" in /*) ;; *) tmp_base=/tmp ;; esac
matches_file=''

cleanup() {
  if [ -n "$matches_file" ] && [ -f "$matches_file" ]; then
    case "$matches_file" in
      "$tmp_base"/crypto-agent-runtime.*) find "$matches_file" -maxdepth 0 -type f -delete ;;
      *) printf '%s\n' "ERROR: refusing cleanup of unexpected temporary file." >&2 ;;
    esac
  fi
}
trap cleanup 0 HUP INT TERM

matches_file=$(mktemp "$tmp_base/crypto-agent-runtime.XXXXXX") || fail "could not create temporary match list."
find "$sessions_dir" -type f -name "rollout-*-$thread_id.jsonl" -print > "$matches_file" 2>/dev/null || fail "could not enumerate rollout filenames."

match_count=$(awk 'END { print NR + 0 }' "$matches_file")
case "$match_count" in
  0) fail "no rollout filename matched the requested thread id." ;;
  1) ;;
  *) fail "multiple rollout filenames matched the requested thread id." ;;
esac

IFS= read -r rollout_file < "$matches_file" || fail "could not read matched rollout filename."
[ -f "$rollout_file" ] || fail "matched rollout is unavailable."

if ! jq -ce -s --arg expected_thread_id "$thread_id" '
  def string_or_null: if type == "string" then . else null end;
  [ .[] | select(.type == "session_meta") | .payload ] as $sessions |
  [ .[] | select(.type == "turn_context") | .payload ] as $turns |
  if ($sessions | length) != 1 then error("missing or ambiguous session metadata")
  elif ($turns | length) == 0 then error("missing turn context")
  else
    $sessions[0] as $session |
    ($session.id? | string_or_null) as $thread_id |
    ($session.agent_role? | string_or_null) as $agent_type |
    [ $turns[] | (.model? | string_or_null) ] as $models |
    [ $turns[] | (.effort? | string_or_null) ] as $efforts |
    [ $turns[] | ((.sandbox_policy? // {}) | .type? | string_or_null) ] as $sandboxes |
    [ $turns[] | ((.permission_profile? // {}) | .type? | string_or_null) ] as $permissions |
    if $thread_id != $expected_thread_id then error("session does not identify requested thread")
    elif $agent_type == null or $agent_type == "" then error("missing agent type")
    elif any($models[]; . == null or . == "") then error("missing model")
    elif any($efforts[]; . == null or . == "") then error("missing effort")
    elif any($sandboxes[]; . == null or . == "") then error("missing sandbox policy type")
    elif any($permissions[]; . == null or . == "") then error("missing permission profile type")
    elif ($models | unique | length) != 1 then error("conflicting models")
    elif ($efforts | unique | length) != 1 then error("conflicting efforts")
    elif ($sandboxes | unique | length) != 1 then error("conflicting sandbox policy types")
    elif ($permissions | unique | length) != 1 then error("conflicting permission profile types")
    else {
      agent_type: $agent_type,
      model: $models[0],
      effort: $efforts[0],
      sandbox_policy_type: $sandboxes[0],
      permission_profile_type: $permissions[0]
    } end
  end
' "$rollout_file" 2>/dev/null; then
  fail "rollout is missing, ambiguous, invalid, or inconsistent required routing metadata."
fi
