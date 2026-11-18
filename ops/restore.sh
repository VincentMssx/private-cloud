#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source ops/restic.sh
project=${1:?Indiquer maison-reprise-nom}
export MAISON_LOCAL_PORT=${2:?Indiquer un port de test disponible}
snapshot=${3:-latest}
[[ "$project" =~ ^maison-reprise-[a-z0-9-]+$ && "$MAISON_LOCAL_PORT" =~ ^[0-9]{2,5}$ ]]
[[ "$snapshot" == latest || "$snapshot" =~ ^[0-9a-f]{8,64}$ ]]
dir="$PWD/backups/$project"
mkdir -p backups
for vol in db nextcloud; do
    if docker volume inspect "${project}_$vol" >/dev/null 2>&1; then echo "Volume déjà présent" >&2; exit 1; fi
done
[[ -z "$(docker ps -aq --filter "label=com.docker.compose.project=$project")" ]]
# La création par Compose attribue les labels officiels aux deux volumes.
if [[ "$snapshot" == latest ]]; then
    snapshot=$(restic snapshots --host maison --tag famille --latest 1 --json | python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["id"])')
fi
revision=$(restic dump "$snapshot" /meta/revision)
if [[ -f RELEASE ]]; then current=$(cat RELEASE); else current=$(git rev-parse HEAD); fi
if [[ "$revision" != "$current" ]]; then
    echo "Utiliser la révision archivée $revision pour cette restauration" >&2
    exit 1
fi
mkdir "$dir"
restic dump --host maison --tag famille "$snapshot" /meta/stack.env > "$dir/.env"
dc=(docker compose -f "$PWD/compose.yaml" --env-file "$dir/.env" -p "$project")
"${dc[@]}" create --no-build db app
mkdir "$dir/meta"
mounts=(--mount "type=volume,src=${project}_nextcloud,dst=/restore/data" --mount "type=bind,src=$dir/meta,dst=/restore/meta")
restic restore --host maison --tag famille "$snapshot" --target /restore --verify
cmp "$dir/.env" "$dir/meta/stack.env"
"${dc[@]}" up -d --wait db
# Le cluster neuf possède déjà son rôle initial famille.
sed '/^CREATE ROLE famille;$/d' "$dir/meta/roles.sql" | "${dc[@]}" exec -T db psql -X -q -v ON_ERROR_STOP=1 -U famille -d famille
"${dc[@]}" exec -T db pg_restore --single-transaction --exit-on-error -U famille -d famille < "$dir/meta/database.dump"
"${dc[@]}" up -d --no-build app analysis
occ() { "${dc[@]}" exec -T -u www-data app php occ "$@"; }
for ((i=0;i<90;i++)); do
    if occ status -e >/dev/null 2>&1; then break; fi
    sleep 2
done
occ status -e
# Une copie d'une instance HTTPS doit aussi pouvoir fonctionner en boucle locale.
occ config:system:delete overwriteprotocol
occ config:system:delete overwritehost
occ config:system:set overwrite.cli.url --value="http://127.0.0.1:$MAISON_LOCAL_PORT"
occ config:system:set trusted_domains 0 --value=127.0.0.1
curl -fsS --retry 15 --retry-connrefused "http://127.0.0.1:$MAISON_LOCAL_PORT/status.php" >/dev/null
printf 'Instance de reprise disponible sur http://127.0.0.1:%s ; version archivée ' "$MAISON_LOCAL_PORT"
cat "$dir/meta/revision"
