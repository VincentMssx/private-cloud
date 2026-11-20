#!/usr/bin/env bash
# Le workflow envoie une archive Git tar.gz sur stdin.
set -euo pipefail
umask 077
revision=${1:?Indiquer le SHA Git de la version}
[[ "$revision" =~ ^[0-9a-f]{40}$ ]]
base=/opt/maison
mkdir -p "$base"/{releases,shared/.cache}
exec 8>"$base/shared/deploy.lock"
flock -n 8
set -a
source /etc/maison/cloud.env
source /etc/maison/backup.env
set +a
export COMPOSE_PROJECT_NAME=nuage-famille COMPOSE_FILE=compose.yaml:compose.cloud.yaml
[[ -s "$base/shared/.env" ]]
stage=$(mktemp -d "$base/releases/$revision.XXXXXXXX")
tar xz --no-same-owner -C "$stage"
printf '%s\n' "$revision" > "$stage/RELEASE"
ln -s "$base/shared/.env" "$stage/.env"
ln -s "$base/shared/.cache" "$stage/.cache"
# Sur une mise à jour, prendre un point de reprise avec la version encore active.
first=1
if [[ -L "$base/current" ]]; then
    first=0
    "$base/current/ops/backup.sh"
else
    "$stage/ops/backup.sh" snapshots >/dev/null
fi
exec 9>"$base/shared/.cache/maintenance.lock"
flock 9
"$stage/ops/cloud.sh"
flock -u 9
if ((first)); then "$stage/ops/backup.sh"; fi
"$stage/ops/monitor.sh"
ln -s "$stage" "$base/current.new.$$"
mv -Tf "$base/current.new.$$" "$base/current"
