#!/usr/bin/env bash
# kurul-ajan-update: fast-forward the worker's two clones and restart the worker when its code changed.
# Run by kurul-ajan-update.service (root oneshot, every 5 minutes via kurul-ajan-update.timer).
#
#   code clone    KURUL_CODE_DIR (default /opt/kurul-ajan/code), on KURUL_CODE_BRANCH
#                 (default: the branch it has checked out)
#   ledger clone  KURUL_REPO (default /opt/kurul-ajan/ledger), on KURUL_REPO_REF (default main)
#
# Git runs as the owner of each clone (setpriv), never as root inside a clone root does not own,
# so file ownership stays as installed and git's safe.directory check passes. Only fast-forwards:
# local commits or a different checked-out branch are left alone (one log line, no reset).
# The worker is restarted only when the code clone moved, only if it is running (a stopped worker
# stays stopped), and not while it is processing an event (busy.json in its state dir, written by
# worker.py) unless the restart has already waited KURUL_UPDATE_MAX_DEFER seconds (default 3600).
# Network errors are logged once per outage and the script exits 0.
set -uo pipefail

CODE=${KURUL_CODE_DIR:-/opt/kurul-ajan/code}
CODE_BRANCH=${KURUL_CODE_BRANCH:-}
LEDGER=${KURUL_REPO:-/opt/kurul-ajan/ledger}
LEDGER_REF=${KURUL_REPO_REF:-main}
WSTATE=${KURUL_STATE_DIR:-/var/lib/kurul-ajan}
UNIT=${KURUL_UNIT:-kurul-ajan}
OPS=${STATE_DIRECTORY:-/var/lib/kurul-ajan-ops}   # set by StateDirectory= in the unit
MAX_DEFER=${KURUL_UPDATE_MAX_DEFER:-3600}
LIB=${KURUL_OPS_LIB:-/usr/local/lib/kurul-ajan-ops}

mkdir -p "$OPS"
say() { echo "kurul-ajan-update: $*"; }

# Log a problem once until it changes or clears (avoids a line every 5 minutes during an outage).
problem() {  # key message
  local f="$OPS/problem-$1"
  if [ ! -f "$f" ] || [ "$(cat "$f")" != "$2" ]; then
    printf '%s' "$2" > "$f"
    say "$2"
  fi
}
cleared() {  # key
  local f="$OPS/problem-$1"
  if [ -f "$f" ]; then rm -f "$f"; say "ok again: $1"; fi
}

# Run git in a clone as that clone's owner.
g() {  # dir git-args...
  local dir=$1; shift
  local owner group home
  owner=$(stat -c %U "$dir") || return 1
  group=$(stat -c %G "$dir") || return 1
  home=$(getent passwd "$owner" | cut -d: -f6)
  if [ "$owner" = "$(id -un)" ]; then
    GIT_TERMINAL_PROMPT=0 timeout 300 git -C "$dir" "$@"
  else
    setpriv --reuid="$owner" --regid="$group" --init-groups \
      env HOME="${home:-/}" GIT_TERMINAL_PROMPT=0 timeout 300 git -C "$dir" "$@"
  fi
}

