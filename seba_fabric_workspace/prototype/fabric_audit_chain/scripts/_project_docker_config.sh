#!/usr/bin/env bash

FABRIC_CHAIN_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FABRIC_CHAIN_PROJECT_DIR="$(cd "$FABRIC_CHAIN_SCRIPT_DIR/.." && pwd)"

if [[ "${FABRIC_USE_GLOBAL_DOCKER_CONFIG:-false}" != "true" ]]; then
  export DOCKER_CONFIG="${FABRIC_DOCKER_CONFIG:-$FABRIC_CHAIN_PROJECT_DIR/.local/docker-config}"
  mkdir -p "$DOCKER_CONFIG"
  if [[ ! -f "$DOCKER_CONFIG/config.json" ]]; then
    printf '{"auths":{},"cliPluginsExtraDirs":["/opt/homebrew/lib/docker/cli-plugins"]}\n' > "$DOCKER_CONFIG/config.json"
  fi
  unset DOCKER_HOST
  if command -v docker >/dev/null 2>&1; then
    if ! docker context inspect colima >/dev/null 2>&1; then
      docker context create colima --docker "host=unix://$HOME/.colima/default/docker.sock" >/dev/null 2>&1 || true
    fi
    export DOCKER_CONTEXT="${DOCKER_CONTEXT:-colima}"
  fi
  export DOCKER_SOCK="${DOCKER_SOCK:-/var/run/docker.sock}"
fi
