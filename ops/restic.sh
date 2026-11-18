#!/usr/bin/env bash
# Source commune aux sauvegardes et à la restauration.
set -euo pipefail
umask 077
restic_image='restic/restic:0.18.1@sha256:39d9072fb5651c80d75c7a811612eb60b4c06b32ffe87c2e9f3c7222e1797e76'
: "${RESTIC_PASSWORD_FILE:?Indiquer le fichier de clé hors dépôt}"
: "${RESTIC_REPOSITORY:?Indiquer un chemin absolu local ou un dépôt s3:https://…}"
[[ -s "$RESTIC_PASSWORD_FILE" ]]
repo_args=(--mount "type=bind,src=$(realpath "$RESTIC_PASSWORD_FILE"),dst=/key,readonly" -e RESTIC_PASSWORD_FILE=/key)
case "$RESTIC_REPOSITORY" in
    /*)
        [[ -d "$RESTIC_REPOSITORY" ]]
        repo_args+=(--mount "type=bind,src=$(realpath "$RESTIC_REPOSITORY"),dst=/repository" -e RESTIC_REPOSITORY=/repository)
        ;;
    s3:https://*)
        repo_args+=(-e RESTIC_REPOSITORY -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN -e AWS_DEFAULT_REGION)
        ;;
    *) echo "Dépôt local ou S3 HTTPS requis" >&2; exit 2 ;;
esac
mounts=()
restic() {
    docker run --rm "${repo_args[@]}" "${mounts[@]}" "$restic_image" --no-cache "$@"
}
