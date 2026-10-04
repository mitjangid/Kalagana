"use strict";

// Same-origin when served by the app; fall back to the default server when the
// page is careful? no. 

const BASE = location.protocol === "file:" ? "http://127.0.0.1:8765" : "";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function el(tag, cls, txt) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (txt != null) n.textContent = txt;
  return n;
}

const MONTHS = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

const RASHI_NAMES = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
  "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"];
const RASHI_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];

const DATE_INPUTS = ["#check-date", "#muh-date", "#find-after", "#k-date",
  "#m-boy-date", "#m-girl-date", "#r-date"];
const TIME_INPUTS = ["#k-time", "#m-boy-time", "#m-girl-time"];

function locParams() {
  const box = $("#custom-loc");
  if (box && !box.hidden) {
    const lat = $("#lat").value.trim();
    const lon = $("#lon").value.trim();
    if (lat !== "" && lon !== "") {
      return { lat: lat, lon: lon, tz: $("#tz").value.trim() };
    }
  }
  return { city: $("#city").value || "delhi" };
}

function baseParams() {
  return Object.assign({
    ayanamsa: $("#ayanamsa").value || "lahiri",
    tradition: $("#tradition").value || "north",
  }, locParams());
}

async function api(path, params) {
  const entries = Object.entries(params || {}).filter(function (kv) {
    return kv[1] !== "" && kv[1] != null;
  });
  const res = await fetch(BASE + path + "?" + new URLSearchParams(entries).toString());
  let body = null;
  try { body = await res.json(); } catch (err) { body = null; }
  if (!res.ok) {
    const msg = (body && body.message) ? body.message : (res.status + " " + res.statusText);
    throw new Error(msg);
  }
  return body;
}

function fmtTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function out(id, node) {
  const host = $(id);
  host.innerHTML = "";
  if (node) host.appendChild(node);
}

function error(text) { return el("p", "muted", text); }
function subhead(text) { return el("p", "subhead", text); }

function headRow(labels) {
  const tr = el("tr");
  for (const l of labels) tr.appendChild(el("th", null, l));
  return tr;
}

// ---------------------------------------------------------------- panchang
function limbTable(title, limbs) {
  const t = el("table");
  t.appendChild(headRow([title, "From", "To"]));
  for (const l of limbs || []) {
    const tr = el("tr");
    tr.appendChild(el("td", null, l.name));
    tr.appendChild(el("td", "date", fmtTime(l.start)));
    tr.appendChild(el("td", "date", fmtTime(l.end)));
    t.appendChild(tr);
  }
  return t;
}

function windowTable(title, windows) {
  const t = el("table");
  t.appendChild(headRow([title, "From", "To"]));
  for (const w of windows || []) {
    const tr = el("tr");
    tr.appendChild(el("td", null, w.name));
    tr.appendChild(el("td", "date", fmtTime(w.start)));
    tr.appendChild(el("td", "date", fmtTime(w.end)));
    t.appendChild(tr);
  }
  return t;
}

function muhurtaFragment(m) {
  const box = document.createDocumentFragment();
  box.appendChild(windowTable("Muhurta", [
    m.rahu_kalam, m.yamaganda, m.gulika_kalam, m.abhijit, m.brahma_muhurta,
  ].filter(Boolean)));
  if (m.durmuhurta && m.durmuhurta.length) {
    box.appendChild(subhead("Durmuhurta"));
    box.appendChild(windowTable("Window", m.durmuhurta));
  }
  if (m.choghadiya) {
    box.appendChild(subhead("Choghadiya — day"));
    box.appendChild(windowTable("Choghadiya", m.choghadiya.day));
    box.appendChild(subhead("Choghadiya — night"));
    box.appendChild(windowTable("Choghadiya", m.choghadiya.night));
  }
  if (m.hora) {
    box.appendChild(subhead("Hora — day"));
    box.appendChild(windowTable("Planet", m.hora.day));
    box.appendChild(subhead("Hora — night"));
    box.appendChild(windowTable("Planet", m.hora.night));
  }
  return box;
}

