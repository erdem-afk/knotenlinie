/* Knotenlinie Board: the single chat screen. */
"use strict";

(() => {
  const { h, clear, link, richText, api, when, fullWhen, initials, toast } = K;
  const $ = (id) => document.getElementById(id);

  const LABELS = {
    recorded: "Recorded", plan_drafted: "Plan drafted", waiting_approval: "Waiting for approval",
    frozen: "Frozen", running: "Running", answered: "Answered", answered_record: "Answered from the record",
    in_ledger: "In ledger", on_hold: "On hold", not_feasible: "Not feasible", withdrawn: "Withdrawn",
    queued: "Queued",
  };
  const TEST_TRACK = ["recorded", "plan_drafted", "waiting_approval", "frozen", "running", "answered", "in_ledger"];
  const RECORD_TRACK = ["recorded", "answered_record", "in_ledger"];
  const SIDE_STATES = new Set(["on_hold", "not_feasible", "withdrawn"]);

  const S = {
    me: null, members: [], feed: [], questions: [], view: "board",
    threadId: null, thread: null, hasMore: false, loadingMore: false,
    known: new Map([["knotenlinie", "agent"], ["coordinator", "coordinator"]]), knownKey: "",
  };
  const HANDLE_RE = /^[a-z0-9_]{2,24}$/;
  const RESERVED = new Set(["knotenlinie", "coordinator", "agent", "admin", "everyone", "all", "here", "board"]);
  const touch = window.matchMedia("(hover: none)").matches;
  const sigs = new WeakMap();

  // ------------------------------------------------------------------ rendering helpers

  /** Keyed list update: unchanged items keep their DOM node (and any half-typed input). */
  function renderKeyed(container, items, keyOf, render) {
    const existing = new Map();
    for (const el of Array.from(container.children)) existing.set(el.dataset.key, el);
    let prev = null;
    for (const item of items) {
      const k = String(keyOf(item));
      const sig = S.knownKey + "|" + JSON.stringify(item);  // known @handles change the rendering
      let el = existing.get(k);
      if (!el || sigs.get(el) !== sig) {
        const fresh = render(item);
        fresh.dataset.key = k;
        sigs.set(fresh, sig);
        if (el) el.replaceWith(fresh);
        el = fresh;
      }
      existing.delete(k);
      const want = prev ? prev.nextSibling : container.firstChild;
      if (el !== want) container.insertBefore(el, want);
      prev = el;
    }
    existing.forEach((el) => el.remove());
  }

  function nearBottom(el) { return el.scrollHeight - el.scrollTop - el.clientHeight < 120; }

  function statusLabel(q) {
    if (q.status === "waiting_approval") return q.mine ? "Waiting for your approval" : "Waiting for approval";
    if (q.status === "queued") return q.queue_pos ? `Queued (position ${q.queue_pos})` : "Queued";
    return LABELS[q.status] || q.status;
  }

  function roleTag(role) {
    if (role === "agent") return h("span", { class: "tag agent-tag", text: "agent" });
    if (role === "coordinator") return h("span", { class: "tag coord-tag", text: "Gradiva" });
    return null;
  }

  function avatar(author) {
    const cls = "avatar" + (author.role === "agent" ? " agent" : author.role === "coordinator" ? " coord" : "");
    return h("span", { class: cls, "aria-hidden": "true", text: author.role === "agent" ? "K" : initials(author.name) });
  }

  function privacyNote(m) {
    if (!m.visible_to) return null;
    const who = m.visible_to === S.me.id ? "you" : (m.visible_to_name || "one member");
    return h("span", { class: "privacy", text: `Visible only to ${who}` });
  }

  function qChip(q) {
    return h("span", { class: "qchip st-" + q.status }, h("strong", { text: q.id }), " · ", statusLabel(q));
  }

  // ------------------------------------------------------------------ cards

  function cardStateLine(m) {
    const st = m.card_state;
    if (!st) return null;
    if (st.void) return h("p", { class: "card-state", text: "The message was hidden, so this card is closed." });
    const by = st.by === S.me.id ? "You" : (st.by_name || "A member");
    const t = m.card.type;
    const box = h("div", { class: "card-state" });
    if (t === "suggest" || t === "confirm") {
      if (st.action === "yes") {
        box.append(`${by} recorded it as ${st.question_id || "a question"}. `);
        const q = st.question_id && S.questions.find((x) => x.id === st.question_id);
        const rootId = st.root_message_id || (q && q.root_message_id);
        if (rootId) box.append(h("button", { type: "button", class: "linkish", text: "Open thread",
          onclick: () => openThread(rootId) }));
      } else {
        box.append(t === "suggest" ? `${by} chose “just chatting”. The agent will not ask about this message again.`
          : `${by} chose not to record it.`);
      }
    } else if (t === "plan") {
      if (st.action === "approve") box.append(`${by} approved this plan.`);
      else { box.append(`${by} asked for a change: `); box.append(h("q", { text: st.text || "" })); }
    } else if (t === "answer_record") {
      if (st.action === "test_anyway") box.append(`${by} asked for a new test anyway.`);
      else {
        box.append(`${by} said this does not answer the question.`);
        if (st.text) { box.append(" "); box.append(h("q", { text: st.text })); }
      }
    }
    box.append(h("span", { class: "muted", text: " · " + when(st.at) }));
    return box;
  }

  async function doAction(m, action, text, btns) {
    btns.forEach((b) => { b.disabled = true; });
    try {
      const r = await api("POST", `/api/cards/${m.id}/action`, { action, text: text || undefined });
      if (r.question_id && (action === "yes")) {
        toast(`Recorded as ${r.question_id}.`);
        await refreshAll();
        if (r.root_message_id) openThread(r.root_message_id);
        return;
      }
      if (action === "approve") {
        toast(r.run_allowed ? "Plan approved. The run is queued for the agents."
          : r.status === "queued" ? `Plan approved. It waits in the queue (position ${r.queue_pos}).`
            : "Plan approved. The coordinator will confirm the run.");
      } else if (action === "change") toast("Your change request was sent to the agent.");
      else if (action === "test_anyway") toast("A new test will be planned.");
      else if (action === "not_answered") toast("Thank you. The agent has been told.");
      else if (action === "no") toast("Noted.");
      await refreshAll();
    } catch (e) {
      toast(e.message, "error");
      btns.forEach((b) => { b.disabled = false; });
    }
  }

  /** buttons: [{action, label, primary, text: {label, required, placeholder}}] */
  function cardButtons(m, buttons) {
    const can = new Set(m.can_act || []);
    const usable = buttons.filter((b) => can.has(b.action));
    if (!usable.length) return null;
    const row = h("div", { class: "card-actions" });
    const formSlot = h("div", { class: "card-form-slot" });
    const btnEls = [];
    for (const b of usable) {
      const el = h("button", { type: "button", class: "btn" + (b.primary ? " primary" : ""), text: b.label });
      btnEls.push(el);
      el.addEventListener("click", () => {
        if (!b.text) { doAction(m, b.action, null, btnEls); return; }
        clear(formSlot);
        const ta = h("textarea", { rows: "3", maxlength: "4000", placeholder: b.text.placeholder || "" });
        const send = h("button", { type: "button", class: "btn primary", text: "Send" });
        const cancel = h("button", { type: "button", class: "btn", text: "Cancel", onclick: () => clear(formSlot) });
        send.addEventListener("click", () => {
          const v = ta.value.trim();
          if (b.text.required && !v) { ta.focus(); toast("Please write what should change.", "error"); return; }
          doAction(m, b.action, v, [...btnEls, send, cancel]);
        });
        formSlot.append(h("label", { class: "field-label", text: b.text.label }), ta,
          h("div", { class: "card-actions" }, send, cancel));
        ta.focus();
      });
      row.append(el);
    }
    return h("div", null, row, formSlot);
  }

  function field(label, value) {
    if (!value) return null;
    return h("div", { class: "card-field" }, h("span", { class: "card-field-label", text: label + " " }),
      h("span", { class: "card-field-text", text: value }));
  }

  function renderCard(m) {
    const c = m.card || {};
    const t = c.type;
    const sec = h("section", { class: "card card-" + t });
    // Element.append(null) would insert the text "null"; skip empty parts.
    const nativeAppend = sec.append.bind(sec);
    sec.append = (...parts) => nativeAppend(...parts.filter((p) => p !== null && p !== undefined && p !== false));
    const head = (label) => sec.append(h("p", { class: "card-label", text: label }));

    if ((t === "suggest" || t === "confirm") && m.card_state) {
      // Answered: keep only the outcome, so the feed stays calm.
      sec.classList.add("collapsed");
      head(t === "suggest" ? "Suggestion" : "Forwarded message");
      sec.append(cardStateLine(m));
      return sec;
    }
    if (t === "suggest") {
      head("Suggestion");
      sec.append(h("p", { text: "This reads as a testable question. Shall I record it for the board?" }));
      sec.append(h("blockquote", { class: "quote", text: c.restated }));
      sec.append(cardButtons(m, [
        { action: "yes", label: "Yes, record it", primary: true },
        { action: "no", label: "No, just chatting" },
      ]));
    } else if (t === "confirm") {
      head("Forwarded message");
      sec.append(h("p", { text: "I would record it as this question. Is that right?" }));
      sec.append(h("blockquote", { class: "quote", text: c.restated }));
      sec.append(cardButtons(m, [
        { action: "yes", label: "Yes, record it", primary: true },
        { action: "no", label: "No" },
      ]));
    } else if (t === "plan") {
      head(`Test plan · draft ${c.draft_no}`);
      sec.append(field("Question as we understood it:", c.question));
      sec.append(field("Data:", c.data));
      sec.append(field("Rule fixed in advance:", c.rule));
      sec.append(field("Smallest effect we could see:", c.smallest_effect));
      sec.append(field("Feasibility:", c.public_feasibility));
      if (c.full_plan_url) sec.append(h("p", { class: "card-links" }, link("Read the full plan", c.full_plan_url)));
      if (m.card_blocked === "superseded") sec.append(h("p", { class: "card-state", text: "A newer draft replaced this plan." }));
      sec.append(cardButtons(m, [
        { action: "approve", label: "Approve plan", primary: true },
        { action: "change", label: "Ask for a change",
          text: { label: "What should change?", required: true, placeholder: "For example: use M 5.5 as the lower limit." } },
      ]));
      if (!m.card_state && !(m.can_act || []).length && m.actors && m.actors.length) {
        sec.append(h("p", { class: "card-state", text: "Waiting for approval by " + m.actors.join(" or ") + "." }));
      }
    } else if (t === "answer_record") {
      head("Answered from the record · not a new test");
      sec.append(h("p", { class: "card-summary", text: c.summary }));
      if (c.points && c.points.length) {
        const ol = h("ol", { class: "points" });
        for (const p of c.points) {
          const li = h("li", null, h("span", { text: p.text }));
          for (const r of p.refs || []) { li.append(" "); li.append(h("span", { class: "ref" }, link(r.label, r.url))); }
          ol.append(li);
        }
        sec.append(ol);
      }
      sec.append(field("Limits:", c.limits));
      sec.append(cardButtons(m, [
        { action: "test_anyway", label: "Test it anyway" },
        { action: "not_answered", label: "This does not answer my question",
          text: { label: "What is missing? (optional)", required: false } },
      ]));
    } else if (t === "answer_test") {
      head("Test result · new test");
      sec.append(h("p", { class: "verdict", text: c.verdict }));
      sec.append(h("p", { class: "card-summary", text: c.summary }));
      sec.append(field("Limits:", c.limits));
      if (c.links && c.links.length) {
        sec.append(h("p", { class: "card-links" }, c.links.map((l) => h("span", { class: "ref" }, link(l.label, l.url)))));
      }
    } else {
      sec.classList.add("card-notice");
      sec.append(h("p", { text: c.text || "" }));
    }
    const st = cardStateLine(m);
    if (st) sec.append(st);
    return sec;
  }

  // ------------------------------------------------------------------ messages

  function messageActions(m, ctx) {
    const acts = [];
    const isText = !m.hidden && m.kind === "text";
    if (!ctx.inThread && m.root_id === null) acts.push({ id: "reply", label: "Reply in thread", run: () => openThread(m.id) });
    if (isText) acts.push({ id: "forward", label: "Forward to agent", run: () => openForward(m) });
    if (isText && touch) acts.push({ id: "copy", label: "Copy text", run: () => copyText(m.body) });
    if (isText && m.author.id === S.me.id) acts.push({ id: "hide", label: "Hide message", danger: true, run: () => hideMessage(m) });
    return acts;
  }

  function renderTrack(q) {
    const track = q.path === "record" ? RECORD_TRACK.slice() : TEST_TRACK.slice();
    let cur = track.indexOf(q.status);
    const labels = track.map((s) => (s === "waiting_approval" ? (q.mine ? "Waiting for your approval" : "Waiting for approval") : LABELS[s]));
    if (q.status === "queued") {
      const i = track.indexOf("waiting_approval") + 1;
      track.splice(i, 0, "queued");
      labels.splice(i, 0, statusLabel(q));
      cur = i;
    }
    const ol = h("ol", { class: "track", "aria-label": "Status of " + q.id });
    track.forEach((s, i) => {
      const cls = cur < 0 ? "todo" : i < cur ? "done" : i === cur ? "current" : "todo";
      ol.append(h("li", { class: "step " + cls, "aria-current": i === cur ? "step" : null }, h("span", { text: labels[i] })));
    });
    const wrap = h("div", { class: "qstatus" });
    wrap.append(h("p", { class: "qstatus-head" }, h("strong", { text: q.id }), " · ", statusLabel(q),
      q.forwarder ? h("span", { class: "muted", text: ` · asked by ${q.author}, forwarded by ${q.forwarder}` })
        : h("span", { class: "muted", text: ` · asked by ${q.author}` })));
    wrap.append(ol);
    if (SIDE_STATES.has(q.status)) {
      wrap.append(h("p", { class: "banner st-" + q.status }, h("strong", { text: LABELS[q.status] }),
        q.hold_reason ? ": " + q.hold_reason : ""));
    }
    if (q.public_summary) wrap.append(h("p", { class: "small muted" }, h("strong", { text: "Feasibility: " }), q.public_summary));
    return wrap;
  }

  /** A private suggest/confirm card that is about a message other than `id`. */
  function quotedOther(p, id) {
    const q = p.card && (p.card.type === "suggest" || p.card.type === "confirm") ? p.card.quoted_message_id : null;
    return !!(q && q !== id);
  }

  function renderMessage(m, ctx) {
    ctx = ctx || {};
    const isAgent = m.author.role === "agent";
    const cls = ["msg"];
    if (isAgent) cls.push("agent");
    if (m.hidden) cls.push("is-hidden");
    if (m.visible_to) cls.push("private");
    if (ctx.compact) cls.push("compact");
    const art = h("article", { class: cls.join(" "), "data-id": m.id });
    const main = h("div", { class: "msg-main" });
    const head = h("div", { class: "msg-head" },
      h("span", { class: "name", text: m.author.name }), roleTag(m.author.role),
      h("time", { datetime: m.created_at, title: fullWhen(m.created_at), text: when(m.created_at) }),
      m.moved_from ? h("span", { class: "moved", text: "moved from a thread" }) : null,
      privacyNote(m));
    main.append(head);

    if (m.hidden) {
      main.append(h("p", { class: "tombstone", text: "Message hidden" }));
    } else if (m.kind === "text") {
      const body = h("div", { class: "msg-body" });
      body.append(richText(m.body || "", S.known));
      main.append(body);
    } else {
      main.append(renderCard(m));
    }

    if (!ctx.inThread && m.root_id === null) {
      const meta = h("div", { class: "msg-meta" });
      if (m.question) meta.append(h("button", { type: "button", class: "qchip-btn", onclick: () => openThread(m.id) }, qChip(m.question)));
      if (m.reply_count) {
        meta.append(h("button", { type: "button", class: "replies", onclick: () => openThread(m.id),
          text: m.reply_count === 1 ? "1 reply" : `${m.reply_count} replies` }));
        if (m.last_reply_at) meta.append(h("span", { class: "muted small", text: "last " + when(m.last_reply_at) }));
      }
      if (meta.childNodes.length) main.append(meta);
      if (m.private_replies) {
        const here = m.private_replies.filter((p) => !quotedOther(p, m.id));
        const elsewhere = m.private_replies.filter((p) => quotedOther(p, m.id) && !p.card_state).length;
        if (here.length) {
          const priv = h("div", { class: "inline-private" });
          for (const p of here) priv.append(renderMessage(p, { inThread: true, compact: true }));
          main.append(priv);
        }
        if (elsewhere) {
          main.append(h("button", { type: "button", class: "replies private-hint", onclick: () => openThread(m.id),
            text: "The agent has a note for you about a reply in this thread · Open thread" }));
        }
      }
    }

    if (m._attached && m._attached.length) {
      const priv = h("div", { class: "inline-private" });
      for (const p of m._attached) priv.append(renderMessage(p, { inThread: true, compact: true }));
      main.append(priv);
    }

    art.append(avatar(m.author), main);

    const acts = messageActions(m, ctx);
    if (acts.length) {
      const tools = h("div", { class: "msg-tools", role: "toolbar", "aria-label": "Message actions" });
      for (const a of acts) {
        if (a.id === "copy" || a.id === "hide") continue;
        tools.append(h("button", { type: "button", class: "tool", text: a.label, onclick: a.run }));
      }
      tools.append(h("button", { type: "button", class: "tool more", "aria-label": "More actions", title: "More actions",
        text: "⋯", onclick: (e) => { e.stopPropagation(); openActions(m, acts); } }));
      art.append(tools);
      attachLongPress(art, () => openActions(m, acts));
    }
    return art;
  }

  // The finger lifting after a long press may produce a click; it must not close the sheet it opened.
  let suppressClickUntil = 0;
  document.addEventListener("click", (e) => {
    if (Date.now() < suppressClickUntil) { e.preventDefault(); e.stopPropagation(); suppressClickUntil = 0; }
  }, true);
  // A new touch is a new gesture: its click is wanted.
  document.addEventListener("pointerdown", () => { suppressClickUntil = 0; }, true);

  function attachLongPress(el, fn) {
    let timer = null, sx = 0, sy = 0, fired = false;
    el.addEventListener("pointerdown", (e) => {
      if (e.pointerType !== "touch") return;
      if (e.target.closest("button, a, textarea, input")) return;
      fired = false; sx = e.clientX; sy = e.clientY;
      timer = setTimeout(() => {
        fired = true; timer = null; suppressClickUntil = Date.now() + 1500;
        if (navigator.vibrate) { try { navigator.vibrate(10); } catch (x) { /* ignore */ } }
        fn();
      }, 520);
    });
    const cancel = () => { clearTimeout(timer); timer = null; };
    el.addEventListener("pointermove", (e) => { if (timer && Math.hypot(e.clientX - sx, e.clientY - sy) > 10) cancel(); });
    el.addEventListener("pointerup", () => { if (!fired) suppressClickUntil = 0; cancel(); });
    el.addEventListener("pointercancel", cancel);
    el.addEventListener("contextmenu", (e) => {
      if (!touch) return;
      if (e.target.closest("a, textarea, input")) return;
      e.preventDefault();
      if (!fired) { cancel(); fired = true; fn(); }
    });
  }

  // ------------------------------------------------------------------ feed

  function renderFeed(stick) {
    const scroller = $("feed-scroll");
    const atBottom = stick || nearBottom(scroller);
    const top = $("feed-top");
    clear(top);
    if (S.hasMore) {
      top.append(h("button", { type: "button", class: "btn ghost", text: "Load earlier messages", onclick: loadEarlier }));
    } else if (!S.feed.length) {
      top.append(h("div", { class: "empty" },
        h("p", { class: "empty-title", text: "The board is quiet." }),
        h("p", { class: "muted", text: "Write a message below. A message becomes a research question only when you confirm it." })));
    }
    renderKeyed($("feed"), S.feed, (m) => m.id, (m) => renderMessage(m, {}));
    if (atBottom) scroller.scrollTop = scroller.scrollHeight;
  }

  async function refreshFeed(stick) {
    let url = "/api/messages?root=none&limit=100";
    if (S.feed.length) url = `/api/messages?root=none&after=${S.feed[0].id - 1}&limit=500`;
    const r = await api("GET", url);
    if (!S.feed.length) S.hasMore = r.messages.length >= 100;
    S.feed = r.messages;
    renderFeed(stick);
  }

  async function loadEarlier() {
    if (S.loadingMore || !S.feed.length) return;
    S.loadingMore = true;
    const scroller = $("feed-scroll");
    const before = scroller.scrollHeight - scroller.scrollTop;
    try {
      const r = await api("GET", `/api/messages?root=none&before=${S.feed[0].id}&limit=100`);
      S.hasMore = r.messages.length >= 100;
      S.feed = r.messages.concat(S.feed);
      renderFeed(false);
      scroller.scrollTop = scroller.scrollHeight - before;
    } catch (e) { toast(e.message, "error"); }
    S.loadingMore = false;
  }

  // ------------------------------------------------------------------ questions view

  function renderQuestions() {
    const n = S.questions.length;
    $("q-count").textContent = n ? `(${n})` : "";
    $("q-count-side").textContent = n ? `(${n})` : "";
    const list = $("qlist");
    if (!n) {
      clear(list).append(h("li", { class: "empty" }, h("p", { class: "muted", text: "No questions yet. A message becomes a question when its author confirms it." })));
      return;
    }
    if (list.querySelector(".empty")) clear(list);
    renderKeyed(list, S.questions, (q) => q.id, (q) => h("li", null,
      h("button", { type: "button", class: "qrow", onclick: () => openThread(q.root_message_id) },
        h("span", { class: "qrow-top" }, qChip(q)),
        h("span", { class: "qrow-text", text: q.restated }),
        h("span", { class: "qrow-meta muted small", text:
          `${q.author}${q.forwarder ? ", forwarded by " + q.forwarder : ""} · ${q.reply_count} ${q.reply_count === 1 ? "reply" : "replies"} · updated ${when(q.updated_at)}` }))));
  }

  async function refreshQuestions() {
    const r = await api("GET", "/api/questions");
    S.questions = r.questions;
    renderQuestions();
  }

  function setView(v) {
    S.view = v;
    $("view-board").hidden = v !== "board";
    $("view-questions").hidden = v !== "questions";
    $("tab-board").setAttribute("aria-pressed", String(v === "board"));
    $("tab-questions").setAttribute("aria-pressed", String(v === "questions"));
    $("side-board").toggleAttribute("aria-current", v === "board");
    $("side-questions").toggleAttribute("aria-current", v === "questions");
    if (v === "board") { const s = $("feed-scroll"); s.scrollTop = s.scrollHeight; }
  }

  // ------------------------------------------------------------------ thread

  async function openThread(id) {
    const changed = S.threadId !== id;
    S.threadId = id;
    if (changed) {
      S.thread = null;
      clear($("thread-root")); clear($("thread-replies")); clear($("thread-divider"));
      $("thread-title").textContent = "Thread";
    }
    $("thread").hidden = false;
    $("layout").classList.add("with-thread");
    document.body.classList.add("thread-open");
    const url = new URL(location.href);
    url.searchParams.set("thread", id);
    history.replaceState(null, "", url.pathname + url.search);
    try {
      await refreshThread(true);
      if (changed && !touch) $("thread-input").focus({ preventScroll: true });
    } catch (e) {
      toast(e.status === 404 ? "That thread is not available." : e.message, "error");
      closeThread();
    }
  }

  function closeThread() {
    S.threadId = null; S.thread = null;
    $("thread").hidden = true;
    $("layout").classList.remove("with-thread");
    document.body.classList.remove("thread-open");
    const url = new URL(location.href);
    url.searchParams.delete("thread");
    history.replaceState(null, "", url.pathname + url.search);
  }

  async function refreshThread(stick) {
    const id = S.threadId;
    if (!id) return;
    const r = await api("GET", `/api/messages?root=${id}&limit=500`);
    if (S.threadId !== id) return;
    S.thread = r;
    const scroller = $("thread-scroll");
    const atBottom = stick || nearBottom(scroller);
    const root = r.root;
    $("thread-title").textContent = root.question ? `Thread · ${root.question.id}` : "Thread";
    renderKeyed($("thread-root"), [Object.assign({}, root, { _q: root.question || null })], (m) => m.id, (m) => {
      const wrap = h("div", { class: "thread-root-wrap" });
      wrap.append(renderMessage(Object.assign({}, m, { private_replies: undefined, question: undefined }), { inThread: true }));
      if (m._q) wrap.append(renderTrack(m._q));
      return wrap;
    });
    const n = r.messages.filter((m) => !m.visible_to).length;
    $("thread-divider").textContent = n ? (n === 1 ? "1 reply" : `${n} replies`) : "No replies yet";
    // Private suggest/confirm cards sit directly under the reply they quote.
    const ids = new Set(r.messages.map((m) => m.id));
    const attached = new Map();
    const list = [];
    for (const m of r.messages) {
      if (quotedOther(m, root.id) && ids.has(m.card.quoted_message_id)) {
        const k = m.card.quoted_message_id;
        if (!attached.has(k)) attached.set(k, []);
        attached.get(k).push(m);
      } else list.push(m);
    }
    const items = list.map((m) => (attached.has(m.id) ? Object.assign({}, m, { _attached: attached.get(m.id) }) : m));
    renderKeyed($("thread-replies"), items, (m) => m.id, (m) => renderMessage(m, { inThread: true }));
    if (atBottom) scroller.scrollTop = scroller.scrollHeight;
  }

  // ------------------------------------------------------------------ dialogs and actions

  function openActions(m, acts) {
    const d = $("actions-dialog");
    $("actions-preview").textContent = m.hidden ? "Message hidden"
      : `${m.author.name}: ${(m.body || (m.card ? "card" : "")).slice(0, 120)}`;
    const box = clear($("actions-buttons"));
    for (const a of acts) {
      box.append(h("button", { type: "button", class: "btn sheet-btn" + (a.danger ? " danger" : ""), text: a.label,
        onclick: () => { d.close(); a.run(); } }));
    }
    d.showModal();
  }

  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); toast("Copied."); }
    catch (e) { toast("Copying is not available here.", "error"); }
  }

  let forwardTarget = null, forwardGhost = null;
  function openForward(m) {
    forwardTarget = m;
    const mine = m.author.id === S.me.id;
    $("forward-from").textContent = mine ? "Your message" : `Message from ${m.author.name}`;
    $("forward-quote").textContent = m.body;
    $("forward-note").value = "";
    if (forwardGhost) forwardGhost.update();
    $("forward-credit").textContent = mine ? "You will be credited as the author."
      : `${m.author.name} will be credited as the author. You will be recorded as the person who forwarded it.`;
    $("forward-send").disabled = false;
    $("forward-dialog").showModal();
    $("forward-note").focus();
  }

  async function sendForward(e) {
    e.preventDefault();
    if (!forwardTarget) return;
    const btn = $("forward-send");
    btn.disabled = true;
    try {
      await api("POST", `/api/messages/${forwardTarget.id}/forward`, { note: $("forward-note").value.trim() });
      $("forward-dialog").close();
      toast("Forwarded. The agent will answer you here shortly.");
    } catch (err) {
      toast(err.message, "error");
      btn.disabled = false;
    }
  }

  function confirmBox(title, text, okLabel) {
    const d = $("confirm-dialog");
    $("confirm-title").textContent = title;
    $("confirm-text").textContent = text;
    $("confirm-ok").textContent = okLabel || "OK";
    d.returnValue = "";
    return new Promise((resolve) => {
      d.addEventListener("close", () => resolve(d.returnValue === "ok"), { once: true });
      d.showModal();
    });
  }

  async function hideMessage(m) {
    const ok = await confirmBox("Hide this message?",
      "Its text will be deleted for everyone, including the agent and the coordinator. A note “Message hidden” stays in its place. This cannot be undone.",
      "Hide message");
    if (!ok) return;
    try {
      await api("POST", `/api/messages/${m.id}/hide`);
      toast("Message hidden.");
      await refreshAll();
    } catch (e) { toast(e.message, "error"); }
  }

  // ------------------------------------------------------------------ composers

  function autogrow(ta) {
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight + 2, Math.round(window.innerHeight * 0.35)) + "px";
  }

  // ------------------------------------------------------------------ @mentions

  /** Ghost-completion candidates: the agent, the coordinator alias, then colleagues by handle. */
  function mentionCandidates() {
    const out = [{ handle: "knotenlinie", words: ["knotenlinie", "agent"] },
      { handle: "coordinator", words: ["coordinator", "gradiva"] }];
    const people = S.members.filter((u) => u.handle && u.role !== "agent" && !RESERVED.has(u.handle)
      && !(S.me && u.id === S.me.id));
    people.sort((a, b) => (a.handle < b.handle ? -1 : a.handle > b.handle ? 1 : 0));
    for (const u of people) out.push({ handle: u.handle, words: K.nameWords(u.name) });
    return out;
  }

  /** Handles that are highlighted in message text. Returns true when the set changed. */
  function updateKnown() {
    const known = new Map([["knotenlinie", "agent"], ["coordinator", "coordinator"]]);
    for (const u of S.members) {
      if (u.handle && !known.has(u.handle)) known.set(u.handle, u.role === "agent" ? "agent" : u.role);
    }
    const key = Array.from(known.keys()).sort().join(",");
    if (key === S.knownKey) return false;
    S.known = known; S.knownKey = key;
    return true;
  }

  function setupComposer(form, input, getRoot, after) {
    input.addEventListener("input", () => autogrow(input));
    const ghost = K.ghost.attach(input, mentionCandidates,
      { chipBefore: form.querySelector("button[type=submit]"), onLayout: () => autogrow(input) });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey && !e.isComposing && !touch) {
        e.preventDefault();
        form.requestSubmit();
      }
    });
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const body = input.value.trim();
      if (!body) return;
      const btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      try {
        await api("POST", "/api/messages", { body, root_id: getRoot() });
        input.value = "";
        autogrow(input);
        ghost.update();
        await after();
      } catch (err) { toast(err.message, "error"); }
      btn.disabled = false;
      if (!touch) input.focus();
    });
  }

  // ------------------------------------------------------------------ profile

  function renderMe() {
    $("profile-name").textContent = S.me.name;
    $("profile-avatar").textContent = initials(S.me.name);
    $("profile-signed-in").textContent = `Signed in as ${S.me.name}` + (S.me.handle ? ` (@${S.me.handle})` : "") + ` · ${S.me.email}`;
    $("menu-admin").hidden = S.me.role !== "coordinator";
    $("menu-invite").hidden = !(S.me.role === "member" && S.me.can_invite);
  }

  function renderMembers() {
    const people = S.members.filter((u) => u.role === "member");
    const staff = S.members.filter((u) => u.role !== "member");
    $("member-count").textContent = `· ${people.length} member${people.length === 1 ? "" : "s"}`;
    const li = (u) => h("li", { title: u.handle ? "@" + u.handle : null }, avatar(u), h("span", { text: u.name }),
      u.role === "agent" ? h("span", { class: "muted small", text: " (agent)" }) : null);
    clear($("members-list")).append(...people.map(li));
    clear($("staff-list")).append(...staff.map(li));
  }

  function toggleMenu(open) {
    const menu = $("profile-menu");
    const show = open === undefined ? menu.hidden : open;
    menu.hidden = !show;
    $("profile-btn").setAttribute("aria-expanded", String(show));
  }

  function openProfile() {
    toggleMenu(false);
    $("profile-name-input").value = S.me.name;
    $("profile-handle").value = S.me.handle || "";
    for (const r of document.querySelectorAll("input[name=profile-public]")) {
      r.checked = (r.value === "yes" && S.me.public_name_ok === true) || (r.value === "no" && S.me.public_name_ok === false);
    }
    $("profile-error").textContent = "";
    $("profile-dialog").showModal();
  }

  async function saveProfile(e, nameId, handleId, radioName, errId, dialogId) {
    e.preventDefault();
    const name = $(nameId).value.trim();
    const handle = $(handleId).value.trim().replace(/^@/, "").toLowerCase();
    const sel = document.querySelector(`input[name=${radioName}]:checked`);
    if (!name) { $(errId).textContent = "Please enter your name."; return; }
    if (!HANDLE_RE.test(handle)) { $(errId).textContent = "Your handle needs 2 to 24 characters: a–z, 0–9 or _."; return; }
    if (!sel) { $(errId).textContent = "Please choose yes or no."; return; }
    try {
      S.me = await api("PATCH", "/api/me", { name, handle, public_name_ok: sel.value === "yes" });
      renderMe();
      $(dialogId).close();
      await Promise.allSettled([loadMembers(), refreshAll()]);
      toast("Saved.");
    } catch (err) { $(errId).textContent = err.message; }
  }

  // ------------------------------------------------------------------ how this works

  /** The explainer. first: shown once at first login; closing it in any way records that it was seen. */
  function showHow(first) {
    toggleMenu(false);
    const d = $("how-dialog");
    $("how-ok").textContent = first && S.me.public_name_ok === null ? "Continue" : "Got it";
    return new Promise((resolve) => {
      d.addEventListener("close", async () => {
        if (first) {
          try { S.me = await api("PATCH", "/api/me", { onboarded: true }); } catch (e) { /* shown again next time */ }
        }
        resolve();
      }, { once: true });
      d.showModal();
      d.querySelector(".how-body").scrollTop = 0;
      $("how-ok").focus();
    });
  }

  // ------------------------------------------------------------------ waiting for the team (coordinator)

  async function loadWaiting() {
    if (!S.me || S.me.role !== "coordinator") return;
    let n = 0;
    try { n = (await api("GET", "/api/admin/waiting")).count; } catch (e) { return; }
    for (const id of ["admin-badge", "profile-badge"]) {
      const b = $(id);
      b.textContent = n ? String(n) : "";
      b.hidden = !n;
      b.setAttribute("aria-label", `${n} waiting for the team`);
      b.title = `${n} question${n === 1 ? "" : "s"} waiting for the team`;
    }
  }

  // ------------------------------------------------------------------ invite a colleague

  function openInvite() {
    toggleMenu(false);
    $("invite-name").value = "";
    $("invite-email").value = "";
    $("invite-error").textContent = "";
    $("invite-fields").hidden = false;
    $("invite-result").hidden = true;
    $("invite-link-box").hidden = true;
    $("invite-link").value = "";
    $("invite-send").hidden = false;
    $("invite-send").disabled = false;
    $("invite-cancel").textContent = "Cancel";
    $("invite-dialog").showModal();
    if (!touch) $("invite-name").focus();
  }

  async function sendInvite(e) {
    e.preventDefault();
    $("invite-error").textContent = "";
    const name = $("invite-name").value.trim(), email = $("invite-email").value.trim();
    if (!name) { $("invite-error").textContent = "Please enter your colleague's name."; return; }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(email)) { $("invite-error").textContent = "Please enter a valid email address."; return; }
    $("invite-send").disabled = true;
    try {
      const r = await api("POST", "/api/invites", { name, email });
      let note;
      if (r.already_invited) note = r.message || "This address has already been invited to the board.";
      else if (r.login_url && r.emailed) note = `We emailed a sign-in link to ${email}. The link is also below.`;
      else if (r.login_url) note = r.created ? `${name} can now join the board.` : "This colleague was already invited by you; here is a fresh link.";
      else note = `We emailed a sign-in link to ${email}.`;
      $("invite-note").textContent = note;
      if (r.login_url) {
        $("invite-link").value = r.login_url;
        $("invite-link-box").hidden = false;
      }
      $("invite-fields").hidden = true;
      $("invite-result").hidden = false;
      $("invite-send").hidden = true;
      $("invite-cancel").textContent = "Close";
      if (r.created) loadMembers().catch(() => {});
    } catch (err) {
      $("invite-error").textContent = err.message;
    }
    $("invite-send").disabled = false;
  }

  async function copyInvite() {
    const input = $("invite-link");
    try { await navigator.clipboard.writeText(input.value); toast("Link copied."); }
    catch (e) { input.focus(); input.select(); toast("Press Ctrl+C (or Cmd+C) to copy."); }
  }

  async function loadMembers() {
    const r = await api("GET", "/api/members");
    S.members = r.members;
    renderMembers();
    if (updateKnown()) {  // re-render messages so new @handles are highlighted
      if (S.feed.length) renderFeed(false);
      if (S.threadId && S.thread) refreshThread(false).catch(() => {});
    }
  }

  // ------------------------------------------------------------------ wiring

  async function refreshAll() {
    const jobs = [refreshFeed(false), refreshQuestions(), loadWaiting()];
    if (S.threadId) jobs.push(refreshThread(false));
    const res = await Promise.allSettled(jobs);
    const bad = res.find((r) => r.status === "rejected");
    if (bad && bad.reason && bad.reason.status !== 401) console.warn(bad.reason);
  }

  function wire() {
    $("tab-board").addEventListener("click", () => setView("board"));
    $("tab-questions").addEventListener("click", () => setView("questions"));
    $("side-board").addEventListener("click", () => setView("board"));
    $("side-questions").addEventListener("click", () => setView("questions"));
    $("thread-close").addEventListener("click", closeThread);
    $("thread-back").addEventListener("click", closeThread);
    $("profile-btn").addEventListener("click", (e) => { e.stopPropagation(); toggleMenu(); });
    document.addEventListener("click", (e) => { if (!e.target.closest(".profile")) toggleMenu(false); });
    $("menu-profile").addEventListener("click", openProfile);
    $("menu-invite").addEventListener("click", openInvite);
    $("menu-how").addEventListener("click", () => showHow(false));
    $("invite-form").addEventListener("submit", sendInvite);
    $("invite-copy").addEventListener("click", copyInvite);
    for (const id of ["invite-name", "invite-email"]) $(id).addEventListener("input", () => { $("invite-error").textContent = ""; });
    $("invite-cancel").addEventListener("click", () => $("invite-dialog").close());
    $("menu-logout").addEventListener("click", async () => {
      try { await api("POST", "/auth/logout"); } catch (e) { /* ignore */ }
      location.href = "/login";
    });
    $("profile-form").addEventListener("submit", (e) => saveProfile(e, "profile-name-input", "profile-handle", "profile-public", "profile-error", "profile-dialog"));
    $("profile-cancel").addEventListener("click", () => $("profile-dialog").close());
    $("welcome-form").addEventListener("submit", (e) => saveProfile(e, "welcome-name", "welcome-handle", "welcome-public", "welcome-error", "welcome-dialog"));
    $("welcome-dialog").addEventListener("cancel", (e) => e.preventDefault());
    $("forward-form").addEventListener("submit", sendForward);
    forwardGhost = K.ghost.attach($("forward-note"), mentionCandidates, { chipBefore: $("forward-send") });
    $("forward-cancel").addEventListener("click", () => $("forward-dialog").close());
    $("actions-cancel").addEventListener("click", () => $("actions-dialog").close());
    for (const d of document.querySelectorAll("dialog.sheet")) {
      d.addEventListener("click", (e) => { if (e.target === d) d.close(); });
    }
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !document.querySelector("dialog[open]")) {
        if (!$("profile-menu").hidden) toggleMenu(false);
        else if (S.threadId) closeThread();
      }
    });
    setupComposer($("composer"), $("composer-input"), () => null, () => refreshFeed(true));
    setupComposer($("thread-composer"), $("thread-input"), () => S.threadId,
      () => Promise.allSettled([refreshThread(true), refreshFeed(false)]));
  }

  async function start() {
    if (touch) document.body.classList.add("touch");
    if (window.innerWidth < 520) $("composer-input").placeholder = "Write a message";
    if (touch) $("composer-hint").textContent = "Type @ to address the agent or a colleague; tap the suggestion to complete.";
    wire();
    try {
      S.me = await api("GET", "/api/me");
    } catch (e) { return; }
    renderMe();
    await Promise.allSettled([loadMembers(), refreshQuestions(), refreshFeed(true)]);
    const t = parseInt(new URLSearchParams(location.search).get("thread") || "", 10);
    if (t) openThread(t);
    K.live((events) => {
      if (events.some((e) => e.type === "visible" || e.type === "reconnected")) loadMembers().catch(() => {});
      refreshAll();
    });
    loadWaiting();
    if (!S.me.onboarded_at) await showHow(true);
    if (S.me.public_name_ok === null) {
      $("welcome-name").value = S.me.name;
      $("welcome-handle").value = S.me.handle || "";
      $("welcome-dialog").showModal();
    } else if (!touch) {
      $("composer-input").focus();
    }
  }

  start();
})();
