#!/usr/bin/env bash
# Exporte les 4 environnements Conda vers conda_envs/*.yaml
# Usage : bash conda_envs/export_all.sh

set -euo pipefail
OUT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENVS=(env_zivid env_ur env_integration env_openvla)

command -v conda >/dev/null 2>&1 || { echo "conda introuvable"; exit 1; }

eval "$(conda shell.bash hook)"

for name in "${ENVS[@]}"; do
  echo "=== $name ==="
  conda activate "$name"
  if [[ "$name" == "env_openvla" ]]; then
    conda env export > "$OUT_DIR/$name.yaml"
  else
    conda env export --from-history > "$OUT_DIR/$name.yaml"
  fi
  echo "  -> $OUT_DIR/$name.yaml"
done

echo "Terminé."
