#!/usr/bin/env bash
set -euo pipefail
# No credentials/privileges on the shared cluster. Private socket, random role,
# no TCP listener; this role does not exist in the host cluster.
ROOT="${1:?supply an existing private test directory}"
[[ "$ROOT" == /tmp/card-1093-* ]] || { echo 'Refusing non-disposable root' >&2; exit 2; }
[[ -d "$ROOT" && ! -e "$ROOT/pg/PG_VERSION" ]] || { echo 'Private empty root required' >&2; exit 2; }
chmod 700 "$ROOT"
/usr/lib/postgresql/16/bin/initdb -D "$ROOT/pg" -U card1093 --auth-local=trust --auth-host=reject >/dev/null
cat >> "$ROOT/pg/postgresql.conf" <<EOF
listen_addresses = ''
unix_socket_directories = '$ROOT'
port = 55493
shared_buffers = '32MB'
max_connections = 12
fsync = on
EOF
/usr/lib/postgresql/16/bin/pg_ctl -D "$ROOT/pg" -l "$ROOT/postgres.log" start >/dev/null
/usr/lib/postgresql/16/bin/createdb -h "$ROOT" -p 55493 -U card1093 crypto_card1093_test
printf 'postgres socket=%s port=55493 role=card1093 database=crypto_card1093_test\n' "$ROOT"
echo 'Stop only this cluster: pg_ctl -D <root>/pg stop -m fast. Keep artifacts; no deletion.'
