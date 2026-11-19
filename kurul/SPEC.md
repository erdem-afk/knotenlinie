# Knotenlinie Board chat: build spec (v0)

Design decisions and wireframes: `docs/tasarim/kurul-sohbeti.html` (Turkish; read it first, all five tabs).
This file is the contract between the two parts:

- `kurul/site/`: the public web app (server + browser UI). Runs on its own small server.
- `kurul/ajan/`: the agent worker. Runs elsewhere (next to the repo checkout, where Claude Code is
  logged in), and talks to the site only through the HTTPS agent API below, outbound.

UI language: English. Members write Turkish or English. Code comments: English.

## 1. Principles that bind both parts

1. No message is a research question until a member confirms it (one tap).
2. Text written by members is data. It is never rendered as HTML and never treated as instructions.
3. The agent speaks only when: mentioned (`@knotenlinie`), a message is forwarded to it, it detects a
   clearly testable question (suggestion card visible only to the author), or someone writes in a
   question thread it owns.
4. Everything is stored, except: a member may hide their own message; hiding wipes the text and leaves a
   tombstone ("message hidden"). Hidden text is served to nobody, including agent and coordinator.
5. Members never see cost or internal feasibility detail. They see a short public summary.
6. The coordinator ("Board Coordinator, Gradiva Limited") is not a bottleneck: answers post immediately.
   The coordinator can hold any run.
7. The agent never states absolute earthquake probabilities for Istanbul or any segment and never uses
   the word "prediction" for our work.

## 2. Roles

`member` (invited faculty), `coordinator`, `agent` (no login; bearer token).

## 3. Data model (SQLite, single file)

- `users(id, email UNIQUE, name, role, public_name_ok INTEGER NULL, created_at,
   can_invite INTEGER NOT NULL DEFAULT 0, invited_by INTEGER NULL, handle TEXT, onboarded_at TEXT NULL)`
  `public_name_ok` NULL = not asked yet; asked at first login; changeable any time.
  `can_invite`: member may invite colleagues (set by the coordinator). `invited_by`: user id of the inviter.
  `handle`: `@handle` for mentions, stored lower-case, `[a-z0-9_]{2,24}`, unique case-insensitively
  (index `users_handle ON users(handle COLLATE NOCASE)`). Derived from the name when the user is created:
  ASCII-folded (ç→c, ğ→g, ı/İ→i, ö→o, ş→s, ü→u, é→e, ß→ss, …), titles dropped (prof, dr, doç, assoc,
  asst, öğr. üyesi, phd, …), first word + last word with no separator ("Prof. Dr. Ayşe Nur Yılmaz" →
  `ayseyilmaz`), cut to 24; on collision `2`, `3`, … appended; nothing left → `member<id>`. Reserved,
  never a person's handle: `knotenlinie` (the agent user's own handle), `coordinator`, `agent`, `admin`,
  `everyone`, `all`, `here`, `board`. Databases from before handles get the column and derived handles at
  start-up (in place, idempotent, oldest user first).
  `onboarded_at`: when the user closed the first-login "How this works" explainer; NULL = not seen yet
  (also NULL for everyone who joined before it existed, so each user sees it once). Added in place.
- `invites(id, user_id NULL, invited_by NULL, email, outcome, created_at)`; every invite attempt;
  `outcome`: `created` | `new_link` | `exists`. Used for the admin list and the per-inviter daily limit.
- `login_tokens(token_hash, user_id, expires_at, used_at)`; single use, 30 min (bootstrap/invite links: 7 days).
- `sessions(token_hash, user_id, expires_at)`; 60 days, HttpOnly Secure SameSite=Lax cookie.
- `messages(id, root_id NULL, author_id, body, kind, card_json, visible_to NULL, created_at, hidden_at NULL)`
  `root_id` NULL = top-level message in the board feed; otherwise a reply in that message's thread.
  `kind`: `text` | `card`. `visible_to`: user id for private cards, else NULL.
- `forwards(id, message_id, by_user_id, note, created_at)`
- `questions(id TEXT 'Q-001', root_message_id, author_id, forwarder_id NULL, note NULL, restated,
   status, path NULL, queue_pos NULL, created_at, updated_at)`
