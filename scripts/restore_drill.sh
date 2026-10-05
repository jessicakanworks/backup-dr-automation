#!/usr/bin/env bash
# Quarterly restore drill: restore a random host's latest snapshot into a scratch dir on a drill VM, verify, log.
set -euo pipefail
. /etc/restic.env
hosts=(dev-web-01 dev-app-01 dev-db-01); host=${hosts[$RANDOM % ${#hosts[@]}]}
export RESTIC_REPOSITORY="sftp:backup@10.10.9.30:/backups/$host"
start=$(date +%s); target=/srv/drill/$host-$(date +%F); mkdir -p "$target"
restic restore latest --target "$target"
restic check
files=$(find "$target" -type f | wc -l); dur=$(( $(date +%s) - start ))
echo "| $(date +%F) | $host | ${dur}s | $files files | PASS |" | tee -a DRILL-LOG.md
rm -rf "$target"