async function runDay(withMuhurta) {
  out("#day-out", error("computing…"));
  try {
    const p = await api("/day", Object.assign(baseParams(), {
      date: $("#check-date").value,
      month_system: $("#month-system").value,
      no_muhurta: withMuhurta ? "" : "true",
    }));
    const box = document.createDocumentFragment();
    const kv = el("dl", "kv");
    const rows = [
      ["Date", p.date],
      ["Place", p.location.name + " (" + p.location.lat.toFixed(2) + ", " + p.location.lon.toFixed(2) + ") · " + p.location.tz],
      ["Vara", p.vara_en + " / " + p.vara],
      ["Paksha", p.paksha],
      ["Masa", p.masa_purnimanta + " (purnimanta) · " + p.masa_amanta + " (amanta)"],
      ["Eras", "Vikram " + p.samvat + " · Shaka " + p.shaka + " · " + p.samvatsara],
      ["Ritu / Ayana", p.ritu + " · " + p.ayana],
      ["Sunrise / Sunset", fmtTime(p.sunrise) + " / " + fmtTime(p.sunset)],
      ["Moonrise / Moonset", fmtTime(p.moonrise) + " / " + fmtTime(p.moonset)],
    ];
    for (const r of rows) kv.append(el("dt", null, r[0]), el("dd", null, String(r[1])));
    box.appendChild(kv);
    box.appendChild(limbTable("Tithi", p.tithi));
    box.appendChild(limbTable("Nakshatra", p.nakshatra));
    box.appendChild(limbTable("Yoga", p.yoga));
    box.appendChild(limbTable("Karana", p.karana));
    if (withMuhurta && p.muhurta) {
      box.appendChild(subhead("Muhurta"));
      box.appendChild(windowTable("Window", [
        p.muhurta.rahu_kalam, p.muhurta.yamaganda, p.muhurta.gulika_kalam,
        p.muhurta.abhijit, p.muhurta.brahma_muhurta,
      ].filter(Boolean)));
    }
    out("#day-out", box);
  } catch (e) {
    out("#day-out", error(e.message));
  }
}

async function runMuhurta() {
  out("#muh-out", error("computing…"));
  try {
    const m = (await api("/muhurta", Object.assign(baseParams(), { date: $("#muh-date").value }))).muhurta;
    out("#muh-out", muhurtaFragment(m));
  } catch (e) {
    out("#muh-out", error(e.message));
  }
}

// ---------------------------------------------------------------- find
async function runFind() {
  out("#find-out", error("searching…"));
  try {
    const o = await api("/find", Object.assign(baseParams(), {
      name: $("#find-name").value.trim(),
      after: $("#find-after").value,
    }));
    const p = el("p");
    const when = o.month ? " [" + o.month + " " + (o.paksha || "") + " " + (o.tithi || "") + "]" : "";
    p.appendChild(el("strong", null, o.date + " — " + o.name + when));
    out("#find-out", p);
  } catch (e) {
    out("#find-out", error(e.message));
  }
}

// ---------------------------------------------------------------- festivals
function festivalTable(festivals) {
  const t = el("table");
  t.appendChild(headRow(["Date", "Festival", "Kind", "Lunar / note"]));
  for (const f of festivals) {
    const tr = el("tr");
    tr.appendChild(el("td", "date", f.date));
    tr.appendChild(el("td", null, f.name));
    const kd = el("td");
    kd.appendChild(el("span", "pill " + (f.kind || "festival"), f.kind || "festival"));
    tr.appendChild(kd);
    const lunar = f.month ? (f.month + " " + (f.paksha || "") + " " + (f.tithi || "")) : (f.note || "");
    tr.appendChild(el("td", "date", lunar.trim()));
    t.appendChild(tr);
  }
  return t;
}

function festFilterParams() {
  return Object.assign(baseParams(), {
    kind: $("#fest-kind").value,
    major_only: $("#fest-major").checked ? "true" : "",
    no_islamic: $("#fest-islamic").checked ? "" : "true",
    no_fixed: $("#fest-fixed").checked ? "" : "true",
  });
}

async function runFestivals() {
  out("#fest-out", error("computing…"));
  try {
    const data = await api("/festivals", Object.assign(festFilterParams(), { year: $("#fest-year").value }));
    const box = document.createDocumentFragment();
    box.appendChild(el("p", "muted", data.count + " festivals in " + data.year));
    box.appendChild(festivalTable(data.festivals));
    out("#fest-out", box);
  } catch (e) {
    out("#fest-out", error(e.message));
  }
}

