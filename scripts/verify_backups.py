#!/usr/bin/env python3
"""Verify every host has a snapshot < 26 h old and the DR copy is in sync; print and exit non-zero on failure."""
import json, os, subprocess, sys, time, yaml

def snapshots(repo, password):
    env = dict(os.environ, RESTIC_REPOSITORY=repo, RESTIC_PASSWORD=password)
    out = subprocess.run(["restic", "snapshots", "--json", "--latest", "1"], env=env, capture_output=True, text=True, check=True).stdout
    return json.loads(out)

def main():
    cfg = yaml.safe_load(open(os.environ.get("VERIFY_CONFIG", "verify.yml")))
    pw = os.environ["RESTIC_PASSWORD"]; bad = 0; now = time.time()
    for host in cfg["hosts"]:
        try:
            snap = snapshots(f"{cfg['repo_base']}/{host}", pw)[0]
            age_h = (now - time.mktime(time.strptime(snap["time"][:19], "%Y-%m-%dT%H:%M:%S"))) / 3600
            ok = age_h < 26
            print(f"{'OK  ' if ok else 'FAIL'} {host:20s} last snapshot {age_h:5.1f}h ago")
            bad += not ok
        except Exception as e:
            print(f"FAIL {host:20s} {e}"); bad += 1
    try:
        local = subprocess.run(["du", "-sb", cfg["local_store"]], capture_output=True, text=True, check=True).stdout.split()[0]
        remote = json.loads(subprocess.run(["rclone", "size", "--json", cfg["dr_remote"]], capture_output=True, text=True, check=True).stdout)["bytes"]
        drift = abs(int(local) - remote) / max(int(local), 1)
        ok = drift < 0.02
        print(f"{'OK  ' if ok else 'FAIL'} DR copy size drift {drift:.1%}"); bad += not ok
    except Exception as e:
        print(f"FAIL DR check {e}"); bad += 1
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
