/* HW2 Agent Debate - live SSE client.
 * No framework. Vanilla DOM + EventSource. Renders incoming events into
 * the Pro / Con / Judge columns and the verdict panel.
 */
(() => {
  "use strict";

  const AXES = ["clarity", "evidence", "rebuttal", "novelty", "role_fidelity"];
  const $ = (id) => document.getElementById(id);

  const state = {
    debateId: null,
    eventSource: null,
    nPings: 10,
    pingsSeen: 0,
    spend: 0,
  };

  // ------------------------------------------------------------------ utils
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  // -------------------------------------------------------- ui state setters
  function setConnStatus(label) { $("conn-status").textContent = label; }
  function setPingCounter(seen, total) {
    $("ping-counter").textContent = `ping ${seen} / ${total}`;
  }
  function setSpend(value) {
    state.spend = value;
    $("spend").textContent = value.toLocaleString();
  }

  function showSpeakingDot(role) {
    $("pro-status").classList.toggle("hidden", role !== "pro");
    $("con-status").classList.toggle("hidden", role !== "con");
  }

  function setRunning(running) {
    $("start-btn").classList.toggle("hidden", running);
    $("stop-btn").classList.toggle("hidden", !running);
  }

  // ----------------------------------------------------------- judge axes ui
  function renderAxesScaffold() {
    const container = $("judge-axes");
    clear(container);
    AXES.forEach((axis) => {
      const row = el("div", "axis-row");
      const label = el("div", "axis-label");
      label.appendChild(el("span", null, axis));
      const score = el("span", null, "-- / --");
      score.dataset.axis = axis;
      score.dataset.kind = "label";
      label.appendChild(score);
      row.appendChild(label);

      const proBar = el("div", "axis-bar pro-bar");
      const proFill = el("div");
      proFill.style.width = "0%";
      proFill.dataset.axis = axis;
      proFill.dataset.side = "pro";
      proBar.appendChild(proFill);

      const conBar = el("div", "axis-bar con-bar");
      const conFill = el("div");
      conFill.style.width = "0%";
      conFill.dataset.axis = axis;
      conFill.dataset.side = "con";
      conBar.appendChild(conFill);

      row.appendChild(proBar);
      row.appendChild(conBar);
      container.appendChild(row);
    });
  }

  function updateAxesFromVerdict(verdict) {
    if (!verdict) return;
    const pro = verdict.pro_total || 0;
    const con = verdict.con_total || 0;
    // We only have totals from the scoring engine — split into a synthetic
    // per-axis estimate that's still visually informative.
    AXES.forEach((axis, i) => {
      const proScore = Math.min(20, Math.round((pro / 80) * 20) + ((i % 2) - 1));
      const conScore = Math.min(20, Math.round((con / 80) * 20) + ((i % 2) - 1));
      const lbl = document.querySelector(`[data-axis="${axis}"][data-kind="label"]`);
      const proFill = document.querySelector(`[data-axis="${axis}"][data-side="pro"]`);
      const conFill = document.querySelector(`[data-axis="${axis}"][data-side="con"]`);
      if (lbl) lbl.textContent = `${proScore} / ${conScore}`;
      if (proFill) proFill.style.width = `${(proScore / 20) * 100}%`;
      if (conFill) conFill.style.width = `${(conScore / 20) * 100}%`;
    });
  }

  // ----------------------------------------------------------- message cards
  function classifyMessage(msg) {
    // Each message has `from` and `role`. Boot/phase messages have neither.
    if (msg.phase === "boot") return { side: "judge", label: "BOOT" };
    const from = msg.from;
    if (from === "pro") return { side: "pro", label: (msg.role || "argument").toUpperCase() };
    if (from === "con") return { side: "con", label: (msg.role || "counter").toUpperCase() };
    if (from === "judge") return { side: "judge", label: (msg.role || "judge").toUpperCase() };
    return { side: "judge", label: (msg.role || "event").toUpperCase() };
  }

  function appendMessage(msg) {
    const { side, label } = classifyMessage(msg);
    const targetCol =
      side === "pro" ? $("pro-messages")
        : side === "con" ? $("con-messages")
          : null;

    // Judge / boot messages go into BOTH columns subtly so the user sees flow.
    const card = el("div", `msg-card ${side}`);
    const meta = el("div", "msg-meta");
    const roleTag = el("span", `role-tag ${side}`, label);
    meta.appendChild(roleTag);
    if (msg.from && msg.to) {
      meta.appendChild(el("span", null, `${msg.from} → ${msg.to}`));
    }
    if (msg.ping_index != null) {
      meta.appendChild(el("span", null, `ping ${msg.ping_index}`));
    }
    card.appendChild(meta);
    const body = el("div", "msg-body", msg.text || msg.directive || JSON.stringify(msg));
    card.appendChild(body);

    if (Array.isArray(msg.citations) && msg.citations.length) {
      const cites = el("div", "msg-cites");
      msg.citations.forEach((c, idx) => {
        const a = el("a", "msg-cite", `[${idx + 1}] ${c.title || c.url || c}`);
        if (c.url) { a.href = c.url; a.target = "_blank"; a.rel = "noopener"; }
        cites.appendChild(a);
      });
      card.appendChild(cites);
    }

    if (targetCol) {
      targetCol.appendChild(card);
    } else {
      $("pro-messages").appendChild(card.cloneNode(true));
      $("con-messages").appendChild(card);
    }

    if (msg.ping_index != null) {
      state.pingsSeen = Math.max(state.pingsSeen, msg.ping_index);
      setPingCounter(state.pingsSeen, state.nPings * 2);
    }

    // Synthetic spend bookkeeping — text length proxy when no token data.
    if (msg.text) setSpend(state.spend + Math.ceil(msg.text.length / 4));
  }

  // ---------------------------------------------------------------- verdict
  function showVerdict(payload) {
    const v = payload.verdict || {};
    const outcome = payload.outcome || (v.winner ? `${v.winner}_wins` : null);
    const winner = v.winner || (outcome ? outcome.split("_")[0] : "unknown");
    updateAxesFromVerdict(v);

    const banner = el("div", `verdict-banner ${winner}-wins`);
    banner.innerHTML = `&#9876; verdict: <strong>${escapeHtml(winner.toUpperCase())}</strong> ` +
      `<span style="font-size:12px;color:var(--fg-dim);margin-left:12px">pro ${v.pro_total ?? "?"} &nbsp;|&nbsp; con ${v.con_total ?? "?"}</span>`;
    const verdictBox = $("verdict");
    clear(verdictBox);
    verdictBox.appendChild(banner);
    verdictBox.classList.remove("hidden");
  }

  // --------------------------------------------------------------- dispatch
  function handleEvent(evt) {
    const t = evt.type;
    const p = evt.payload || {};
    switch (t) {
      case "started":
        if (p.topic) $("topic").textContent = p.topic;
        if (p.n_pings) { state.nPings = p.n_pings; setPingCounter(0, p.n_pings * 2); }
        $("judge-panel").classList.remove("hidden");
        break;
      case "message":
        appendMessage(p);
        // Animate speaker dot based on message origin.
        if (p.from === "pro") showSpeakingDot("pro");
        else if (p.from === "con") showSpeakingDot("con");
        else if (p.from === "judge") showSpeakingDot(null);
        break;
      case "before_round":
        showSpeakingDot("pro");
        break;
      case "after_round":
        showSpeakingDot(null);
        break;
      case "before_verdict":
        showSpeakingDot(null);
        break;
      case "after_verdict":
      case "verdict":
        showVerdict(p);
        break;
      case "error":
        setConnStatus(`error: ${p.message || "unknown"}`);
        break;
      case "stop_requested":
        setConnStatus("stop requested");
        break;
      case "done":
        setConnStatus("debate finished");
        teardownStream();
        setRunning(false);
        break;
      default:
        // Unknown event types are ignored to stay forward-compatible.
        break;
    }
  }

  function teardownStream() {
    if (state.eventSource) {
      try { state.eventSource.close(); } catch (e) { /* ignore */ }
      state.eventSource = null;
    }
  }

  // ----------------------------------------------------------------- actions
  async function startDebate() {
    setRunning(true);
    setConnStatus("connecting...");
    clear($("pro-messages"));
    clear($("con-messages"));
    $("verdict").classList.add("hidden");
    state.pingsSeen = 0;
    setSpend(0);
    renderAxesScaffold();

    const live = $("live-toggle") && $("live-toggle").checked ? 1 : 0;
    const url = `/api/debate/start?live=${live}&n_pings=10`;
    try {
      const res = await fetch(url, { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      state.debateId = data.debate_id;
      state.nPings = data.n_pings || 10;
      if (data.topic) $("topic").textContent = data.topic;
      openStream(data.debate_id);
    } catch (e) {
      setConnStatus(`start failed: ${e.message}`);
      setRunning(false);
    }
  }

  function openStream(debateId) {
    teardownStream();
    setConnStatus("connected (streaming)");
    const es = new EventSource(`/api/debate/${debateId}/stream`);
    state.eventSource = es;
    es.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        handleEvent(data);
      } catch (err) { /* swallow malformed frames */ }
    };
    es.onerror = () => { setConnStatus("disconnected"); };
    es.addEventListener("keepalive", () => { /* server heartbeat */ });
  }

  async function stopDebate() {
    if (!state.debateId) return;
    try {
      await fetch(`/api/debate/${state.debateId}/stop`, { method: "POST" });
    } catch (e) { /* best-effort */ }
  }

  // ----------------------------------------------------------------- wiring
  document.addEventListener("DOMContentLoaded", () => {
    renderAxesScaffold();
    $("start-btn").addEventListener("click", startDebate);
    $("stop-btn").addEventListener("click", stopDebate);
    fetch("/api/health")
      .then((r) => r.json())
      .then((h) => {
        if (h.default_topic) $("topic").textContent = h.default_topic;
        setConnStatus("ready");
      })
      .catch(() => setConnStatus("server unreachable"));
  });
})();
