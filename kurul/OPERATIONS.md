# Knotenlinie Board: operations runbook

Two servers. Placeholders: `<site-host>` (public name of the board), `<deploy-branch>` (the branch
both servers deploy from), `<ledger-branch>` (`KURUL_REPO_REF`). All commands run as root unless
shown otherwise.

## 1. Where everything lives

### Site server (`kurul/site/`)

| What | Where |
|---|---|
| Git clone the server deploys from | `/opt/kurul-src` (on `<deploy-branch>`) |
| Running app + venv (copied from the clone by `install.sh`) | `/opt/kurul/site` |
| Service | `kurul-site` (uvicorn on `127.0.0.1:8000`, user `kurul`) |
| Database (SQLite) | `/var/lib/kurul/kurul.db` |
| Secrets and settings | `/etc/kurul/env` (root, 0600): `KURUL_BASE_URL`, `KURUL_AGENT_TOKEN`, `KURUL_SESSION_SECRET`, `KURUL_BOOTSTRAP_TOKEN`, `KURUL_COORDINATOR_EMAIL`, `KURUL_SMTP_URL`, `KURUL_MAIL_FROM` |
| TLS / reverse proxy | Caddy: `/etc/caddy/Caddyfile` (rewritten on every deploy; do not hand-edit), host name in `/etc/systemd/system/caddy.service.d/kurul.conf` (`KURUL_HOST=`), access log `/var/log/caddy/kurul.log` |
| Auto-deploy | `kurul-update.timer` → `/usr/local/bin/kurul-update` |
| Backups | `/var/backups/kurul/kurul-YYYY-MM-DD.db` (`/etc/cron.daily/kurul-backup`, 14 days) |
| First-boot log | `/var/log/kurul-firstboot.log` |
| Health endpoint | `https://<site-host>/healthz` → `{"ok": true}` |

### Worker server (`kurul/ajan/`)

| What | Where |
|---|---|
| Worker code clone | `/opt/kurul-ajan/code` (on `<deploy-branch>`; code in `kurul/ajan/`) |
| Ledger clone (read by the model) | `/opt/kurul-ajan/ledger` (`KURUL_REPO`, on `<ledger-branch>`) |
| Service | `kurul-ajan` (user `kurul-ajan`) |
| Secrets and settings | `/etc/kurul-ajan.env` (root, 0600): `KURUL_BASE_URL`, `KURUL_AGENT_TOKEN`, model and behaviour settings |
| Claude Code CLI login | home of the `kurul-ajan` user (`/home/kurul-ajan`) |
| State | `/var/lib/kurul-ajan`: `ajan.sqlite3` (cursor, handled events, cards, questions), `coordinator.jsonl`, `kuyruk/` (queued run requests), `worktrees/` (only with `KURUL_AUTORUN=1`), `heartbeat`, `busy.json`, `usage.jsonl`, `health.json` |
| Ops scripts (installed copies) | `/usr/local/lib/kurul-ajan-ops/` |
| Ops timers | `kurul-ajan-update.timer` (5 min), `kurul-ajan-health.timer` (10 min), `kurul-ajan-backup.timer` (daily) |
| Updater state (pending restart, open problems) | `/var/lib/kurul-ajan-ops/` |
| Backups | `/var/backups/kurul-ajan/kurul-ajan-state-YYYY-MM-DD.tar.gz` (14 kept) |

Install or refresh the worker's ops timers (idempotent, prints what it did):

```sh
sudo bash /opt/kurul-ajan/code/kurul/ajan/deploy/install-ops.sh
```

## 2. How deploy works

**Site: a push is a deploy.** Every 5 minutes `kurul-update` fetches `<deploy-branch>` into
`/opt/kurul-src` and resets to it (`git reset --hard`, so a force push deploys too). Only when the
commit changed does it run `kurul/site/deploy/install.sh`: rsync to `/opt/kurul/site`, pip install,
rewrite the Caddyfile, restart `kurul-site`, reload Caddy. Log: `journalctl -u kurul-update`.

**Worker: the same, after `install-ops.sh`.** Every 5 minutes `kurul-ajan-update`:

- fetches and fast-forwards the code clone on its checked-out branch (or `KURUL_CODE_BRANCH` if set
  in `/etc/kurul-ajan.env`) and the ledger clone on `KURUL_REPO_REF`;
- runs git as the owner of each clone (root only for root-owned clones), so ownership never changes;
  the unit itself runs as root because it restarts `kurul-ajan`;
- only fast-forwards. A force push, local commits or another checked-out branch are logged once and
  left alone. To accept a force push on the code clone:
  `sudo -u <clone-owner> git -C /opt/kurul-ajan/code fetch origin <deploy-branch> && sudo -u <clone-owner> git -C /opt/kurul-ajan/code reset --hard FETCH_HEAD`;
