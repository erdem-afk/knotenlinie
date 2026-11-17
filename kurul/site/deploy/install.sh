#!/usr/bin/env bash
# Idempotent installer for Ubuntu 24.04. Run as root from a checkout:
#   sudo KURUL_HOST=board.example.org bash kurul/site/deploy/install.sh
# Re-running updates the code and venv and restarts the service. Secrets are never written by
# this script except a freshly generated /etc/kurul/env on first install (root-only, 0600).
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
APP=/opt/kurul/site
DATA=/var/lib/kurul
ENVFILE=/etc/kurul/env
HOST="${KURUL_HOST:-}"

[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 1; }

apt-get update -y
apt-get install -y python3 python3-venv rsync caddy sqlite3

id kurul >/dev/null 2>&1 || useradd --system --home "$DATA" --shell /usr/sbin/nologin kurul
install -d -o kurul -g kurul -m 0700 "$DATA"
install -d -o root -g root -m 0755 /opt/kurul
install -d -o root -g root -m 0700 /etc/kurul

rsync -a --delete --exclude .venv --exclude tests --exclude '__pycache__' --exclude '*.db*' "$SRC/" "$APP/"
[ -x "$APP/.venv/bin/python" ] || python3 -m venv "$APP/.venv"
"$APP/.venv/bin/pip" install --quiet --upgrade pip
"$APP/.venv/bin/pip" install --quiet -r "$APP/requirements.txt"
chown -R root:root "$APP"

if [ ! -f "$ENVFILE" ]; then
  [ -n "$HOST" ] || { echo "first install: set KURUL_HOST=your.domain" >&2; exit 1; }
  rnd() { python3 -c 'import secrets; print(secrets.token_urlsafe(32))'; }
  umask 077
  cat > "$ENVFILE" <<ENV
KURUL_DB=$DATA/kurul.db
KURUL_BASE_URL=https://$HOST
KURUL_AGENT_TOKEN=$(rnd)
KURUL_SESSION_SECRET=$(rnd)
KURUL_BOOTSTRAP_TOKEN=$(rnd)
KURUL_COORDINATOR_EMAIL=coordinator@invalid
# KURUL_SMTP_URL=smtp://user:password@smtp.example.org:587
# KURUL_MAIL_FROM=Knotenlinie Board <board@example.org>
ENV
  echo "Wrote $ENVFILE. First coordinator login: https://$HOST/auth/verify?token=<KURUL_BOOTSTRAP_TOKEN from that file>"
fi
chmod 0600 "$ENVFILE"

install -m 0644 "$SRC/deploy/kurul-site.service" /etc/systemd/system/kurul-site.service
install -m 0644 "$SRC/deploy/Caddyfile.template" /etc/caddy/Caddyfile
install -d -o caddy -g caddy /var/log/caddy
if [ -n "$HOST" ]; then
  install -d /etc/systemd/system/caddy.service.d
  printf '[Service]\nEnvironment=KURUL_HOST=%s\n' "$HOST" > /etc/systemd/system/caddy.service.d/kurul.conf
fi

systemctl daemon-reload
systemctl enable kurul-site caddy
systemctl restart kurul-site
systemctl reload-or-restart caddy
systemctl --no-pager --lines=0 status kurul-site
