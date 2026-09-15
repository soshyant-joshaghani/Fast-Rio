#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "$0")/../.." && pwd)"
if [[ ! -f .env ]]; then
  cp -n .env.example .env 2>/dev/null || true
fi

# Bake + default attestations can fail with: image "…:prod": already exists
# (same issue foxg-front / fast-game work around). Prefer classic compose build.
export COMPOSE_BAKE=false
export BUILDX_NO_DEFAULT_ATTESTATIONS=1

source "$(dirname "$0")/lib/ensure-letsencrypt.sh"
docker network inspect traefik-public >/dev/null 2>&1 || docker network create traefik-public

# Clear app tags so export can always write (BuildKit may refuse overwrite).
for img in fast-rio-backend:prod fast-rio-frontend:prod; do
  if docker image inspect "$img" >/dev/null 2>&1; then
    docker rmi -f "$img" || true
  fi
done

COMPOSE_ARGS=(-f compose.yml)
# Optional bundled MinIO when this kit ships compose.minio.yml. Skip with:
#   FAST_RIO_STORAGE=external bash __ctrl__/remote/start-prod.sh
if [[ -f compose.minio.yml && "${FAST_RIO_STORAGE:-bundled}" != "external" ]]; then
  COMPOSE_ARGS+=(-f compose.minio.yml)
  if ! grep -qE '^DOMAIN=' .env 2>/dev/null; then
    echo "WARNING: .env has no DOMAIN=… — Traefik MinIO host labels need it"
    echo "  (e.g. DOMAIN=example.com). Public object URLs will break."
  fi
fi

# Build first (sole builders), then up without --build so shared-tag
# services (prestart/worker) do not race a registry pull.
docker compose "${COMPOSE_ARGS[@]}" build backend frontend
docker compose "${COMPOSE_ARGS[@]}" up -d --pull never
echo
echo "fast-rio production stack started (includes ARQ worker)."
if [[ -f compose.minio.yml && "${FAST_RIO_STORAGE:-bundled}" != "external" ]]; then
  echo "Object storage: bundled MinIO (compose.minio.yml)."
  echo "DNS A records required: minio.\${DOMAIN} and (optional) minio-console.\${DOMAIN}"
elif [[ -f compose.minio.yml ]]; then
  echo "Object storage: external (FAST_RIO_STORAGE=external — no compose.minio.yml)."
fi
echo "Update DOMAIN in compose.yml / .env, ACME email in compose.traefik.yml, and DNS before going live."
