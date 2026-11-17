#!/usr/bin/env bash
# Install or refresh the agent worker's ops timers: self-update (5 min), health check (10 min),
# daily local state backup. Idempotent; prints what it did. Run as root on the worker server:
#   sudo bash /opt/kurul-ajan/code/kurul/ajan/deploy/install-ops.sh
# Expects the worker set up as in kurul-ajan.service (user kurul-ajan, /etc/kurul-ajan.env,
# /opt/kurul-ajan/{code,ledger}, /var/lib/kurul-ajan). Installs nothing else and touches no secret.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
LIB=/usr/local/lib/kurul-ajan-ops
UNITDIR=/etc/systemd/system
BACKUPS=/var/backups/kurul-ajan
USER_=kurul-ajan
ENVFILE=/etc/kurul-ajan.env

[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 1; }
say() { echo "install-ops: $*"; }

for bin in git python3 setpriv systemctl tar; do
  command -v "$bin" >/dev/null || { echo "missing command: $bin" >&2; exit 1; }
done
id "$USER_" >/dev/null 2>&1 || { echo "user $USER_ does not exist; set up kurul-ajan.service first" >&2; exit 1; }
[ -f "$ENVFILE" ] || say "WARNING: $ENVFILE missing; the health check needs KURUL_BASE_URL from it"

changed=0
put() {  # mode src dst
  if [ -f "$3" ] && cmp -s "$2" "$3"; then
    say "unchanged $3"
  else
    install -m "$1" -o root -g root "$2" "$3"
    say "installed $3"
    changed=1
  fi
}

install -d -m 0755 -o root -g root "$LIB"
put 0755 "$SRC/kurul-ajan-update.sh" "$LIB/kurul-ajan-update.sh"
put 0755 "$SRC/kurul-ajan-backup.sh" "$LIB/kurul-ajan-backup.sh"
put 0755 "$SRC/kurul-ajan-health.py" "$LIB/kurul-ajan-health.py"
for u in kurul-ajan-update kurul-ajan-health kurul-ajan-backup; do
  put 0644 "$SRC/$u.service" "$UNITDIR/$u.service"
  put 0644 "$SRC/$u.timer" "$UNITDIR/$u.timer"
done

if [ -d "$BACKUPS" ]; then
  say "exists $BACKUPS"
else
  say "created $BACKUPS"
fi
install -d -m 0700 -o "$USER_" -g "$USER_" "$BACKUPS"

if [ -f "$UNITDIR/kurul-ajan.service" ] && ! cmp -s "$SRC/kurul-ajan.service" "$UNITDIR/kurul-ajan.service"; then
  say "NOTE: $UNITDIR/kurul-ajan.service differs from the one in git (not changed by this script)"
fi

[ "$changed" -eq 0 ] || { systemctl daemon-reload; say "systemd reloaded"; }
for t in kurul-ajan-update.timer kurul-ajan-health.timer kurul-ajan-backup.timer; do
  if systemctl is-enabled --quiet "$t" && systemctl is-active --quiet "$t"; then
    if [ "$changed" -eq 1 ]; then
      systemctl restart "$t"
      say "restarted $t"
    else
      say "already enabled and running $t"
    fi
  else
    systemctl enable --now "$t" >/dev/null
    say "enabled and started $t"
  fi
done

# Report clone ownership: git runs as each clone's owner. The ledger must belong to kurul-ajan
# when KURUL_AUTORUN=1 (the worker adds git worktrees there).
for d in /opt/kurul-ajan/code /opt/kurul-ajan/ledger; do
  if [ -e "$d/.git" ]; then
    br=$(setpriv --reuid="$(stat -c %U "$d")" --regid="$(stat -c %G "$d")" --init-groups \
         env HOME=/ git -C "$d" symbolic-ref --quiet --short HEAD 2>/dev/null || echo "detached HEAD")
    say "clone $d: owner $(stat -c %U "$d"), branch $br"
  else
    say "WARNING: no git clone at $d"
  fi
done

say "running the health check once:"
systemctl start kurul-ajan-health.service || true
journalctl -u kurul-ajan-health.service -n 1 --no-pager -o cat 2>/dev/null || true
say "done. Timers: systemctl list-timers 'kurul-ajan-*'"