// ---------------------------------------------------------------- month
async function runMonth() {
  out("#month-out", error("computing…"));
  try {
    const data = await api("/month", Object.assign(baseParams(), { month: $("#month-input").value }));
    const t = el("table");
    t.appendChild(headRow(["Date", "Vara", "Paksha", "Tithi", "Nakshatra", "Sunrise", "Sunset"]));
    for (const d of data.days) {
      const tr = el("tr");
      tr.appendChild(el("td", "date", d.date));
      tr.appendChild(el("td", null, d.vara_en));
      tr.appendChild(el("td", null, d.paksha));
      tr.appendChild(el("td", null, d.tithi || ""));
      tr.appendChild(el("td", null, d.nakshatra || ""));
      tr.appendChild(el("td", "date", fmtTime(d.sunrise)));
      tr.appendChild(el("td", "date", fmtTime(d.sunset)));
      t.appendChild(tr);
    }
    const box = document.createDocumentFragment();
    box.appendChild(el("p", "muted", data.count + " days in " + data.month));
    box.appendChild(t);
    out("#month-out", box);
  } catch (e) {
    out("#month-out", error(e.message));
  }
}

// ---------------------------------------------------------------- eclipses
async function runEclipses() {
  out("#ecl-out", error("computing…"));
  try {
    const data = await api("/eclipses", Object.assign(locParams(), { year: $("#ecl-year").value }));
    if (!data.count) { out("#ecl-out", error("No eclipses found in " + data.year + ".")); return; }
    const t = el("table");
    t.appendChild(headRow(["Date", "Kind", "Type", "Greatest"]));
    for (const e of data.eclipses) {
      const tr = el("tr");
      tr.appendChild(el("td", "date", e.date));
      tr.appendChild(el("td", null, e.kind));
      tr.appendChild(el("td", null, e.type));
      tr.appendChild(el("td", "date", fmtTime(e.greatest)));
      t.appendChild(tr);
    }
    const box = document.createDocumentFragment();
    box.appendChild(el("p", "muted", data.count + " eclipses in " + data.year));
    box.appendChild(t);
    out("#ecl-out", box);
  } catch (e) {
    out("#ecl-out", error(e.message));
  }
}

// ---------------------------------------------------------------- kundali
function chartGrid(cells) {
  const box = el("div", "chart-grid");
  for (const c of cells || []) {
    const cell = el("div", "chart-cell" + (c.lagna ? " lagna" : ""));
    cell.appendChild(el("span", "cell-sign", c.rashi_name + " · H" + c.house));
    if (c.grahas && c.grahas.length) {
      cell.appendChild(el("span", "cell-grahas", c.grahas.join(" ")));
    }
    box.appendChild(cell);
  }
  return box;
}

function renderKundali(k, fmt) {
  const box = document.createDocumentFragment();
  const kv = el("dl", "kv");
  const rows = [
    ["When", k.when + " · " + k.location.name],
    ["Lagna", k.ascendant.rashi_name + " " + k.ascendant.degree_in_rashi.toFixed(2) + "°"],
    ["Midheaven", k.ascendant.midheaven.toFixed(2) + "°"],
    ["Moon", k.avakhada.rashi + " · " + k.avakhada.nakshatra + " (pada " + k.avakhada.pada + ")"],
    ["Gana / Yoni", k.avakhada.gana + " · " + k.avakhada.yoni],
    ["Nadi / Varna", k.avakhada.nadi + " · " + k.avakhada.varna],
    ["Tithi / Vara", k.panchang.tithi + " · " + k.panchang.vara_en],
  ];
  for (const r of rows) kv.append(el("dt", null, r[0]), el("dd", null, String(r[1])));
  box.appendChild(kv);

  box.appendChild(subhead("Grahas"));
  const gt = el("table");
  gt.appendChild(headRow(["Graha", "Rashi", "Deg", "Nakshatra", "Pd", "H", "Flags", "Dignity"]));
  for (const name of Object.keys(k.grahas)) {
    const p = k.grahas[name];
    const tr = el("tr");
    tr.appendChild(el("td", null, name));
    tr.appendChild(el("td", null, p.rashi_name));
    tr.appendChild(el("td", "date", p.degree_in_rashi.toFixed(2)));
    tr.appendChild(el("td", null, p.nakshatra_name));
    tr.appendChild(el("td", null, String(p.pada)));
    tr.appendChild(el("td", null, String(p.house)));
    const flags = (p.retrograde ? "R" : "") + (p.combust ? "C" : "");
    tr.appendChild(el("td", null, flags || "—"));
    tr.appendChild(el("td", null, p.dignity));
    gt.appendChild(tr);
  }
  box.appendChild(gt);

  const layouts = k.charts || {};
  if (layouts[fmt]) {
    box.appendChild(subhead("Chart — " + fmt + " Indian"));
    box.appendChild(chartGrid(layouts[fmt]));
  }

  if (k.dasha && k.dasha.length) {
    box.appendChild(subhead("Vimshottari dasha"));
    const dt = el("table");
    dt.appendChild(headRow(["Lord", "From", "To", "Antardasha"]));
    for (const d of k.dasha) {
      const tr = el("tr");
      tr.appendChild(el("td", null, d.lord));
      tr.appendChild(el("td", "date", d.start.slice(0, 10)));
      tr.appendChild(el("td", "date", d.end.slice(0, 10)));
      tr.appendChild(el("td", null, (d.sub || []).map(function (s) { return s.lord; }).join(" → ")));
      dt.appendChild(tr);
    }
    box.appendChild(dt);
  }
  return box;
}

