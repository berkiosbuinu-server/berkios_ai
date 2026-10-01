#!/usr/bin/env sh
set -eu

mkdir -p backups
stamp="$(date +%Y%m%d-%H%M%S)"
docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-berkios}" "${POSTGRES_DB:-berkios}" > "backups/berkios-${stamp}.sql"
echo "Backup created: backups/berkios-${stamp}.sql"
