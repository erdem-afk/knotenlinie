"""HTTP layer: human API, agent API, pages and the live event stream."""

from __future__ import annotations

import asyncio
import html
import json
import logging
import signal
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qs, quote

from fastapi import Body, Depends, FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from . import core
from .config import Settings
from .core import ApiError
from .mail import Mailer
from .security import HardeningMiddleware, same
from .service import Board, Bus

log = logging.getLogger("kurul")
STATIC = Path(__file__).parent / "static"
COOKIE = "kurul_session"


def safe_next(n: str | None) -> str:
    if not n or not n.startswith("/") or n.startswith("//") or n.startswith("/\\") or len(n) > 300:
        return "/"
    return n


def install_stop_hook(hook) -> callable:
    """Call hook() first when the server receives SIGTERM/SIGINT, then the server's own handler.

    uvicorn installs its handlers with signal.signal before the lifespan starts; we chain in front of
    them so open long-polls can answer before uvicorn's graceful-shutdown timeout cancels them (a
    cancelled request that has not started its response is answered with HTTP 500). Outside the main
    thread (e.g. the test client) this does nothing. Returns a function that restores the handlers.
    """
    saved = {}
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            prev = signal.getsignal(sig)
            if not callable(prev):
                continue

            def handler(signum, frame, prev=prev):
                try:
                    hook()
                except Exception:  # never block the shutdown
                    log.exception("stop hook failed")
                prev(signum, frame)

            signal.signal(sig, handler)
            saved[sig] = prev
        except ValueError:  # not the main thread
            return lambda: None

    def restore():
        for sig, prev in saved.items():
            try:
                if signal.getsignal(sig) is not prev:
                    signal.signal(sig, prev)
            except ValueError:
                pass
    return restore