- restarts `kurul-ajan` only when the code moved, only if it is running (a stopped worker stays
  stopped), and not while it is processing an event (`busy.json`); a deferred restart is retried
  every run and forced after 60 minutes (`KURUL_UPDATE_MAX_DEFER`). The worker is idempotent: an
  event cut by a restart is replayed without double posts;
- never fails on a network error: one log line when a problem starts, one when it clears.

Not automatic: changes to the ops files themselves or to `kurul-ajan.service`. The updater logs
`deploy file changed in git: ...` when that happens; then run `install-ops.sh` again (ops files), or
for the worker unit: `install -m 0644 /opt/kurul-ajan/code/kurul/ajan/deploy/kurul-ajan.service /etc/systemd/system/ && systemctl daemon-reload && systemctl restart kurul-ajan`.

## 3. Move the site to its final domain

The first install uses a temporary name. To switch to `<site-host>`:

1. **DNS**: create an `A` record `<site-host>` → the site server's public IPv4 (plus `AAAA` if the
   server has IPv6). Wait until `dig +short <site-host>` returns it. Ports 80 and 443 must be open:
   Caddy gets the certificate by itself.
2. **Site env**: in `/etc/kurul/env` set `KURUL_BASE_URL=https://<site-host>`. Do **not** change
   `KURUL_SESSION_SECRET` (that would void every session and every sign-in link).
3. **Caddy host**:
   ```sh
   printf '[Service]\nEnvironment=KURUL_HOST=%s\n' '<site-host>' > /etc/systemd/system/caddy.service.d/kurul.conf
   systemctl daemon-reload && systemctl restart caddy   # restart, not reload: the variable is read at start
   ```
   (Equivalent: `KURUL_HOST=<site-host> bash /opt/kurul-src/kurul/site/deploy/install.sh`.)
   Optional transition: `KURUL_HOST=<site-host>, <old-host>` serves both names for a while; check
   with `caddy validate --config /etc/caddy/Caddyfile` under that environment before restarting.
4. `systemctl restart kurul-site`, then `curl -fsS https://<site-host>/healthz`.
5. **Worker env**: in `/etc/kurul-ajan.env` set `KURUL_BASE_URL=https://<site-host>`, then
   `systemctl restart kurul-ajan`. The health check reads the env file on every run.
6. Check: `journalctl -u kurul-ajan -n 20` (polls succeed), `systemctl start kurul-ajan-health`.

What happens to links and sessions (from the code): sign-in tokens are stored as an HMAC of the
token (keyed with `KURUL_SESSION_SECRET`) and are not tied to a host name; links are built from
`KURUL_BASE_URL` when sent. So a link already sent still holds a valid token until it is used or
expires (30 minutes; invite and bootstrap links 7 days), but its URL names the old host and stops
working once Caddy no longer serves that host (unless the old host is kept as in step 3, or the user
swaps the host name in the link by hand). Session cookies belong to the old host name: everyone signs
in once more on `<site-host>` (request a new link on the login page). Data is unaffected.

## 4. Configure SMTP (site)

In `/etc/kurul/env` (read by `kurul_site/config.py`; delivery in `kurul_site/mail.py`):

```sh
KURUL_SMTP_URL=smtp://USER:PASSWORD@smtp.provider.example:587    # STARTTLS (any port other than 25)
# KURUL_SMTP_URL=smtps://USER:PASSWORD@smtp.provider.example:465 # implicit TLS
# KURUL_SMTP_URL=smtp://relay.local:25                            # plain, no TLS (local relay only)
KURUL_MAIL_FROM=Knotenlinie Board <board@<site-host>>
```

