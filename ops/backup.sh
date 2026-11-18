#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source ops/restic.sh
case "${1:-backup}" in
    init|snapshots|check) restic "$1"; exit ;;
    backup) ;;
    *) echo "Utilisation : backup.sh [init|backup|snapshots|check]" >&2; exit 2 ;;
esac
mkdir -p .cache
exec 9>".cache/maintenance.lock"
flock -n 9
# Valider le dépôt et l'image avant la coupure d'écriture.
restic cat config >/dev/null
for service in db app cron; do
    [[ -n "$(docker compose ps -q --status running "$service")" ]]
done
volume=$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/var/www/html"}}{{.Name}}{{end}}{{end}}' "$(docker compose ps -q app)")
[[ -n "$volume" ]]
meta=$(mktemp -d)
restart=0
finish() {
    status=$?
    trap - EXIT
    if ((restart)); then docker compose start app cron || status=1; fi
    rm -f -- "$meta"/{roles.sql,database.dump,stack.env,revision}
    rmdir "$meta"
    exit "$status"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
install -m 600 .env "$meta/stack.env"
if [[ -f RELEASE ]]; then cat RELEASE; else git rev-parse HEAD; fi > "$meta/revision"
restart=1
docker compose stop -t 120 cron app
docker compose exec -T db pg_dumpall -U famille --roles-only > "$meta/roles.sql"
docker compose exec -T db pg_dump -U famille -Fc famille > "$meta/database.dump"
mounts=(--mount "type=volume,src=$volume,dst=/data,readonly" --mount "type=bind,src=$meta,dst=/meta,readonly")
restic backup --host maison --tag famille /data /meta
docker compose start app cron
restart=0
mounts=()
restic check
restic forget --host maison --tag famille --keep-daily 7 --keep-weekly 4 --prune