# Returns 0 when the clone moved, 1 when unchanged, 2 when skipped or failed.
update_clone() {  # label dir wanted-branch
  local label=$1 dir=$2 want=$3 cur old new n err
  if [ ! -e "$dir/.git" ]; then
    problem "$label-missing" "$label: $dir is not a git clone; skipped"
    return 2
  fi
  cleared "$label-missing"
  if ! err=$(g "$dir" rev-parse --verify --quiet HEAD 2>&1 >/dev/null); then
    problem "$label-read" "$label: git cannot read $dir as its owner $(stat -c %U "$dir"): $(printf %s "${err//$'\n'/ }" | cut -c1-200)"
    return 2
  fi
  cleared "$label-read"
  if ! cur=$(g "$dir" symbolic-ref --quiet --short HEAD 2>/dev/null); then
    problem "$label-branch" "$label: detached HEAD in $dir; not updating"
    return 2
  fi
  [ -n "$want" ] || want=$cur
  if [ "$cur" != "$want" ]; then
    problem "$label-branch" "$label: $dir has $cur checked out, expected $want; not updating"
    return 2
  fi
  cleared "$label-branch"
  old=$(g "$dir" rev-parse HEAD) || return 2
  if ! err=$(g "$dir" fetch --quiet origin "$want" 2>&1); then
    problem "$label-fetch" "$label: fetch failed (will retry): $(printf %s "${err//$'\n'/ }" | cut -c1-200)"
    return 2
  fi
  cleared "$label-fetch"
  new=$(g "$dir" rev-parse FETCH_HEAD) || return 2
  [ "$old" != "$new" ] || return 1
  if g "$dir" merge-base --is-ancestor "$new" "$old" 2>/dev/null; then
    return 1  # local is ahead of the remote: nothing to do
  fi
  if ! err=$(g "$dir" merge --ff-only --quiet FETCH_HEAD 2>&1); then
    problem "$label-merge" "$label: cannot fast-forward $want to ${new:0:12} (local changes?): $(printf %s "${err//$'\n'/ }" | cut -c1-200)"
    return 2
  fi
  cleared "$label-merge"
  n=$(g "$dir" rev-list --count "$old..$new" 2>/dev/null || echo "?")
  say "$label: $want ${old:0:12} -> ${new:0:12} ($n commit(s))"
  return 0
}

# --- clones ------------------------------------------------------------------------------------

update_clone code "$CODE" "$CODE_BRANCH"
code_rc=$?
if [ "$(realpath -m "$LEDGER")" != "$(realpath -m "$CODE")" ]; then
  update_clone ledger "$LEDGER" "$LEDGER_REF"
fi

pending="$OPS/restart-pending"
if [ "$code_rc" -eq 0 ]; then
  [ -f "$pending" ] || date +%s > "$pending"
  # Ops files are copied by install-ops.sh; say so when the pulled ones differ from the installed ones.
  d="$CODE/kurul/ajan/deploy"
  for pair in "kurul-ajan.service:/etc/systemd/system/kurul-ajan.service" \
              "kurul-ajan-update.service:/etc/systemd/system/kurul-ajan-update.service" \
              "kurul-ajan-update.timer:/etc/systemd/system/kurul-ajan-update.timer" \
              "kurul-ajan-health.service:/etc/systemd/system/kurul-ajan-health.service" \
              "kurul-ajan-health.timer:/etc/systemd/system/kurul-ajan-health.timer" \
              "kurul-ajan-backup.service:/etc/systemd/system/kurul-ajan-backup.service" \
              "kurul-ajan-backup.timer:/etc/systemd/system/kurul-ajan-backup.timer" \
              "kurul-ajan-update.sh:$LIB/kurul-ajan-update.sh" \
              "kurul-ajan-health.py:$LIB/kurul-ajan-health.py" \
              "kurul-ajan-backup.sh:$LIB/kurul-ajan-backup.sh"; do
    src="$d/${pair%%:*}" dst="${pair#*:}"
    if [ -f "$src" ] && [ -f "$dst" ] && ! cmp -s "$src" "$dst"; then
      say "deploy file changed in git: ${pair%%:*}; run: sudo bash $d/install-ops.sh"
    fi
  done
fi

# --- restart -----------------------------------------------------------------------------------

[ -f "$pending" ] || exit 0

if ! systemctl is-active --quiet "$UNIT"; then
  rm -f "$pending" "$OPS/restart-deferred"
  say "code updated; $UNIT is not running, left stopped (it starts on the new code)"
  exit 0
fi

busy_event=""
if [ -f "$WSTATE/busy.json" ]; then
  bpid=$(sed -n 's/.*"pid": *\([0-9][0-9]*\).*/\1/p' "$WSTATE/busy.json" 2>/dev/null)
  mpid=$(systemctl show -p MainPID --value "$UNIT" 2>/dev/null)
  if [ -n "$bpid" ] && [ "$bpid" = "$mpid" ]; then
    busy_event=$(sed -n 's/.*"event_id": *\([0-9][0-9]*\).*/\1/p' "$WSTATE/busy.json" 2>/dev/null)
    busy_event=${busy_event:-?}
  fi
fi

since=$(cat "$pending" 2>/dev/null || date +%s)
waited=$(( $(date +%s) - since ))
if [ -n "$busy_event" ] && [ "$waited" -lt "$MAX_DEFER" ]; then
  if [ ! -f "$OPS/restart-deferred" ]; then
    touch "$OPS/restart-deferred"
    say "restart of $UNIT deferred: busy on event $busy_event (retry every run, at most ${MAX_DEFER}s)"
  fi
  exit 0
fi

# Test gate: the new code must pass the worker's own tests (run as the service user, fake model)
# before the running worker is replaced. On failure the old process keeps running; retried every run.
svc_user=$(systemctl show -p User --value "$UNIT" 2>/dev/null); svc_user=${svc_user:-kurul-ajan}
if [ "${KURUL_UPDATE_TESTS:-1}" = "1" ] && id "$svc_user" >/dev/null 2>&1; then
  if ! err=$(cd "$CODE/kurul" 2>/dev/null && setpriv --reuid="$svc_user" --regid="$(id -gn "$svc_user")" --init-groups \
        env -i HOME=/tmp PATH=/usr/bin:/bin KURUL_LLM=fake PYTHONDONTWRITEBYTECODE=1 \
        timeout 600 python3 -m unittest discover -s ajan/tests -t . 2>&1); then
    problem tests "new code fails the worker tests; $UNIT not restarted: $(printf %s "$err" | tail -n 3 | tr '\n' ' ' | cut -c1-300)"
    exit 0
  fi
  cleared tests
fi

if systemctl restart "$UNIT"; then
  if [ -n "$busy_event" ]; then
    say "restarted $UNIT on new code (waited ${waited}s; event $busy_event is replayed if it was cut)"
  else
    say "restarted $UNIT on new code"
  fi
  rm -f "$pending" "$OPS/restart-deferred"
  cleared restart
else
  problem restart "restart of $UNIT failed; will retry"
fi
exit 0