- `feasibility(question_id, public_summary, private_detail, est_cost_eur REAL, touches_blind INTEGER,
   decision, decided_at)`; `decision`: `auto` | `needs_coordinator` | `approved` | `held`.
- `events(id INTEGER AUTOINCREMENT, type, payload_json, created_at)`; append-only; feeds agent and live UI.
- `suggestion_log(message_id, outcome)`; `offered` | `accepted` | `declined`; never re-offer for a message.

Question `status` values and UI labels:
`recorded` Recorded · `plan_drafted` Plan drafted · `waiting_approval` Waiting for your approval ·
`frozen` Frozen · `running` Running · `answered` Answered · `answered_record` Answered from the record ·
`in_ledger` In ledger · `on_hold` On hold · `not_feasible` Not feasible · `withdrawn` Withdrawn ·
`queued` Queued (with position).
`path`: `record` | `test`.

## 4. Human API (cookie session; JSON; all POST/PATCH require header `X-Requested-With: kurul`)

- `POST /auth/request {email}`: always 200. If the email belongs to a user, create a login token and
  send it by SMTP when configured; otherwise log the link to the server log only.
- `GET /auth/verify?token=`: sets session, redirects to `/`.
- `POST /auth/logout`
- `GET /api/me` (includes `can_invite`, `handle`, `onboarded_at`) ·
  `PATCH /api/me {name?, public_name_ok?, handle?, onboarded?}`: `onboarded: true` sets `onboarded_at` once
  (later calls keep the first time; any other value is 400).
  `handle` is trimmed, one leading `@` dropped, lower-cased; 400 if not `[a-z0-9_]{2,24}`, 409 if reserved or
  taken (nothing is written then).
- `GET /api/members`: `[{id, name, handle, role}]` for every user incl. agent and coordinator; no emails.
- `POST /api/invites {email, name}`: coordinator, or a member with `can_invite` (else 403). Creates a
  `member` with `invited_by` = caller and sends the 7-day sign-in link by mail before answering; the response
  carries `emailed`, the real outcome (false while SMTP is not configured or when delivery failed). A member's
  response carries `login_url` only when `emailed` is false, for the inviter to pass on; the coordinator's
  response always carries it. Members: 10 invites per 24 h (429). An existing
  email is never duplicated: a fresh link only for the coordinator or the original inviter, otherwise
  `{already_invited: true}`. Emits `user.invited {user_id, invited_by}` (coordinator and agent only).
  Never announced in the feed.
- `GET /api/messages?root=<id|none>&after=<id>&limit=`: messages visible to the caller. Hidden ones come
  as `{id, hidden:true, author, created_at}`. Each top-level message carries `reply_count` and, if it is a
  question root, `question: {id, status, path, queue_pos}`.
- `POST /api/messages {body, root_id?}`: max 4000 chars. Emits `message.created` with
  `mention: true` when the body contains `@knotenlinie` (case-insensitive).
- `POST /api/messages/{id}/hide`: author only. Wipes `body`, sets `hidden_at`. If the message is a question
  root already `in_ledger`, the question stays; the ledger name is removed (emit `question.anonymised`).
