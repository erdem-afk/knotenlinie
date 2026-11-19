# Knotenlinie Board: site

The web app for the board chat (contract: `../SPEC.md`). FastAPI + SQLite, one HTML page with
vanilla JS, no build step and no external requests.

## Run locally

```sh
cd kurul/site
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
KURUL_DB=./kurul.db KURUL_BASE_URL=http://localhost:8000 \
KURUL_AGENT_TOKEN=dev-agent-token KURUL_BOOTSTRAP_TOKEN=dev-boot \
.venv/bin/uvicorn kurul_site.app:main_app --factory --port 8000
```

Open `http://localhost:8000/auth/verify?token=dev-boot` once to sign in as the coordinator, then
invite members on `/admin` (it emails the sign-in link to the invitee and also shows it for you to
copy). Without SMTP, every email (sign-in links, notifications) is written to the server log instead.

Run with one worker: live updates and rate limits are kept in process memory.

## Environment

| Variable | Meaning |
|---|---|
| `KURUL_DB` | SQLite file (WAL mode). Default `kurul.db`. |
| `KURUL_BASE_URL` | Public URL, used in links. Cookies are `Secure` unless it starts with `http://localhost` or `http://127.0.0.1`. |
| `KURUL_AGENT_TOKEN` | Bearer token for `/api/agent/*`. Unset: the agent API answers 503. |
| `KURUL_SESSION_SECRET` | Key for hashing tokens (HMAC-SHA256). Unset: generated once and kept in the database. |
| `KURUL_BOOTSTRAP_TOKEN` | Accepted once (7 days) as the coordinator's login token when the coordinator is first created. Unset: a link is generated and logged. |
| `KURUL_COORDINATOR_EMAIL` | Coordinator address. Default `coordinator@invalid`. |
| `KURUL_SMTP_URL` | Optional. `smtp://user:pass@host:587` (STARTTLS), `smtps://…:465`, or `smtp://host:25`. |
| `KURUL_MAIL_FROM` | Optional sender. |

## Tests

```sh
.venv/bin/python -m pytest -q
```

## Deploy (Ubuntu 24.04)

`sudo KURUL_HOST=board.example.org bash deploy/install.sh` installs Caddy (automatic TLS), a
`kurul` system user, a venv in `/opt/kurul/site`, data in `/var/lib/kurul`, the systemd unit
`kurul-site` (uvicorn on 127.0.0.1:8000) and, on first run only, `/etc/kurul/env` with fresh
random secrets. Re-run it to update.