async function runKundali() {
  out("#kundali-out", error("computing…"));
  const when = $("#k-date").value;
  if (!when) { out("#kundali-out", error("Pick a birth date.")); return; }
  try {
    const k = await api("/kundali", Object.assign(baseParams(), {
      date: when,
      time: $("#k-time").value || "12:00",
      dasha_depth: $("#k-depth").value,
    }));
    out("#kundali-out", renderKundali(k, $("#k-format").value));
  } catch (e) {
    out("#kundali-out", error(e.message));
  }
}

// Prefixed location query for the two-person /match endpoint.
function prefixedLocation(prefix) {
  const loc = locParams();
  const q = {};
  for (const key of Object.keys(loc)) {
    if (loc[key] !== "" && loc[key] != null) q[prefix + "_" + key] = loc[key];
  }
  return q;
}

function mangalText(d) {
  if (!d) return "—";
  if (!d.present) return "none";
  const from = (d.from || []).join(", ") || "—";
  return "present — from " + from;
}

function renderMatch(m) {
  const box = document.createDocumentFragment();
  const kv = el("dl", "kv");
  for (const pair of [["Boy", m.boy], ["Girl", m.girl]]) {
    const who = pair[0], p = pair[1] || {};
    kv.append(el("dt", null, who + " Moon"),
      el("dd", null, p.moon_rashi + " · " + p.moon_nakshatra + " · Lagna " + p.lagna));
    kv.append(el("dt", null, who + " Mangal"),
      el("dd", null, mangalText(p.mangal_dosha)));
  }
  box.appendChild(kv);

  const a = m.ashtakoota || {};
  const head = el("p", "score-head");
  head.appendChild(el("strong", null, "Ashtakoota " + (a.total != null ? a.total : "?") +
    " / " + (a.maximum != null ? a.maximum : 36) + " "));
  if (a.verdict) head.appendChild(el("span", "band " + bandClass(a.verdict), a.verdict));
  box.appendChild(head);

  const t = el("table");
  t.appendChild(headRow(["Koota", "Score / Max", "Detail"]));
  for (const k of (a.kootas || [])) {
    const tr = el("tr");
    const ok = k.score >= k.max * 0.5;
    tr.appendChild(el("td", null, (ok ? "✓ " : "✗ ") + k.name));
    tr.appendChild(el("td", "date", k.score + " / " + k.max));
    tr.appendChild(el("td", null, k.detail || ""));
    t.appendChild(tr);
  }
  box.appendChild(t);

  if (a.notes && a.notes.length) {
    const ul = el("ul", "notes");
    for (const n of a.notes) ul.appendChild(el("li", null, n));
    box.appendChild(ul);
  }
  return box;
}

async function runMatch() {
  out("#match-out", error("computing…"));
  const boyDate = $("#m-boy-date").value, girlDate = $("#m-girl-date").value;
  if (!boyDate || !girlDate) { out("#match-out", error("Pick both birth dates.")); return; }
  const params = Object.assign({}, prefixedLocation("boy"), prefixedLocation("girl"), {
    ayanamsa: $("#ayanamsa").value || "lahiri",
    boy_date: boyDate,
    girl_date: girlDate,
    boy_time: $("#m-boy-time").value || "12:00",
    girl_time: $("#m-girl-time").value || "12:00",
  });
  try {
    const m = await api("/match", params);
    out("#match-out", renderMatch(m));
  } catch (e) {
    out("#match-out", error(e.message));
  }
}

// ---------------------------------------------------------------- rashifal
function bandClass(label) {
  return "band-" + String(label || "").toLowerCase().split(/\s+/)[0];
}

