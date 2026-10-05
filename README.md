# backup-dr-automation

Scheduled, verified backups of server data and network configurations to on-site and **DR-site**
storage, with integrity checks, quarterly restore drills and replication monitoring. Complements
`dr-runbooks` (the procedures) with the automation that makes them routine.

| Component | Purpose |
|---|---|
| `ansible/backup-agents.yml` | installs restic on hosts, creates per-host repositories, schedules nightly runs |
| `ansible/replicate-to-dr.yml` | rclone sync of the backup repository to the DR-site object store, nightly after backups |
| `scripts/verify_backups.py` | checks every host backed up in the last 26 h, snapshot integrity, DR copy in sync → Prometheus textfile metrics |
| `scripts/restore_drill.sh` | restores a random host's latest snapshot to a scratch VM and runs its smoke test; logs result |
| `prometheus/rules/backup.yml` | alerts: backup missing, verify failed, DR replication lag > 6 h |
| `DRILL-LOG.md` | record of quarterly restore drills (date, host, duration, outcome) |
