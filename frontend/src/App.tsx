import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

const API_BASE = "http://127.0.0.1:8000";

type Page = "dashboard" | "sync" | "tables" | "raw" | "settings";
type Row = Record<string, string | number | null>;
type StatusBlock = { exists: boolean; rows: number; updated_at: number | null };
type Status = Record<string, StatusBlock>;
type RawNote = { name: string; text: string };
type SyncLog = { script: string; returncode: number; output: string };

const styles = `
:root {
  color: #171717;
  background: #eeeeec;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  --bg: #eeeeec;
  --panel: rgba(255,255,255,0.72);
  --panel-solid: #fafaf9;
  --ink: #171717;
  --muted: #6b6b67;
  --soft: #9b9b96;
  --line: #d8d8d3;
  --line-dark: #c6c6bf;
  --wash: #f4f4f2;
  --dark: #20201e;
  --danger: #6f2828;
  --danger-bg: #f2e7e7;
  --safe: #2f4f3a;
  --safe-bg: #e8eee9;
  --shadow: 0 24px 70px rgba(20, 20, 18, 0.10);
  --shadow-soft: 0 12px 30px rgba(20, 20, 18, 0.07);
}

* { box-sizing: border-box; }
html { background: var(--bg); }
body { margin: 0; min-width: 320px; background: radial-gradient(circle at top left, #fafaf8 0, var(--bg) 34rem); }
button, input, select { font: inherit; }
button { cursor: pointer; }

.app {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 268px minmax(0, 1fr);
  color: var(--ink);
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 18px;
  background: rgba(238,238,236,0.74);
  backdrop-filter: blur(18px);
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
}

.brand {
  padding: 10px 8px 20px;
  border-bottom: 1px solid var(--line);
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 11px;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(145deg, #242422, #6d6d67);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.25), 0 18px 34px rgba(0,0,0,0.16);
}

.brand-title {
  font-size: 21px;
  font-weight: 760;
  letter-spacing: -0.04em;
}

.brand-subtitle {
  color: var(--muted);
  font-size: 12px;
  margin-top: 3px;
}

.nav-section-title {
  color: var(--soft);
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 720;
  letter-spacing: 0.12em;
  margin: 0 8px 10px;
}

.nav { display: grid; gap: 6px; }

.nav button {
  width: 100%;
  min-height: 42px;
  border: 1px solid transparent;
  border-radius: 12px;
  padding: 10px 12px;
  background: transparent;
  color: #4c4c48;
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-align: left;
  font-weight: 650;
  transition: background 160ms ease, color 160ms ease, border-color 160ms ease, transform 160ms ease;
}

.nav button::after {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 99px;
  background: transparent;
}

.nav button:hover {
  background: rgba(255,255,255,0.56);
  color: var(--ink);
}

.nav button.active {
  background: var(--panel-solid);
  color: var(--ink);
  border-color: var(--line-dark);
  box-shadow: var(--shadow-soft);
}

.nav button.active::after { background: #1f1f1d; }

.side-card {
  padding: 14px;
  border: 1px solid var(--line);
  background: rgba(250,250,249,0.62);
  border-radius: 18px;
}

.side-card-title {
  font-weight: 760;
  font-size: 13px;
  margin-bottom: 12px;
  letter-spacing: -0.01em;
}

.side-line {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.65;
}

.side-line b { color: var(--ink); font-weight: 680; }

.dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  display: inline-block;
  background: #30302d;
  margin-right: 7px;
  box-shadow: 0 0 0 4px rgba(48,48,45,0.10);
}

.dot.off {
  background: #9d4b4b;
  box-shadow: 0 0 0 4px rgba(157,75,75,0.10);
}

.main {
  min-width: 0;
  padding: 34px;
}

.page-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: end;
  margin-bottom: 22px;
}

.kicker {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  font-weight: 760;
  letter-spacing: 0.14em;
}

h1 {
  max-width: 920px;
  margin: 5px 0 10px;
  font-size: clamp(40px, 5.4vw, 82px);
  line-height: 0.92;
  letter-spacing: -0.075em;
  font-weight: 780;
}

.lead {
  max-width: 760px;
  margin: 0;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.7;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  background: rgba(250,250,249,0.78);
  border: 1px solid var(--line);
  border-radius: 999px;
  color: #3e3e3a;
  font-size: 13px;
  white-space: nowrap;
  box-shadow: var(--shadow-soft);
}

.grid { display: grid; gap: 14px; }
.kpi-grid { grid-template-columns: repeat(6, minmax(0, 1fr)); }
.fact-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 14px; }
.chart-grid { grid-template-columns: minmax(0, 1.18fr) minmax(320px, 0.82fr); margin-top: 14px; }
.table-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }

.card {
  background: var(--panel);
  border: 1px solid rgba(198,198,191,0.72);
  border-radius: 24px;
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(14px);
}

.kpi, .fact {
  padding: 17px;
  min-height: 122px;
  position: relative;
  overflow: hidden;
}

.kpi::before, .fact::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.95), transparent);
}

.kpi-label, .fact-label {
  color: var(--soft);
  font-size: 11px;
  font-weight: 760;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.kpi-value {
  font-size: 34px;
  font-weight: 780;
  letter-spacing: -0.05em;
  margin-top: 12px;
}

.kpi-detail, .fact-detail {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
  margin-top: 7px;
}

.fact-value {
  font-size: 28px;
  font-weight: 760;
  letter-spacing: -0.04em;
  margin-top: 10px;
}

.panel {
  padding: 19px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 14px;
}

.panel-title {
  font-size: 18px;
  font-weight: 760;
  letter-spacing: -0.035em;
}

.panel-copy {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.55;
  margin-top: 5px;
}

.empty {
  padding: 28px;
  border: 1px dashed var(--line-dark);
  border-radius: 18px;
  color: var(--muted);
  background: rgba(250,250,249,0.50);
}

.btn {
  border: 1px solid var(--line-dark);
  background: var(--panel-solid);
  color: var(--ink);
  min-height: 42px;
  padding: 10px 15px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 720;
  box-shadow: var(--shadow-soft);
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}

.btn:hover {
  transform: translateY(-1px);
  border-color: #9d9d96;
  box-shadow: var(--shadow);
}

.btn.primary {
  background: var(--dark);
  color: #f7f7f4;
  border-color: var(--dark);
}

.btn.danger {
  background: var(--danger-bg);
  color: var(--danger);
  border-color: #dec7c7;
}

.btn:disabled {
  opacity: 0.62;
  cursor: wait;
  transform: none;
}

.confirm-block {
  margin-top: 18px;
  display: grid;
  gap: 8px;
}

.confirm-label {
  color: var(--ink);
  font-size: 13px;
  font-weight: 700;
}

.confirm-label code {
  padding: 2px 6px;
  border-radius: 8px;
  background: rgba(255,255,255,0.72);
  border: 1px solid var(--line);
  color: var(--danger);
}

.confirm-input {
  width: min(100%, 420px);
  min-height: 42px;
  border: 1px solid var(--line-dark);
  border-radius: 14px;
  background: rgba(250,250,249,0.86);
  color: var(--ink);
  padding: 10px 13px;
  outline: none;
  transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
}

.confirm-input:focus {
  border-color: #9d9d96;
  box-shadow: 0 0 0 4px rgba(32,32,30,0.07);
  background: var(--panel-solid);
}

.loader-dot {
  width: 14px;
  height: 14px;
  border-radius: 99px;
  border: 2px solid rgba(255,255,255,0.32);
  border-top-color: currentColor;
  animation: spin 0.8s linear infinite;
}

.progress-row {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.progress-row:last-child { border-bottom: 0; }
.progress-name { font-weight: 720; font-size: 13px; }
.progress-text { color: var(--muted); font-size: 13px; }

.log-box {
  max-height: 360px;
  overflow: auto;
  background: #20201e;
  color: #ececea;
  padding: 15px;
  border-radius: 18px;
  font-size: 12px;
  line-height: 1.55;
  white-space: pre-wrap;
  border: 1px solid #30302d;
}

.table-wrap {
  overflow: auto;
  max-height: 430px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(255,255,255,0.42);
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
  font-size: 13px;
}

th, td {
  padding: 11px 12px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}

th {
  position: sticky;
  top: 0;
  background: rgba(244,244,242,0.96);
  color: #4d4d49;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 760;
  letter-spacing: 0.10em;
  backdrop-filter: blur(12px);
}

td { color: #333330; }
tr:hover td { background: rgba(255,255,255,0.48); }

.risk {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 9px;
  border-radius: 999px;
  font-weight: 720;
  font-size: 12px;
}
.risk.high { color: var(--danger); background: var(--danger-bg); }
.risk.safe { color: var(--safe); background: var(--safe-bg); }

.bars { display: grid; gap: 11px; }
.bar-row {
  display: grid;
  grid-template-columns: 132px minmax(0, 1fr) 52px;
  align-items: center;
  gap: 11px;
  font-size: 12px;
}
.bar-label { font-weight: 700; color: #363633; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar-track { height: 11px; background: #deded8; border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #323230, #86867f); }
.bar-fill.warn { background: linear-gradient(90deg, #6f2828, #b98d8d); }
.bar-value { text-align: right; color: var(--muted); font-weight: 700; }

.note-list { display: grid; gap: 12px; }
.note-header { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.note-name { font-weight: 760; color: #282825; letter-spacing: -0.02em; }
.note-body {
  max-height: 230px;
  overflow: auto;
  white-space: pre-wrap;
  color: #555550;
  font-size: 12px;
  line-height: 1.6;
  margin-top: 10px;
  border-top: 1px solid var(--line);
  padding-top: 10px;
}

.svg-chart { width: 100%; min-height: 280px; }
.donut-wrap { display: grid; place-items: center; gap: 12px; }

.app.sidebar-collapsed { grid-template-columns: 86px minmax(0, 1fr); }
.sidebar { transition: width 260ms cubic-bezier(.22,1,.36,1), padding 260ms cubic-bezier(.22,1,.36,1); }
.sidebar-top { display:flex; align-items:center; justify-content:space-between; gap:10px; padding: 10px 8px 20px; border-bottom: 1px solid var(--line); }
.brand { padding: 0; border-bottom: 0; min-width: 0; }
.brand-row { gap: 0; }
.brand-title-wrap { min-width:0; transition: opacity 180ms ease, transform 220ms ease; }
.sidebar-toggle {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid var(--line-dark);
  background: rgba(250,250,249,0.78);
  color: var(--ink);
  font-weight: 760;
  box-shadow: var(--shadow-soft);
  transition: transform 180ms ease, background 180ms ease;
}
.sidebar-toggle:hover { transform: translateY(-1px); background: var(--panel-solid); }
.nav button { justify-content: flex-start; gap: 11px; }
.nav button::after { margin-left: auto; flex: 0 0 auto; }
.nav-icon {
  width: 24px;
  height: 24px;
  border-radius: 9px;
  border: 1px solid rgba(198,198,191,0.72);
  display: inline-grid;
  place-items: center;
  font-size: 11px;
  font-weight: 820;
  letter-spacing: -0.03em;
  color: #555550;
  background: rgba(255,255,255,0.46);
  flex: 0 0 auto;
}
.nav-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sidebar-collapsed .sidebar { padding: 18px 12px; overflow-x: hidden; }
.sidebar-collapsed .sidebar-top { justify-content: center; padding: 10px 0 18px; }
.sidebar-collapsed .brand { display: none; }
.sidebar-collapsed .nav-section-title,
.sidebar-collapsed .side-card,
.sidebar-collapsed .nav-label,
.sidebar-collapsed .nav button::after { display: none; }
.sidebar-collapsed .nav button { justify-content: center; padding: 10px; }
.sidebar-collapsed .nav-icon { width: 34px; height: 34px; border-radius: 12px; }
.sidebar-collapsed .main { padding-left: 34px; }
.section-spaced { margin-top: 18px; }
.section-spaced-lg { margin-top: 22px; }
.table-wrap.compact { max-height: 520px; }
.table-wrap.compact th,
.table-wrap.compact td { padding: 7px 10px; line-height: 1.22; vertical-align: middle; }
.table-wrap.compact table { font-size: 12px; }
.risk { white-space: nowrap; }
.metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 14px; }
.metric-grid > .panel:only-child { grid-column: 1 / -1; }
.insight-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 14px; }
.mini-chart { width: 100%; min-height: 245px; display:block; }
.chart-caption { color: var(--muted); font-size: 12px; line-height: 1.5; margin-top: 8px; }
.legend-row { display:flex; gap:14px; flex-wrap:wrap; margin-top: 10px; color: var(--muted); font-size: 12px; }
.legend-key { display:inline-flex; align-items:center; gap:7px; }
.legend-dot { width:9px; height:9px; border-radius:99px; display:inline-block; background:#30302d; }
.legend-dot.safe { background:#4d7659; }
.legend-dot.warn { background:#9a3333; }
.legend-line { width:24px; height:4px; border-radius:99px; display:inline-block; background:#30302d; }
.legend-line.dark { background:#30302d; }
.legend-line.safe { background:#5f7f66; }
.legend-line.warn { background:#9a3333; }
.quadrant-label {
  font-size: 11px;
  font-weight: 820;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  paint-order: stroke;
  stroke: rgba(250,250,249,0.92);
  stroke-width: 5px;
  stroke-linejoin: round;
}
.quadrant-label.good { fill:#3f744e; }
.quadrant-label.bad { fill:#8f4a4a; }
.quadrant-label.danger { fill:#7d2525; }
.quadrant-label.neutral { fill:#6b6b67; }
.box-band { opacity:0.72; }
.box-band.good { fill:rgba(63,116,78,0.08); }
.box-band.neutral { fill:rgba(48,48,45,0.045); }
.box-band.bad { fill:rgba(201,143,143,0.13); }
.box-band.danger { fill:rgba(143,32,32,0.10); }
.bubble-code {
  font-size: 10px;
  font-weight: 860;
  letter-spacing: 0.01em;
  fill: #ffffff;
  pointer-events: none;
}

.placeholder-panel {
  min-height: 340px;
  border: 1.5px dashed rgba(32,32,30,0.22);
  background:
    radial-gradient(circle at 1px 1px, rgba(32,32,30,0.13) 1px, transparent 0) 0 0 / 18px 18px,
    linear-gradient(135deg, rgba(250,250,249,0.72), rgba(232,232,227,0.38));
  display: grid;
  place-items: center;
  text-align: center;
}
.placeholder-inner { max-width: 320px; color: var(--muted); }
.placeholder-title { color: var(--ink); font-weight: 820; font-size: 18px; margin-bottom: 8px; }
.placeholder-copy { font-size: 13px; line-height: 1.55; }

.heatmap-legend { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-top:10px; color:var(--muted); font-size:12px; }
.heatmap-scale { width:180px; height:10px; border-radius:99px; background:linear-gradient(90deg, #edf2ee, #d9ddd5, #d8bbb7, #9a3333); border:1px solid rgba(32,32,30,0.10); }

.subject-label {
  font-size: 10px;
  font-weight: 760;
  fill: #20201e;
  paint-order: stroke;
  stroke: rgba(250,250,249,0.92);
  stroke-width: 4px;
  stroke-linejoin: round;
}
.axis-label { font-size: 11px; fill: #6b6b67; }
.heatmap-wrap { overflow:hidden; width:100%; }
.heatmap-cell { rx: 0; stroke: rgba(250,250,249,0.92); stroke-width: 1.5; }
.box-note { color: var(--muted); font-size: 12px; line-height: 1.45; margin-top: 8px; }

.filter-row { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom: 14px; }
.filter-pills { display:flex; gap:8px; flex-wrap:wrap; }
.filter-pill {
  border:1px solid var(--line-dark);
  background: rgba(250,250,249,0.68);
  color:#444440;
  border-radius:999px;
  min-height:36px;
  padding:8px 12px;
  font-size:12px;
  font-weight:760;
  transition: background 160ms ease, color 160ms ease, transform 160ms ease;
}
.filter-pill:hover { transform: translateY(-1px); }
.filter-pill.active { background: var(--dark); color:#f7f7f4; border-color: var(--dark); }
.note-card { padding: 0; overflow: hidden; }
.note-toggle {
  width:100%;
  border:0;
  background: transparent;
  padding: 17px 19px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  text-align:left;
  color: var(--ink);
}
.note-meta { display:flex; align-items:center; gap:10px; min-width:0; }
.note-actions { display:flex; align-items:center; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
.note-body { margin: 0 19px 19px; }
.note-card.collapsed .note-body { display:none; }
.download-link { text-decoration:none; }
@media (max-width: 1180px) { .metric-grid, .insight-grid { grid-template-columns: 1fr; } }
@media (max-width: 820px) {
  .app, .app.sidebar-collapsed { grid-template-columns: 1fr; }
  .sidebar-collapsed .brand { display:block; }
  .sidebar-collapsed .nav-section-title,
  .sidebar-collapsed .side-card,
  .sidebar-collapsed .nav-label { display:block; }
  .sidebar-collapsed .nav button::after { display:block; }
  .sidebar-collapsed .nav button { justify-content:flex-start; padding:10px 12px; }
  .sidebar-collapsed .main { padding-left:18px; }
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1180px) {
  .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .fact-grid, .chart-grid, .table-grid { grid-template-columns: 1fr; }
}

@media (max-width: 820px) {
  .app { grid-template-columns: 1fr; }
  .sidebar { position: relative; height: auto; }
  .main { padding: 18px; }
  .page-header { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .progress-row { grid-template-columns: 1fr; }
  h1 { letter-spacing: -0.06em; }
}

@media (max-width: 520px) {
  .kpi-grid, .fact-grid { grid-template-columns: 1fr; }
  h1 { font-size: 42px; }
}
`;