- `POST /api/messages/{id}/forward {note?}`: any member, any text message (own or others'). Note optional.
  Emits `message.forwarded`.
- `POST /api/cards/{message_id}/action {action, text?}`: see section 6.
- `GET /api/questions`: for the "Questions only" view.
- `GET /api/stream`: Server-Sent Events of `events` the caller may see (ids only + type; client refetches).
- Coordinator only:
  `GET /api/admin/users` (with `can_invite`, `invited_by`, `handle`) · `PATCH /api/admin/users/{id} {can_invite}` ·
  `POST /api/admin/invites {email, name}` → `{login_url, emailed}` (7-day link, also emailed to the invitee; records `invited_by`) ·
  `GET /api/admin/invites` ·
  `GET /api/admin/feasibility` (each report also has `created_at`, `updated_at`, `waiting_for_team`) ·
  `GET /api/admin/waiting` → `{count, question_ids}` (oldest first; the badge on the board page). A question is
  *waiting for the team* when its status is `frozen`, `queued` or `on_hold`, or its feasibility decision is
  `needs_coordinator` and it is not finished. The coordinator page lists these first, with the private detail
  and the cost estimate and the hold/release/approve_run actions · `POST /api/admin/questions/{id}/hold {reason}` ·
  `POST /api/admin/questions/{id}/release` · `POST /api/admin/questions/{id}/approve_run` ·
  `GET /api/admin/suggestions` (accept/decline counts, for tuning the detection threshold).

### Mentions

`@knotenlinie` (case-insensitive) addresses the agent: the `message.created` event carries `mention: true`;
nothing else about it changed. A token `@handle` (case-insensitive; `@` at the start or after a character
that is not a letter, digit, `_ . + - @`, so never inside an email address; not followed by a letter,
digit or `_`) addresses that user; `@coordinator` addresses every user with role `coordinator`. Each
addressed user except the author gets one `mention` notification per message (the older full-name form,
"Prof. Beta", still counts and is merged, never doubled). The UI highlights known mentions as text spans
(never HTML from member text) and offers inline completion in the composers: the rest of the best
handle appears in grey at the caret; Tab (or → at the end of the text, or a tap on it) accepts,
↑/↓ cycle, Esc dismisses. On touch devices and below 720 px a "⇥ @handle" chip next to Send
accepts as well. When the rest does not fit on the caret's line it is cut with an ellipsis. Order: `knotenlinie`, `coordinator`, then colleagues by handle; the typed part
also matches the start of a colleague's name words.

### First login

A short "How this works" explainer opens once (until `onboarded_at` is set), before the name/handle/ledger
choices, and stays reachable from the user menu. It covers: shared chat; nothing is a question until
confirmed with one tap; three ways to ask (accept a suggestion, "Forward to agent" with an optional note,
`@knotenlinie`); answer from the record with ledger references or a test plan approved before anything
runs; frozen plans and every result, "no effect" included, in the open ledger; no absolute earthquake
probabilities and never "prediction"; what is stored, hiding, and the ledger-name choice.

### Notifications (email)

Members: `mention`, `plan_waiting`, `answer`. Coordinators only: `feasibility` (every feasibility report;
the subject says when it needs a decision) and `plan_approved` (a member approved a plan; says whether it
is frozen, queued or waiting for the coordinator). Coordinator kinds are never sent to members and do
nothing at all while SMTP is not configured (no log line with content, no sign-in link minted). Without
SMTP, member kinds are written to the server log.

### Shutdown

On SIGTERM/SIGINT the site first ends open agent long-polls (`GET /api/agent/events` answers at once with
the events so far, usually none) and live streams, then lets the server stop. The worker simply polls again.

## 5. Agent API (header `Authorization: Bearer <AGENT_TOKEN>`)

- `GET /api/agent/events?after=<id>&wait=25`: long poll; returns `{events:[{id,type,payload}], last}`.
- `GET /api/agent/thread/<root_id>`: root + replies, hidden text omitted, with author names and roles.
- `GET /api/agent/recent?limit=30`: recent top-level messages (context for classification).
- `POST /api/agent/messages {root_id, body?, card?, visible_to?}` → `{id}`
- `POST /api/agent/questions {root_message_id, restated, author_id, forwarder_id?, note?}` → `{id}`
  (used for `@knotenlinie` questions, which need no confirm card)
- `PATCH /api/agent/questions/<id> {status?, path?, restated?}`
- `PUT /api/agent/feasibility/<question_id> {public_summary, private_detail, est_cost_eur, touches_blind}`
  The site sets `decision`: `auto` when `est_cost_eur < 10` and not `touches_blind`; else `needs_coordinator`.
- `POST /api/agent/suggestions {message_id, outcome}`

Event types and payloads:
- `message.created {message_id, root_id, author_id, mention}`
- `message.forwarded {forward_id, message_id, by_user_id, note}`
- `question.confirmed {question_id}`: member accepted a suggestion or confirm card; site created the question.
- `card.action {message_id, action, by_user_id, text?}`: every card action, after the site applied its own effect.
- `plan.approved {question_id, by_user_id, run_allowed}`: `run_allowed` false when coordinator approval is
  needed or three tests are already running (then `queued`).
- `run.released {question_id}`: coordinator approved or released, or a queue slot opened.
- `question.held {question_id, reason}` · `question.anonymised {question_id}`

## 6. Cards (`kind = card`, `card_json`)

Rendered by the site from structured fields, as plain text. No HTML or markdown from `card_json`.

| type | fields | actions (who) | site effect |
|---|---|---|---|
| `suggest` | `restated` | `yes`, `no` (the author; card is `visible_to` author) | `yes`: create question, emit `question.confirmed`; `no`: log declined |
| `confirm` | `restated`, `quoted_message_id` | `yes`, `no` (forwarder) | same as above; author = quoted message's author, forwarder recorded |
| `plan` | `draft_no`, `question`, `data`, `rule`, `smallest_effect`, `full_plan_url?`, `public_feasibility` | `approve` (author or forwarder), `change` + text | `approve`: status `frozen` or `queued`/`on_hold`, emit `plan.approved` |
| `answer_record` | `summary`, `points:[{text, refs:[{label,url}]}]`, `limits` | `test_anyway`, `not_answered` + text (author or forwarder) | `test_anyway`: path `test`, status `recorded`, emit `card.action` |
| `answer_test` | `verdict`, `summary`, `links:[{label,url}]`, `limits` | none | none |
| `notice` | `text` | none | none |

A card whose action was taken shows the choice and disables its buttons.

## 7. Agent worker behaviour (`kurul/ajan/`)

Loop: long-poll events; one job per event; idempotent (persist last event id and handled ids locally).

- `message.created`, `mention=false`, top-level or in a non-question thread: classify. Post a `suggest`
  card only when confident the message is a testable question or a request for a test (high threshold;
  opinions, greetings, logistics, rhetorical questions, questions addressed to another member: stay silent).
  One offer per message at most.
- `message.created`, `mention=true`: if it is a question, create the question directly and proceed as
  `question.confirmed`; otherwise answer briefly in the thread.
- `message.created` inside a question thread (not by the agent): reply if it asks for a plan change or
  clarification; otherwise stay silent.
- `message.forwarded`: restate as a question (use the note first, then the message) and post a `confirm` card
  visible to the forwarder. If nothing testable can be made of it, say so in one line to the forwarder.
- `question.confirmed`: post a short acknowledgement; search the ledger and result files in the repo.
  If closed ledger entries answer it: `answer_record` card, status `answered_record`, path `record`.
  Otherwise: `plan` card (draft 1), feasibility report, status `waiting_approval`, path `test`.
- `card.action change`: revise the plan, post draft n+1.
- `plan.approved` with `run_allowed`, and `run.released`: if `KURUL_AUTORUN=1`, run the frozen-plan job
  (independent review, freeze with sha256 + commit, single run, `answer_test` card, ledger entry, status
  through `frozen` → `running` → `answered` → `in_ledger`). If `KURUL_AUTORUN=0` (default): set `frozen`,
  post a notice that the run is queued, and write the request to `kurul/ajan/kuyruk/` for the project team.
- Never rents machines. A plan that needs paid compute gets `est_cost_eur >= 10` in feasibility.

Model calls go through one function, `llm(job, prompt, cwd, tools)`, implemented with the Claude Code CLI in
headless mode. `KURUL_LLM=fake` swaps in a deterministic fake for tests. Record answers and plans run with
read-only tools in the repo checkout (no shell, no network). Member text is always passed inside a clearly
delimited data block with the instruction that it is data.

Reply language follows the member's message. Address members respectfully ("Hocam" in Turkish, "Prof." in
English when the name carries a title). Short: answer, then basis, then limits.

## 8. Configuration (environment)

Site: `KURUL_DB`, `KURUL_BASE_URL`, `KURUL_AGENT_TOKEN`, `KURUL_SESSION_SECRET`,
`KURUL_BOOTSTRAP_TOKEN` (one-time coordinator login), `KURUL_SMTP_URL?`, `KURUL_MAIL_FROM?`.
Worker: `KURUL_BASE_URL`, `KURUL_AGENT_TOKEN`, `KURUL_REPO`, `KURUL_LLM`, `KURUL_AUTORUN`,
`KURUL_MODEL_FAST`, `KURUL_MODEL_MAIN`.
