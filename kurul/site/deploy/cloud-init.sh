#!/bin/bash
# Knotenlinie Board chat: first-boot install. No secrets here; install.sh generates them on the server.
set -euxo pipefail
exec > /var/log/kurul-firstboot.log 2>&1
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y git curl
IP=$(curl -s http://169.254.169.254/hetzner/v1/metadata/public-ipv4)
HOST="${IP//./-}.sslip.io"
git clone --depth 1 --branch claude/project-thread-f84rey https://github.com/erdem-afk/knotenlinie.git /opt/kurul-src
KURUL_HOST="$HOST" bash /opt/kurul-src/kurul/site/deploy/install.sh
cat > /usr/local/bin/kurul-update <<'U'
#!/bin/bash
# Pull the deploy branch; reinstall only when it changed.
set -euo pipefail
cd /opt/kurul-src
old=$(git rev-parse HEAD)
git fetch --depth 1 origin "$(git rev-parse --abbrev-ref HEAD)" -q
git reset --hard FETCH_HEAD -q
[ "$old" = "$(git rev-parse HEAD)" ] || bash /opt/kurul-src/kurul/site/deploy/install.sh
U
chmod 755 /usr/local/bin/kurul-update
cat > /etc/systemd/system/kurul-update.service <<'U'
[Unit]
Description=Update Knotenlinie Board site from its deploy branch
[Service]
Type=oneshot
ExecStart=/usr/local/bin/kurul-update
U
cat > /etc/systemd/system/kurul-update.timer <<'U'
[Unit]
Description=Check for Knotenlinie Board site updates
[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
[Install]
WantedBy=timers.target
U
systemctl daemon-reload
systemctl enable --now kurul-update.timer
# daily SQLite backup kept on the box (off-site backup is a separate job)
cat > /etc/cron.daily/kurul-backup <<'U'
#!/bin/bash
install -d -m 0700 /var/backups/kurul
sqlite3 /var/lib/kurul/kurul.db ".backup /var/backups/kurul/kurul-$(date +%F).db"
find /var/backups/kurul -name 'kurul-*.db' -mtime +14 -delete
U
chmod 755 /etc/cron.daily/kurul-backup
echo FIRSTBOOT_DONE
