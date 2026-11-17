#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
if [[ ! -e .env ]]; then
  (set -C; { printf 'ADMIN_PASSWORD=%s\n' "$(openssl rand -hex 24)"; printf 'DB_PASSWORD=%s\n' "$(openssl rand -hex 24)"; } > .env)
fi
mkdir -p .cache
build_args=()
if [[ -n "${CODEX_PROXY_CERT:-}" ]]; then
  build_args+=(--secret id=ca_bundle,src=/etc/ssl/certs/ca-certificates.crt)
fi
docker build "${build_args[@]}" -t famille-analysis:local worker
docker compose up -d --no-build app analysis
occ() { docker compose exec -T -u www-data app php occ "$@"; }
for ((i=0;i<180;i++)); do
  if occ status --output=json 2>/dev/null | python3 -c 'import json,sys; sys.exit(not json.load(sys.stdin)["installed"])' 2>/dev/null; then break; fi
  sleep 2
done
occ status -e
while read -r app digest url; do
  archive=".cache/$app.tar.gz"
  if [[ ! -s "$archive" ]]; then
    curl -fsSL --retry 3 "$url" -o "$archive.part"
    mv "$archive.part" "$archive"
  fi
  printf '%s  %s\n' "$digest" "$archive" | sha256sum -c -
  docker compose exec -T app tar -xzf - -C /var/www/html/custom_apps --no-same-owner < "$archive"
  occ app:enable "$app" < /dev/null
done < scripts/apps.lock
tar --mode='u+rwX,go+rX' -C apps -cf - familytri | docker compose exec -T app tar -xf - -C /var/www/html/custom_apps --no-same-owner
occ app:enable familytri
occ app:enable twofactor_totp
occ app:enable files_trashbin
occ config:system:set memories.timeline.default_path --value=/
occ app:disable files_sharing
occ app:disable firstrunwizard
occ config:system:set defaultapp --value=files
occ config:system:set default_language --value=fr
occ config:system:set trashbin_retention_obligation --value='30, 30'
occ twofactorauth:enforce --on --group=admin
occ config:system:set skeletondirectory --value=''
occ config:system:set enabledPreviewProviders --type=json --value='["OC\\Preview\\PNG","OC\\Preview\\JPEG","OC\\Preview\\HEIC","OC\\Preview\\WebP","OC\\Preview\\GIF","OC\\Preview\\TXT"]'
if ! occ config:system:get memories.exiftool >/dev/null; then occ maintenance:repair; fi
occ background:cron
docker compose up -d cron
occ status
