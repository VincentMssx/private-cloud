#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${MAISON_DOMAIN:?Indiquer le nom DNS}"
[[ "$MAISON_DOMAIN" =~ ^[a-z0-9.-]+\.[a-z]+$ ]]
export COMPOSE_FILE="${COMPOSE_FILE:-compose.yaml:compose.cloud.yaml}"
bash scripts/local.sh
occ() { docker compose exec -T -u www-data app php occ "$@"; }
occ config:system:set trusted_domains 2 --value="$MAISON_DOMAIN"
occ config:system:set trusted_proxies 0 --value=172.30.50.2
occ config:system:set overwriteprotocol --value=https
occ config:system:set overwrite.cli.url --value="https://$MAISON_DOMAIN"
docker compose up -d caddy
curl -fsS --retry 18 --retry-all-errors --retry-delay 3 "https://$MAISON_DOMAIN/status.php" |
    python3 -c 'import json,sys; s=json.load(sys.stdin); sys.exit(not (s["installed"] and not s["maintenance"] and not s["needsDbUpgrade"]))'
