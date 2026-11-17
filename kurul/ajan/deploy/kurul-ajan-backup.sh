#!/usr/bin/env bash
# kurul-ajan-backup: daily local tar.gz of the worker state directory, newest KURUL_BACKUP_KEEP kept.
# Run by kurul-ajan-backup.service as the kurul-ajan user. The SQLite file (WAL mode) is copied with
# SQLite's online backup, so the archive holds a consistent snapshot while the worker runs.
# Not included: scratch/ (empty working dir), temp files, and anything outside the state directory
# (in particular /etc/kurul-ajan.env, the Claude CLI login, and the git clones).
set -euo pipefail

SRC=${KURUL_STATE_DIR:-/var/lib/kurul-ajan}
DEST=${KURUL_BACKUP_DIR:-/var/backups/kurul-ajan}
KEEP=${KURUL_BACKUP_KEEP:-14}
umask 077

[ -d "$SRC" ] || { echo "kurul-ajan-backup: no state dir $SRC; nothing to back up"; exit 0; }
mkdir -p "$DEST"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

if [ -f "$SRC/ajan.sqlite3" ]; then
  python3 - "$SRC/ajan.sqlite3" "$tmp/ajan.sqlite3" <<'PY'
import sqlite3, sys
src = sqlite3.connect(sys.argv[1])
dst = sqlite3.connect(sys.argv[2])
src.backup(dst)
dst.close()
src.close()
PY
fi

stamp=$(date -u +%Y-%m-%d)
out="$DEST/kurul-ajan-state-$stamp.tar.gz"
part="$DEST/.kurul-ajan-state-$stamp.tar.gz.part"
snap=()
[ -f "$tmp/ajan.sqlite3" ] && snap=(-C "$tmp" ajan.sqlite3)
rc=0
tar -czf "$part" \
  --exclude=./ajan.sqlite3 --exclude=./ajan.sqlite3-wal --exclude=./ajan.sqlite3-shm \
  --exclude=./scratch --exclude='*.tmp' --exclude='./.*.tmp' \
  -C "$SRC" . "${snap[@]}" || rc=$?
# tar exit 1 = a file changed while being read (e.g. usage.jsonl appended): archive is still usable.
if [ "$rc" -gt 1 ]; then
  rm -f "$part"
  echo "kurul-ajan-backup: tar failed (exit $rc)" >&2
  exit 1
fi
mv -f "$part" "$out"

# Keep the newest $KEEP archives.
mapfile -t old < <(find "$DEST" -maxdepth 1 -name 'kurul-ajan-state-*.tar.gz' -printf '%f\n' | sort -r | tail -n +"$((KEEP + 1))")
for f in "${old[@]}"; do rm -f "$DEST/$f"; done

echo "kurul-ajan-backup: wrote $out ($(du -h "$out" | cut -f1)); removed ${#old[@]} old archive(s)"