function chipList(title, items, cls) {
  const box = el("div", "signed " + cls);
  box.appendChild(subhead(title));
  const ul = el("ul");
  if (!items || !items.length) ul.appendChild(el("li", "muted", "none"));
  else for (const it of items) ul.appendChild(el("li", null, it));
  box.appendChild(ul);
  return box;
}

function renderRashifalCard(r) {
  const card = el("div", "rashi-card");
  const head = el("div", "rashi-head");
  head.appendChild(el("span", "rashi-name", r.rashi_name + " (" + r.rashi_en + ")"));
  head.appendChild(el("span", "band " + bandClass(r.band), r.band + " · " + r.score));
  card.appendChild(head);
  card.appendChild(el("p", "rashi-lord",
    "Lord " + r.rashi_lord + " · " + r.period + " · " + String(r.when).slice(0, 10)));
  card.appendChild(el("p", "rashi-headline", r.headline));
  card.appendChild(el("p", null, r.summary));

  const cols = el("div", "rashi-cols");
  cols.appendChild(chipList("Favourable", r.favourable, "good"));
  cols.appendChild(chipList("Challenging", r.challenging, "bad"));
  card.appendChild(cols);

  if (r.transits && r.transits.length) {
    const t = el("table");
    t.appendChild(headRow(["Graha", "Rashi", "House", "Theme", "Verdict"]));
    for (const g of r.transits) {
      const tr = el("tr");
      tr.appendChild(el("td", null, g.graha));
      tr.appendChild(el("td", null, g.rashi_name));
      tr.appendChild(el("td", null, String(g.house)));
      tr.appendChild(el("td", null, g.house_theme));
      tr.appendChild(el("td", null, g.verdict));
      t.appendChild(tr);
    }
    card.appendChild(t);
  }
  if (r.disclaimer) card.appendChild(el("p", "muted", r.disclaimer));
  return card;
}

async function runRashifal() {
  out("#rashifal-out", error("computing…"));
  const params = Object.assign(locParams(), {
    ayanamsa: $("#ayanamsa").value || "lahiri",
    date: $("#r-date").value,
    rashi: $("#r-rashi").value,
  });
  try {
    const data = await api("/rashifal", params);
    const box = document.createDocumentFragment();
    if (data.rashifals) {
      box.appendChild(subhead("Rashifal for all 12 rashis — " + data.period));
      for (const r of data.rashifals) box.appendChild(renderRashifalCard(r));
    } else {
      box.appendChild(renderRashifalCard(data));
    }
    out("#rashifal-out", box);
  } catch (e) {
    out("#rashifal-out", error(e.message));
  }
}

// ---------------------------------------------------------------- year calendar
function monthOf(isoDate) {
  return parseInt(String(isoDate).slice(5, 7), 10) - 1;
}

async function runYear() {
  const year = $("#year-select").value;
  $("#year-count").textContent = "computing…";
  const params = Object.assign(locParams(), {
    year: year,
    kind: $("#year-kind").value,
    major_only: $("#year-major").checked ? "true" : "",
    no_islamic: $("#year-islamic").checked ? "" : "true",
    no_fixed: $("#year-fixed").checked ? "" : "true",
  });
  try {
    const data = await api("/festivals", params);
    const byMonth = [];
    for (let i = 0; i < 12; i++) byMonth.push([]);
    for (const f of data.festivals) {
      const m = monthOf(f.date);
      if (m >= 0 && m < 12) byMonth[m].push(f);
    }
    const cal = $("#calendar");
    cal.innerHTML = "";
    for (let i = 0; i < 12; i++) {
      const card = el("div", "month");
      card.appendChild(el("h3", null, MONTHS[i] + " " + year));
      const list = el("ul");
      if (!byMonth[i].length) list.appendChild(el("li", "empty", "—"));
      for (const f of byMonth[i]) {
        const li = el("li");
        li.appendChild(el("span", "d", String(f.date).slice(8, 10)));
        li.appendChild(el("span", "n", f.name));
        list.appendChild(li);
      }
      card.appendChild(list);
      cal.appendChild(card);
    }
    $("#year-count").textContent = data.count + " festivals in " + year;
  } catch (e) {
    $("#year-count").textContent = e.message;
  }
}