def create_app(settings: Settings | None = None, mailer: Mailer | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    board = Board(settings, mailer)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        board.bus.attach(asyncio.get_running_loop())
        restore = install_stop_hook(board.bus.close)
        try:
            yield
        finally:
            board.bus.close()
            restore()

    app = FastAPI(title="Knotenlinie Board", lifespan=lifespan, docs_url=None, redoc_url=None,
                  openapi_url=None)
    app.state.board = board
    app.add_middleware(HardeningMiddleware)
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    @app.exception_handler(ApiError)
    async def api_error(request: Request, exc: ApiError):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status)

    # ------------------------------------------------------------ helpers

    def session_cookie(request: Request) -> str | None:
        return request.cookies.get(COOKIE)

    def current_user(request: Request) -> dict:
        u = board.session_user(session_cookie(request))
        if not u:
            raise ApiError(401, "not signed in")
        return u

    def coordinator(user: dict = Depends(current_user)) -> dict:
        if user["role"] != "coordinator":
            raise ApiError(403, "coordinator only")
        return user

    def agent(request: Request) -> None:
        if not settings.agent_token:
            raise ApiError(503, "agent API is disabled (KURUL_AGENT_TOKEN not set)")
        h = request.headers.get("authorization", "")
        given = h[7:] if h[:7].lower() == "bearer " else ""
        if not same(given, settings.agent_token):
            raise ApiError(401, "bad agent token")

    def client_ip(request: Request) -> str:
        return request.client.host if request.client else "unknown"

    def page(name: str) -> FileResponse:
        return FileResponse(STATIC / name, media_type="text/html",
                            headers={"Cache-Control": "no-cache"})

    def int_param(v, name: str) -> int | None:
        if v is None or v == "":
            return None
        try:
            return int(v)
        except ValueError:
            raise ApiError(400, f"{name} must be an integer")

    # ------------------------------------------------------------ pages

    @app.api_route("/", include_in_schema=False, methods=["GET", "HEAD"])
    def index(request: Request):
        if not board.session_user(session_cookie(request)):
            nxt = request.url.path + (("?" + request.url.query) if request.url.query else "")
            target = "/login" + ("" if nxt == "/" else "?next=" + quote(nxt, safe=""))
            return RedirectResponse(target, status_code=303)
        return page("index.html")

    @app.api_route("/login", include_in_schema=False, methods=["GET", "HEAD"])
    def login_page(request: Request):
        if board.session_user(session_cookie(request)):
            return RedirectResponse(safe_next(request.query_params.get("next")), status_code=303)
        return page("login.html")

    @app.api_route("/admin", include_in_schema=False, methods=["GET", "HEAD"])
    def admin_page(request: Request):
        u = board.session_user(session_cookie(request))
        if not u:
            return RedirectResponse("/login?next=%2Fadmin", status_code=303)
        if u["role"] != "coordinator":
            return RedirectResponse("/", status_code=303)
        return page("admin.html")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return FileResponse(STATIC / "icon.svg", media_type="image/svg+xml")

    @app.get("/healthz", include_in_schema=False)
    def healthz():
        return {"ok": True}

    # ------------------------------------------------------------ auth

    @app.post("/auth/request")
    def auth_request(request: Request, data: dict = Body(default={})):
        board.request_login(str(data.get("email") or ""), client_ip(request))
        return {"ok": True, "message": "If this address is on the board, a sign-in link is on its way."}

    def _verify_page(title: str, text: str, form_token: str | None = None, nxt: str = "/",
                     status: int = 200) -> HTMLResponse:
        e = html.escape
        form = ""
        if form_token:
            form = (f'<form method="post" action="/auth/verify">'
                    f'<input type="hidden" name="token" value="{e(form_token)}">'
                    f'<input type="hidden" name="next" value="{e(nxt)}">'
                    f'<button class="btn primary big" type="submit">Sign in</button></form>')
        else:
            form = '<p><a class="btn primary big" href="/login">Get a new link</a></p>'
        doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
               f'<meta name="viewport" content="width=device-width, initial-scale=1">'
               f'<title>Knotenlinie Board</title><link rel="icon" href="/static/icon.svg">'
               f'<link rel="stylesheet" href="/static/style.css"></head>'
               f'<body class="auth-page"><main class="auth-card"><p class="brand">Knotenlinie Board</p>'
               f'<h1>{e(title)}</h1><p class="muted">{e(text)}</p>{form}</main></body></html>')
        return HTMLResponse(doc, status_code=status, headers={"Cache-Control": "no-store"})

    @app.get("/auth/verify", include_in_schema=False)
    def auth_verify_get(request: Request, token: str = "", next: str = "/"):
        # The link only shows a confirmation button. Mail scanners that prefetch links
        # therefore cannot use up the single-use token; the POST below signs in.
        nxt = safe_next(next)
        if not board.limiter.hit(f"verify-ip:{client_ip(request)}", 60, 900):
            return _verify_page("Too many attempts", "Please wait a few minutes and try again.", status=429)
        u = board.peek_login_token(token)
        if not u:
            if board.session_user(session_cookie(request)):
                return RedirectResponse(nxt, status_code=303)
            return _verify_page("This link has expired",
                                "Sign-in links work once and expire after 30 minutes. "
                                "Ask for a new one below.", status=400)
        return _verify_page(f"Welcome, {u['name']}", "Press the button to sign in to the board.",
                            form_token=token, nxt=nxt)

    @app.post("/auth/verify", include_in_schema=False)
    async def auth_verify_post(request: Request):
        origin = request.headers.get("origin")
        if origin and origin != "null" and origin.rstrip("/") != settings.base_url.rstrip("/") \
                and origin.rstrip("/") != f"{request.url.scheme}://{request.url.netloc}":
            return _verify_page("Sign-in refused", "This form was sent from another site.", status=403)
        if not board.limiter.hit(f"verify-ip:{client_ip(request)}", 60, 900):
            return _verify_page("Too many attempts", "Please wait a few minutes and try again.", status=429)
        form = parse_qs((await request.body()).decode("utf-8", "replace"))
        token = (form.get("token") or [""])[0]
        nxt = safe_next((form.get("next") or ["/"])[0])
        session = await run_in_threadpool(board.consume_login_token, token)
        if not session:
            if board.session_user(session_cookie(request)):
                return RedirectResponse(nxt, status_code=303)
            return _verify_page("This link has expired",
                                "Sign-in links work once and expire after 30 minutes. "
                                "Ask for a new one below.", status=400)
        resp = RedirectResponse(nxt, status_code=303)
        resp.set_cookie(COOKIE, session, max_age=60 * 24 * 3600, httponly=True,
                        secure=settings.secure_cookie, samesite="lax", path="/")
        return resp

    @app.post("/auth/logout")
    def auth_logout(request: Request):
        board.logout(session_cookie(request))
        resp = JSONResponse({"ok": True})
        resp.delete_cookie(COOKIE, path="/", httponly=True, secure=settings.secure_cookie, samesite="lax")
        return resp

    # ------------------------------------------------------------ human API

    @app.get("/api/me")
    def me(user: dict = Depends(current_user)):
        return board.me_out(user)

    @app.patch("/api/me")
    def patch_me(data: dict = Body(default={}), user: dict = Depends(current_user)):
        return board.update_me(user, data)

    @app.get("/api/members")
    def members(user: dict = Depends(current_user)):
        return {"members": board.members()}

    @app.get("/api/messages")
    def get_messages(request: Request, user: dict = Depends(current_user)):
        qp = request.query_params
        root = qp.get("root", "none")
        after = int_param(qp.get("after"), "after")
        before = int_param(qp.get("before"), "before")
        limit = max(1, min(int_param(qp.get("limit"), "limit") or 100, 500))
        with board.store.read() as db:
            if root in ("", "none", "null"):
                return {"messages": core.list_feed(db, user["id"], after, before, limit)}
            return core.list_thread(db, int_param(root, "root"), user["id"], after, limit)

    @app.post("/api/messages")
    def post_message(data: dict = Body(default={}), user: dict = Depends(current_user)):
        return board.post_message(user, data.get("body"), data.get("root_id"))

    @app.post("/api/messages/{msg_id}/hide")
    def hide(msg_id: int, user: dict = Depends(current_user)):
        board.hide(user, msg_id)
        return {"ok": True}

    @app.post("/api/messages/{msg_id}/forward")
    def forward(msg_id: int, data: dict = Body(default={}), user: dict = Depends(current_user)):
        return board.forward(user, msg_id, data.get("note"))

    @app.post("/api/cards/{msg_id}/action")
    def card_action(msg_id: int, data: dict = Body(default={}), user: dict = Depends(current_user)):
        return board.card_action(user, msg_id, data.get("action"), data.get("text"))

    @app.post("/api/invites")
    def member_invite(data: dict = Body(default={}), user: dict = Depends(current_user)):
        # Authorization (coordinator, or a member with can_invite) is checked in Board.invite.
        return board.invite(data, user)

    @app.get("/api/questions")
    def questions(user: dict = Depends(current_user)):
        with board.store.read() as db:
            return {"questions": core.list_questions(db, user["id"])}

    @app.get("/api/events")
    def poll_events(after: int | None = None, user: dict = Depends(current_user)):
        """Polling fallback for clients without a working event stream. Without `after`: just the head."""
        if after is None:
            return {"events": [], "last": board.last_event_id()}
        events, last = board.visible_events(user, after)
        return {"events": events, "last": last}

    @app.get("/api/stream")
    async def stream(request: Request):
        user = await run_in_threadpool(current_user, request)
        hdr = request.headers.get("last-event-id") or request.query_params.get("after")
        try:
            start = int(hdr) if hdr else None
        except ValueError:
            start = None
        if start is None:
            start = await run_in_threadpool(board.last_event_id)

        async def gen():
            last = start
            yield f"retry: 3000\nevent: hello\ndata: {json.dumps({'last': last})}\n\n"
            idle = 0.0
            while True:
                if board.bus.closing or await request.is_disconnected():
                    return
                ev = board.bus.snapshot()
                items, last = await run_in_threadpool(board.visible_events, user, last)
                for it in items:
                    yield f"id: {it['id']}\ndata: {json.dumps(it)}\n\n"
                if items:
                    idle = 0.0
                    continue
                await Bus.wait(ev, 2.0)
                idle += 2.0
                if idle >= 20:
                    idle = 0.0
                    if not await run_in_threadpool(board.session_user, session_cookie(request)):
                        yield "event: bye\ndata: {}\n\n"
                        return
                    yield ": ping\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    # ------------------------------------------------------------ coordinator

    @app.get("/api/admin/users")
    def admin_users(user: dict = Depends(coordinator)):
        return {"users": board.admin_users()}

    @app.patch("/api/admin/users/{user_id}")
    def admin_patch_user(user_id: int, data: dict = Body(default={}), user: dict = Depends(coordinator)):
        return board.admin_set_user(user_id, data)

    @app.post("/api/admin/invites")
    def admin_invite(data: dict = Body(default={}), user: dict = Depends(coordinator)):
        return board.invite(data, user)

    @app.get("/api/admin/invites")
    def admin_invites(user: dict = Depends(coordinator)):
        return {"invites": board.admin_invites()}

    @app.get("/api/admin/waiting")
    def admin_waiting(user: dict = Depends(coordinator)):
        return board.admin_waiting()

    @app.get("/api/admin/feasibility")
    def admin_feas(user: dict = Depends(coordinator)):
        return {"reports": board.admin_feasibility()}

    @app.post("/api/admin/questions/{qid}/hold")
    def admin_hold(qid: str, data: dict = Body(default={}), user: dict = Depends(coordinator)):
        return board.admin_hold(user, qid, data.get("reason"))

    @app.post("/api/admin/questions/{qid}/release")
    def admin_release(qid: str, user: dict = Depends(coordinator)):
        return board.admin_allow(user, qid, release=True)

    @app.post("/api/admin/questions/{qid}/approve_run")
    def admin_approve(qid: str, user: dict = Depends(coordinator)):
        return board.admin_allow(user, qid, release=False)

    @app.get("/api/admin/suggestions")
    def admin_suggestions(user: dict = Depends(coordinator)):
        return board.admin_suggestions()

    # ------------------------------------------------------------ agent API

    @app.get("/api/agent/events", dependencies=[Depends(agent)])
    async def agent_events(request: Request, after: int = 0, wait: float = 25):
        wait = max(0.0, min(wait, 30.0))
        loop = asyncio.get_running_loop()
        deadline = loop.time() + wait
        while True:
            ev = board.bus.snapshot()
            events = await run_in_threadpool(board.agent_events, after)
            remaining = deadline - loop.time()
            if events or remaining <= 0 or board.bus.closing or await request.is_disconnected():
                break
            await Bus.wait(ev, min(2.0, remaining))
        last = events[-1]["id"] if events else after
        head = await run_in_threadpool(board.last_event_id)
        return {"events": events, "last": last, "head": head}

    @app.get("/api/agent/thread/{root_id}", dependencies=[Depends(agent)])
    def agent_thread(root_id: int):
        return board.agent_thread(root_id)

    @app.get("/api/agent/recent", dependencies=[Depends(agent)])
    def agent_recent(limit: int = 30):
        return {"messages": board.agent_recent(max(1, min(limit, 200)))}

    @app.get("/api/agent/questions/{qid}", dependencies=[Depends(agent)])
    def agent_get_question(qid: str):
        return board.agent_question(qid)

    @app.post("/api/agent/messages", dependencies=[Depends(agent)])
    def agent_post(request: Request, data: dict = Body(default={})):
        return board.agent_post(data, request.headers.get("idempotency-key"))

    @app.post("/api/agent/questions", dependencies=[Depends(agent)])
    def agent_question(data: dict = Body(default={})):
        return board.agent_create_question(data)

    @app.patch("/api/agent/questions/{qid}", dependencies=[Depends(agent)])
    def agent_patch_question(qid: str, data: dict = Body(default={})):
        return board.agent_patch_question(qid, data)

    @app.put("/api/agent/feasibility/{qid}", dependencies=[Depends(agent)])
    def agent_feasibility(qid: str, data: dict = Body(default={})):
        return board.agent_feasibility(qid, data)

    @app.post("/api/agent/suggestions", dependencies=[Depends(agent)])
    def agent_suggestion(data: dict = Body(default={})):
        return board.agent_suggestion(data)

    return app


def main_app() -> FastAPI:
    """Entry point for uvicorn: `uvicorn kurul_site.app:main_app --factory`."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return create_app()
