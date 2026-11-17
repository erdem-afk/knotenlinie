/* Inline ("ghost") completion of @handles in a textarea.

   A mirror element lies exactly over the textarea with the same font, padding, border widths,
   wrapping and scroll position. It holds the textarea's text in transparent ink with the rest of the
   suggested handle, in grey, at the caret. The real text and caret stay the textarea's own, so nothing
   shifts. Tab (or ArrowRight at the end of the text, or a tap on the grey text) accepts; ArrowUp/Down
   cycle; Escape dismisses until the token changes. Text goes into the DOM as text nodes only. */
"use strict";

K.ghost = (() => {
  const { h } = K;
  const touch = window.matchMedia("(hover: none)").matches;
  const COPY = ["fontFamily", "fontSize", "fontWeight", "fontStyle", "fontVariant", "fontStretch", "fontKerning",
    "fontFeatureSettings", "fontVariantLigatures", "lineHeight", "letterSpacing", "wordSpacing", "textTransform",
    "textIndent", "textRendering", "tabSize", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
    "borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth", "boxSizing", "direction", "textAlign"];
  // "@" at the start of the text or after whitespace, then the typed part, ending at the caret.
  const TOKEN_RE = /(^|\s)@([^\s@]{0,40})$/u;

  /** Candidates in order, each {handle, words}. Handle-prefix matches first, then name-word matches. */
  function matches(cands, typed) {
    const p = K.fold(typed);
    if (!p) return cands.slice();
    if (cands.some((c) => c.handle === p)) return [];  // already a complete handle
    const byHandle = cands.filter((c) => c.handle.startsWith(p));
    const byName = cands.filter((c) => !c.handle.startsWith(p) && c.words.some((w) => w.startsWith(p)));
    return byHandle.concat(byName).map((c) => Object.assign({ viaName: !c.handle.startsWith(p), prefixLen: p.length }, c));
  }

  /**
   * ta: the textarea. candidates(): the current list [{handle, words}].
   * Returns {update} so callers can refresh after changing the value programmatically.
   */
  function attach(ta, candidates) {
    const wrap = h("div", { class: "ghost-wrap" });
    ta.parentNode.insertBefore(wrap, ta);
    const mirror = h("div", { class: "ghost-mirror", "aria-hidden": "true", hidden: true });
    const hint = h("span", { class: "sr-only", "aria-live": "polite" });
    wrap.append(ta, mirror, hint);

    let composing = false;
    let dismissed = null;      // token key the user dismissed with Escape
    let pick = { key: null, idx: 0 };
    let announced = "";

    /** The suggestion for the current caret position, or null. */
    function compute() {
      if (composing || document.activeElement !== ta) return null;
      const caret = ta.selectionStart;
      if (caret !== ta.selectionEnd) return null;
      const v = ta.value;
      // Only at the end of a line: the grey text must not cover typed text after the caret.
      const after = v.slice(caret);
      const nl = after.indexOf("\n");
      if ((nl < 0 ? after : after.slice(0, nl)).trim()) return null;
      const m = TOKEN_RE.exec(v.slice(0, caret));
      if (!m) return null;
      const typed = m[2];
      const start = caret - typed.length - 1;  // index of "@"
      const key = start + ":" + typed;
      if (dismissed !== null) {
        if (dismissed === key) return null;
        dismissed = null;
      }
      const list = matches(candidates(), typed);
      if (!list.length) return null;
      if (pick.key !== key) pick = { key, idx: 0 };
      const c = list[pick.idx % list.length];
      return { start, end: caret, key, list, c,
        ghost: c.viaName ? " → @" + c.handle : c.handle.slice(c.prefixLen) };
    }

    function syncBox() {
      const cs = getComputedStyle(ta);
      for (const p of COPY) mirror.style[p] = cs[p];
      const bl = parseFloat(cs.borderLeftWidth) || 0, br = parseFloat(cs.borderRightWidth) || 0;
      const scrollbar = Math.max(0, ta.offsetWidth - ta.clientWidth - bl - br);
      mirror.style.width = (ta.offsetWidth - scrollbar) + "px";
      mirror.style.height = ta.offsetHeight + "px";
      mirror.style.left = ta.offsetLeft + "px";
      mirror.style.top = ta.offsetTop + "px";
    }

    function render(st) {
      if (!st) {
        if (!mirror.hidden) { mirror.hidden = true; K.clear(mirror); }
        if (announced) { announced = ""; hint.textContent = ""; }
        return;
      }
      syncBox();
      const v = ta.value;
      const g = h("span", { class: "ghost-text", text: st.ghost });
      g.addEventListener("pointerdown", (e) => { e.preventDefault(); accept(); });
      K.clear(mirror).append(document.createTextNode(v.slice(0, st.end)), g,
        document.createTextNode(v.slice(st.end) + "​"));
      mirror.hidden = false;
      mirror.scrollTop = ta.scrollTop;
      const say = `${touch ? "Tap the suggestion" : "Tab"} to complete @${st.c.handle}`;
      if (say !== announced) { announced = say; hint.textContent = say; }
    }

    function update() { render(compute()); }

    function accept() {
      const st = compute();
      if (!st) return false;
      const v = ta.value;
      const text = st.c.handle + (v.charAt(st.end) === " " ? "" : " ");
      ta.focus();
      ta.setSelectionRange(st.start + 1, st.end);
      let ok = false;
      try { ok = document.execCommand("insertText", false, text); } catch (e) { ok = false; }
      if (!ok || ta.value === v) {
        ta.setRangeText(text, st.start + 1, st.end, "end");
        ta.dispatchEvent(new Event("input", { bubbles: true }));
      }
      if (v.charAt(st.end) === " ") ta.setSelectionRange(ta.selectionEnd + 1, ta.selectionEnd + 1);
      update();
      return true;
    }

    ta.addEventListener("keydown", (e) => {
      if (e.isComposing || e.keyCode === 229) return;
      const mods = e.altKey || e.ctrlKey || e.metaKey;
      const k = e.key;
      if (!(k === "Tab" || k === "ArrowRight" || k === "ArrowDown" || k === "ArrowUp" || k === "Escape")) return;
      const st = compute();
      if (!st || mods) return;  // no ghost: Tab moves focus, arrows move the caret, Escape does its usual job
      if (k === "Tab" && !e.shiftKey) {
        e.preventDefault(); accept();
      } else if (k === "ArrowRight" && !e.shiftKey && st.end === ta.value.length) {
        e.preventDefault(); accept();
      } else if ((k === "ArrowDown" || k === "ArrowUp") && !e.shiftKey && st.list.length > 1) {
        e.preventDefault();
        const n = st.list.length;
        pick.idx = ((pick.idx % n) + (k === "ArrowDown" ? 1 : n - 1)) % n;
        update();
      } else if (k === "Escape") {
        e.preventDefault(); e.stopPropagation();
        dismissed = st.key;
        render(null);
      }
    });
    ta.addEventListener("input", update);
    ta.addEventListener("focus", update);
    ta.addEventListener("blur", () => render(null));
    ta.addEventListener("click", update);
    ta.addEventListener("keyup", (e) => { if (e.key.startsWith("Arrow") || e.key === "Home" || e.key === "End") update(); });
    ta.addEventListener("select", update);
    ta.addEventListener("scroll", () => { mirror.scrollTop = ta.scrollTop; });
    ta.addEventListener("compositionstart", () => { composing = true; render(null); });
    ta.addEventListener("compositionend", () => { composing = false; update(); });
    document.addEventListener("selectionchange", () => { if (document.activeElement === ta) update(); });
    if ("ResizeObserver" in window) new ResizeObserver(() => { if (!mirror.hidden) update(); }).observe(ta);
    window.addEventListener("resize", () => { if (!mirror.hidden) update(); });
    return { update };
  }

  return { attach, matches };
})();