function toNumber(value: unknown): number {
  const num = Number(value);
  return Number.isFinite(num) ? num : 0;
}

function normalizeSubject(value: unknown): string {
  return String(value ?? "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function subjectCode(value: unknown): string {
  const normalized = normalizeSubject(value);
  if (normalized.includes("software construction") && normalized.includes("lab")) return "SCD-L";
  if (normalized.includes("software construction")) return "SCD";
  if (normalized.includes("formal methods")) return "FMI";
  if (normalized.includes("artificial intelligence")) return "AI";
  if (normalized.includes("information security")) return "IS";
  if (normalized.includes("professional practices")) return "PP";
  if (normalized.includes("web engineering")) return "WE";
  if (normalized.includes("quran")) return "TOHQ";
  const words = String(value ?? "Subject").replace(/[^a-zA-Z0-9\s]/g, " ").trim().split(/\s+/).filter(Boolean);
  if (!words.length) return "SBJ";
  if (words.length === 1) return words[0].slice(0, 4).toUpperCase();
  return words.slice(0, 3).map((word) => word[0]).join("").toUpperCase();
}

function shortSubject(value: unknown): string {
  const normalized = normalizeSubject(value);
  if (normalized.includes("software construction") && normalized.includes("lab")) return "SCD Lab";
  if (normalized.includes("software construction")) return "SCD";
  if (normalized.includes("formal methods")) return "Formal Methods";
  if (normalized.includes("artificial intelligence")) return "AI";
  if (normalized.includes("information security")) return "InfoSec";
  if (normalized.includes("professional practices")) return "Pro Practices";
  if (normalized.includes("web engineering")) return "Web Eng";
  if (normalized.includes("quran")) return "Quran";
  return String(value ?? "Subject");
}

function average(rows: Row[], key: string): number {
  if (!rows.length) return 0;
  return Number((rows.reduce((sum, row) => sum + toNumber(row[key]), 0) / rows.length).toFixed(2));
}

function riskClass(value: unknown): string {
  return String(value ?? "").toLowerCase().includes("high") ? "high" : "safe";
}

function formatDate(seconds: number | null | undefined): string {
  if (!seconds) return "Not built yet";
  return new Date(seconds * 1000).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    let detail: unknown = await response.text();
    try {
      detail = JSON.parse(String(detail));
    } catch {
      // Keep text detail.
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return response.json() as Promise<T>;
}

function Kpi({ label, value, detail }: { label: string; value: string | number; detail: string }) {
  return (
    <div className="card kpi">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-detail">{detail}</div>
    </div>
  );
}

function Fact({ label, value, detail }: { label: string; value: string | number; detail: string }) {
  return (
    <div className="card fact">
      <div className="fact-label">{label}</div>
      <div className="fact-value">{value}</div>
      <div className="fact-detail">{detail}</div>
    </div>
  );
}

function Panel({ title, copy, children }: { title: string; copy?: string; children: ReactNode }) {
  return (
    <section className="card panel">
      <div className="panel-header">
        <div>
          <div className="panel-title">{title}</div>
          {copy ? <div className="panel-copy">{copy}</div> : null}
        </div>
      </div>
      {children}
    </section>
  );
}

function PageHeader({
  kicker,
  title,
  copy,
  status,
}: {
  kicker: string;
  title: string;
  copy: string;
  status?: string;
}) {
  return (
    <header className="page-header">
      <div>
        <div className="kicker">{kicker}</div>
        <h1>{title}</h1>
        <p className="lead">{copy}</p>
      </div>
      {status ? (
        <div className="status-pill">
          <span className="dot" />
          {status}
        </div>
      ) : null}
    </header>
  );
}

function scoreColor(value: number, target: number): string {
  const delta = value - target;
  if (delta < -25) return "#8f2020";
  if (delta < -12) return "#a84646";
  if (delta < 0) return "#c98f8f";
  if (delta < 10) return "#6f746d";
  if (delta < 22) return "#5f7f66";
  return "#3f744e";
}

function GpaChart({ rows }: { rows: Row[] }) {
  if (!rows.length) return <div className="empty">No previous semester GPA data found yet.</div>;
  const width = 720;
  const height = 300;
  const pad = 40;
  let runningCredits = 0;
  let runningWeighted = 0;
  const points = rows.map((row, index) => {
    const credits = toNumber(row.total_credit_hours);
    const sgpa = toNumber(row.semester_gpa);
    runningCredits += credits;
    runningWeighted += sgpa * credits;
    const cgpa = runningCredits ? runningWeighted / runningCredits : sgpa;
    const x = pad + (index * (width - pad * 2)) / Math.max(1, rows.length - 1);
    return {
      x,
      label: String(row.semester ?? `S${index + 1}`),
      sgpa,
      cgpa,
      sgpaY: height - pad - (sgpa / 4) * (height - pad * 2),
      cgpaY: height - pad - (cgpa / 4) * (height - pad * 2),
    };
  });
  const sgpaPath = points.map((p, index) => `${index ? "L" : "M"} ${p.x} ${p.sgpaY}`).join(" ");
  const cgpaPath = points.map((p, index) => `${index ? "L" : "M"} ${p.x} ${p.cgpaY}`).join(" ");

  return (
    <>
      <svg className="svg-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="SGPA and CGPA trend">
        {[1, 2, 3, 4].map((tick) => {
          const y = height - pad - (tick / 4) * (height - pad * 2);
          return (
            <g key={tick}>
              <line x1={pad} x2={width - pad} y1={y} y2={y} stroke="#d8d8d3" />
              <text x={12} y={y + 4} fontSize="11" fill="#6b6b67">
                {tick}
              </text>
            </g>
          );
        })}
        <path d={cgpaPath} fill="none" stroke="#5f7f66" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <path d={sgpaPath} fill="none" stroke="#30302d" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {points.map((point) => (
          <g key={point.label}>
            <circle cx={point.x} cy={point.sgpaY} r="6" fill="#fafaf9" stroke="#30302d" strokeWidth="3" />
            <circle cx={point.x} cy={point.cgpaY} r="5" fill="#fafaf9" stroke="#5f7f66" strokeWidth="3" />
            <text x={point.x} y={Math.min(point.sgpaY, point.cgpaY) - 13} textAnchor="middle" fontSize="11" fontWeight="760" fill="#20201e">
              {point.sgpa.toFixed(2)} / {point.cgpa.toFixed(2)}
            </text>
            <text x={point.x} y={height - 12} textAnchor="middle" fontSize="11" fill="#6b6b67">
              {point.label.replace("Spring", "Spr")}
            </text>
          </g>
        ))}
      </svg>
      <div className="legend-row">
        <span className="legend-key"><span className="legend-line dark" /> SGPA</span>
        <span className="legend-key"><span className="legend-line safe" /> CGPA</span>
      </div>
    </>
  );
}

function RiskDonut({ rows }: { rows: Row[] }) {
  const high = rows.filter((row) => riskClass(row.final_risk_status) === "high").length;
  const safe = Math.max(0, rows.length - high);
  const total = Math.max(1, rows.length);
  const highPct = (high / total) * 100;
  return (
    <div className="donut-wrap">
      <svg width="230" height="230" viewBox="0 0 42 42" role="img" aria-label="Risk distribution">
        <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#deded8" strokeWidth="6" />
        <circle
          cx="21"
          cy="21"
          r="15.915"
          fill="transparent"
          stroke="#6f2828"
          strokeWidth="6"
          strokeDasharray={`${highPct} ${100 - highPct}`}
          strokeDashoffset="25"
        />
        <text x="21" y="20" textAnchor="middle" fontSize="7" fontWeight="760" fill="#20201e">
          {high}
        </text>
        <text x="21" y="26" textAnchor="middle" fontSize="3.5" fill="#6b6b67">
          high risk
        </text>
      </svg>
      <div className="side-line" style={{ width: "100%" }}>
        <span>Safe subjects</span>
        <b>{safe}</b>
      </div>
    </div>
  );
}


function orderedDashboard(rows: Row[]): Row[] {
  return [...rows].sort((a, b) => {
    const aRisk = (100 - toNumber(a.attendance_percentage)) + (70 - toNumber(a.current_marks_percentage)) + toNumber(a.total_absent) * 2;
    const bRisk = (100 - toNumber(b.attendance_percentage)) + (70 - toNumber(b.current_marks_percentage)) + toNumber(b.total_absent) * 2;
    return bRisk - aRisk;
  });
}

function subjectInitials(value: unknown): string {
  return subjectCode(value);
}

function AttendanceMarksBubble({ rows }: { rows: Row[] }) {
  if (!rows.length) return <div className="empty">No dashboard data found yet.</div>;
  const width = 760;
  const height = 410;
  const pad = 62;
  const xScale = (value: number) => pad + (Math.max(0, Math.min(100, value)) / 100) * (width - pad * 2);
  const yScale = (value: number) => height - pad - (Math.max(0, Math.min(100, value)) / 100) * (height - pad * 2);
  const maxAbsent = Math.max(1, ...rows.map((row) => toNumber(row.total_absent)));
  const sorted = [...rows].sort((a, b) => toNumber(b.total_absent) - toNumber(a.total_absent));
  return (
    <>
      <svg className="mini-chart bubble-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Attendance and marks bubble chart">
        <rect x={pad} y={pad} width={width - pad * 2} height={height - pad * 2} fill="rgba(255,255,255,0.34)" stroke="#d8d8d3" />
        <rect x={pad} y={pad} width={xScale(80) - pad} height={yScale(55) - pad} fill="rgba(143,32,32,0.07)" />
        <rect x={xScale(80)} y={pad} width={width - pad - xScale(80)} height={yScale(55) - pad} fill="rgba(63,116,78,0.10)" />
        <rect x={pad} y={yScale(55)} width={xScale(80) - pad} height={height - pad - yScale(55)} fill="rgba(111,40,40,0.13)" />
        <rect x={xScale(80)} y={yScale(55)} width={width - pad - xScale(80)} height={height - pad - yScale(55)} fill="rgba(201,143,143,0.12)" />
        {[20, 40, 60, 80, 100].map((tick) => (
          <g key={`grid-${tick}`}>
            <line x1={xScale(tick)} x2={xScale(tick)} y1={pad} y2={height - pad} stroke="#e3e3de" />
            <line x1={pad} x2={width - pad} y1={yScale(tick)} y2={yScale(tick)} stroke="#e3e3de" />
          </g>
        ))}
        <line x1={xScale(80)} x2={xScale(80)} y1={pad} y2={height - pad} stroke="#8f8f88" strokeDasharray="5 5" />
        <line x1={pad} x2={width - pad} y1={yScale(55)} y2={yScale(55)} stroke="#8f8f88" strokeDasharray="5 5" />
        <text x={(pad + xScale(80)) / 2} y={pad + 18} className="quadrant-label bad">Attendance risk</text>
        <text x={(xScale(80) + width - pad) / 2} y={pad + 18} className="quadrant-label good">Healthy zone</text>
        <text x={(pad + xScale(80)) / 2} y={height - pad - 12} className="quadrant-label danger">Critical</text>
        <text x={(xScale(80) + width - pad) / 2} y={height - pad - 12} className="quadrant-label bad">Marks risk</text>
        <text x={xScale(80) + 6} y={pad + 35} className="axis-label">80% attendance</text>
        <text x={pad + 6} y={yScale(55) - 7} className="axis-label">55% marks</text>
        {sorted.map((row) => {
          const attendanceValue = toNumber(row.attendance_percentage);
          const marksValue = toNumber(row.current_marks_percentage);
          const absent = toNumber(row.total_absent);
          const safe = attendanceValue >= 80 && marksValue >= 55;
          const radius = 10 + (absent / maxAbsent) * 16 + (riskClass(row.final_risk_status) === "high" ? 4 : 0);
          const x = xScale(attendanceValue);
          const y = yScale(marksValue);
          const code = subjectCode(row.subject);
          return (
            <g key={`bubble-${row.subject}`} className="bubble-node">
              <circle cx={x} cy={y} r={radius} fill={safe ? "#5f7f66" : scoreColor(Math.min(attendanceValue, marksValue), safe ? 55 : 80)} opacity="0.88" stroke="#fafaf9" strokeWidth="2.5" />
              <text x={x} y={y + 3} textAnchor="middle" className="bubble-code">{code}</text>
              <title>{`${row.subject}: ${attendanceValue.toFixed(1)}% attendance, ${marksValue.toFixed(1)}% marks, ${absent} absences, status ${String(row.final_risk_status ?? "unknown")}`}</title>
            </g>
          );
        })}
        <text x={width / 2} y={height - 12} textAnchor="middle" className="axis-label">Attendance percentage</text>
        <text x="14" y="26" className="axis-label">Marks percentage</text>
      </svg>
      <div className="legend-row">
        <span className="legend-key"><span className="legend-dot safe" /> healthy subject</span>
        <span className="legend-key"><span className="legend-dot warn" /> below target</span>
        <span className="legend-key">bubble size = absence pressure plus high-risk status</span>
        <span className="legend-key">hover a bubble for the full subject name</span>
      </div>
    </>
  );
}

function AttendanceMarksWorm({ rows }: { rows: Row[] }) {
  if (!rows.length) return <div className="empty">No dashboard data found yet.</div>;
  const data = orderedDashboard(rows).slice(0, 10).reverse();
  const width = 720;
  const height = 310;
  const pad = 42;
  const x = (index: number) => pad + (index * (width - pad * 2)) / Math.max(1, data.length - 1);
  const y = (value: number) => height - pad - (Math.max(0, Math.min(100, value)) / 100) * (height - pad * 2);
  const attendancePath = data.map((row, index) => `${index ? "L" : "M"} ${x(index)} ${y(toNumber(row.attendance_percentage))}`).join(" ");
  const marksPath = data.map((row, index) => `${index ? "L" : "M"} ${x(index)} ${y(toNumber(row.current_marks_percentage))}`).join(" ");
  return (
    <>
      <svg className="mini-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Attendance and marks worm chart">
        {[25, 50, 55, 75, 80, 100].map((tick) => (
          <g key={`worm-grid-${tick}`}>
            <line x1={pad} x2={width - pad} y1={y(tick)} y2={y(tick)} stroke={tick === 55 || tick === 80 ? "#9b9b96" : "#e3e3de"} strokeDasharray={tick === 55 || tick === 80 ? "5 5" : ""} />
            <text x={12} y={y(tick) + 4} fontSize="10" fill="#6b6b67">{tick}%</text>
          </g>
        ))}
        <path d={attendancePath} fill="none" stroke="#5f7f66" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <path d={marksPath} fill="none" stroke="#9a3333" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {data.map((row, index) => {
          const ax = x(index);
          const ay = y(toNumber(row.attendance_percentage));
          const my = y(toNumber(row.current_marks_percentage));
          return (
            <g key={`worm-${row.subject}`}>
              <circle cx={ax} cy={ay} r="5" fill="#fafaf9" stroke="#5f7f66" strokeWidth="3" />
              <circle cx={ax} cy={my} r="5" fill="#fafaf9" stroke="#9a3333" strokeWidth="3" />
              <text x={ax} y={height - 12} textAnchor="middle" fontSize="10" fill="#6b6b67">{subjectInitials(row.subject)}</text>
            </g>
          );
        })}
      </svg>
      <div className="legend-row">
        <span className="legend-key"><span className="legend-line safe" /> Attendance</span>
        <span className="legend-key"><span className="legend-line warn" /> Marks</span>
        <span className="legend-key">dashed lines = 80% attendance and 55% marks targets</span>
      </div>
    </>
  );
}

function quantile(values: number[], q: number): number {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  return sorted[base + 1] === undefined ? sorted[base] : sorted[base] + rest * (sorted[base + 1] - sorted[base]);
}

function MetricBoxPlots({ rows }: { rows: Row[] }) {
  const metrics = [
    { label: "Attendance", values: rows.map((row) => toNumber(row.attendance_percentage)), target: 80 },
    { label: "Marks", values: rows.map((row) => toNumber(row.current_marks_percentage)), target: 55 },
    { label: "Presence", values: rows.map((row) => 100 - Math.min(100, toNumber(row.total_absent) * 8)), target: 70 },
  ].filter((metric) => metric.values.length);
  if (!metrics.length) return <div className="empty">No numeric subject metrics found yet.</div>;
  const width = 740;
  const height = 330;
  const pad = 58;
  const x = (value: number) => pad + (Math.max(0, Math.min(100, value)) / 100) * (width - pad * 2);
  const bands = [
    { from: 0, to: 55, label: "weak", className: "danger" },
    { from: 55, to: 70, label: "watch", className: "bad" },
    { from: 70, to: 85, label: "stable", className: "neutral" },
    { from: 85, to: 100, label: "strong", className: "good" },
  ];
  return (
    <>
      <svg className="mini-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Metric box plots">
        {bands.map((band) => (
          <g key={`band-${band.label}`}>
            <rect x={x(band.from)} y={pad - 22} width={x(band.to) - x(band.from)} height={height - pad * 2 + 36} className={`box-band ${band.className}`} />
            <text x={(x(band.from) + x(band.to)) / 2} y={pad - 30} textAnchor="middle" className={`quadrant-label ${band.className}`}>{band.label}</text>
          </g>
        ))}
        {[0, 25, 50, 55, 70, 80, 85, 100].map((tick) => (
          <g key={`box-grid-${tick}`}>
            <line x1={x(tick)} x2={x(tick)} y1={pad - 22} y2={height - pad + 8} stroke={tick === 55 || tick === 80 ? "#9b9b96" : "#ecece8"} strokeDasharray={tick === 55 || tick === 80 ? "4 4" : ""} />
            <text x={x(tick)} y={height - 10} textAnchor="middle" fontSize="10" fill="#6b6b67">{tick}</text>
          </g>
        ))}
        {metrics.map((metric, index) => {
          const y = pad + index * 78;
          const vals = metric.values;
          const min = Math.min(...vals);
          const max = Math.max(...vals);
          const q1 = quantile(vals, 0.25);
          const med = quantile(vals, 0.5);
          const q3 = quantile(vals, 0.75);
          const color = scoreColor(med, metric.target);
          return (
            <g key={`box-${metric.label}`}>
              <text x={pad - 10} y={y + 5} textAnchor="end" fontSize="12" fontWeight="760" fill="#20201e">{metric.label}</text>
              <line x1={x(min)} x2={x(max)} y1={y} y2={y} stroke="#6b6b67" strokeWidth="2" />
              <line x1={x(min)} x2={x(min)} y1={y - 10} y2={y + 10} stroke="#6b6b67" strokeWidth="2" />
              <line x1={x(max)} x2={x(max)} y1={y - 10} y2={y + 10} stroke="#6b6b67" strokeWidth="2" />
              <rect x={x(q1)} y={y - 16} width={Math.max(2, x(q3) - x(q1))} height="32" rx="8" fill="rgba(250,250,249,0.74)" stroke={color} strokeWidth="3" />
              <line x1={x(med)} x2={x(med)} y1={y - 20} y2={y + 20} stroke={color} strokeWidth="4" />
              <line x1={x(metric.target)} x2={x(metric.target)} y1={y - 24} y2={y + 24} stroke="#20201e" strokeDasharray="4 4" opacity="0.55" />
              <text x={x(med)} y={y + 38} textAnchor="middle" fontSize="11" fontWeight="760" fill="#20201e">median {med.toFixed(1)}%</text>
            </g>
          );
        })}
      </svg>
      <div className="box-note">Background bands read left to right: weak, watch, stable, strong. Dashed lines mark practical targets.</div>
    </>
  );
}

function RiskHeatmap({ rows }: { rows: Row[] }) {
  if (!rows.length) return <div className="empty">No subject data found yet.</div>;
  const data = orderedDashboard(rows).slice(0, 10);
  const cols = [
    { key: "att", label: "Attend gap", value: (row: Row) => Math.max(0, 80 - toNumber(row.attendance_percentage)) / 80 * 100 },
    { key: "marks", label: "Marks gap", value: (row: Row) => Math.max(0, 55 - toNumber(row.current_marks_percentage)) / 55 * 100 },
    { key: "abs", label: "Absences", value: (row: Row) => Math.min(100, toNumber(row.total_absent) * 10) },
    { key: "final", label: "Final", value: (row: Row) => toNumber(row.final_marks) > 0 ? 0 : 100 },
  ];
  const cellW = 104;
  const cellH = 34;
  const left = 96;
  const top = 50;
  const width = left + cols.length * cellW + 18;
  const height = top + data.length * cellH + 24;
  const colorFor = (value: number) => value <= 5 ? "#edf2ee" : value < 35 ? "#d9ddd5" : value < 70 ? "#d8bbb7" : "#9a3333";
  return (
    <div className="heatmap-wrap">
      <svg className="mini-chart heatmap-svg" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Risk heatmap" preserveAspectRatio="xMidYMid meet">
        <rect x="0" y="0" width={width} height={height} rx="22" fill="rgba(255,255,255,0.28)" />
        {cols.map((col, index) => (
          <text key={`heat-head-${col.key}`} x={left + index * cellW + cellW / 2} y="30" textAnchor="middle" fontSize="10" fontWeight="820" fill="#6b6b67">{col.label}</text>
        ))}
        {data.map((row, rowIndex) => {
          const y = top + rowIndex * cellH;
          return (
            <g key={`heat-row-${row.subject}`}>
              <rect x="8" y={y - 3} width={width - 16} height={cellH - 2} rx="10" fill={rowIndex % 2 ? "rgba(250,250,249,0.30)" : "rgba(232,232,227,0.20)"} />
              <text x={left - 10} y={y + 18} textAnchor="end" fontSize="11" fontWeight="820" fill="#20201e">{subjectCode(row.subject)}</text>
              {cols.map((col, colIndex) => {
                const value = col.value(row);
                return (
                  <g key={`heat-cell-${row.subject}-${col.key}`}>
                    <rect className="heatmap-cell" x={left + colIndex * cellW} y={y} width={cellW} height={cellH - 6} fill={colorFor(value)} />
                    <text x={left + colIndex * cellW + cellW / 2} y={y + 18} textAnchor="middle" fontSize="10" fontWeight="820" fill={value > 70 ? "#ffffff" : "#20201e"}>{Math.round(value)}%</text>
                    <title>{`${row.subject} | ${col.label}: ${Math.round(value)}% pressure`}</title>
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
      <div className="heatmap-legend">
        <span>low pressure</span>
        <span className="heatmap-scale" />
        <span>high pressure</span>
        <span>Hover cells for full subject names.</span>
      </div>
    </div>
  );
}

function DottedGraphPlaceholder() {
  return (
    <Panel title="Reserved insight slot" copy="No extra graph added here to avoid redundant analysis.">
      <div className="placeholder-panel">
        <div className="placeholder-inner">
          <div className="placeholder-title">Dotted placeholder</div>
          <div className="placeholder-copy">The box plot keeps its normal card width. This space is intentionally left open for a future non-redundant insight when more data becomes available.</div>
        </div>
      </div>
    </Panel>
  );
}

function SubjectBalanceRadar({ rows }: { rows: Row[] }) {
  if (!rows.length) return <div className="empty">No balance data found yet.</div>;
  const attendanceAvg = average(rows, "attendance_percentage");
  const marksAvg = average(rows, "current_marks_percentage");
  const safeShare = (rows.filter((row) => riskClass(row.final_risk_status) !== "high").length / Math.max(1, rows.length)) * 100;
  const finalEntry = rows.filter((row) => toNumber(row.final_marks) > 0).length / Math.max(1, rows.length) * 100;
  const lowAbsence = Math.max(0, 100 - rows.reduce((sum, row) => sum + toNumber(row.total_absent), 0) / Math.max(1, rows.length) * 8);
  const metrics = [
    { label: "Attendance", value: attendanceAvg },
    { label: "Marks", value: marksAvg },
    { label: "Safe", value: safeShare },
    { label: "Finals", value: finalEntry },
    { label: "Presence", value: lowAbsence },
  ];
  const width = 360;
  const height = 280;
  const cx = width / 2;
  const cy = height / 2;
  const radius = 94;
  const pointFor = (index: number, value: number) => {
    const angle = -Math.PI / 2 + (index * Math.PI * 2) / metrics.length;
    const r = (Math.max(0, Math.min(100, value)) / 100) * radius;
    return [cx + Math.cos(angle) * r, cy + Math.sin(angle) * r];
  };
  const axisFor = (index: number) => {
    const angle = -Math.PI / 2 + (index * Math.PI * 2) / metrics.length;
    return [cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius];
  };
  const polygon = metrics.map((metric, index) => pointFor(index, metric.value).join(",")).join(" ");
  return (
    <svg className="mini-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Subject balance radar">
      {[25, 50, 75, 100].map((tick) => {
        const points = metrics.map((_, index) => pointFor(index, tick).join(",")).join(" ");
        return <polygon key={tick} points={points} fill="none" stroke="#d8d8d3" />;
      })}
      {metrics.map((metric, index) => {
        const [x, y] = axisFor(index);
        return (
          <g key={metric.label}>
            <line x1={cx} y1={cy} x2={x} y2={y} stroke="#d8d8d3" />
            <text x={x} y={y + (y > cy ? 16 : -8)} textAnchor="middle" fontSize="11" fill="#6b6b67">{metric.label}</text>
          </g>
        );
      })}
      <polygon points={polygon} fill="rgba(63,116,78,0.20)" stroke="#3f744e" strokeWidth="3" />
    </svg>
  );
}

function DataTable({ rows, columns, compact = false }: { rows: Row[]; columns?: string[]; compact?: boolean }) {
  if (!rows.length) return <div className="empty">No rows available.</div>;
  const visible = columns ?? Object.keys(rows[0]);
  return (
    <div className={`table-wrap ${compact ? "compact" : ""}`}>
      <table>
        <thead>
          <tr>
            {visible.map((column) => (
              <th key={column}>{column.replace(/_/g, " ")}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {visible.map((column) => {
                const value = row[column];
                if (column.includes("risk")) {
                  return (
                    <td key={column}>
                      <span className={`risk ${riskClass(value)}`}>{String(value ?? "-")}</span>
                    </td>
                  );
                }
                return <td key={column}>{String(value ?? "")}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function noteCategory(name: string, text: string): "attendance" | "marks" | "gpa" | "other" {
  const haystack = `${name} ${text.slice(0, 700)}`.toLowerCase();
  if (haystack.includes("attendance") || haystack.includes("absent") || haystack.includes("present")) return "attendance";
  if (haystack.includes("marks") || haystack.includes("mid") || haystack.includes("final") || haystack.includes("quiz")) return "marks";
  if (haystack.includes("gpa") || haystack.includes("cgpa") || haystack.includes("semester")) return "gpa";
  return "other";
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function crc32(data: Uint8Array): number {
  let crc = -1;
  for (let i = 0; i < data.length; i += 1) {
    crc ^= data[i];
    for (let j = 0; j < 8; j += 1) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ -1) >>> 0;
}

function makeZip(files: { name: string; text: string }[]): Blob {
  const encoder = new TextEncoder();
  const localParts: Uint8Array[] = [];
  const centralParts: Uint8Array[] = [];
  let offset = 0;
  const push16 = (arr: number[], value: number) => arr.push(value & 255, (value >>> 8) & 255);
  const push32 = (arr: number[], value: number) => arr.push(value & 255, (value >>> 8) & 255, (value >>> 16) & 255, (value >>> 24) & 255);

  files.forEach((file) => {
    const nameBytes = encoder.encode(file.name.replace(/^\/+/, ""));
    const data = encoder.encode(file.text);
    const crc = crc32(data);
    const local: number[] = [];
    push32(local, 0x04034b50);
    push16(local, 20);
    push16(local, 0);
    push16(local, 0);
    push16(local, 0);
    push16(local, 0);
    push32(local, crc);
    push32(local, data.length);
    push32(local, data.length);
    push16(local, nameBytes.length);
    push16(local, 0);
    const localHeader = new Uint8Array([...local, ...nameBytes]);
    localParts.push(localHeader, data);

    const central: number[] = [];
    push32(central, 0x02014b50);
    push16(central, 20);
    push16(central, 20);
    push16(central, 0);
    push16(central, 0);
    push16(central, 0);
    push16(central, 0);
    push32(central, crc);
    push32(central, data.length);
    push32(central, data.length);
    push16(central, nameBytes.length);
    push16(central, 0);
    push16(central, 0);
    push16(central, 0);
    push16(central, 0);
    push32(central, 0);
    push32(central, offset);
    centralParts.push(new Uint8Array([...central, ...nameBytes]));
    offset += localHeader.length + data.length;
  });

  const centralSize = centralParts.reduce((sum, part) => sum + part.length, 0);
  const end: number[] = [];
  push32(end, 0x06054b50);
  push16(end, 0);
  push16(end, 0);
  push16(end, files.length);
  push16(end, files.length);
  push32(end, centralSize);
  push32(end, offset);
  push16(end, 0);
  const parts = [...localParts, ...centralParts, new Uint8Array(end)];
  const zipBytes = new Uint8Array(parts.reduce((sum, part) => sum + part.length, 0));
  let position = 0;

  for (const part of parts) {
    zipBytes.set(part, position);
    position += part.length;
  }

  return new Blob([zipBytes.buffer as ArrayBuffer], { type: "application/zip" });
}

function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [dashboard, setDashboard] = useState<Row[]>([]);
  const [attendance, setAttendance] = useState<Row[]>([]);
  const [marks, setMarks] = useState<Row[]>([]);
  const [gpa, setGpa] = useState<Row[]>([]);
  const [gpaCourses, setGpaCourses] = useState<Row[]>([]);
  const [notes, setNotes] = useState<RawNote[]>([]);
  const [status, setStatus] = useState<Status>({});
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncLogs, setSyncLogs] = useState<SyncLog[]>([]);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [rawFilter, setRawFilter] = useState<"all" | "attendance" | "marks" | "gpa" | "other">("all");
  const [openNotes, setOpenNotes] = useState<Record<string, boolean>>({});
  const [clearConfirmText, setClearConfirmText] = useState("");
  const [clearingData, setClearingData] = useState(false);

  async function refresh() {
    setError("");
    const [statusData, dashboardData, attendanceData, marksData, gpaData, gpaCourseData, rawData] = await Promise.all([
      api<Status>("/api/status"),
      api<Row[]>("/api/dashboard"),
      api<Row[]>("/api/attendance"),
      api<Row[]>("/api/marks"),
      api<Row[]>("/api/gpa"),
      api<Row[]>("/api/gpa-courses"),
      api<RawNote[]>("/api/raw-notes"),
    ]);
    setStatus(statusData);
    setDashboard(dashboardData);
    setAttendance(attendanceData);
    setMarks(marksData);
    setGpa(gpaData);
    setGpaCourses(gpaCourseData);
    setNotes(rawData);
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(`Backend is not reachable: ${err.message}`))
      .finally(() => setLoading(false));
  }, []);

  const stats = useMemo(() => {
    const highRisk = dashboard.filter((row) => riskClass(row.final_risk_status) === "high").length;
    const latestGpa = gpa.length ? toNumber(gpa[gpa.length - 1].semester_gpa).toFixed(2) : "0.00";
    const creditTotal = gpa.reduce((sum, row) => sum + toNumber(row.total_credit_hours), 0);
    const weighted = gpa.reduce((sum, row) => sum + toNumber(row.semester_gpa) * toNumber(row.total_credit_hours), 0);
    const cgpa = creditTotal ? (weighted / creditTotal).toFixed(2) : "0.00";
    return {
      subjects: dashboard.length,
      highRisk,
      safe: Math.max(0, dashboard.length - highRisk),
      attendance: average(dashboard, "attendance_percentage"),
      marks: average(dashboard, "current_marks_percentage"),
      belowAttendance: dashboard.filter((row) => toNumber(row.attendance_percentage) < 80).length,
      belowMarks: dashboard.filter((row) => toNumber(row.current_marks_percentage) < 55).length,
      missingFinals: dashboard.filter((row) => toNumber(row.final_marks) === 0).length,
      absents: dashboard.reduce((sum, row) => sum + toNumber(row.total_absent), 0),
      latestGpa,
      cgpa,
    };
  }, [dashboard, gpa]);

  const filteredNotes = useMemo(() => {
    if (rawFilter === "all") return notes;
    return notes.filter((note) => noteCategory(note.name, note.text) === rawFilter);
  }, [notes, rawFilter]);

  function toggleNote(name: string) {
    setOpenNotes((current) => ({ ...current, [name]: !current[name] }));
  }

  function downloadTextFile(note: RawNote) {
    const blob = new Blob([note.text], { type: "text/plain;charset=utf-8" });
    downloadBlob(blob, note.name.endsWith(".txt") ? note.name : `${note.name}.txt`);
  }

  async function downloadAllNotes() {
    if (!filteredNotes.length) return;
    const zip = makeZip(filteredNotes.map((note) => ({ name: note.name.endsWith(".txt") ? note.name : `${note.name}.txt`, text: note.text })));
    downloadBlob(zip, `gradescope-raw-${rawFilter}.zip`);
  }

  async function startSync() {
    setSyncing(true);
    setError("");
    setSyncLogs([]);
    try {
      const result = await api<{ ok: boolean; logs: SyncLog[] }>("/api/sync", { method: "POST" });
      setSyncLogs(result.logs);
      await refresh();
      setPage("dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sync failed.");
    } finally {
      setSyncing(false);
    }
  }

  async function clearData() {
    if (clearConfirmText !== "clear-all-local-data") {
      setError('Type "clear-all-local-data" exactly before clearing local data.');
      return;
    }

    setError("");
    setClearingData(true);
    try {
      await api("/api/clear-data", { method: "POST" });
      setClearConfirmText("");
      await refresh();
      setPage("dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not clear local data.");
    } finally {
      setClearingData(false);
    }
  }

  const nav: { key: Page; label: string; icon: string }[] = [
    { key: "dashboard", label: "Dashboard", icon: "D" },
    { key: "sync", label: "Portal Sync", icon: "S" },
    { key: "tables", label: "Tables", icon: "T" },
    { key: "raw", label: "Raw Notes", icon: "R" },
    { key: "settings", label: "Settings", icon: "C" },
  ];

  return (
    <>
      <style>{styles}</style>
      <div className={`app ${sidebarOpen ? "" : "sidebar-collapsed"}`}>
        <aside className="sidebar">
          <div className="sidebar-top">
            <div className="brand">
              <div className="brand-row">
                <div className="brand-title-wrap">
                  <div className="brand-title">GradeScope</div>
                  <div className="brand-subtitle">Local academic dashboard</div>
                </div>
              </div>
            </div>
            <button className="sidebar-toggle" onClick={() => setSidebarOpen((value) => !value)} aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}>
              {sidebarOpen ? "‹" : "›"}
            </button>
          </div>

          <div>
            <div className="nav-section-title">Navigation</div>
            <nav className="nav">
              {nav.map(({ key, label, icon }) => (
                <button key={key} className={page === key ? "active" : ""} onClick={() => setPage(key)} title={label}>
                  <span className="nav-icon" aria-hidden="true">{icon}</span>
                  <span className="nav-label">{label}</span>
                </button>
              ))}
            </nav>
          </div>

          <div className="side-card">
            <div className="side-card-title">Current Dataset</div>
            <div className="side-line">
              <span>
                <span className={`dot ${status.dashboard?.exists ? "" : "off"}`} />
                Dashboard
              </span>
              <b>{status.dashboard?.exists ? "Ready" : "Missing"}</b>
            </div>
            <div className="side-line">
              <span>Subjects</span>
              <b>{stats.subjects}</b>
            </div>
            <div className="side-line">
              <span>High risk</span>
              <b>{stats.highRisk}</b>
            </div>
            <div className="side-line">
              <span>Updated</span>
              <b>{formatDate(status.dashboard?.updated_at)}</b>
            </div>
          </div>

          <div className="side-card">
            <div className="side-card-title">Rules</div>
            <div className="side-line">
              <span>Attendance target</span>
              <b>80%</b>
            </div>
            <div className="side-line">
              <span>Marks target</span>
              <b>55%</b>
            </div>
            <div className="side-line">
              <span>Data storage</span>
              <b>Local</b>
            </div>
          </div>
        </aside>

        <main className="main">
          {error ? (
            <div className="empty" style={{ marginBottom: 16 }}>
              {error}
            </div>
          ) : null}

          {loading ? (
            <Panel title="Loading GradeScope">
              <div className="empty">Connecting to the local backend.</div>
            </Panel>
          ) : null}

          {!loading && page === "dashboard" ? (
            <>
              <PageHeader
                kicker="Dashboard"
                title="Academic control room"
                copy="A focused dashboard for attendance, marks, GPA movement, subject health, and practical risk signals."
                status={status.dashboard?.exists ? "Dashboard ready" : "No dashboard file"}
              />

              <div className="grid kpi-grid">
                <Kpi label="Subjects" value={stats.subjects} detail="tracked courses" />
                <Kpi label="High Risk" value={stats.highRisk} detail="needs action" />
                <Kpi label="Attendance" value={`${stats.attendance}%`} detail="80% target" />
                <Kpi label="Marks" value={`${stats.marks}%`} detail="55% target" />
                <Kpi label="Latest GPA" value={stats.latestGpa} detail="latest semester" />
                <Kpi label="CGPA" value={stats.cgpa} detail={`${gpa.length} semesters`} />
              </div>

              <div className="grid fact-grid">
                <Fact label="Attendance alerts" value={stats.belowAttendance} detail="Subjects below the safe line." />
                <Fact label="Marks alerts" value={stats.belowMarks} detail="Subjects below passing level." />
                <Fact label="Missing finals" value={stats.missingFinals} detail="Final marks not entered yet." />
                <Fact label="Total absents" value={stats.absents} detail="Across tracked subjects." />
              </div>

              <div className="grid chart-grid">
                <Panel title="SGPA and CGPA trend" copy="Semester GPA and cumulative GPA movement.">
                  <GpaChart rows={gpa} />
                </Panel>
                <Panel title="Risk distribution" copy="Current subject risk count.">
                  <RiskDonut rows={dashboard} />
                </Panel>
              </div>

              <div className="grid metric-grid">
                <Panel title="Attendance vs marks bubble map" copy="Labeled subjects. Bubble size grows with absences and high-risk status.">
                  <AttendanceMarksBubble rows={dashboard} />
                </Panel>
                <Panel title="Attendance and marks worms" copy="Subject-by-subject movement for attendance and marks.">
                  <AttendanceMarksWorm rows={dashboard} />
                </Panel>
              </div>

              <div className="grid metric-grid">
                <Panel title="Class balance" copy="One-view health across attendance, marks, risk, finals, and presence.">
                  <SubjectBalanceRadar rows={dashboard} />
                </Panel>
                <Panel title="Risk heatmap" copy="Pinpoints which issue is creating pressure for each subject.">
                  <RiskHeatmap rows={dashboard} />
                </Panel>
              </div>

              <div className="grid metric-grid">
                <Panel title="Performance spread box plot" copy="Color-coded spread with median, quartiles, range, and target bands.">
                  <MetricBoxPlots rows={dashboard} />
                </Panel>
                <DottedGraphPlaceholder />
              </div>

              <div className="section-spaced-lg">
                <Panel title="Subject action table" copy="Merged attendance, marks, and recommendations.">
                <DataTable
                  rows={dashboard}
                  compact
                  columns={[
                    "subject",
                    "attendance_percentage",
                    "current_marks_percentage",
                    "total_absent",
                    "grade",
                    "final_risk_status",
                    "recommendation",
                  ]}
                />
                </Panel>
              </div>
            </>
          ) : null}

          {!loading && page === "sync" ? (
            <>
              <PageHeader
                kicker="Portal Sync"
                title="Fresh ZABDesk capture"
                copy="Open ZABDesk, log in manually, then GradeScope captures attendance, marks, previous semester GPA, and rebuilds the local dataset."
                status={syncing ? "Sync running" : "Ready"}
              />
              <Panel title="Live portal sync">
                <div className="grid fact-grid">
                  <Fact label="Step 1" value="Open" detail="The portal opens in a browser window." />
                  <Fact label="Step 2" value="Capture" detail="Attendance, marks, and GPA pages are saved locally." />
                  <Fact label="Step 3" value="Parse" detail="Captured pages become clean CSV data." />
                  <Fact label="Step 4" value="Build" detail="React reads the finished dashboard dataset." />
                </div>
                <div style={{ marginTop: 16 }}>
                  <button className="btn primary" disabled={syncing} onClick={startSync}>
                    {syncing ? <span className="loader-dot" /> : null}
                    {syncing ? "Sync in progress" : "Start live portal sync"}
                  </button>
                </div>
              </Panel>

              <div className="section-spaced-lg">
                <Panel title="Latest sync logs" copy="Output from the Python backend pipeline.">
                {syncLogs.length ? (
                  <div className="grid">
                    {syncLogs.map((log) => (
                      <div key={log.script}>
                        <div className="progress-row">
                          <div className="progress-name">{log.script}</div>
                          <div className="progress-text">{log.returncode === 0 ? "Completed" : "Failed"}</div>
                        </div>
                        <pre className="log-box">{log.output || "No output."}</pre>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty">No sync logs in this React session yet.</div>
                )}
                </Panel>
              </div>
            </>
          ) : null}

          {!loading && page === "tables" ? (
            <>
              <PageHeader
                kicker="Tables"
                title="Source data library"
                copy="Parsed and merged datasets used by the dashboard."
                status={`${dashboard.length} dashboard rows`}
              />
              <div className="grid table-grid">
                <Panel title="Final dashboard table">
                  <DataTable rows={dashboard} compact />
                </Panel>
                <Panel title="GPA summary">
                  <DataTable rows={gpa} />
                </Panel>
                <Panel title="Attendance parser output">
                  <DataTable rows={attendance} />
                </Panel>
                <Panel title="Marks parser output">
                  <DataTable rows={marks} />
                </Panel>
                <Panel title="GPA course rows">
                  <DataTable rows={gpaCourses} />
                </Panel>
              </div>
            </>
          ) : null}

          {!loading && page === "raw" ? (
            <>
              <PageHeader
                kicker="Raw Notes"
                title="Captured portal text"
                copy="Rough captured portal text before cleaning, parsing, and dashboard shaping."
                status={`${notes.length} files`}
              />
              <div className="filter-row">
                <div className="filter-pills" aria-label="Raw note filters">
                  {(["all", "attendance", "marks", "gpa", "other"] as const).map((filter) => (
                    <button key={filter} className={`filter-pill ${rawFilter === filter ? "active" : ""}`} onClick={() => setRawFilter(filter)}>
                      {filter === "all" ? "All" : filter[0].toUpperCase() + filter.slice(1)}
                    </button>
                  ))}
                </div>
                <button className="btn" onClick={downloadAllNotes} disabled={!filteredNotes.length}>
                  Download all shown
                </button>
              </div>

              <div className="note-list">
                {filteredNotes.length ? (
                  filteredNotes.map((note) => {
                    const opened = !!openNotes[note.name];
                    return (
                      <section className={`card note-card ${opened ? "" : "collapsed"}`} key={note.name}>
                        <button className="note-toggle" onClick={() => toggleNote(note.name)} aria-expanded={opened}>
                          <span className="note-meta">
                            <span className="note-name">{note.name}</span>
                            <span className="status-pill">{note.text.length.toLocaleString()} chars</span>
                          </span>
                          <span>{opened ? "Collapse" : "Expand"}</span>
                        </button>
                        <div className="note-actions" style={{ padding: "0 19px 14px" }}>
                          <button className="btn" onClick={() => downloadTextFile(note)}>Download txt</button>
                        </div>
                        <div className="note-body">{note.text}</div>
                      </section>
                    );
                  })
                ) : (
                  <div className="empty">No raw sync text found for this filter. Run Portal Sync first or switch filters.</div>
                )}
              </div>
            </>
          ) : null}

          {!loading && page === "settings" ? (
            <>
              <PageHeader
                kicker="Settings"
                title="Local data control"
                copy="Reset dashboard data before a fresh sync or when you want a clean local state."
                status="Local only"
              />
              <Panel title="Clear local data">
                <div className="empty" style={{ marginBottom: 16 }}>
                  This removes dashboard CSVs, parser summaries, raw portal captures, and raw text dumps from the backend data folder.
                  <div className="confirm-block">
                    <label className="confirm-label" htmlFor="clear-confirm">
                      Type <code>clear-all-local-data</code> to enable deletion.
                    </label>
                    <input
                      id="clear-confirm"
                      className="confirm-input"
                      value={clearConfirmText}
                      onChange={(event) => setClearConfirmText(event.target.value)}
                      placeholder="clear-all-local-data"
                      spellCheck={false}
                      autoComplete="off"
                    />
                  </div>
                </div>
                <button className="btn danger" onClick={clearData} disabled={clearConfirmText !== "clear-all-local-data" || clearingData}>
                  {clearingData ? "Clearing..." : "Clear all local data"}
                </button>
              </Panel>
            </>
          ) : null}
        </main>
      </div>
    </>
  );
}

export default App;