// ---------------------------------------------------------------- samples
async function runSamples() {
  out("#samples-out", error("running…"));
  const checks = [
    ["/health", {}],
    ["/cities", {}],
    ["/ayanamsas", {}],
    ["/day", { date: "2026-11-08", city: "delhi", no_muhurta: "true" }],
    ["/month", { month: "2026-11", city: "delhi" }],
    ["/muhurta", { date: "2026-11-08", city: "delhi" }],
    ["/festivals", { year: "2026", city: "delhi", kind: "national" }],
    ["/eclipses", { year: "2026", city: "delhi" }],
    ["/find", { name: "Diwali", after: "2026-01-01", city: "delhi" }],
    ["/kundali", { date: "1990-05-15", time: "10:30", city: "delhi", dasha_depth: "1" }],
    ["/match", { boy_date: "1990-05-15", girl_date: "1992-03-02", boy_city: "delhi", girl_city: "delhi" }],
    ["/rashifal", { date: "2026-10-04", rashi: "Mesha" }],
  ];
  const box = document.createDocumentFragment();
  for (const c of checks) {
    let ok = false, detail = "";
    try {
      const body = await api(c[0], c[1]);
      ok = body != null;
      if (!ok) detail = "empty response";
    } catch (e) {
      detail = e.message;
    }
    const row = el("div", "sample");
    row.appendChild(el("span", ok ? "ok" : "fail", ok ? "\u2713" : "\u2717"));
    row.appendChild(el("code", null, "GET " + c[0]));
    if (detail) row.appendChild(el("span", "muted", detail));
    box.appendChild(row);
  }
  out("#samples-out", box);
}

// ---------------------------------------------------------------- boot
function setStatus(text, bad) {
  const s = $("#status");
  s.textContent = text;
  s.classList.toggle("bad", !!bad);
}

function localISO(d) {
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

function populateRashi() {
  const sel = $("#r-rashi");
  for (let i = 0; i < RASHI_NAMES.length; i++) {
    const o = el("option", null, RASHI_NAMES[i] + " (" + RASHI_EN[i] + ")");
    o.value = RASHI_NAMES[i];
    sel.appendChild(o);
  }
}

function populateYears() {
  const now = new Date().getFullYear();
  const sel = $("#year-select");
  for (let y = now - 3; y <= now + 5; y++) {
    const o = el("option", null, String(y));
    o.value = String(y);
    sel.appendChild(o);
  }
  sel.value = String(now);
  $("#fest-year").value = String(now);
  $("#ecl-year").value = String(now);
}

function setDefaults() {
  const today = localISO(new Date());
  for (const sel of DATE_INPUTS) { const n = $(sel); if (n && !n.value) n.value = today; }
  for (const sel of TIME_INPUTS) { const n = $(sel); if (n && !n.value) n.value = "10:30"; }
}

async function loadCities() {
  const sel = $("#city");
  try {
    const data = await api("/cities", {});
    for (const c of data.cities) {
      const o = el("option", null, c.name);
      o.value = c.key;
      sel.appendChild(o);
    }
    if (Array.from(sel.options).some(function (o) { return o.value === "delhi"; })) sel.value = "delhi";
  } catch (e) {
    setStatus("offline", true);
  }
}

async function ping() {
  try {
    const h = await api("/health", {});
    setStatus("ready · v" + h.version, false);
  } catch (e) {
    setStatus("offline", true);
  }
}

function wire() {
  const on = function (id, fn) { const n = $(id); if (n) n.addEventListener("click", fn); };
  on("#btn-day", function () { runDay(false); });
  on("#btn-day-muh", function () { runDay(true); });
  on("#btn-muh", runMuhurta);
  on("#btn-find", runFind);
  on("#btn-fest", runFestivals);
  on("#btn-month", runMonth);
  on("#btn-ecl", runEclipses);
  on("#btn-kundali", runKundali);
  on("#btn-match", runMatch);
  on("#btn-rashifal", runRashifal);
  on("#btn-samples", runSamples);
  on("#btn-loc", function () { $("#custom-loc").hidden = !$("#custom-loc").hidden; });
  $("#year-select").addEventListener("change", runYear);
  for (const id of ["#year-kind", "#year-major", "#year-islamic", "#year-fixed"]) {
    const n = $(id); if (n) n.addEventListener("change", runYear);
  }
}

function setupTabs() {
  $$(".tabs button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      $$(".tabs button").forEach(function (b) { b.classList.toggle("active", b === btn); });
      $$("main .panel").forEach(function (p) { p.classList.toggle("active", p.id === btn.dataset.tab); });
      if (btn.dataset.tab === "year" && !$("#calendar").childElementCount) runYear();
    });
  });
}

async function init() {
  setDefaults();
  populateRashi();
  populateYears();
  wire();
  setupTabs();
  await loadCities();
  await ping();
  runDay(false);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}