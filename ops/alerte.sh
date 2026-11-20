#!/usr/bin/env bash
set -euo pipefail
: "${ALERT_WEBHOOK_URL:?Configurer le point de réception HTTPS de l’admin}"
[[ "$ALERT_WEBHOOK_URL" == https://* ]]
curl --silent --show-error --fail --retry 2 --max-time 15 --data-urlencode "message=Maison : échec de l’unité $1 sur $(hostname)" "$ALERT_WEBHOOK_URL" > /dev/null