- User and password are URL-decoded: write `@` as `%40`, `:` as `%3A`, `/` as `%2F`, `%` as `%25`.
- No quotes needed (systemd environment file; the rest of the line is the value).
- The From address must be allowed by the provider (SPF/DKIM for `<site-host>`'s domain).
- `systemctl restart kurul-site`. Test: request a sign-in link for your own address on the login
  page; `journalctl -u kurul-site | grep -i mail` shows `mail sent` or `mail delivery failed`.
- Without `KURUL_SMTP_URL` nothing is sent: the message and its link go to the `kurul-site` log, and
  invite responses carry `login_url` for the inviter to pass on; `/admin` then says the email could not be
  sent (it says the same when SMTP is configured but delivery fails). With SMTP the invitation email goes
  out, and `/admin` still shows the link.

## 5. Rotate tokens

**Agent token** (shared secret between site and worker):

```sh
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'   # new value
# site server: set KURUL_AGENT_TOKEN in /etc/kurul/env, then
systemctl restart kurul-site
# worker server: set the same KURUL_AGENT_TOKEN in /etc/kurul-ajan.env, then
systemctl restart kurul-ajan
```

Between the two steps the worker gets 401 and backs off; no events are lost (it resumes from its
cursor).

**Claude token** (the CLI login of the `kurul-ajan` user):

- Interactive login: `sudo -u kurul-ajan -H claude`, then `/login`, finish in the browser, `/exit`.
- If `/etc/kurul-ajan.env` carries a token variable for the CLI instead (for example
  `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`, or `ANTHROPIC_API_KEY`), replace the value
  there. The worker passes its environment to the CLI (only `KURUL_AGENT_TOKEN` is removed).
- Revoke the old token/session in the account's console, then `systemctl restart kurul-ajan`.
- Check configuration as the service sees it:
  `systemd-run --pty --wait -p User=kurul-ajan -p EnvironmentFile=/etc/kurul-ajan.env -p WorkingDirectory=/opt/kurul-ajan/code/kurul /usr/bin/python3 -m ajan check`;
  a real call then shows up in `usage.jsonl` with `"ok": true`.

## 6. Stop the agent quickly

- `systemctl stop kurul-ajan`: stops now. The updater does not start a stopped worker. Survives
  reboots only with `systemctl disable --now kurul-ajan`.
- Also freeze code updates: `systemctl disable --now kurul-ajan-update.timer`.
- From the site server (worker server unreachable): change `KURUL_AGENT_TOKEN` in `/etc/kurul/env`
  and `systemctl restart kurul-site`; the agent can no longer read or post.
- Individual runs: the coordinator can hold any question in the admin page.
- On restart the worker processes every event since its cursor (its backlog). With
  `KURUL_AUTORUN=0` nothing runs without an approved plan.

## 7. Backups

| Backup | Where | Kept |
|---|---|---|
| Site database | site server `/var/backups/kurul/kurul-YYYY-MM-DD.db` (SQLite `.backup`) | 14 days |
| Worker state | worker server `/var/backups/kurul-ajan/kurul-ajan-state-YYYY-MM-DD.tar.gz` | newest 14 |

**Nothing is backed up off-site.** Each backup sits on the same disk as what it protects; losing a
server loses its backups. Also not in any backup: `/etc/kurul/env` and `/etc/kurul-ajan.env`
(secrets: keep a copy in the coordinator's password manager), the Claude CLI login, Caddy's
certificates (reissued automatically), logs and the journal, and, with `KURUL_AUTORUN=1`, the
`kurul/q-nnn` branches and commits in the ledger clone (never pushed by the agent; the worktree files
are in the state backup, the git history is not). Code and ledger are in git.

Restore the worker state: `systemctl stop kurul-ajan`, empty `/var/lib/kurul-ajan`, then
`tar -xzf <archive> -C /var/lib/kurul-ajan && chown -R kurul-ajan: /var/lib/kurul-ajan`,
`systemctl start kurul-ajan`. Restore the site: `systemctl stop kurul-site`, copy the backup to
`/var/lib/kurul/kurul.db`, delete `kurul.db-wal` and `kurul.db-shm`, `chown kurul: /var/lib/kurul/kurul.db`,
`systemctl start kurul-site`.

## 8. Health and usage

Health (worker server, every 10 minutes): unit active, `https://<site-host>/healthz` reachable, last
successful long-poll younger than 5 minutes (a long event in progress is allowed up to 4 x
`KURUL_LLM_TIMEOUT`, or `KURUL_RUN_TIMEOUT` + 30 min with autorun).

```sh
journalctl -u kurul-ajan-health -o cat -n 20 | grep KURUL-HEALTH   # KURUL-HEALTH OK ... | FAIL <reasons>
journalctl -u kurul-ajan-health -p err --since today                # failures only
cat /var/lib/kurul-ajan/health.json
systemctl list-timers 'kurul-ajan-*'; systemctl --failed
journalctl -u kurul-ajan-update -o cat -n 50                        # updates, deferred restarts, problems
journalctl -u kurul-ajan -f                                         # worker log, one JSON object per line
```

There is no external alerting; look at these, or wire the `KURUL-HEALTH FAIL` line into whatever
the coordinator already watches.

Usage: one line per model call in `/var/lib/kurul-ajan/usage.jsonl` (`ts`, `job`, `model` alias,
`seconds`, `ok`, `error`, and when the CLI reports them `total_cost_usd`, `duration_ms`,
`num_turns`, `input_tokens`, `output_tokens`, cache token counts, `models`). Cost is internal: it is
never shown to members. Summary per day and job:

```sh
python3 - <<'PY'
import collections, json
agg = collections.defaultdict(lambda: [0, 0.0, 0, 0])
for line in open("/var/lib/kurul-ajan/usage.jsonl"):
    r = json.loads(line)
    a = agg[(r["ts"][:10], r["job"], r["model"])]
    a[0] += 1; a[1] += r.get("total_cost_usd") or 0
    a[2] += r.get("input_tokens") or 0; a[3] += r.get("output_tokens") or 0
for k, (n, usd, ti, to) in sorted(agg.items()):
    print(*k, f"calls={n} usd={usd:.2f} in={ti} out={to}")
PY
```
