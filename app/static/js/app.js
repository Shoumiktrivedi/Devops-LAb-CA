(() => {
  "use strict";
  const API = "/api";
  const $ = (id) => document.getElementById(id);
  const money = (n) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(n);
  const fmtDate = (s) => new Date(s + "T00:00:00").toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
  const monthLabel = (ym) => new Date(ym + "-01T00:00:00").toLocaleDateString("en-IN", { month: "short", year: "2-digit" });
  const todayStr = () => { const d = new Date(); return new Date(d - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); };

  let categories = { expense: [], income: [] };
  let pendingDeleteId = null;
  let catChart = null, monthChart = null;

  /* ---------- helpers ---------- */
  function el(tag, props = {}, ...kids) {
    const n = document.createElement(tag);
    Object.entries(props).forEach(([k, v]) => (k === "class" ? (n.className = v) : k === "text" ? (n.textContent = v) : n.setAttribute(k, v)));
    kids.forEach((k) => n.append(k));
    return n;
  }
  function toast(msg, isError = false) {
    const t = el("div", { class: "toast" + (isError ? " error" : ""), text: msg });
    $("toasts").append(t);
    setTimeout(() => t.remove(), 3500);
  }
  async function api(path, opts = {}) {
    const res = await fetch(API + path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error(data.error || "Request failed");
      err.details = data.details;
      throw err;
    }
    return data;
  }

  /* ---------- navigation ---------- */
  const titles = { dashboard: "Dashboard", transactions: "Transactions", form: "Add transaction" };
  function show(view) {
    document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === "view-" + view));
    document.querySelectorAll(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
    $("view-title").textContent = view === "form" && $("tx-id").value ? "Edit transaction" : titles[view];
    $("sidebar").classList.remove("open");
    if (view === "dashboard") loadDashboard();
    if (view === "transactions") loadTransactions();
    window.scrollTo({ top: 0 });
  }
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-view]");
    if (!b) return;
    if (b.dataset.view === "form") resetForm();
    show(b.dataset.view);
  });
  $("top-add").onclick = () => { resetForm(); show("form"); };
  $("menu-btn").onclick = () => $("sidebar").classList.toggle("open");

  /* ---------- dashboard ---------- */
  const PALETTE = ["#C4503A", "#E3B04B", "#1E8C6E", "#3B6E8F", "#8A5A9B", "#D98A5F", "#5E8C4A", "#A34B6E", "#7C8A8E"];

  async function loadDashboard() {
    try {
      const d = await api("/dashboard");
      $("s-balance").textContent = money(d.balance);
      $("s-balance").classList.toggle("neg", d.balance < 0);
      $("s-income").textContent = money(d.total_income);
      $("s-expense").textContent = money(d.total_expenses);
      $("s-tx").textContent = d.transaction_count;
      $("s-count").textContent = `Across ${d.transaction_count} transaction${d.transaction_count === 1 ? "" : "s"}`;
      renderRecent(d.recent_transactions);
      drawCharts(d);
    } catch (e) { toast(e.message, true); }
  }
  function renderRecent(list) {
    const ul = $("recent-list");
    ul.replaceChildren();
    if (!list.length) { ul.append(el("li", { class: "empty", text: "Nothing here yet. Add a transaction or load demo data." })); return; }
    list.forEach((t) => ul.append(el("li", {},
      el("span", { class: "dot " + t.type }),
      el("div", { class: "meta" }, el("b", { text: t.description || t.category }), el("small", { text: `${t.category} · ${fmtDate(t.date)}` })),
      el("span", { class: "amt " + t.type, text: (t.type === "income" ? "+" : "−") + money(t.amount) }))));
  }
  function drawCharts(d) {
    const cats = Object.keys(d.category_expenses), months = Object.keys(d.monthly_expenses);
    $("cat-empty").hidden = cats.length > 0; $("month-empty").hidden = months.length > 0;
    catChart && catChart.destroy(); monthChart && monthChart.destroy();
    if (cats.length) {
      catChart = new Chart($("cat-chart"), {
        type: "doughnut",
        data: { labels: cats, datasets: [{ data: cats.map((c) => d.category_expenses[c]), backgroundColor: PALETTE, borderWidth: 2, borderColor: "#fff" }] },
        options: { maintainAspectRatio: false, cutout: "58%", plugins: { legend: { position: "bottom", labels: { boxWidth: 12 } }, tooltip: { callbacks: { label: (c) => ` ${c.label}: ${money(c.parsed)}` } } } },
      });
    }
    if (months.length) {
      monthChart = new Chart($("month-chart"), {
        type: "bar",
        data: { labels: months.map(monthLabel), datasets: [{ label: "Expenses", data: months.map((m) => d.monthly_expenses[m]), backgroundColor: "#C4503A", borderRadius: 5 }] },
        options: { maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => " " + money(c.parsed.y) } } }, scales: { y: { beginAtZero: true, ticks: { callback: (v) => "₹" + v.toLocaleString("en-IN") } }, x: { grid: { display: false } } } },
      });
    }
  }

  /* ---------- transactions list + filters ---------- */
  function filterQuery() {
    const p = new URLSearchParams();
    [["type", "f-type"], ["category", "f-category"], ["start_date", "f-start"], ["end_date", "f-end"], ["search", "f-search"]]
      .forEach(([k, id]) => $(id).value && p.set(k, $(id).value.trim()));
    const s = p.toString();
    return s ? "?" + s : "";
  }
  async function loadTransactions() {
    try {
      const list = await api("/transactions" + filterQuery());
      const body = $("tx-body");
      body.replaceChildren();
      $("tx-empty").hidden = list.length > 0;
      list.forEach((t) => {
        const edit = el("button", { class: "ghost small", text: "Edit" });
        const del = el("button", { class: "ghost small", text: "Delete", style: "margin-left:6px;color:#C4503A" });
        edit.onclick = () => startEdit(t.id);
        del.onclick = () => askDelete(t);
        body.append(el("tr", {},
          el("td", { text: fmtDate(t.date) }),
          el("td", {}, el("span", { class: "badge " + t.type, text: t.type === "income" ? "Income" : "Expense" })),
          el("td", { text: t.category }),
          el("td", { text: t.description || "–" }),
          el("td", { class: "num " + t.type, text: (t.type === "income" ? "+" : "−") + money(t.amount) }),
          el("td", { class: "actions" }, edit, del)));
      });
    } catch (e) { toast(e.message, true); }
  }
  let debounce;
  ["f-type", "f-category", "f-start", "f-end"].forEach((id) => $(id).addEventListener("change", loadTransactions));
  $("f-search").addEventListener("input", () => { clearTimeout(debounce); debounce = setTimeout(loadTransactions, 250); });
  $("f-clear").onclick = () => { ["f-search", "f-type", "f-category", "f-start", "f-end"].forEach((id) => ($(id).value = "")); loadTransactions(); };

  /* ---------- delete ---------- */
  function askDelete(t) {
    pendingDeleteId = t.id;
    $("confirm-text").textContent = `${t.category} · ${money(t.amount)} on ${fmtDate(t.date)} will be removed permanently.`;
    $("confirm-dialog").showModal();
  }
  $("confirm-no").onclick = () => $("confirm-dialog").close();
  $("confirm-yes").onclick = async () => {
    $("confirm-dialog").close();
    try { await api("/transactions/" + pendingDeleteId, { method: "DELETE" }); toast("Transaction deleted"); loadTransactions(); }
    catch (e) { toast(e.message, true); }
  };

  /* ---------- form (add + edit) ---------- */
  const selectedType = () => document.querySelector('input[name="type"]:checked').value;
  function fillCategories(selected) {
    const sel = $("category");
    sel.replaceChildren(el("option", { value: "", text: "Select a category" }));
    categories[selectedType()].forEach((c) => sel.append(el("option", { value: c, text: c })));
    sel.value = selected || "";
  }
  document.querySelectorAll('input[name="type"]').forEach((r) => r.addEventListener("change", () => fillCategories()));

  function clearErrors() {
    document.querySelectorAll(".err").forEach((e) => (e.textContent = ""));
    document.querySelectorAll(".invalid").forEach((e) => e.classList.remove("invalid"));
  }
  function showErrors(map) {
    Object.entries(map).forEach(([k, msg]) => {
      const e = $("err-" + k), i = $(k);
      if (e) e.textContent = msg;
      if (i) i.classList.add("invalid");
    });
  }
  function resetForm() {
    $("tx-form").reset(); $("tx-id").value = ""; clearErrors();
    $("t-expense").checked = true; fillCategories();
    $("date").value = todayStr();
    $("form-title").textContent = "Add transaction"; $("save-btn").textContent = "Save transaction";
    titles.form = "Add transaction";
  }
  async function startEdit(id) {
    try {
      const t = await api("/transactions/" + id);
      resetForm();
      $("tx-id").value = t.id;
      (t.type === "income" ? $("t-income") : $("t-expense")).checked = true;
      fillCategories(t.category);
      $("amount").value = t.amount; $("date").value = t.date; $("description").value = t.description;
      $("form-title").textContent = "Edit transaction"; $("save-btn").textContent = "Update transaction";
      show("form");
    } catch (e) { toast(e.message, true); }
  }
  $("cancel-btn").onclick = () => show("transactions");

  $("tx-form").addEventListener("submit", async (e) => {
    e.preventDefault(); clearErrors();
    const payload = { type: selectedType(), amount: $("amount").value, category: $("category").value, description: $("description").value, date: $("date").value };
    const errs = {};
    if (!(parseFloat(payload.amount) > 0)) errs.amount = "Enter an amount greater than zero";
    if (!payload.category) errs.category = "Select a category";
    if (!payload.date) errs.date = "Pick a date";
    if (Object.keys(errs).length) return showErrors(errs);
    payload.amount = parseFloat(payload.amount);

    const id = $("tx-id").value;
    try {
      await api(id ? "/transactions/" + id : "/transactions", { method: id ? "PUT" : "POST", body: payload });
      toast(id ? "Transaction updated" : "Transaction added");
      resetForm(); show("transactions");
    } catch (err) {
      err.details ? showErrors(err.details) : toast(err.message, true);
    }
  });

  /* ---------- demo data ---------- */
  $("seed-btn").onclick = async () => {
    try {
      const r = await api("/seed", { method: "POST" });
      toast(r.message);
      show("dashboard");
    } catch (e) { toast(e.message, true); }
  };

  /* ---------- init ---------- */
  (async function init() {
    try {
      categories = await api("/categories");
      const sel = $("f-category");
      [...new Set([...categories.expense, ...categories.income])].forEach((c) => sel.append(el("option", { value: c, text: c })));
    } catch (e) { toast("Could not load categories", true); }
    resetForm();
    show("dashboard");
  })();
})();
