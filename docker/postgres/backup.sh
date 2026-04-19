#!/bin/sh
set -eu

BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_INTERVAL_SECONDS="${BACKUP_INTERVAL_SECONDS:-86400}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
BACKUP_ON_STARTUP="${BACKUP_ON_STARTUP:-1}"

POSTGRES_USER="${POSTGRES_USER:?POSTGRES_USER is required}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
PGHOST="${PGHOST:-postgres}"
PGPORT="${PGPORT:-5432}"

export PGPASSWORD="$POSTGRES_PASSWORD"

mkdir -p "$BACKUP_DIR"

list_databases() {
  psql \
    -h "$PGHOST" \
    -p "$PGPORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -Atc "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;"
}

run_backup() {
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  echo "Starting PostgreSQL backup at $timestamp"

  for database_name in $(list_databases); do
    backup_file="$BACKUP_DIR/${database_name}_${timestamp}.dump"
    echo "Backing up database '$database_name' to '$backup_file'"
    pg_dump \
      -h "$PGHOST" \
      -p "$PGPORT" \
      -U "$POSTGRES_USER" \
      -d "$database_name" \
      -Fc \
      -f "$backup_file"
  done

  find "$BACKUP_DIR" -type f -name "*.dump" -mtime +"$BACKUP_RETENTION_DAYS" -delete
  echo "PostgreSQL backup finished"
}

if [ "${1:-}" = "--once" ]; then
  run_backup
  exit 0
fi

if [ "$BACKUP_ON_STARTUP" = "1" ]; then
  run_backup
fi

while true; do
  sleep "$BACKUP_INTERVAL_SECONDS"
  run_backup
done
