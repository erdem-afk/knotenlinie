/* Coordinator page. */
"use strict";
(() => {
  const { h, clear, api, when, toast } = K;
  const $ = (id) => document.getElementById(id);
  const DECISION = {
    auto: "Starts automatically", approved: "Approved by you", needs_coordinator: "Needs your decision",
    held: "Held",
  };
  const FINISHED = new Set(["answered", "answered_record", "in_ledger", "not_feasible", "withdrawn"]);

  const WHY = {
    frozen: "Plan approved and frozen. The run waits for the project team.",
    queued: "Plan approved. Waiting for a free run slot.",
    on_hold: "On hold.",
  };

  async function loadReports() {
    const { reports } = await api("GET", "/api/admin/feasibility");
    const waiting = reports.filter((r) => r.waiting_for_team)
      .sort((a, b) => (a.updated_at < b.updated_at ? -1 : a.updated_at > b.updated_at ? 1 : 0));
    $("waiting-count").textContent = waiting.length ? `(${waiting.length})` : "";
    const wbox = clear($("waiting"));
    if (!waiting.length) wbox.append(h("p", { class: "muted", text: "Nothing is waiting for the team." }));
    for (const r of waiting) wbox.append(reportEl(r, true));
    const box = clear($("reports"));
    if (!reports.length) { box.append(h("p", { class: "muted", text: "No questions yet." })); return; }
    for (const r of reports) box.append(reportEl(r, false));
  }

  function reportEl(r, waiting) {
    const dec = r.decision || "none";
    const el = h("article", { class: "report" + (waiting ? " waiting" : "") });
    el.append(h("div", { class: "report-head" },
      h("strong", { text: r.question_id }),
      h("span", { class: "qchip st-" + r.status, text: r.status === "queued" ? `Queued (position ${r.queue_pos})` : r.status_label }),
      h("span", { class: "decision " + dec, text: DECISION[dec] || "No report yet" }),
      waiting ? h("span", { class: "small muted", title: K.fullWhen(r.updated_at), text: "since " + when(r.updated_at) }) : null));
    if (waiting) {
      const why = dec === "needs_coordinator" && r.status !== "on_hold" ? "The feasibility report needs your decision."
        : r.status === "on_hold" && dec === "needs_coordinator" ? "Plan approved; waiting for your approval to run."
          : WHY[r.status];
      if (why) el.append(h("p", { class: "small", text: why }));
    }
    el.append(h("p", { text: r.restated }));
    el.append(h("p", { class: "small muted", text: `Asked by ${r.author}` + (r.forwarder ? `, forwarded by ${r.forwarder}` : "") +
      ` · plan ${r.plan_approved ? "approved by the member" : "not yet approved"}` }));
    if (r.hold_reason) el.append(h("p", { class: "banner", text: "On hold: " + r.hold_reason }));
    if (r.has_report) {
      el.append(h("p", null, h("strong", { text: "Estimated cost: " }),
        r.est_cost_eur === null ? "unknown" : `${Number(r.est_cost_eur).toFixed(2)} EUR`,
        h("strong", { text: " · Blind data: " }), r.touches_blind ? "yes" : "no"));
      el.append(h("p", null, h("strong", { text: "Members see: " }), h("span", { class: "pre", text: r.public_summary || "" })));
      el.append(h("p", null, h("strong", { text: "Private detail: " })));
      el.append(h("div", { class: "pre small quote", text: r.private_detail || "(none)" }));
    }
    const actions = h("div", { class: "card-actions" });
    actions.append(h("a", { class: "btn", href: `/?thread=${r.root_message_id}`, text: "Open thread" }));
    if (!FINISHED.has(r.status)) {
      if (r.status !== "on_hold") actions.append(h("button", { type: "button", class: "btn danger", text: "Hold this run", onclick: () => openHold(r.question_id) }));
      if (r.status === "on_hold") actions.append(h("button", { type: "button", class: "btn primary", text: "Release", onclick: () => act(r.question_id, "release") }));
      if (dec === "needs_coordinator" || (dec === "held" && r.status !== "on_hold"))
        actions.append(h("button", { type: "button", class: "btn primary", text: "Approve run", onclick: () => act(r.question_id, "approve_run") }));
    }
    el.append(actions);
    return el;
  }

  async function act(qid, what) {
    try {
      const r = await api("POST", `/api/admin/questions/${encodeURIComponent(qid)}/${what}`);
      toast(`${qid}: ${r.status === "queued" ? "queued at position " + r.queue_pos : r.status.replace("_", " ")}.`);
      await loadAll();
    } catch (e) { toast(e.message, "error"); }
  }

  let holdQid = null;
  function openHold(qid) {
    holdQid = qid;
    $("hold-title").textContent = `Hold the run of ${qid}`;
    $("hold-reason").value = "";
    $("hold-error").textContent = "";
    $("hold-dialog").showModal();
    $("hold-reason").focus();
  }
  $("hold-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const reason = $("hold-reason").value.trim();
    if (!reason) { $("hold-error").textContent = "Please give a reason."; return; }
    try {
      await api("POST", `/api/admin/questions/${encodeURIComponent(holdQid)}/hold`, { reason });
      $("hold-dialog").close();
      toast(`${holdQid} is on hold.`);
      await loadAll();
    } catch (err) { $("hold-error").textContent = err.message; }
  });
  $("hold-cancel").addEventListener("click", () => $("hold-dialog").close());

  async function loadSuggestions() {
    const s = await api("GET", "/api/admin/suggestions");
    const box = clear($("suggestions"));
    const stat = (n, label) => h("div", { class: "stat" }, h("span", { class: "n", text: String(n) }), h("span", { class: "small muted", text: label }));
    const sg = s.suggest;
    box.append(h("div", { class: "stats" },
      stat(sg.accepted, "suggestions accepted"), stat(sg.declined, "declined (“just chatting”)"),
      stat(sg.offered, "still open"),
      stat(sg.accept_rate === null ? "–" : Math.round(sg.accept_rate * 100) + "%", "acceptance rate"),
      stat(s.confirm.accepted, "forwards confirmed"), stat(s.confirm.declined, "forwards not confirmed")));
  }

  async function loadUsers() {
    const { users } = await api("GET", "/api/admin/users");
    const tb = clear($("users-table").querySelector("tbody"));
    for (const u of users) {
      let canInvite;
      if (u.role === "member") {
        const box = h("input", { type: "checkbox", "aria-label": `${u.name} can invite colleagues` });
        box.checked = !!u.can_invite;
        box.addEventListener("change", async () => {
          box.disabled = true;
          try {
            const r = await api("PATCH", `/api/admin/users/${u.id}`, { can_invite: box.checked });
            box.checked = !!r.can_invite;
            toast(`${u.name} ${r.can_invite ? "can now invite colleagues" : "can no longer invite"}.`);
          } catch (err) { box.checked = !box.checked; toast(err.message, "error"); }
          box.disabled = false;
        });
        canInvite = h("td", null, box);
      } else {
        canInvite = h("td", { class: "muted", text: u.role === "coordinator" ? "always" : "" });
      }
      tb.append(h("tr", null,
        h("td", null, h("span", { text: u.name }), u.handle ? h("span", { class: "muted small", text: " @" + u.handle }) : null),
        h("td", { text: u.email }), h("td", { text: u.role }),
        h("td", { text: u.invited_by ? u.invited_by.name : "" }), canInvite,
        h("td", { text: u.public_name_ok === null ? "not asked yet" : u.public_name_ok ? "yes" : "no" }),
        h("td", { text: when(u.created_at) }), h("td", { text: u.last_message_at ? when(u.last_message_at) : "" })));
    }
  }

  const OUTCOME = { created: "New member", new_link: "Fresh link for an existing invitee", exists: "Already on the board; no link given" };

  async function loadInvites() {
    const { invites } = await api("GET", "/api/admin/invites");
    const tb = clear($("invites-table").querySelector("tbody"));
    if (!invites.length) { tb.append(h("tr", null, h("td", { colspan: 5, class: "muted", text: "No invitations recorded yet." }))); return; }
    for (const v of invites) {
      tb.append(h("tr", null,
        h("td", { text: when(v.created_at) }), h("td", { text: v.user ? v.user.name : "" }), h("td", { text: v.email }),
        h("td", { text: v.invited_by ? v.invited_by.name + (v.invited_by.role === "coordinator" ? " (coordinator)" : "") : "" }),
        h("td", { text: OUTCOME[v.outcome] || v.outcome })));
    }
  }

  $("invite-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    $("invite-error").textContent = "";
    const name = $("invite-name").value.trim(), email = $("invite-email").value.trim();
    if (!name || !email) { $("invite-error").textContent = "Please enter a name and an email address."; return; }
    $("invite-send").disabled = true;
    try {
      const r = await api("POST", "/api/admin/invites", { name, email });
      $("invite-link").value = r.login_url;
      $("invite-note").textContent = r.created ? `${name} was added to the board.` : "This address was already on the board; here is a fresh link.";
      $("invite-result").hidden = false;
      $("invite-name").value = ""; $("invite-email").value = "";
      await Promise.allSettled([loadUsers(), loadInvites()]);
    } catch (err) { $("invite-error").textContent = err.message; }
    $("invite-send").disabled = false;
  });
  $("invite-copy").addEventListener("click", async () => {
    const input = $("invite-link");
    try { await navigator.clipboard.writeText(input.value); toast("Link copied."); }
    catch (e) { input.select(); toast("Press Ctrl+C (or Cmd+C) to copy."); }
  });

  async function loadAll() {
    const res = await Promise.allSettled([loadReports(), loadSuggestions(), loadUsers(), loadInvites()]);
    const bad = res.find((r) => r.status === "rejected");
    if (bad) toast(bad.reason.message, "error");
  }

  loadAll();
  K.live(() => { if (!document.querySelector("dialog[open]")) loadAll(); });
})();
