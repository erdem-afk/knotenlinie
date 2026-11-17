/* Shared helpers for the board, login and coordinator pages.
   All user and card text is inserted with textContent / text nodes, never as HTML. */
"use strict";

const K = (() => {
  /** Build an element. attrs: class, text, on<Event>, dataset via data-*, everything else as attribute. */
  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (v === null || v === undefined || v === false) continue;
        if (k === "class") el.className = v;
        else if (k === "text") el.textContent = v;
        else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2), v);
        else if (v === true) el.setAttribute(k, "");
        else el.setAttribute(k, String(v));
      }
    }
    for (const c of children.flat()) {
      if (c === null || c === undefined || c === false) continue;
      el.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
    }
    return el;
  }

  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); return el; }

  /** Only http(s) URLs become links. */
  function safeUrl(u) {
    if (typeof u !== "string") return null;
    try {
      const p = new URL(u, location.href);
      return (p.protocol === "https:" || p.protocol === "http:") ? p.href : null;
    } catch (e) { return null; }
  }

  function link(label, url) {
    const href = safeUrl(url);
    if (!href) return h("span", { text: label });
    return h("a", { href, target: "_blank", rel: "noopener noreferrer", text: label });
  }

  /** Text with bare http(s) URLs turned into links; everything else stays plain text. */
  function linkify(text) {
    const frag = document.createDocumentFragment();
    const re = /https?:\/\/[^\s<>"']+[^\s<>"'.,;:!?)\]]/g;
    let last = 0, m;
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      frag.appendChild(link(m[0], m[0]));
      last = m.index + m[0].length;
    }
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    return frag;
  }

  // Mirrors kurul_site/handles.py: ASCII folding and the titles dropped from names.
  const FOLD = { "ı": "i", "İ": "i", "ß": "ss", "æ": "ae", "Æ": "ae", "ø": "o", "Ø": "o", "đ": "d", "Đ": "d",
    "ð": "d", "Ð": "d", "ł": "l", "Ł": "l", "œ": "oe", "Œ": "oe", "þ": "th", "Þ": "th", "ħ": "h", "Ħ": "h" };
  const TITLES = new Set(["prof", "professor", "dr", "doc", "docent", "assoc", "asst", "assist", "yrd", "ogr",
    "uyesi", "ars", "gor", "phd", "md", "mr", "mrs", "ms", "dipl", "ing", "emer", "emeritus"]);

  function fold(s) {
    return String(s || "").replace(/[ıİßæÆøØđĐðÐłŁœŒþÞħĦ]/g, (c) => FOLD[c])
      .normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();
  }

  function nameWords(name) {
    return fold(name).split(/[^a-z0-9]+/).filter((w) => w && !TITLES.has(w));
  }

  // An @handle token: not after a letter, digit, "_", ".", "+", "-" or "@" (so never inside an email
  // address), and not followed by a letter, digit, "_" or "@". Same rule as the server.
  const MENTION_RE = /(^|[^\p{L}\p{N}_.+\-@])@([A-Za-z0-9_]{2,24})(?![\p{L}\p{N}_@])/gu;

  /**
   * Plain text with links (linkify) and known @mentions wrapped in <span class="mention">.
   * known: Map lower-case handle -> kind ("agent" | "coordinator" | "member"). Text nodes only.
   */
  function richText(text, known) {
    const frag = linkify(text);
    if (!known || !known.size) return frag;
    for (const node of Array.from(frag.childNodes)) {
      if (node.nodeType !== Node.TEXT_NODE) continue;
      const t = node.nodeValue;
      const parts = [];
      let last = 0, m;
      MENTION_RE.lastIndex = 0;
      while ((m = MENTION_RE.exec(t)) !== null) {
        const kind = known.get(m[2].toLowerCase());
        if (!kind) continue;
        const at = m.index + m[1].length;
        if (at > last) parts.push(document.createTextNode(t.slice(last, at)));
        parts.push(h("span", { class: "mention mention-" + kind, text: "@" + m[2] }));
        last = at + 1 + m[2].length;
      }
      if (!parts.length) continue;
      if (last < t.length) parts.push(document.createTextNode(t.slice(last)));
      node.replaceWith(...parts);
    }
    return frag;
  }

  class ApiError extends Error {
    constructor(status, detail) { super(detail); this.status = status; }
  }

  async function api(method, url, body) {
    const opts = { method, credentials: "same-origin", headers: { "X-Requested-With": "kurul" } };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    let r;
    try { r = await fetch(url, opts); }
    catch (e) { throw new ApiError(0, "The connection failed. Please check your network."); }
    if (r.status === 401 && !url.startsWith("/auth/")) {
      const next = location.pathname + location.search;
      location.href = "/login" + (next === "/" ? "" : "?next=" + encodeURIComponent(next));
      throw new ApiError(401, "Please sign in again.");
    }
    let data = {};
    try { data = await r.json(); } catch (e) { /* empty body */ }
    if (!r.ok) {
      let d = data && data.detail;
      if (Array.isArray(d)) d = "The request was not understood.";
      throw new ApiError(r.status, d || ("Something went wrong (" + r.status + ")."));
    }
    return data;
  }

  const timeFmt = new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit" });
  const dayFmt = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short" });
  const yearFmt = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric" });

  function when(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    const now = new Date();
    if (d.toDateString() === now.toDateString()) return timeFmt.format(d);
    if (d.getFullYear() === now.getFullYear()) return dayFmt.format(d) + ", " + timeFmt.format(d);
    return yearFmt.format(d);
  }

  function fullWhen(iso) {
    return iso ? new Date(iso).toLocaleString("en-GB") : "";
  }

  function initials(name) {
    const parts = String(name || "?").replace(/^(prof\.?|dr\.?|doç\.?|doc\.?)\s+/i, "").split(/\s+/).filter(Boolean);
    return (parts[0] || "?").charAt(0).toUpperCase();
  }

  let toastTimer = null;
  function toast(msg, kind) {
    let el = document.getElementById("toast");
    if (!el) { el = h("div", { id: "toast", role: "status", "aria-live": "polite" }); document.body.appendChild(el); }
    el.textContent = msg;
    el.className = "toast show" + (kind ? " " + kind : "");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.className = "toast"; }, kind === "error" ? 6000 : 3500);
  }

  /**
   * Live updates: Server-Sent Events with reconnect; while the stream is down,
   * poll /api/events every 5 s. onChange(events) is called (debounced) on news.
   */
  function live(onChange) {
    let last = null, es = null, pollTimer = null, retry = 1000, pending = [], debounce = null;
    const fire = (evs) => {
      pending.push(...evs);
      clearTimeout(debounce);
      debounce = setTimeout(() => { const p = pending; pending = []; onChange(p); }, 200);
    };
    async function poll() {
      try {
        const r = await api("GET", "/api/events" + (last !== null ? "?after=" + last : ""));
        if (last !== null && r.events.length) fire(r.events);
        last = r.last;
      } catch (e) { /* keep polling */ }
    }
    function startPolling() {
      if (pollTimer) return;
      poll();
      pollTimer = setInterval(poll, 5000);
    }
    function stopPolling() { clearInterval(pollTimer); pollTimer = null; }
    function connect() {
      if (!("EventSource" in window)) { startPolling(); return; }
      es = new EventSource("/api/stream" + (last !== null ? "?after=" + last : ""));
      es.addEventListener("hello", (e) => {
        const wasDown = !!pollTimer;
        retry = 1000;
        stopPolling();
        try { const d = JSON.parse(e.data); if (last === null) last = d.last; } catch (x) { /* ignore */ }
        if (wasDown) fire([{ type: "reconnected" }]);
      });
      es.onmessage = (e) => {
        try { const d = JSON.parse(e.data); last = Math.max(last || 0, d.id || 0); fire([d]); } catch (x) { /* ignore */ }
      };
      es.addEventListener("bye", () => { es.close(); location.reload(); });
      es.onerror = () => {
        es.close();
        startPolling();
        setTimeout(connect, retry);
        retry = Math.min(retry * 2, 60000);
      };
    }
    connect();
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") fire([{ type: "visible" }]);
    });
  }

  return { h, clear, link, linkify, richText, fold, nameWords, safeUrl, api, ApiError, when, fullWhen, initials, toast, live };
})();
