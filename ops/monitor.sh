#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source ops/restic.sh
limit=${DISK_ALERT_PERCENT:-85}
[[ "$limit" =~ ^[0-9]+$ ]] && ((limit > 0 && limit <= 100)) || exit 2
mkdir -p .cache
exec 9>".cache/maintenance.lock"
# L'arrêt de l'application pendant la capture est prévu.
flock -ns 9 || exit 0
for item in 'app /var/www/html' 'db /var/lib/postgresql/data'; do
    read -r service path <<< "$item"
    usage=$(docker compose exec -T "$service" df -P "$path" | awk 'NR==2 {gsub("%","",$5); print $5}')
    [[ "$usage" =~ ^[0-9]+$ ]]
    printf '%s disque %s%%\n' "$service" "$usage"
    if ((usage >= limit)); then echo "Seuil disque atteint" >&2; exit 1; fi
done
if [[ "$RESTIC_REPOSITORY" == /* ]]; then
    usage=$(df -P "$RESTIC_REPOSITORY" | awk 'NR==2 {gsub("%","",$5); print $5}')
    if ((usage >= limit)); then echo "Seuil disque du dépôt atteint" >&2; exit 1; fi
fi
restic snapshots --host maison --tag famille --latest 1 --json |
    python3 -c 'import datetime as d,json,sys
rows=json.load(sys.stdin)
if not rows: sys.exit("Aucune sauvegarde")
age=d.datetime.now(d.timezone.utc)-d.datetime.fromisoformat(rows[0]["time"].replace("Z","+00:00"))
print(f"Dernière sauvegarde : {age.total_seconds()/3600:.1f} heures")
if not d.timedelta(0) <= age < d.timedelta(hours=30): sys.exit("Âge de sauvegarde hors limite")'
