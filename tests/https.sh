#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
network=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' "$(docker compose ps -q app)")
tmp=$(mktemp -d)
image=$(MAISON_DOMAIN=localhost docker compose -f compose.yaml -f compose.cloud.yaml config --images caddy)
proxy=$(docker run -d --network "$network" -p 127.0.0.1::443 -e NO_PROXY=app,localhost,127.0.0.1 -e no_proxy=app,localhost,127.0.0.1 -e MAISON_DOMAIN=localhost \
    --mount "type=bind,src=$PWD/ops/Caddyfile,dst=/etc/caddy/Caddyfile,readonly" "$image")
finish() {
    docker rm -f -v "$proxy" >/dev/null
    rm -f "$tmp"/{ca.crt,headers}
    rmdir "$tmp"
}
trap finish EXIT
for ((i=0;i<30;i++)); do
    if docker cp "$proxy:/data/caddy/pki/authorities/local/root.crt" "$tmp/ca.crt" 2>/dev/null; then break; fi
    sleep 1
done
port=$(docker port "$proxy" 443/tcp | cut -d: -f2)
url="https://localhost:$port"
curl --noproxy '*' --cacert "$tmp/ca.crt" -D "$tmp/headers" -fsS "$url/status.php" |
    python3 -c 'import json,sys; s=json.load(sys.stdin); assert s["installed"] and not s["maintenance"]'
grep -iq '^strict-transport-security: max-age=15552000' "$tmp/headers"
curl --noproxy '*' --cacert "$tmp/ca.crt" -IsS "$url/.well-known/caldav" | grep -iq '^location: /remote.php/dav/'
echo "OK · HTTPS, HSTS et découverte DAV sur proxy local"
