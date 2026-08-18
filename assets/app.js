/* =============================================================================
 * app.js — UI ของ CI/CD Resource & Compliance Planner
 * ไม่มี dependency ภายนอก · ไม่ใช้ browser storage (เก็บ state ไว้ใน URL hash)
 *
 * ลำดับการทำงานของหน้า "วางแผนทรัพยากร"
 *   1 ข้อมูลโครงการ            -> ประเภทโครงการ + ระดับผลกระทบ
 *   2 เลือกมาตรฐานรายฉบับ       -> ได้ "มาตรการที่ต้องทำ" และ "capability ที่ต้องมี"
 *   3 เงื่อนไข/ข้อจำกัดโครงการ  -> นโยบาย license, สภาพแวดล้อม, ปริมาณงาน (คิด Scale ให้)
 *   4 เครื่องมือที่ต้องติดตั้ง   -> เลือกเองหรือให้ระบบเลือกให้ (greedy set-cover)
 *   5 จัดลง VM                 -> คำนวณ A / B1 / B2 / C แล้วเอาค่ามากสุด
 *   แท็บ 6 สถาปัตยกรรม         -> Mermaid จากเครื่องมือที่เลือก
 *   แท็บ 7 Pipeline + .sh ติดตั้ง -> YAML ต่อสภาพแวดล้อม และสคริปต์ต่อเครื่อง
 * ========================================================================== */
'use strict';
import { Planner, round } from './engine.js';
import {
  buildPipelineIR, emitGitlab, emitGithub, emitAzure, emitJenkins,
  mermaidFlow, mermaidVms, mermaidEnvs, svgPipeline, buildInstallPack,
} from './pipeline.js';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = (n, d = 0) => (n == null || !Number.isFinite(+n)) ? '–'
  : (+n).toLocaleString('th-TH', { minimumFractionDigits: d, maximumFractionDigits: d });
const toNum = (v) => { const n = parseFloat(v); return Number.isFinite(n) ? n : 0; };

const SERIES = { A: 'var(--series-1)', B: 'var(--series-2)', C: 'var(--series-3)' };
const VERDICT = {
  ok:           { cls: 'ok',   icon: '✔', th: 'พอเพียง' },
  'disk-risk':  { cls: 'warn', icon: '▲', th: 'เสี่ยง: Disk ไม่พอ' },
  insufficient: { cls: 'bad',  icon: '✖', th: 'ไม่พอ: CPU/RAM' },
  unknown:      { cls: '',     icon: '·', th: 'ยังไม่กรอก spec จริง' },
};
const SEV_BADGE = {
  mandatory:   ['bad',  'บังคับ'],
  conditional: ['warn', 'บังคับเมื่อผลกระทบสูง'],
  recommended: ['opt',  'แนะนำ'],
};
/* capability ที่ต้องมี mirror ในเครื่องเมื่อระบบอยู่ในเครือข่ายปิด */
const MIRROR_CAPS = ['sca', 'container_scan', 'registry', 'sbom'];
const AIRGAP_MIRROR_GB = 250;

let CAT = null, P = null, ST = null, PLAN = null, D = null;

/* ========================================================================== */
/* state                                                                      */
/* ========================================================================== */
function defaultState() {
  return {
    project: { name: '', org: '', env: 'UAT / SIT', note: '' },
    profile: 'gov', impact: 'high', mode: 'realistic',
    pipelineOff: [], pipelineFlavor: '', pipelineView: 'flow',
    pipeKind: 'yaml', pipeFile: '',
    horizon: 36, retention: 90,
    frameworks: [],
    fit: 'all',
    licenseBlock: ['strong-copyleft', 'network-copyleft'],
    env: { airgap: false, nogpu: false, ha: false, sso: false, waf: false, monitor: false, backup: false },
    workload: { builds: 10, apps: 2, team: 10 },
    scaleAuto: true, scale: 1,
    tools: [], vms: [], vmTarget: 4,
    toolView: 'required',
  };
}

const ARCH = () => CAT.archetypes || CAT.presets || [];

function encodeState() {
  try { location.replace('#' + btoa(unescape(encodeURIComponent(JSON.stringify(ST))))); }
  catch (e) { /* ignore */ }
}
function decodeState() {
  if (!location.hash || location.hash.length < 4) return null;
  try { return JSON.parse(decodeURIComponent(escape(atob(location.hash.slice(1))))); }
  catch (e) { return null; }
}

/** ค่าที่คำนวณจาก state — เรียกทุกครั้งก่อน render */
function derive() {
  /* ใช้รายการที่ผู้ใช้ติ๊กไว้ตรง ๆ — ถ้าล้างทั้งหมดก็ต้องไม่มีมาตรการเลย
     (การเติมชุดสำเร็จให้ทำที่ boot และตอนเปลี่ยนประเภทโครงการเท่านั้น) */
  const fws = ST.frameworks || [];
  const extCaps = [];
  if (ST.env.sso) extCaps.push('iam_mfa');
  if (ST.env.waf) extCaps.push('waf');
  if (ST.env.monitor) extCaps.push('monitoring', 'siem_alert');
  if (ST.env.backup) extCaps.push('backup_dr');
  return {
    fws,
    ctrls: P.requiredControls(fws, ST.impact),
    reqCaps: P.requiredCapabilities(fws, ST.impact),
    extCaps: [...new Set(extCaps)],
    scale: ST.scaleAuto ? deriveScale(ST.workload) : +ST.scale,
    licBlock: [...(ST.licenseBlock || [])],
  };
}

/** Scale Factor จากปริมาณงานจริง — ค่าฐาน 1.0 = 10 builds/วัน, 2 แอป, ทีม 10 คน */
function deriveScale(w) {
  const s = 0.55 * (toNum(w.builds) / 10) + 0.30 * (toNum(w.apps) / 2) + 0.15 * (toNum(w.team) / 10);
  return Math.max(0.3, round(s, 1));
}

function optsFor() {
  return {
    horizonMonths: ST.horizon, scaleFactor: D.scale, mode: ST.mode,
    retentionOverride: ST.retention, profileId: ST.profile, impact: ST.impact,
    frameworks: D.fws, licenseBlocklist: D.licBlock, externalCaps: D.extCaps,
  };
}

/* ========================================================================== */
/* boot                                                                       */
/* ========================================================================== */
async function loadCatalog() {
  const embedded = window.__CATALOG__;
  if (embedded && Array.isArray(embedded.tools) && embedded.tools.length) {
    return embedded;
  }
  if (window.__STANDALONE__) {
    throw new Error('ข้อมูลที่ฝังในหน้านี้เสีย — รัน python scripts/build_standalone.py แล้วรีเฟรช (Ctrl+F5)');
  }
  const paths = ['data/catalog.json', './data/catalog.json'];
  let last = null;
  for (const p of paths) {
    try {
      const res = await fetch(p, { cache: 'no-cache' });
      const text = await res.text();
      const trimmed = text.trim();
      if (!res.ok) throw new Error(p + ' HTTP ' + res.status);
      if (!trimmed || trimmed.charAt(0) !== '{') {
        throw new Error('ได้ไฟล์ที่ไม่ใช่ JSON จาก ' + p);
      }
      return JSON.parse(text);
    } catch (e) { last = e; }
  }
  throw new Error((last && last.message ? last.message + ' — ' : '') +
    'เปิด index.html ที่ build แล้ว (มีข้อมูลฝังในไฟล์) หรือรัน python scripts/build_standalone.py');
}

async function boot() {
  CAT = await loadCatalog();
  P = new Planner(CAT);
  const def = defaultState();
  ST = Object.assign(def, decodeState() || {});
  ST.project = Object.assign(def.project, ST.project || {});
  ST.env = Object.assign(def.env, ST.env || {});
  ST.workload = Object.assign(def.workload, ST.workload || {});
  if (!ST.frameworks || !ST.frameworks.length) ST.frameworks = P.resolveFrameworks(ST.profile, null);
  if (!Array.isArray(ST.pipelineOff)) ST.pipelineOff = [];
  if (!ST.pipelineFlavor) ST.pipelineFlavor = '';
  if (!ST.pipelineView) ST.pipelineView = 'flow';
  if (!ST.pipeKind) ST.pipeKind = 'yaml';
  if (!ST.fit) ST.fit = 'all';
  D = derive();
  /* ไม่ติ๊กเครื่องมือให้อัตโนมัติตอนเปิดหน้า — ผู้ใช้กดปุ่มเอง */

  buildStaticUI();
  buildCatalogPanel();
  buildMethodPanel();
  buildFrameworkTable();
  wireTabs();
  wireTopbar();
  wirePipelineUi();
  render();
}

/* ========================================================================== */
/* toggle-button helper                                                       */
/* ========================================================================== */
function togRow(host, items, mode, isOn, onToggle) {
  if (!host) return;
  host.innerHTML = items.map(it =>
    '<button type="button" class="tog' + (mode === 'radio' ? ' radio' : '') +
    (it.cls ? ' ' + it.cls : '') + '" role="' + (mode === 'radio' ? 'radio' : 'checkbox') +
    '" aria-pressed="' + isOn(it.value) + '" data-v="' + esc(it.value) + '"' +
    (it.title ? ' title="' + esc(it.title) + '"' : '') + '>' +
    '<span class="box"></span><span>' + esc(it.label) +
    (it.flag ? ' <span class="flag">⚠</span>' : '') +
    (it.sub ? '<span class="sub">' + esc(it.sub) + '</span>' : '') + '</span></button>').join('');
  $$('.tog', host).forEach(b => {
    b.onclick = () => onToggle(b.dataset.v, b.getAttribute('aria-pressed') !== 'true');
  });
}

function refreshTog(sel, isOn) {
  const host = $(sel);
  if (host) $$('.tog', host).forEach(b => b.setAttribute('aria-pressed', String(!!isOn(b.dataset.v))));
}

/* ========================================================================== */
/* static UI                                                                  */
/* ========================================================================== */
function buildStaticUI() {
  togRow($('#pjEnvRow'), ['UAT / SIT', 'Production', 'DR / Standby', 'Development']
    .map(v => ({ value: v, label: v })), 'radio',
    v => (ST.project.env || 'UAT / SIT') === v,
    v => { ST.project.env = v; render(); });

  togRow($('#profileRow'), CAT.profiles.map(p => ({
    value: p.id, label: p.name_th, sub: 'Security ' + p.security, title: p.notes_th,
  })), 'radio', v => ST.profile === v, v => {
    ST.profile = v;
    const prof = P.profileById.get(v);
    ST.impact = prof.impact;
    ST.retention = prof.log_retention_days;
    ST.frameworks = P.resolveFrameworks(v, null);
    D = derive(); render();
  });

  togRow($('#impactRow'), [
    { value: 'low', label: 'ต่ำ (Low)' },
    { value: 'medium', label: 'กลาง (Medium)' },
    { value: 'high', label: 'สูง (High)' },
  ], 'radio', v => ST.impact === v, v => { ST.impact = v; render(); });

  $('#fwPresets').innerHTML = Object.keys(CAT.framework_presets).map(k =>
    '<button class="btn small" data-p="' + k + '" title="' +
    esc((CAT.framework_presets[k] || []).length + ' ฉบับ') + '">' +
    esc(CAT.framework_preset_labels[k] || k) + '</button>').join('');
  $$('#fwPresets button').forEach(b => {
    b.onclick = () => {
      ST.frameworks = [...CAT.framework_presets[b.dataset.p]];
      D = derive(); render();
    };
  });
  $('#fwAll').onclick = () => {
    ST.frameworks = CAT.frameworks.map(f => f.id); D = derive(); render();
  };
  $('#fwNone').onclick = () => { ST.frameworks = []; render(); };
  $('#fwRestore').onclick = () => {
    ST.frameworks = P.resolveFrameworks(ST.profile, null);
    D = derive(); render();
  };

  togRow($('#licRow'), Object.entries(CAT.license_classes)
    .filter(([k]) => k !== 'permissive' && k !== 'n/a')
    .map(([k, v]) => ({ value: k, label: shortLic(k), sub: v.split('—')[0].trim(), title: v })),
    'check', v => ST.licenseBlock.includes(v), (v, on) => {
      ST.licenseBlock = on ? [...new Set([...ST.licenseBlock, v])]
        : ST.licenseBlock.filter(x => x !== v);
      D = derive();
      ST.tools = ST.tools.filter(id => {
        const t = P.toolById.get(id);
        return t && !D.licBlock.includes(t.license_class);
      });
      syncToolsToVms(); render();
    });

  togRow($('#envRow'), [
    { value: 'airgap', label: 'เครือข่ายปิด (Air-gapped)', sub: 'ต้องมี mirror ในเครื่อง +' + AIRGAP_MIRROR_GB + ' GB' },
    { value: 'nogpu', label: 'สภาพแวดล้อมไม่รองรับ GPU', sub: 'ตัดเครื่องมือที่ต้องใช้ GPU ออก' },
    { value: 'ha', label: 'ต้องทำ High Availability', sub: 'บริการที่รันค้างคูณ 2 ชุด' },
    { value: 'sso', label: 'มี SSO/MFA ส่วนกลางแล้ว', sub: 'ถือว่าครอบคลุม iam_mfa' },
    { value: 'waf', label: 'มี WAF ที่ Edge แล้ว', sub: 'ถือว่าครอบคลุม waf' },
    { value: 'monitor', label: 'มี Monitoring/SIEM ส่วนกลางแล้ว', sub: 'ครอบคลุม monitoring, siem_alert' },
    { value: 'backup', label: 'มีระบบ Backup ส่วนกลางแล้ว', sub: 'ถือว่าครอบคลุม backup_dr' },
  ], 'check', v => !!ST.env[v], (v, on) => {
    ST.env[v] = on; D = derive();
    if (v === 'nogpu' && on) ST.tools = ST.tools.filter(t => !P.toolById.get(t).gpu);
    syncToolsToVms(); render();
  });

  const fitOpts = [
    { value: 'all', label: 'ทั้งหมด', sub: 'ไม่กรองรายการ' },
    { value: 'cloud', label: 'Cloud', sub: 'บริการจัดการบนคลาวด์' },
    { value: 'hybrid', label: 'Hybrid', sub: 'คลาวด์ + ติดตั้งเอง' },
    { value: 'private', label: 'Private / On-prem', sub: 'ศูนย์ข้อมูลปิด' },
    { value: 'local', label: 'Local / Dev', sub: 'เครื่องพัฒนาและ CI ในเครื่อง' },
  ];
  togRow($('#fitRow'), fitOpts, 'radio', v => ST.fit === v, v => { ST.fit = v; render(); });

  [['builds', '#wlBuilds'], ['apps', '#wlApps'], ['team', '#wlTeam']].forEach(([k, sel]) => {
    const el = $(sel);
    el.onchange = el.oninput = e => {
      ST.workload[k] = Math.max(1, parseInt(e.target.value, 10) || 1); render();
    };
  });
  togRow($('#scaleModeRow'), [
    { value: 'auto', label: 'คิด Scale จากปริมาณงานให้อัตโนมัติ' },
    { value: 'manual', label: 'กำหนด Scale เอง' },
  ], 'radio', v => (ST.scaleAuto ? 'auto' : 'manual') === v, v => {
    ST.scaleAuto = v === 'auto';
    if (!ST.scaleAuto) ST.scale = deriveScale(ST.workload);
    render();
  });
  $('#scaleRange').oninput = e => { ST.scale = +e.target.value; render(); };

  togRow($('#modeRow'), [
    { value: 'realistic', label: 'realistic', sub: 'บวกข้ามกลุ่ม ใช้ค่าสูงสุดในกลุ่ม (ค่าเริ่มต้น)' },
    { value: 'strict', label: 'strict', sub: 'บวกทุกเครื่องมือที่ถ่วงน้ำหนักแล้ว' },
  ], 'radio', v => ST.mode === v, v => { ST.mode = v; render(); });

  togRow($('#horizonRow'), CAT.model.horizons.map(h => ({
    value: String(h), label: h + ' เดือน', sub: round(h / 12, 1) + ' ปี',
  })), 'radio', v => String(ST.horizon) === v, v => { ST.horizon = +v; render(); });

  $('#retentionInput').onchange = e => {
    const v = parseInt(e.target.value, 10);
    ST.retention = Number.isFinite(v) && v > 0 ? v : null; render();
  };

  togRow($('#toolViewRow'), [
    { value: 'required', label: 'ที่มาตรฐานเรียกร้อง' },
    { value: 'selected', label: 'ที่เลือกไว้' },
    { value: 'all', label: 'ทั้งหมด' },
  ], 'radio', v => ST.toolView === v, v => { ST.toolView = v; renderTools(); });
  $('#qToolPlan').oninput = () => renderTools();
  $('#btnAutoTools').onclick = () => { D = derive(); autoTools(true); render(); };
  $('#btnAddMissing').onclick = () => {
    (PLAN && PLAN.compliance.recommendations || []).forEach(r => {
      if (!ST.tools.includes(r.tool_id)) ST.tools.push(r.tool_id);
    });
    syncToolsToVms(); render();
  };
  $('#btnClearTools').onclick = () => { ST.tools = []; ST.vms = []; render(); };

  $('#vmTarget').onchange = e => {
    ST.vmTarget = Math.max(1, Math.min(12, parseInt(e.target.value, 10) || 4));
    autoLayout(); render();
  };
  $('#btnAutoLayout').onclick = () => { autoLayout(); render(); };
  $('#btnAddVm').onclick = () => {
    ST.vms.push({ name: 'VM-' + (ST.vms.length + 1), role: '', tools: [], executors: {}, spec: {} });
    render();
  };

  [['#pjName', 'name'], ['#pjOrg', 'org'], ['#pjNote', 'note']].forEach(([sel, key]) => {
    const el = $(sel);
    el.oninput = e => { ST.project[key] = e.target.value; refreshMeta(); };
    el.onchange = e => { ST.project[key] = e.target.value; refreshMeta(); encodeState(); };
  });
}

function shortLic(k) {
  return { 'weak-copyleft': 'ห้าม LGPL/MPL/EPL', 'strong-copyleft': 'ห้าม GPL',
           'network-copyleft': 'ห้าม AGPL',
           'source-available': 'ห้าม SSPL/BUSL/Elastic' }[k] || k;
}

function activateTab(btn, focusPanel) {
  if (!btn) return;
  $$('.tabs button').forEach(x => {
    const on = x === btn;
    x.setAttribute('aria-selected', on ? 'true' : 'false');
    x.tabIndex = on ? 0 : -1;
  });
  $$('.panel').forEach(p => {
    const on = p.id === 'panel-' + btn.dataset.tab;
    p.classList.toggle('active', on);
    if (on) p.removeAttribute('hidden');
    else p.setAttribute('hidden', '');
  });
  if (focusPanel) {
    const panel = $('#panel-' + btn.dataset.tab);
    if (panel) {
      panel.setAttribute('tabindex', '-1');
      panel.focus();
    }
  }
}

function wireTabs() {
  const tabs = $$('.tabs button');
  tabs.forEach((b, i) => {
    b.onclick = () => activateTab(b, false);
    b.onkeydown = (e) => {
      const key = e.key;
      let next = -1;
      if (key === 'ArrowRight' || key === 'ArrowDown') next = (i + 1) % tabs.length;
      else if (key === 'ArrowLeft' || key === 'ArrowUp') next = (i - 1 + tabs.length) % tabs.length;
      else if (key === 'Home') next = 0;
      else if (key === 'End') next = tabs.length - 1;
      else return;
      e.preventDefault();
      tabs[next].focus();
      activateTab(tabs[next], false);
    };
  });
}

function wireTopbar() {
  $('#btnTheme').onclick = () => {
    const cur = document.documentElement.getAttribute('data-theme');
    document.documentElement.setAttribute('data-theme', cur === 'dark' ? 'light' : 'dark');
  };
  $('#btnPrint').onclick = () => window.print();
  $('#btnExportJson').onclick = () => download(fileStem() + '.json',
    JSON.stringify(exportPlan(), null, 2), 'application/json');
  $('#btnExportCsv').onclick = () => download(fileStem() + '.csv', buildCsv(), 'text/csv;charset=utf-8');
  const pre = $('#presetSel');
  pre.innerHTML = '<option value="">— โหลดผังเครื่องอ้างอิง —</option>' +
    ARCH().map(a => '<option value="' + a.id + '">' + esc(a.name_th) + '</option>').join('');
  pre.onchange = () => { if (pre.value) { loadArchetype(pre.value); pre.value = ''; } };
}

function currentIR() {
  return buildPipelineIR(ST.tools, {
    vms: ST.vms, profile: ST.profile, disabled: ST.pipelineOff, project: ST.project,
  });
}

function currentPack() {
  return buildInstallPack(currentIR(), CAT.tools);
}

function fitArg() {
  return (!ST.fit || ST.fit === 'all') ? null : ST.fit;
}

function yamlFor(ir, flavor) {
  if (flavor === 'github') return emitGithub(ir);
  if (flavor === 'azure') return emitAzure(ir);
  if (flavor === 'jenkins') return emitJenkins(ir);
  return emitGitlab(ir);
}

function yamlFileName(flavor) {
  if (flavor === 'github') return 'cicd.yml';
  if (flavor === 'azure') return 'azure-pipelines.yml';
  if (flavor === 'jenkins') return 'Jenkinsfile';
  return '.gitlab-ci.yml';
}

function selectedFrameworksFor(t) {
  const cm = t.compliance || { frameworks_th: [], frameworks_intl: [] };
  return [...cm.frameworks_th, ...cm.frameworks_intl].filter(f => ST.frameworks.includes(f));
}

function fwChipLabel(id) {
  const f = P.frameworkById.get(id);
  const s = (f && (f.short_th || f.id)) || id;
  return s.length <= 18 ? s : id.replace(/-20\d{2}$/, '').replace(/-256\d$/, '');
}

function ensureTip() {
  let el = $('#fwTip');
  if (!el) {
    el = document.createElement('div');
    el.id = 'fwTip';
    el.className = 'tooltip';
    el.setAttribute('role', 'tooltip');
    document.body.appendChild(el);
  }
  return el;
}

function showFwTip(anchor, t) {
  const el = ensureTip();
  const fws = selectedFrameworksFor(t);
  const extra = (t.compliance && t.compliance.framework_count)
    ? ' จากทั้งหมด ' + t.compliance.framework_count + ' ฉบับที่เครื่องมือนี้ตอบได้'
    : '';
  const list = fws.length
    ? '<ul style="margin:6px 0 0;padding-left:18px">' + fws.map(id => {
        const f = P.frameworkById.get(id);
        return '<li>' + esc((f && f.short_th) || id) + '</li>';
      }).join('') + '</ul>'
    : '<div class="hint" style="margin-top:6px">ไม่ผูกกับมาตรฐานที่เลือกอยู่ในตอนนี้</div>';
  el.innerHTML = '<b>' + esc(t.name.split(' (')[0]) + '</b><div class="hint">ตอบ ' +
    fws.length + ' มาตรฐานที่เลือก' + extra + '</div>' + list;
  const r = anchor.getBoundingClientRect();
  el.style.left = Math.min(window.innerWidth - 336, Math.max(8, r.left)) + 'px';
  el.style.top = Math.min(window.innerHeight - 12, r.bottom + 8) + 'px';
  el.classList.add('show');
}

function hideFwTip() {
  const el = $('#fwTip');
  if (el) el.classList.remove('show');
}

function toast(msg) {
  let el = $('#toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.remove('show'), 2000);
}

function addToolToVm(tid, vmIndex, fromDrag) {
  const t = P.toolById.get(tid);
  if (!t) return;
  if (!ST.tools.includes(tid)) ST.tools = [...ST.tools, tid];
  if (!ST.vms.length) autoLayout();
  const i = Math.max(0, Math.min(ST.vms.length - 1, vmIndex));
  ST.vms.forEach((v, j) => { if (j !== i) v.tools = v.tools.filter(x => x !== tid); });
  if (!ST.vms[i].tools.includes(tid)) ST.vms[i].tools.push(tid);
  const n = selectedFrameworksFor(t).length;
  if (fromDrag) toast('เพิ่ม ' + t.name.split(' (')[0] + ' — ตอบ ' + n + ' จากมาตรฐานที่เลือก');
  render();
}

function crc32(bytes) {
  let c = ~0 >>> 0;
  for (let i = 0; i < bytes.length; i++) {
    c ^= bytes[i];
    for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1));
  }
  return (~c) >>> 0;
}

function zipStore(files) {
  const enc = new TextEncoder();
  const u16 = n => { const b = new Uint8Array(2); new DataView(b.buffer).setUint16(0, n, true); return b; };
  const u32 = n => { const b = new Uint8Array(4); new DataView(b.buffer).setUint32(0, n, true); return b; };
  const chunks = [], central = [];
  let offset = 0;
  const concat = parts => {
    const n = parts.reduce((s, p) => s + p.length, 0);
    const o = new Uint8Array(n); let p = 0;
    parts.forEach(x => { o.set(x, p); p += x.length; });
    return o;
  };
  files.forEach(f => {
    const name = enc.encode(f.name.replace(/\\/g, '/'));
    const data = enc.encode(f.content);
    const crc = crc32(data);
    const local = concat([
      u32(0x04034b50), u16(20), u16(0), u16(0), u16(0), u16(0),
      u32(crc), u32(data.length), u32(data.length), u16(name.length), u16(0),
      name, data,
    ]);
    chunks.push(local);
    central.push(concat([
      u32(0x02014b50), u16(20), u16(20), u16(0), u16(0), u16(0), u16(0),
      u32(crc), u32(data.length), u32(data.length), u16(name.length), u16(0),
      u16(0), u16(0), u16(0), u32(0), u32(offset), name,
    ]));
    offset += local.length;
  });
  const cen = concat(central);
  const end = concat([
    u32(0x06054b50), u16(0), u16(0), u16(files.length), u16(files.length),
    u32(cen.length), u32(offset), u16(0),
  ]);
  return concat([...chunks, cen, end]);
}

function wirePipelineUi() {
  const copy = (sel) => {
    const el = $(sel);
    if (!el) return;
    const t = el.value || '';
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).catch(() => {});
    } else {
      el.focus(); el.select();
      try { document.execCommand('copy'); } catch (e) { /* ignore */ }
    }
  };
  const btnM = $('#btnCopyMermaid');
  if (btnM) btnM.onclick = () => copy('#archMermaid');
  const btnDm = $('#btnDlMermaid');
  if (btnDm) btnDm.onclick = () => {
    const ir = currentIR();
    const src = ST.pipelineView === 'vms' ? mermaidVms(ir)
      : ST.pipelineView === 'env' ? mermaidEnvs(ir) : mermaidFlow(ir);
    download(fileStem() + '-architecture.mmd', src, 'text/plain');
  };
  const btnY = $('#btnCopyYaml');
  if (btnY) btnY.onclick = () => copy('#pipeYaml');
  const btnDy = $('#btnDlYaml');
  if (btnDy) btnDy.onclick = () => {
    const y = $('#pipeYaml');
    const name = ST._pipeName || yamlFileName(ST.pipelineFlavor || 'gitlab');
    download(fileStem() + '-' + name.replace(/\//g, '_'), (y && y.value) || '', 'text/plain');
  };
  const btnPack = $('#btnDlPack');
  if (btnPack) btnPack.onclick = () => {
    const ir = currentIR();
    const flavor = ST.pipelineFlavor || ir.flavors[0] || 'gitlab';
    const pack = currentPack();
    const files = [
      { name: yamlFileName(flavor), content: yamlFor(ir, flavor) },
    ];
    Object.keys(pack).sort().forEach(k => files.push({ name: k, content: pack[k] }));
    download(fileStem() + '-cicd-pack.zip', zipStore(files), 'application/zip');
  };
}

function renderArchitecture() {
  const canvas = $('#archCanvas');
  if (!canvas) return;
  togRow($('#archViewRow'), [
    { value: 'flow', label: '6 ขั้น Pipeline', sub: 'งานตามเครื่องมือที่เลือก' },
    { value: 'vms', label: 'ผัง VM', sub: 'เครื่องมือต่อเครื่อง' },
    { value: 'env', label: 'Dev → Prod', sub: 'เส้นทางสภาพแวดล้อม' },
  ], 'radio', v => ST.pipelineView === v, v => { ST.pipelineView = v; render(); });
  const ir = currentIR();
  canvas.innerHTML = svgPipeline(ir, ST.pipelineView);
  const src = ST.pipelineView === 'vms' ? mermaidVms(ir)
    : ST.pipelineView === 'env' ? mermaidEnvs(ir) : mermaidFlow(ir);
  const ta = $('#archMermaid');
  if (ta) ta.value = src;
  const req = $('#archReqs');
  if (!req) return;
  const jobs = ir.jobs.filter(j => j.enabled);
  const gates = [...new Set(jobs.flatMap(j => j.gates))].sort();
  req.innerHTML =
    '<div class="grid3">' +
      tile('งานใน Pipeline', fmt(jobs.length), 'จากเครื่องมือที่เลือก ' + ST.tools.length + ' รายการ', '') +
      tile('สภาพแวดล้อม', ir.envs.map(e => e.toUpperCase()).join(' → '), 'ขั้นท้ายของ pipeline', '') +
      tile('Orchestrator', ir.orchestrator, 'รูปแบบไฟล์: ' + ir.flavors.join(', '), '') +
      tile('เกณฑ์ Gate', gates.join(' ') || '–', 'อ้างจากงานที่เปิดอยู่', gates.length ? 'ok' : 'warn') +
    '</div>' +
    '<ul class="hint" style="margin-top:10px;line-height:1.8">' +
      '<li>Secret ที่พบในโค้ดต้อง block และ revoke (G-07)</li>' +
      '<li>ภาครัฐบังคับ SBOM (G-10) และลายเซ็น artifact (G-11) ก่อนขึ้น Prod</li>' +
      (ST.tools.includes('owasp-zap')
        ? '<li>DAST บน UAT ก่อนขึ้น Prod ตามมาตรฐานเว็บไซต์ 2568</li>' : '') +
      (ST.profile === 'gov'
        ? '<li>โปรไฟล์ภาครัฐ: มีขั้น DR และ Prod เป็น manual approval</li>' : '') +
    '</ul>';
}

function renderPipeline() {
  const host = $('#pipeJobs');
  if (!host) return;
  const ir = currentIR();
  const flavor = ST.pipelineFlavor || ir.flavors[0] || 'gitlab';
  const pack = currentPack();
  const installNames = Object.keys(pack).sort();
  togRow($('#pipeKindRow'), [
    { value: 'yaml', label: 'Pipeline YAML', sub: yamlFileName(flavor) },
    { value: 'install', label: 'สคริปต์ติดตั้ง (.sh)', sub: installNames.length + ' ไฟล์' },
  ], 'radio', v => ST.pipeKind === v, v => { ST.pipeKind = v; render(); });
  togRow($('#pipeFlavorRow'), [
    { value: 'gitlab', label: 'GitLab CI', sub: '.gitlab-ci.yml' },
    { value: 'github', label: 'GitHub Actions', sub: '.github/workflows/cicd.yml' },
    { value: 'azure', label: 'Azure Pipelines', sub: 'azure-pipelines.yml' },
    { value: 'jenkins', label: 'Jenkins', sub: 'Jenkinsfile' },
  ], 'radio', v => flavor === v, v => { ST.pipelineFlavor = v; render(); });
  const fileHost = $('#pipeFileRow');
  if (fileHost) {
    if (ST.pipeKind === 'install') {
      if (!ST.pipeFile || !pack[ST.pipeFile]) ST.pipeFile = installNames[0] || '';
      togRow(fileHost, installNames.map(n => ({
        value: n, label: n.replace(/^install\//, ''), sub: n,
      })), 'radio', v => ST.pipeFile === v, v => { ST.pipeFile = v; render(); });
    } else {
      fileHost.innerHTML = '';
    }
  }
  const meta = $('#pipeMeta');
  const yname = ST.pipeKind === 'install' ? (ST.pipeFile || 'install/all.sh') : yamlFileName(flavor);
  ST._pipeName = yname;
  if (meta) {
    meta.innerHTML = 'ตรวจพบ orchestrator = <b>' + esc(ir.orchestrator) +
      '</b> · งานที่เปิด ' + ir.jobs.filter(j => j.enabled).length + '/' + ir.jobs.length +
      ' · ไฟล์ <b>' + esc(yname) + '</b>' +
      (ir.vms.length ? ' · ติดตั้ง ' + ir.vms.length + ' เครื่อง' : ' · ยังไม่มี VM');
  }
  host.innerHTML = ir.stages.map(st => {
    const list = ir.jobs.filter(j => j.stage === st.id);
    if (!list.length) return '';
    return '<div class="stagebox"><div class="sh"><span class="stage-pill st' + st.n + '">' +
      st.n + '</span>' + esc(st.label) + '</div><div class="togrow">' +
      list.map(j => '<button type="button" class="tog" role="checkbox" aria-pressed="' +
        j.enabled + '" data-job="' + esc(j.id) + '"><span class="box"></span><span>' +
        esc(j.name) + '<span class="sub">' + esc(j.tool_id || 'bootstrap') +
        (j.env ? ' · ' + j.env : '') +
        (j.gates.length ? ' · ' + j.gates.join(' ') : '') +
        '</span></span></button>').join('') + '</div></div>';
  }).join('') || '<div class="note">เลือกเครื่องมือในแท็บวางแผนก่อน จึงจะมีงานใน pipeline</div>';
  $$('#pipeJobs .tog').forEach(b => {
    b.onclick = () => {
      const id = b.dataset.job;
      ST.pipelineOff = ST.pipelineOff.includes(id)
        ? ST.pipelineOff.filter(x => x !== id) : [...ST.pipelineOff, id];
      render();
    };
  });
  const y = $('#pipeYaml');
  if (y) {
    y.value = ST.pipeKind === 'install'
      ? (pack[ST.pipeFile] || pack['install/all.sh'] || '')
      : yamlFor(ir, flavor);
  }
}

/* ========================================================================== */
/* tool selection & VM layout                                                 */
/* ========================================================================== */
function toolPool() {
  return CAT.tools.filter(t =>
    t.profiles.includes(ST.profile) &&
    !D.licBlock.includes(t.license_class || 'permissive') &&
    !(ST.env.nogpu && t.gpu) &&
    P.toolFits(t, fitArg()));
}

function autoTools(relayout) {
  const r = P.requiredTools(D.fws, ST.profile, ST.impact, D.licBlock, [], D.extCaps, fitArg());
  ST.tools = r.tools.filter(id => !(ST.env.nogpu && P.toolById.get(id).gpu));
  if (relayout || !ST.vms.length) autoLayout(); else syncToolsToVms();
}

/**
 * จัดเครื่องมือลง VM อัตโนมัติ
 * หลักการ: กลุ่ม ci_seq / async / load ยุบเป็นค่าสูงสุดเมื่ออยู่เครื่องเดียวกัน จึงรวมไว้เครื่องเดียวคุ้มกว่า
 *          ส่วน resident ต้องบวกกันทุกตัว จึงต้องกระจายให้สมดุล
 */
function autoLayout() {
  const n = Math.max(1, Math.min(12, ST.vmTarget || 4));
  const byGroup = { resident: [], ci_seq: [], async: [], load: [] };
  ST.tools.forEach(id => { byGroup[P.toolById.get(id).conc_group].push(id); });
  const vms = [];
  const mk = (name, role) => {
    vms.push({ name, role, tools: [], executors: {}, spec: {} });
    return vms[vms.length - 1];
  };
  const loadOf = v => v.tools.reduce((s, x) =>
    s + P.toolById.get(x).min.ram_gb * P.dutyWeight(P.toolById.get(x).freq), 0);

  if (n === 1) {
    mk('ALL-IN-ONE-01', 'รวมทุกหน้าที่ไว้เครื่องเดียว (เหมาะกับ Dev/PoC เท่านั้น)').tools = [...ST.tools];
  } else if (n === 2) {
    mk('CI-CONTROL-01', 'บริการที่รันค้างตลอด: Git, Pipeline, SAST, ฐานข้อมูล, Log').tools = byGroup.resident;
    mk('WORKER-01', 'งานเป็นรอบ: Build, Test, สแกนความปลอดภัย, ทดสอบภาระ')
      .tools = [...byGroup.ci_seq, ...byGroup.async, ...byGroup.load];
  } else {
    mk('BUILD-AGENT-01', 'ขั้นตอนภายใน Pipeline ที่รันเรียงต่อกัน (Build, Test, Scan, Sign)')
      .tools = byGroup.ci_seq;
    mk('SEC-TEST-01', 'งานหลังบ้านและงานภาระหนัก (DAST, Accessibility, Load Test, Posture Scan)')
      .tools = [...byGroup.async, ...byGroup.load];
    const roles = [
      'ศูนย์กลาง CI/CD: Git, Pipeline Orchestration, SAST, ฐานข้อมูลของเครื่องมือ',
      'ที่เก็บและบันทึก: Registry, Object Storage, Secret, Log, Audit Trail',
      'ขึ้นระบบและเฝ้าระวัง: Orchestration, GitOps, Observability, Runtime Security',
      'Edge และการยืนยันตัวตน: Reverse Proxy, WAF, SSO',
      'บริการเสริม: Cache, Queue, File Server',
      'สำรองและกู้คืน: Backup, Archive',
      'เครื่องสำรองสำหรับงานเฉพาะ',
    ];
    const resVms = [];
    for (let i = 0; i < n - 2; i++) {
      resVms.push(mk('CORE-' + String(i + 1).padStart(2, '0'),
        roles[i] || roles[roles.length - 1]));
    }
    [...byGroup.resident]
      .sort((a, b) => P.toolById.get(b).min.ram_gb - P.toolById.get(a).min.ram_gb)
      .forEach(id => {
        let best = resVms[0], bestLoad = Infinity;
        resVms.forEach(v => { const l = loadOf(v); if (l < bestLoad) { bestLoad = l; best = v; } });
        best.tools.push(id);
      });
  }
  ST.vms = vms.filter(v => v.tools.length);
  applyVmOptions();
}

/** ให้ VM ครอบคลุมเครื่องมือที่เลือกไว้พอดี (ไม่ขาด ไม่เกิน) */
function syncToolsToVms() {
  if (!ST.vms.length) { autoLayout(); return; }
  const sel = new Set(ST.tools);
  ST.vms.forEach(v => { v.tools = v.tools.filter(t => sel.has(t)); });
  const placed = new Set(ST.vms.flatMap(v => v.tools));
  const loadOf = v => v.tools.reduce((s, x) =>
    s + P.toolById.get(x).min.ram_gb * P.dutyWeight(P.toolById.get(x).freq), 0);
  ST.tools.filter(t => !placed.has(t)).forEach(id => {
    const g = P.toolById.get(id).conc_group;
    const same = ST.vms.filter(v => v.tools.some(t => P.toolById.get(t).conc_group === g));
    const pool = (g !== 'resident' && same.length) ? same : ST.vms;
    let best = pool[0], bestLoad = Infinity;
    pool.forEach(v => { const l = loadOf(v); if (l < bestLoad) { bestLoad = l; best = v; } });
    best.tools.push(id);
  });
  ST.vms = ST.vms.filter(v => v.tools.length);
  applyVmOptions();
}

/** ใส่เงื่อนไข HA และ Air-gapped ลงในแต่ละ VM */
function applyVmOptions() {
  ST.vms.forEach(v => {
    v.executors = v.executors || {};
    v.tools.forEach(id => {
      const t = P.toolById.get(id);
      if (ST.env.ha && t.resident) v.executors[id] = Math.max(2, v.executors[id] || 1);
      else if (!ST.env.ha && v.executors[id] === 2 && t.resident) delete v.executors[id];
    });
    Object.keys(v.executors).forEach(k => { if (!v.tools.includes(k)) delete v.executors[k]; });
    v.extraInstallGb = (ST.env.airgap &&
      v.tools.some(id => P.toolById.get(id).capabilities.some(c => MIRROR_CAPS.includes(c))))
      ? AIRGAP_MIRROR_GB : 0;
  });
}

function loadArchetype(id) {
  const a = ARCH().find(x => x.id === id);
  if (!a) return;
  ST.profile = a.profile;
  ST.impact = P.profileById.get(a.profile).impact;
  ST.frameworks = P.resolveFrameworks(a.profile, null);
  ST.tools = [...new Set(a.vms.flatMap(v => v.tools))];
  ST.vmTarget = a.vms.length;
  ST.vms = a.vms.map(v => ({ name: v.host, role: v.role_th, tools: [...v.tools], executors: {}, spec: {} }));
  D = derive(); applyVmOptions(); render();
}

/* ========================================================================== */
/* render                                                                     */
/* ========================================================================== */
function render() {
  D = derive();
  syncControlValues();
  applyVmOptions();
  PLAN = P.planFleet(ST.vms, optsFor());
  renderStandards();
  renderTools();
  renderFleet();
  renderArchetypes();
  renderVms();
  renderCompliance();
  renderStorage();
  renderArchitecture();
  renderPipeline();
  refreshMeta();
  encodeState();
}

function syncControlValues() {
  $('#pjName').value = ST.project.name || '';
  $('#pjOrg').value = ST.project.org || '';
  $('#pjNote').value = ST.project.note || '';
  $('#wlBuilds').value = ST.workload.builds;
  $('#wlApps').value = ST.workload.apps;
  $('#wlTeam').value = ST.workload.team;
  $('#retentionInput').value = ST.retention || '';
  $('#vmTarget').value = ST.vmTarget;
  $('#scaleRange').value = ST.scale;
  $('#scaleVal').textContent = (+ST.scale).toFixed(1) + '×';
  $('#scaleManualWrap').style.display = ST.scaleAuto ? 'none' : 'block';
  const auto = deriveScale(ST.workload);
  $('#scaleHint').innerHTML =
    'คิดจากปริมาณงาน: 0.55×(build/10) + 0.30×(แอป/2) + 0.15×(ทีม/10) = <b>' +
    auto.toFixed(1) + '×</b>' + (ST.scaleAuto ? ' — ใช้ค่านี้'
      : ' — แต่กำหนดเองไว้ที่ <b>' + (+ST.scale).toFixed(1) + '×</b>');
  const prof = P.profileById.get(ST.profile);
  $('#profileHint').textContent = prof ? prof.notes_th : '';
  const logCtl = D.ctrls.find(c => c.control_id === 'C-LOG-90');
  $('#retentionHint').innerHTML = logCtl
    ? 'มาตรฐานที่เลือกบังคับเก็บ Log ขั้นต่ำ <b>' + logCtl.param.log_retention_days +
      ' วัน</b> (อ้างจาก ' + Object.keys(logCtl.refs)
        .map(f => esc(P.frameworkById.get(f).short_th)).join(', ') + ')'
    : 'มาตรฐานที่เลือกไม่มีข้อบังคับเรื่องอายุการเก็บ Log โดยเฉพาะ';
  refreshTog('#pjEnvRow', v => (ST.project.env || 'UAT / SIT') === v);
  refreshTog('#profileRow', v => ST.profile === v);
  refreshTog('#impactRow', v => ST.impact === v);
  refreshTog('#licRow', v => ST.licenseBlock.includes(v));
  refreshTog('#envRow', v => !!ST.env[v]);
  refreshTog('#fitRow', v => ST.fit === v);
  refreshTog('#scaleModeRow', v => (ST.scaleAuto ? 'auto' : 'manual') === v);
  refreshTog('#modeRow', v => ST.mode === v);
  refreshTog('#horizonRow', v => String(ST.horizon) === v);
  refreshTog('#toolViewRow', v => ST.toolView === v);
}

function tile(k, v, s, cls) {
  return '<div class="tile ' + (cls || '') + '"><div class="k">' + esc(k) + '</div>' +
    '<div class="v" style="font-size:' + (String(v).length > 12 ? '1rem' : '1.5rem') + '">' +
    esc(v) + '</div><div class="s">' + esc(s) + '</div></div>';
}

/* --------------------------------------------- step 2: standards ---------- */
function renderStandards() {
  const fams = Object.entries(CAT.framework_families).sort((a, b) => a[1].order - b[1].order);
  const sel = new Set(ST.frameworks);

  const build = (region) => fams.filter(([, f]) => f.region === region).map(([fid, fam]) => {
    const list = CAT.frameworks.filter(f => f.family === fid);
    if (!list.length) return '';
    const on = list.filter(f => sel.has(f.id)).length;
    return '<div class="fwgroup"><div class="gh">' + esc(fam.label_th) +
      '<span class="cnt">' + on + '/' + list.length + '</span>' +
      '<button class="btn small ghost noprint famall" data-f="' + fid + '">' +
      (on === list.length ? 'เอาออกทั้งกลุ่ม' : 'เลือกทั้งกลุ่ม') + '</button></div><div class="togrow">' +
      list.map(f => '<button type="button" class="tog" role="checkbox" aria-pressed="' +
        sel.has(f.id) + '" data-v="' + esc(f.id) + '" title="' +
        esc(f.name_th + ' — ' + (f.scope_th || '')) + '"><span class="box"></span><span>' +
        esc(f.short_th) + (f.verify ? ' <span class="flag">⚠</span>' : '') +
        '<span class="sub">' + esc(f.authority || '') + ' · ' +
        Object.keys(f.controls).length + ' มาตรการ</span></span></button>').join('') +
      '</div></div>';
  }).join('');

  $('#fwTh').innerHTML = build('th');
  $('#fwIntl').innerHTML = build('intl');
  $$('#fwTh .tog, #fwIntl .tog').forEach(b => {
    b.onclick = () => {
      const id = b.dataset.v;
      ST.frameworks = sel.has(id) ? ST.frameworks.filter(x => x !== id) : [...ST.frameworks, id];
      render();
    };
  });
  $$('.famall').forEach(b => {
    b.onclick = () => {
      const ids = CAT.frameworks.filter(f => f.family === b.dataset.f).map(f => f.id);
      const allOn = ids.every(i => sel.has(i));
      ST.frameworks = allOn ? ST.frameworks.filter(x => !ids.includes(x))
        : [...new Set([...ST.frameworks, ...ids])];
      render();
    };
  });

  const nMand = D.ctrls.filter(c => c.severity === 'mandatory').length;
  const verify = ST.frameworks.filter(f => P.frameworkById.get(f) && P.frameworkById.get(f).verify);
  $('#fwSummary').innerHTML = '<div class="grid3">' +
    tile('มาตรฐานที่เลือก', fmt(ST.frameworks.length),
      'จาก ' + CAT.frameworks.length + ' ฉบับในระบบ', ST.frameworks.length ? '' : 'bad') +
    tile('มาตรการที่ต้องทำ', fmt(D.ctrls.length),
      'บังคับ ' + nMand + ' · ที่เหลือเป็นเงื่อนไข/แนะนำ', '') +
    tile('Capability ที่ต้องมี', fmt(Object.keys(D.reqCaps).length),
      'จาก ' + Object.keys(CAT.capabilities).length + ' รายการ', '') +
    '</div>' + (verify.length ? '<div class="note">⚠ มาตรฐาน ' + verify.length +
      ' ฉบับที่เลือกไว้ (' + verify.map(f => esc(P.frameworkById.get(f).short_th)).join(', ') +
      ') ควรตรวจเลขที่ประกาศและปีกับราชกิจจานุเบกษาหรือเว็บไซต์ของหน่วยงานเจ้าของมาตรฐาน ' +
      'ก่อนนำไปอ้างอิงใน TOR — ตัวมาตรการที่ผูกไว้เป็นสาระของข้อกำหนด ใช้ได้ตามปกติ</div>' : '');

  const groups = {};
  D.ctrls.forEach(c => { (groups[c.group] = groups[c.group] || []).push(c); });
  $('#ctrlTbl').innerHTML =
    '<thead><tr><th>มาตรการ</th><th class="ctr">ระดับ</th><th>Capability ที่ต้องมี</th>' +
    '<th>อ้างจากมาตรฐาน (เลขข้อ)</th></tr></thead><tbody>' +
    Object.entries(groups).map(([g, list]) =>
      '<tr><td colspan="4" style="background:var(--surface-3);font-weight:800">' +
      esc(CAT.control_groups[g]) + ' — ' + list.length + ' มาตรการ</td></tr>' +
      list.map(c => {
        const sb = SEV_BADGE[c.severity];
        return '<tr><td><b>' + esc(c.title_th) + '</b><div class="hint mono">' +
          esc(c.control_id) + '</div>' +
          (c.detail_th ? '<div class="hint">' + esc(c.detail_th) + '</div>' : '') + '</td>' +
          '<td class="ctr"><span class="badge ' + sb[0] + '">' + esc(sb[1]) + '</span></td><td>' +
          c.caps.map(x => '<span class="chip">' + esc(x) + '</span>').join(' ') + '</td>' +
          '<td class="hint">' + Object.entries(c.refs).map(([f, cl]) =>
            '<div><b>' + esc(P.frameworkById.get(f).short_th) + '</b> — ' + esc(cl) + '</div>')
            .join('') + '</td></tr>';
      }).join('')).join('') + '</tbody>';

  const have = P.coveredCapabilities(ST.tools);
  $('#capTbl').innerHTML =
    '<thead><tr><th>Capability</th><th class="ctr">มาตรการที่เรียกร้อง</th><th class="ctr">สถานะ</th>' +
    '<th>เครื่องมือที่ตอบได้ (ตาม profile และนโยบายลิขสิทธิ์)</th></tr></thead><tbody>' +
    Object.entries(D.reqCaps).map(([cap, ctl]) => {
      const ext = D.extCaps.includes(cap);
      const cand = toolPool().filter(t => t.capabilities.includes(cap));
      return '<tr><td><b>' + esc(CAT.capabilities[cap]) + '</b><div class="hint mono">' +
        esc(cap) + '</div></td><td class="ctr hint mono">' + ctl.map(esc).join(', ') + '</td>' +
        '<td class="ctr">' + (ext ? '<span class="badge core">ระบบส่วนกลาง</span>'
          : have.has(cap) ? '<span class="badge ok">มีแล้ว</span>'
          : '<span class="badge bad">ยังขาด</span>') + '</td><td>' +
        (cand.length ? cand.map(t => '<span class="chip' +
          (ST.tools.includes(t.id) ? ' on' : '') + '">' + esc(t.name.split(' (')[0]) + '</span>').join(' ')
          : '<span class="hint">ไม่มีเครื่องมือที่ใช้ได้ภายใต้เงื่อนไขนี้</span>') + '</td></tr>';
    }).join('') + '</tbody>';
}

/* --------------------------------------------- step 4: tools -------------- */
function renderTools() {
  const reqCaps = Object.keys(D.reqCaps);
  const have = P.coveredCapabilities(ST.tools);
  const okN = reqCaps.filter(c => have.has(c) && !D.extCaps.includes(c)).length;
  const extN = reqCaps.filter(c => D.extCaps.includes(c)).length;
  const missN = reqCaps.length - okN - extN;
  const pct = n => (reqCaps.length ? (n / reqCaps.length * 100).toFixed(1) : 0);
  const comp = PLAN ? PLAN.compliance : null;

  $('#coverBar').innerHTML =
    '<div class="cover"><span class="ok" style="width:' + pct(okN) + '%"></span>' +
    '<span class="ext" style="width:' + pct(extN) + '%"></span>' +
    '<span class="miss" style="width:' + pct(missN) + '%"></span></div><div class="covleg">' +
    '<span><i style="background:var(--good)"></i>มีเครื่องมือรองรับ ' + okN + '</span>' +
    '<span><i style="background:var(--series-1)"></i>ระบบส่วนกลางรองรับ ' + extN + '</span>' +
    '<span><i style="background:var(--critical)"></i>ยังขาด ' + missN + '</span>' +
    '<span>เลือกไว้ ' + ST.tools.length + ' เครื่องมือ</span>' +
    (comp ? '<span>คะแนน Compliance <b>' + comp.score + '%</b> · ไม่ผ่าน ' +
      comp.failed_count + ' มาตรการ</span>' : '') + '</div>';

  const hint = $('#toolHint');
  if (hint) {
    const rec = P.requiredTools(D.fws, ST.profile, ST.impact, D.licBlock, ST.tools, D.extCaps, fitArg());
    const n = rec.added.length;
    if (!ST.tools.length && n) {
      hint.innerHTML = '<div class="hintbar">ยังไม่ได้เลือกเครื่องมือ — แนะนำ <b>' + n +
        '</b> รายการจากมาตรฐานที่เลือก (กดปุ่มเลือกอัตโนมัติเมื่อพร้อม)</div>';
    } else if (n) {
      hint.innerHTML = '<div class="hintbar">แนะนำเพิ่มอีก <b>' + n +
        '</b> รายการเพื่อปิดช่องว่าง — กด «เพิ่มเฉพาะตัวที่ยังขาด» หรือเลือกอัตโนมัติใหม่</div>';
    } else if (!ST.tools.length) {
      hint.innerHTML = '<div class="hintbar">เลือกมาตรฐานก่อน แล้วค่อยติ๊กเครื่องมือหรือกดเลือกอัตโนมัติ</div>';
    } else {
      hint.innerHTML = '';
    }
  }

  const q = ($('#qToolPlan').value || '').trim().toLowerCase();
  const missing = new Set(comp ? Object.keys(comp.gaps) : []);
  const shown = toolPool().filter(t => {
    if (ST.toolView === 'selected' && !ST.tools.includes(t.id)) return false;
    if (ST.toolView === 'required' && !ST.tools.includes(t.id) &&
        !t.capabilities.some(c => reqCaps.includes(c))) return false;
    if (q && !(t.name + ' ' + t.category + ' ' + t.id + ' ' +
               t.capabilities.join(' ')).toLowerCase().includes(q)) return false;
    return true;
  });
  const byStage = {};
  shown.forEach(t => { (byStage[t.stage] = byStage[t.stage] || []).push(t); });
  $('#toolPicker').innerHTML = Object.keys(CAT.stages).map(sn => {
    const list = byStage[sn] || [];
    if (!list.length) return '';
    const onN = list.filter(t => ST.tools.includes(t.id)).length;
    return '<div class="stagebox"><div class="sh"><span class="stage-pill st' + sn + '">' + sn +
      '</span>' + esc(CAT.stages[sn]) + '<span class="hint">เลือก ' + onN + '/' + list.length +
      '</span></div><div class="togrow">' + list.map(t => toolTog(t, missing)).join('') + '</div></div>';
  }).join('') ||
    '<div class="note">ไม่มีเครื่องมือที่ตรงเงื่อนไข — ลองเปลี่ยนตัวกรองหรือนโยบายลิขสิทธิ์</div>';

  $$('#toolPicker .tog').forEach(b => {
    let dragged = false;
    b.onclick = () => {
      if (dragged) { dragged = false; return; }
      const id = b.dataset.v;
      ST.tools = ST.tools.includes(id) ? ST.tools.filter(x => x !== id) : [...ST.tools, id];
      syncToolsToVms(); render();
    };
    b.ondragstart = (e) => {
      dragged = true;
      e.dataTransfer.setData('text/plain', b.dataset.v);
      e.dataTransfer.effectAllowed = 'copy';
      const t = P.toolById.get(b.dataset.v);
      if (t) {
        const ghost = document.createElement('div');
        ghost.className = 'drag-ghost';
        ghost.id = 'dragGhost';
        const fws = selectedFrameworksFor(t).slice(0, 6);
        ghost.innerHTML = '<b>' + esc(t.name.split(' (')[0]) + '</b><div class="fwchips">' +
          fws.map(id => '<span class="fwchip">' + esc(fwChipLabel(id)) + '</span>').join('') +
          '</div>';
        document.body.appendChild(ghost);
        e.dataTransfer.setDragImage(ghost, 16, 16);
      }
    };
    b.ondragend = () => {
      const g = $('#dragGhost');
      if (g) g.remove();
      hideFwTip();
    };
    let tipTimer = 0;
    b.onmouseenter = () => {
      const t = P.toolById.get(b.dataset.v);
      if (!t) return;
      tipTimer = setTimeout(() => showFwTip(b, t), 280);
    };
    b.onmouseleave = () => { clearTimeout(tipTimer); hideFwTip(); };
    b.onfocus = () => { const t = P.toolById.get(b.dataset.v); if (t) showFwTip(b, t); };
    b.onblur = hideFwTip;
  });
}

function toolTog(t, missing) {
  const on = ST.tools.includes(t.id);
  const closes = t.capabilities.filter(c => missing.has(c));
  const need = !on && closes.length > 0;
  const fws = selectedFrameworksFor(t);
  const nFw = fws.length;
  const shown = fws.slice(0, 5);
  const extra = nFw > shown.length ? '<span class="fwchip">+' + (nFw - shown.length) + '</span>' : '';
  const chips = nFw
    ? '<span class="fwchips">' + shown.map(id => '<span class="fwchip">' + esc(fwChipLabel(id)) +
      '</span>').join('') + extra + '</span>'
    : '';
  const sub = t.min.vcpu + 'c / ' + t.min.ram_gb + 'G · ' + t.conc_group +
    ' · w=' + Math.round(P.dutyWeight(t.freq) * 100) + '% · ' + t.license;
  const fwText = nFw ? 'ตอบ ' + nFw + ' มาตรฐานที่เลือก' : 'ไม่ผูกกับมาตรฐานที่เลือก';
  return '<button type="button" class="tog' + (need ? ' req' : '') + '" role="checkbox" ' +
    'draggable="true" aria-pressed="' + on + '" data-v="' + esc(t.id) + '" title="' +
    esc(t.name + ' — ลากไปวางบนการ์ด VM ได้') + '"><span class="box"></span><span>' +
    esc(t.name.split(' (')[0]) + (need ? ' <span class="flag">จำเป็น</span>' : '') +
    '<span class="sub">' + esc(sub) + '</span><span class="sub">' + esc(fwText) +
    (closes.length ? ' · ปิดช่องว่าง: ' + esc(closes.join(', ')) : '') +
    '</span>' + chips + '</span></button>';
}

/* --------------------------------------------- fleet ---------------------- */
function renderFleet() {
  const t = PLAN.totals;
  const specKnown = t.spec_vcpu > 0;
  $('#fleetTiles').innerHTML = [
    tile('จำนวน VM', fmt(t.vm_count), ST.tools.length + ' เครื่องมือ · โหมด ' + ST.mode, ''),
    tile('vCPU ที่ต้องจัดสรร', fmt(t.alloc_vcpu),
      specKnown ? 'spec ที่ขอไว้ ' + fmt(t.spec_vcpu) : 'รวมทุกเครื่อง',
      specKnown ? (t.spec_vcpu >= t.alloc_vcpu ? 'ok' : 'bad') : ''),
    tile('RAM ที่ต้องจัดสรร (GB)', fmt(t.alloc_ram_gb),
      specKnown ? 'spec ที่ขอไว้ ' + fmt(t.spec_ram_gb) : 'รวมทุกเครื่อง',
      specKnown ? (t.spec_ram_gb >= t.alloc_ram_gb ? 'ok' : 'bad') : ''),
    tile('Disk ที่ต้องจัดสรร (GB)', fmt(t.alloc_disk_gb),
      'ณ ' + ST.horizon + ' เดือน · Scale ' + D.scale.toFixed(1) + '×',
      specKnown ? (t.spec_disk_gb >= t.alloc_disk_gb ? 'ok' : 'warn') : ''),
    tile('เครื่องที่ทรัพยากรไม่พอ', fmt(t.insufficient),
      'เสี่ยง Disk อีก ' + fmt(t.disk_risk) + ' เครื่อง',
      t.insufficient ? 'bad' : (t.disk_risk ? 'warn' : 'ok')),
    tile('คะแนน Compliance', PLAN.compliance.score + '%',
      'ผ่าน ' + PLAN.compliance.passed + '/' + PLAN.compliance.total_rules + ' มาตรการ',
      PLAN.compliance.failed_count ? 'bad' : 'ok'),
  ].join('');

  const warns = [];
  if (ST.env.ha) warns.push('เปิดโหมด HA อยู่ — บริการที่รันค้างถูกคูณ 2 ชุดในการคำนวณ');
  if (ST.env.airgap) warns.push('เครือข่ายปิด — เพิ่ม Disk OS ' + AIRGAP_MIRROR_GB +
    ' GB ในเครื่องที่มี Registry/Scanner เพื่อเก็บ mirror ของฐานข้อมูลช่องโหว่และ package');
  if (PLAN.totals.gpu_needed && ST.env.nogpu) {
    warns.push('มีเครื่องมือที่ต้องใช้ GPU แต่ระบุว่าสภาพแวดล้อมไม่รองรับ GPU');
  } else if (PLAN.totals.gpu_needed) {
    warns.push('มีเครื่องมือที่ต้องใช้ GPU — ต้องระบุผู้รับผิดชอบจัดหา GPU ให้ชัดใน TOR');
  }
  if (D.extCaps.length) warns.push('ถือว่า capability เหล่านี้มีระบบส่วนกลางรองรับแล้ว: ' +
    D.extCaps.map(c => CAT.capabilities[c]).join(', '));
  $('#fleetWarn').innerHTML = warns.length ? '<div class="note">' +
    warns.map(w => '<div>• ' + esc(w) + '</div>').join('') + '</div>' : '';

  if (!ST.vms.length) {
    $('#fleetChart').innerHTML =
      '<div class="note">ยังไม่มี VM — กด "จัดเครื่องมือลง VM อัตโนมัติ"</div>';
    return;
  }
  const leg = specKnown
    ? [['ที่ต้องจัดสรร (คำนวณ)', 'var(--series-1)'], ['spec ที่ขอไว้จริง', 'var(--series-2)']]
    : [['ที่ต้องจัดสรร (คำนวณ)', 'var(--series-1)']];
  $('#fleetChart').innerHTML = legend(leg) +
    (specKnown ? '' : '<div class="hint">ยังไม่ได้กรอก spec ที่ขอไว้จริง — ' +
      'เปิดหัวข้อ "spec ที่ขอไว้จริง และส่วนต่าง" ในการ์ดของแต่ละเครื่องเพื่อกรอก</div>') +
    groupedBars('vCPU ต่อเครื่อง', PLAN.vms.map(v => ({
      label: v.name, a: v.calc.allocated.vcpu, b: toNum(v.spec && v.spec.vcpu) })), 'vCPU', specKnown) +
    groupedBars('RAM ต่อเครื่อง (GB)', PLAN.vms.map(v => ({
      label: v.name, a: v.calc.allocated.ram_gb, b: toNum(v.spec && v.spec.ram_gb) })), 'GB', specKnown);
}

/* --------------------------------------------- archetypes ----------------- */
function renderArchetypes() {
  const host = $('#archTbl');
  if (!host) return;
  const rows = ARCH().map(a => {
    const per = a.vms.map(v => P.colocate(v.tools, optsFor()));
    const tools = [...new Set(a.vms.flatMap(v => v.tools))];
    const comp = P.complianceCheck(tools, a.profile, null, D.fws, D.licBlock, D.extCaps);
    const sum = f => per.reduce((s, c) => s + f(c), 0);
    return { a, per, tools, comp, vcpu: sum(c => c.allocated.vcpu), ram: sum(c => c.allocated.ram_gb),
             dos: sum(c => c.allocated.disk_os_gb), ddat: sum(c => c.allocated.disk_data_gb),
             gpu: per.some(c => c.gpu_required) };
  });
  const maxV = Math.max(...rows.map(r => r.vcpu), 1);
  host.innerHTML =
    '<thead><tr><th>ผังอ้างอิง</th><th>เหมาะกับ</th><th class="ctr">VM</th><th class="ctr">เครื่องมือ</th>' +
    '<th class="num">vCPU รวม</th><th class="num">RAM รวม</th><th class="num">Disk OS</th>' +
    '<th class="num">Disk Data</th><th class="ctr">Compliance<br>(มาตรฐานที่เลือก)</th>' +
    '<th class="ctr">GPU</th><th class="noprint ctr">ใช้ผังนี้</th></tr></thead><tbody>' +
    rows.map(r => '<tr><td><b>' + esc(r.a.name_th) + '</b><div class="hint">' +
      esc(r.a.network_th) + '</div><div class="hint" style="margin-top:3px">' +
      r.a.vms.map((v, i) => '<span class="chip">' + esc(v.host) + ' ' +
        r.per[i].allocated.vcpu + 'c/' + r.per[i].allocated.ram_gb + 'G</span>').join(' ') +
      '</div></td><td>' + esc(P.profileById.get(r.a.profile).name_th) + '</td>' +
      '<td class="ctr">' + r.a.vms.length + '</td><td class="ctr">' + r.tools.length + '</td>' +
      '<td class="num"><b>' + fmt(r.vcpu) + '</b><div style="height:6px;background:var(--surface-3);' +
      'border-radius:3px;margin-top:3px"><div style="height:6px;border-radius:3px;' +
      'background:var(--series-1);width:' + (r.vcpu / maxV * 100).toFixed(0) + '%"></div></div></td>' +
      '<td class="num"><b>' + fmt(r.ram) + '</b></td><td class="num">' + fmt(r.dos) + '</td>' +
      '<td class="num">' + fmt(r.ddat) + '</td><td class="ctr"><span class="badge ' +
      (r.comp.score >= 100 ? 'ok' : r.comp.score >= 80 ? 'warn' : 'bad') + '">' +
      r.comp.score + '%</span></td><td class="ctr">' +
      (r.gpu ? '<span class="badge warn">ต้องมี</span>' : '–') +
      '</td><td class="ctr noprint"><button class="btn small useArch" data-id="' + r.a.id +
      '">ใช้ผังนี้</button></td></tr>').join('') + '</tbody>';
  $$('.useArch').forEach(b => { b.onclick = () => loadArchetype(b.dataset.id); });
}

/* --------------------------------------------- VM cards ------------------- */
function renderVms() {
  $('#vmList').innerHTML = PLAN.vms.map((v, i) => vmCard(v, i)).join('');
  PLAN.vms.forEach((v, i) => {
    const card = $('#vm-' + i);
    $('.vmname', card).oninput = e => { ST.vms[i].name = e.target.value; };
    $('.vmrole', card).oninput = e => { ST.vms[i].role = e.target.value; };
    $$('.specin', card).forEach(inp => {
      inp.onchange = e => {
        ST.vms[i].spec = ST.vms[i].spec || {};
        ST.vms[i].spec[e.target.dataset.k] = e.target.value === '' ? '' : +e.target.value;
        render();
      };
    });
    $$('.execin', card).forEach(inp => {
      inp.onchange = e => {
        ST.vms[i].executors = ST.vms[i].executors || {};
        const n = Math.max(1, parseInt(e.target.value, 10) || 1);
        if (n === 1) delete ST.vms[i].executors[e.target.dataset.id];
        else ST.vms[i].executors[e.target.dataset.id] = n;
        render();
      };
    });
    $$('.movetool', card).forEach(s => {
      s.onchange = () => {
        const j = parseInt(s.value, 10);
        if (!Number.isFinite(j)) return;
        ST.vms[i].tools = ST.vms[i].tools.filter(x => x !== s.dataset.id);
        if (!ST.vms[j].tools.includes(s.dataset.id)) ST.vms[j].tools.push(s.dataset.id);
        render();
      };
    });
    const del = $('.vmdel', card);
    if (del) del.onclick = () => { ST.vms.splice(i, 1); syncToolsToVms(); render(); };
    const fx = $('.vmfix', card);
    if (fx) fx.onclick = () => {
      ST.vms[i].spec = { vcpu: v.calc.allocated.vcpu, ram_gb: v.calc.allocated.ram_gb,
        disk_os_gb: v.calc.allocated.disk_os_gb, disk_data_gb: v.calc.allocated.disk_data_gb };
      render();
    };
    card.ondragover = (e) => { e.preventDefault(); card.classList.add('drop-ready'); };
    card.ondragleave = () => card.classList.remove('drop-ready');
    card.ondrop = (e) => {
      e.preventDefault();
      card.classList.remove('drop-ready');
      const id = e.dataTransfer.getData('text/plain');
      if (id) addToolToVm(id, i, true);
    };
  });
}

function vmCard(v, i) {
  const c = v.calc, vd = VERDICT[v.verdict];
  const maxV = Math.max(c.method_a.vcpu, c.method_b.vcpu, c.method_b2.vcpu, c.method_c.vcpu, 1);
  const maxR = Math.max(c.method_a.ram_gb, c.method_b.ram_gb, c.method_b2.ram_gb, c.method_c.ram_gb, 1);
  const govV = c.governing.vcpu, govR = c.governing.ram;
  const selB = ST.mode === 'strict' ? 'B1' : 'B2';
  const mrow = (lbl, val, max, color, isGov, tip) =>
    '<div class="mbar ' + (isGov ? 'gov' : '') + '" title="' + esc(tip) + '"><div class="lbl">' +
    esc(lbl) + (isGov ? ' ◄' : '') + '</div><div class="track"><div class="fill" style="width:' +
    (val / max * 100).toFixed(1) + '%;background:' + color + '"></div></div><div class="n">' +
    fmt(val, 1) + '</div></div>';
  const spec = v.spec || {};
  const specIn = (k, lbl) => '<label class="field" style="margin:0"><span class="lbl" ' +
    'style="font-size:10.5px">' + esc(lbl) + '</span><input type="number" class="specin" data-k="' +
    k + '" value="' + (spec[k] === undefined || spec[k] === null ? '' : spec[k]) +
    '" min="0" placeholder="–"></label>';
  const gapCell = (g, unit) => g == null ? '<td class="num">–</td>' :
    '<td class="num" style="color:' + (g < 0 ? 'var(--critical)' : 'var(--good)') +
    ';font-weight:700">' + (g > 0 ? '+' : '') + fmt(g) + ' ' + esc(unit) + '</td>';

  return '<div class="vmcard ' + vd.cls + '" id="vm-' + i + '" data-vm="' + i + '"><header>' +
    '<input class="vmname" type="text" value="' + esc(v.name) + '">' +
    '<span class="badge ' + (vd.cls === 'ok' ? 'ok' : vd.cls === 'bad' ? 'bad' : 'warn') + '">' +
    vd.icon + ' ' + esc(vd.th) + '</span>' +
    '<button class="btn small ghost vmdel noprint" title="ลบเครื่องนี้">✕</button></header>' +
    '<input class="vmrole" type="text" value="' + esc(v.role || '') +
    '" placeholder="บทบาทหน้าที่ของเครื่องนี้" style="margin-bottom:8px;font-size:12px">' +
    '<div class="hint noprint" style="margin-bottom:8px">ลากเครื่องมือจากขั้นที่ 4 มาวางที่การ์ดนี้ได้</div>' +
    '<div class="grid3" style="gap:8px">' +
      '<div class="tile"><div class="k">ต้องจัดสรร vCPU</div><div class="v">' +
        fmt(c.allocated.vcpu) + '</div><div class="s">ดิบ ' + fmt(c.raw.vcpu, 2) + ' + OS ' +
        c.os_reserve.vcpu + ' · ตัวกำหนด ' + govV + '</div></div>' +
      '<div class="tile"><div class="k">ต้องจัดสรร RAM</div><div class="v">' +
        fmt(c.allocated.ram_gb) + ' <span style="font-size:.7em">GB</span></div><div class="s">ดิบ ' +
        fmt(c.raw.ram_gb, 2) + ' + OS ' + c.os_reserve.ram_gb + ' · ตัวกำหนด ' + govR + '</div></div>' +
      '<div class="tile"><div class="k">ต้องจัดสรร Disk</div><div class="v">' +
        fmt(c.allocated.disk_os_gb) + '<span style="font-size:.6em"> OS</span> + ' +
        fmt(c.allocated.disk_data_gb) + '<span style="font-size:.6em"> Data</span></div>' +
        '<div class="s">ณ ' + ST.horizon + ' เดือน' +
        (v.extraInstallGb ? ' · รวม mirror ' + v.extraInstallGb + ' GB' : '') + '</div></div>' +
    '</div>' +
    '<details class="acc" style="margin-top:10px" open><summary>เปรียบเทียบเงื่อนไขการคำนวณ (' +
      v.tools.length + ' เครื่องมือ' +
      (c.weight_model ? ' · n=' + c.weight_model.n_selfhosted +
        ' · w_max=' + Math.round(c.weight_model.w_max * 100) + '%' : '') +
      ')</summary><div style="margin-top:8px">' +
      '<div class="hint" style="margin-bottom:4px"><b>vCPU</b></div>' +
      mrow('A Peak-Max', c.method_a.vcpu, maxV, SERIES.A, govV === 'A', 'ตัวที่หนักสุด: ' + c.method_a.driver_vcpu) +
      mrow('B1 Strict', c.method_b.vcpu, maxV, SERIES.B, govV === 'B' && selB === 'B1', c.method_b.label_th) +
      mrow('B2 Realistic', c.method_b2.vcpu, maxV, SERIES.B, govV === 'B' && selB === 'B2', c.method_b2.label_th) +
      mrow('C Resident', c.method_c.vcpu, maxV, SERIES.C, govV === 'C', c.method_c.label_th) +
      '<div class="hint" style="margin:8px 0 4px"><b>RAM (GB)</b></div>' +
      mrow('A Peak-Max', c.method_a.ram_gb, maxR, SERIES.A, govR === 'A', 'ตัวที่หนักสุด: ' + c.method_a.driver_ram) +
      mrow('B1 Strict', c.method_b.ram_gb, maxR, SERIES.B, govR === 'B' && selB === 'B1', c.method_b.label_th) +
      mrow('B2 Realistic', c.method_b2.ram_gb, maxR, SERIES.B, govR === 'B' && selB === 'B2', c.method_b2.label_th) +
      mrow('C Resident', c.method_c.ram_gb, maxR, SERIES.C, govR === 'C', c.method_c.label_th) +
      '<div class="hint" style="margin-top:6px">◄ = เงื่อนไขที่กำหนดผลลัพธ์ (ใช้ค่ามากสุดเสมอ) · B2 แยกกลุ่ม: ' +
      c.method_b2.detail.map(d => esc(d.group) + ' ' + (d.rule === 'sum' ? 'Σ' : 'max') + ' ' +
        fmt(d.ram_gb, 1) + 'GB').join(' + ') + '</div></div></details>' +
    '<details class="acc"><summary>spec ที่ขอไว้จริง และส่วนต่าง</summary>' +
      '<div class="grid3" style="gap:8px;margin:8px 0">' + specIn('vcpu', 'spec vCPU') +
      specIn('ram_gb', 'spec RAM (GB)') + specIn('disk_os_gb', 'spec Disk OS (GB)') +
      specIn('disk_data_gb', 'spec Disk Data (GB)') + '</div>' +
      '<table class="tbl"><thead><tr><th></th><th class="num">vCPU</th><th class="num">RAM</th>' +
      '<th class="num">Disk OS</th><th class="num">Disk Data</th></tr></thead><tbody>' +
      '<tr><td>ต้องจัดสรร</td><td class="num">' + fmt(c.allocated.vcpu) + '</td><td class="num">' +
      fmt(c.allocated.ram_gb) + '</td><td class="num">' + fmt(c.allocated.disk_os_gb) +
      '</td><td class="num">' + fmt(c.allocated.disk_data_gb) + '</td></tr>' +
      '<tr><td>spec ที่ขอไว้</td><td class="num">' + fmt(toNum(spec.vcpu)) + '</td><td class="num">' +
      fmt(toNum(spec.ram_gb)) + '</td><td class="num">' + fmt(toNum(spec.disk_os_gb)) +
      '</td><td class="num">' + fmt(toNum(spec.disk_data_gb)) + '</td></tr>' +
      '<tr><td><b>ส่วนต่าง</b></td>' + gapCell(v.gap && v.gap.vcpu, 'c') +
      gapCell(v.gap && v.gap.ram_gb, 'GB') + gapCell(v.gap && v.gap.disk_os_gb, 'GB') +
      gapCell(v.gap && v.gap.disk_data_gb, 'GB') + '</tr></tbody></table>' +
      '<div class="btnrow noprint" style="margin-top:8px">' +
      '<button class="btn small vmfix">ตั้ง spec ให้เท่ากับค่าที่คำนวณได้</button></div></details>' +
    '<details class="acc"><summary>เครื่องมือบนเครื่องนี้ และการย้ายเครื่อง</summary>' +
      '<div class="scrollx" style="max-height:320px;margin-top:8px"><table class="tbl">' +
      '<thead><tr><th>เครื่องมือ</th><th class="ctr">กลุ่ม</th><th class="ctr">w</th>' +
      '<th class="num">min</th><th class="num">w×RAM</th><th class="num">Data GB</th>' +
      '<th class="ctr noprint">จำนวนชุด</th><th class="noprint">ย้ายไป</th></tr></thead><tbody>' +
      c.tools.map(t => '<tr><td>' + esc(t.name.split(' (')[0]) +
        (t.instances > 1 ? ' <span class="badge opt">×' + t.instances + '</span>' : '') +
        '</td><td class="ctr"><span class="chip">' + esc(t.conc_group) + '</span></td>' +
        '<td class="ctr">' + Math.round(t.weight * 100) + '%</td><td class="num">' +
        fmt(t.min_vcpu, 0) + 'c/' + fmt(t.min_ram, 0) + 'G</td><td class="num">' +
        fmt(t.w_ram, 2) + '</td><td class="num">' + fmt(t.storage.data_gb, 1) + '</td>' +
        '<td class="ctr noprint"><input type="number" class="execin" data-id="' + t.tool_id +
        '" value="' + t.instances + '" min="1" max="32" style="width:52px"></td>' +
        '<td class="noprint">' + (ST.vms.length > 1
          ? '<select class="movetool" data-id="' + t.tool_id + '" style="font-size:11px">' +
            '<option value="">–</option>' + ST.vms.map((vv, j) => j === i ? ''
              : '<option value="' + j + '">' + esc(vv.name) + '</option>').join('') + '</select>'
          : '–') + '</td></tr>').join('') +
      '</tbody></table></div></details></div>';
}

/* --------------------------------------------- compliance tab ------------- */
function renderCompliance() {
  const c = PLAN.compliance;
  const fwRows = Object.values(c.by_framework)
    .sort((a, b) => a.score - b.score || a.short_th.localeCompare(b.short_th));
  $('#compTiles').innerHTML = [
    tile('คะแนน Compliance', c.score + '%', 'ผ่าน ' + c.passed + ' จาก ' + c.total_rules + ' มาตรการ',
      c.failed_count ? (c.score >= 80 ? 'warn' : 'bad') : 'ok'),
    tile('มาตรการที่ไม่ผ่าน', fmt(c.failed_count), 'ต้องแก้ก่อนขึ้นระบบ', c.failed_count ? 'bad' : 'ok'),
    tile('มาตรการที่ควรทำเพิ่ม', fmt(c.warn_count), 'ระดับแนะนำ', c.warn_count ? 'warn' : 'ok'),
    tile('มาตรฐานที่ยังไม่ผ่านครบ', fmt(fwRows.filter(f => f.score < 100).length),
      'จาก ' + fwRows.length + ' ฉบับที่เลือก', fwRows.some(f => f.score < 100) ? 'warn' : 'ok'),
    tile('Capability ที่ยังขาด', fmt(Object.keys(c.gaps).length), 'ดูเครื่องมือที่แนะนำด้านล่าง',
      Object.keys(c.gaps).length ? 'warn' : 'ok'),
    tile('เครื่องมือที่ใช้อยู่', fmt(PLAN.all_tools.length), 'จาก ' + CAT.tools.length + ' รายการ', ''),
  ].join('');

  $('#fwScoreTbl').innerHTML =
    '<thead><tr><th>มาตรฐาน</th><th class="ctr">ขอบเขต</th><th>หน่วยงานเจ้าของ</th>' +
    '<th class="ctr">ผ่าน</th><th class="ctr">คะแนน</th><th>มาตรการที่ยังไม่ผ่าน</th></tr></thead><tbody>' +
    fwRows.map(f => '<tr><td><b>' + esc(f.short_th) + '</b>' +
      (f.verify ? ' <span class="flag">⚠</span>' : '') + '<div class="hint">' +
      esc(f.name_th) + '</div></td><td class="ctr">' + (f.region === 'th' ? 'ไทย' : 'สากล') +
      '</td><td class="hint">' + esc(f.authority) + '</td><td class="ctr">' + f.passed + '/' +
      f.total + '</td><td class="ctr"><span class="badge ' +
      (f.score >= 100 ? 'ok' : f.score >= 70 ? 'warn' : 'bad') + '">' + f.score +
      '%</span></td><td class="hint mono">' + (f.failed.map(esc).join(', ') || '–') +
      '</td></tr>').join('') + '</tbody>';

  if (!c.recommendations.length) {
    $('#recoList').innerHTML = '<div class="note">ชุดเครื่องมือปัจจุบันครอบคลุมทุก capability ' +
      'ที่มาตรฐานที่เลือกเรียกร้องแล้ว</div>';
  } else {
    const tot = c.recommendations.reduce((a, r) => ({ v: a.v + r.add_vcpu, r: a.r + r.add_ram_gb,
      d: a.d + r.add_disk_gb }), { v: 0, r: 0, d: 0 });
    $('#recoList').innerHTML = '<div class="note">เพิ่ม ' + c.recommendations.length +
      ' เครื่องมือ ปิดช่องว่างได้ ' + (Object.keys(c.gaps).length - c.uncovered_caps.length) + '/' +
      Object.keys(c.gaps).length + ' capability · ทรัพยากรเพิ่ม (ถ้าแยกเครื่อง) ' + tot.v +
      ' vCPU / ' + tot.r + ' GB RAM / ' + tot.d + ' GB Disk' +
      (c.uncovered_caps.length ? '<br><b style="color:var(--critical)">ไม่มีเครื่องมือที่ใช้ได้' +
        'ภายใต้เงื่อนไขนี้สำหรับ: ' + c.uncovered_caps.map(esc).join(', ') + '</b>' : '') +
      '</div><div class="scrollx" style="max-height:none"><table class="tbl"><thead><tr>' +
      '<th class="ctr">Stage</th><th>เครื่องมือที่แนะนำ</th><th>ปิด capability</th>' +
      '<th>มาตรการที่ปิดได้</th><th>มาตรฐานที่เกี่ยว</th><th class="num">+vCPU</th>' +
      '<th class="num">+RAM</th><th class="num">+Disk</th><th>License</th>' +
      '<th class="noprint ctr">เพิ่ม</th></tr></thead><tbody>' +
      c.recommendations.map(r => '<tr><td class="ctr"><span class="stage-pill st' + r.stage + '">' +
        r.stage + '</span></td><td><b>' + esc(r.name) + '</b><div class="hint">' +
        esc(r.note_th).slice(0, 170) + '</div></td><td>' +
        r.closes.map(x => '<span class="chip on">' + esc(x) + '</span>').join(' ') +
        '</td><td class="hint mono">' + r.controls.map(esc).join(', ') + '</td><td class="hint">' +
        r.frameworks.map(f => esc(P.frameworkById.get(f).short_th)).join('; ') +
        '</td><td class="num">' + r.add_vcpu + '</td><td class="num">' + r.add_ram_gb +
        '</td><td class="num">' + r.add_disk_gb + '</td><td class="hint">' + esc(r.license) +
        '<div class="hint">' + esc(r.license_class) + '</div></td>' +
        '<td class="ctr noprint"><button class="btn small addtool" data-t="' + r.tool_id +
        '">+</button></td></tr>').join('') + '</tbody></table></div>';
    $$('.addtool').forEach(b => {
      b.onclick = () => {
        if (!ST.tools.includes(b.dataset.t)) ST.tools.push(b.dataset.t);
        syncToolsToVms(); render();
      };
    });
  }

  const groups = {};
  c.results.forEach(r => { (groups[r.group] = groups[r.group] || []).push(r); });
  $('#ruleTbl').innerHTML =
    '<thead><tr><th>มาตรการ</th><th class="ctr">ระดับ</th><th>Capability ที่ต้องมี</th>' +
    '<th>อ้างจากมาตรฐาน</th><th class="ctr">สถานะ</th></tr></thead><tbody>' +
    Object.entries(groups).map(([g, list]) =>
      '<tr><td colspan="5" style="background:var(--surface-3);font-weight:800">' +
      esc(CAT.control_groups[g]) + '</td></tr>' + list.map(r => {
        const st = r.status === 'pass' ? '<span class="badge ok">✔ ผ่าน</span>'
          : r.status === 'warn' ? '<span class="badge warn">▲ ควรทำเพิ่ม</span>'
          : '<span class="badge bad">✖ ไม่ผ่าน</span>';
        const sb = SEV_BADGE[r.severity];
        return '<tr><td><b>' + esc(r.title_th) + '</b><div class="hint mono">' + esc(r.control_id) +
          '</div></td><td class="ctr"><span class="badge ' + sb[0] + '">' + esc(sb[1]) +
          '</span></td><td>' + r.caps.map(x => '<span class="chip ' +
            (r.missing.includes(x) ? '' : 'on') + '">' + esc(x) + '</span>').join(' ') +
          '</td><td class="hint">' + Object.entries(r.refs).map(([f, cl]) =>
            '<div>' + esc(P.frameworkById.get(f).short_th) + ' — ' + esc(cl) + '</div>').join('') +
          '</td><td class="ctr">' + st + '</td></tr>';
      }).join('')).join('') + '</tbody>';
}

function buildFrameworkTable() {
  const fams = Object.entries(CAT.framework_families).sort((a, b) => a[1].order - b[1].order);
  $('#fwTbl').innerHTML =
    '<thead><tr><th>รหัส</th><th>กฎหมาย / มาตรฐาน</th><th>หน่วยงานเจ้าของ</th>' +
    '<th>ขอบเขตที่บังคับใช้</th><th class="ctr">มาตรการ</th></tr></thead><tbody>' +
    fams.map(([fid, fam]) => {
      const list = CAT.frameworks.filter(f => f.family === fid);
      if (!list.length) return '';
      return '<tr><td colspan="5" style="background:var(--surface-3);font-weight:800">' +
        esc(fam.label_th) + ' (' + list.length + ' ฉบับ)</td></tr>' +
        list.map(f => '<tr><td class="mono">' + esc(f.id) +
          (f.verify ? ' <span class="flag">⚠</span>' : '') + '</td><td><b>' +
          esc(f.short_th) + '</b><div class="hint">' + esc(f.name_th) + '</div></td>' +
          '<td class="hint">' + esc(f.authority || '') + '</td><td class="hint">' +
          esc(f.scope_th || '') + '</td><td class="ctr">' + Object.keys(f.controls).length +
          '</td></tr>').join('');
    }).join('') + '</tbody>';
  $('#fwNote').innerHTML = '⚠ = ควรตรวจเลขที่ประกาศและปีกับราชกิจจานุเบกษาหรือเว็บไซต์ของ' +
    'หน่วยงานเจ้าของมาตรฐานก่อนนำไปอ้างอิงใน TOR เพราะชุดประกาศกลุ่มนี้มีการออกเพิ่มและปรับปรุงเป็นระยะ ' +
    '— ตัวมาตรการที่ผูกไว้เป็นสาระของข้อกำหนด ใช้ได้ตามปกติ';
}

/* --------------------------------------------- storage ------------------- */
function renderStorage() {
  const lt = PLAN.totals.long_term;
  $('#storageMeta').textContent = CAT.storage_baseline_th + ' · Scale ที่ใช้ ' +
    D.scale.toFixed(1) + '× ' + (ST.retention
      ? '· บังคับ retention ' + ST.retention + ' วันทุกเครื่องมือ'
      : '· ใช้ retention ตามค่าของแต่ละเครื่องมือ');
  if (!ST.vms.length) {
    $('#storageChart').innerHTML = '<div class="note">ยังไม่มี VM ในแผน</div>';
    $('#storageVmTbl').innerHTML = ''; $('#storageToolTbl').innerHTML = ''; return;
  }
  $('#storageChart').innerHTML =
    legend([['ข้อมูลจริง (Data)', 'var(--series-1)'],
            ['ที่ต้องจัดสรร (รวม OS + เผื่อว่าง)', 'var(--series-2)']]) +
    groupedBars('พื้นที่จัดเก็บรวมทุกเครื่อง (GB)',
      lt.map(x => ({ label: x.months + ' เดือน', a: x.gb, b: x.provisioned_gb })), 'GB', true);

  $('#storageVmTbl').innerHTML =
    '<thead><tr><th>VM</th><th class="num">Install</th>' +
    CAT.model.horizons.map(h => '<th class="num">Data @' + h + 'ด.</th>').join('') +
    CAT.model.horizons.map(h => '<th class="num">จัดสรร @' + h + 'ด.</th>').join('') +
    '<th class="num">spec Data</th><th class="ctr">พอถึงเมื่อไหร่</th></tr></thead><tbody>' +
    PLAN.vms.map(v => {
      const spec = toNum(v.spec && v.spec.disk_data_gb);
      const ok = v.calc.storage.long_term.filter(x => x.provisioned_gb <= spec).map(x => x.months);
      return '<tr><td><b>' + esc(v.name) + '</b></td><td class="num">' +
        fmt(v.calc.storage.install_gb) + '</td>' +
        v.calc.storage.long_term.map(x => '<td class="num">' + fmt(x.data_gb) + '</td>').join('') +
        v.calc.storage.long_term.map(x => '<td class="num"><b>' + fmt(x.provisioned_gb) +
          '</b></td>').join('') + '<td class="num">' + (spec ? fmt(spec) : '–') +
        '</td><td class="ctr"><span class="badge ' +
        (ok.length >= CAT.model.horizons.length ? 'ok' : ok.length ? 'warn' : 'bad') + '">' +
        (ok.length ? Math.max(...ok) + ' เดือน' : 'ยังไม่กรอก/ไม่พอ') + '</span></td></tr>';
    }).join('') + '</tbody>';

  const used = new Map();
  PLAN.vms.forEach(v => v.calc.tools.forEach(t => {
    const prev = used.get(t.tool_id);
    if (!prev) used.set(t.tool_id, Object.assign({}, t, { vms: [v.name] }));
    else {
      prev.vms.push(v.name);
      prev.storage = Object.assign({}, prev.storage,
        { data_gb: prev.storage.data_gb + t.storage.data_gb });
    }
  }));
  const rows = [...used.values()].sort((a, b) => b.storage.data_gb - a.storage.data_gb);
  const tot = rows.reduce((s, r) => s + r.storage.data_gb, 0) || 1;
  $('#storageToolTbl').innerHTML =
    '<thead><tr><th class="ctr">Stage</th><th>เครื่องมือ</th><th>อยู่บนเครื่อง</th>' +
    '<th class="num">Install</th><th class="num">GB/วัน</th><th class="num">Retention</th>' +
    '<th class="num">Index OH</th><th class="num">Growth/ปี</th><th class="num">Data @' +
    ST.horizon + 'ด.</th><th class="num">สัดส่วน</th></tr></thead><tbody>' +
    rows.map(r => {
      const t = P.toolById.get(r.tool_id), s = t.storage;
      const pc = r.storage.data_gb / tot * 100;
      return '<tr><td class="ctr"><span class="stage-pill st' + t.stage + '">' + t.stage +
        '</span></td><td><b>' + esc(t.name.split(' (')[0]) + '</b></td><td class="hint">' +
        r.vms.map(esc).join(', ') + '</td><td class="num">' + fmt(r.storage.install_gb) +
        '</td><td class="num">' + fmt(s.data_daily_gb, 2) + '</td><td class="num">' +
        fmt(ST.retention || s.retention_days) + '</td><td class="num">' +
        Math.round(s.index_overhead * 100) + '%</td><td class="num">' +
        Math.round(s.growth_yr * 100) + '%</td><td class="num"><b>' +
        fmt(r.storage.data_gb, 1) + '</b></td><td class="num">' +
        (pc >= 0.05 ? pc.toFixed(1) + '%' : '&lt;0.1%') + '</td></tr>';
    }).join('') + '</tbody>';
}

/* --------------------------------------------- catalog tab --------------- */
function buildCatalogPanel() {
  $('#catalogMeta').textContent = CAT.tools.length +
    ' เครื่องมือ ครอบคลุม 6 Stage · min = ค่าต่ำสุดที่รันได้จริง · ' +
    'rec = ค่าที่แนะนำเมื่อรับงานต่อเนื่อง · w = น้ำหนักที่ใช้ในเงื่อนไขที่ 2';
  $('#fStage').innerHTML = '<option value="">ทุก Stage</option>' +
    Object.entries(CAT.stages).map(([k, v]) =>
      '<option value="' + k + '">Stage ' + k + ' — ' + esc(v) + '</option>').join('');
  $('#fProfile').innerHTML = '<option value="">ทั้งหมด</option>' +
    CAT.profiles.map(p => '<option value="' + p.id + '">' + esc(p.name_th) + '</option>').join('');
  const fams = Object.entries(CAT.framework_families).sort((a, b) => a[1].order - b[1].order);
  $('#fFramework').innerHTML = '<option value="">ทุกมาตรฐาน</option>' +
    '<option value="__th">— ทุกมาตรฐานไทย —</option>' +
    '<option value="__intl">— ทุกมาตรฐานสากล —</option>' +
    fams.map(([fid, fam]) => {
      const list = CAT.frameworks.filter(f => f.family === fid);
      return list.length ? '<optgroup label="' + esc(fam.label_th) + '">' +
        list.map(f => '<option value="' + f.id + '">' + esc(f.short_th) + '</option>').join('') +
        '</optgroup>' : '';
    }).join('');
  $('#fCap').innerHTML = '<option value="">ทุก capability</option>' +
    Object.entries(CAT.capabilities).sort((a, b) => a[1].localeCompare(b[1]))
      .map(([k, v]) => '<option value="' + k + '">' + esc(v) + '</option>').join('');
  $('#fLic').innerHTML = '<option value="">ทุกประเภทลิขสิทธิ์</option>' +
    Object.entries(CAT.license_classes).map(([k, v]) =>
      '<option value="' + k + '">' + esc(k) + ' — ' +
      esc(v.split('—')[0].trim()) + '</option>').join('');
  ['#qTool', '#fStage', '#fCore', '#fProfile', '#fFramework', '#fCap', '#fLic'].forEach(s => {
    $(s).oninput = drawCatalog; $(s).onchange = drawCatalog;
  });
  drawCatalog();
}

function drawCatalog() {
  const q = $('#qTool').value.trim().toLowerCase();
  const st = $('#fStage').value, co = $('#fCore').value, pf = $('#fProfile').value;
  const fw = $('#fFramework').value, cap = $('#fCap').value, lic = $('#fLic').value;
  const rows = CAT.tools.filter(t => {
    if (st && String(t.stage) !== st) return false;
    if (co && t.core !== co) return false;
    if (pf && !t.profiles.includes(pf)) return false;
    if (cap && !t.capabilities.includes(cap)) return false;
    if (lic && t.license_class !== lic) return false;
    const cm = t.compliance || { frameworks_th: [], frameworks_intl: [] };
    if (fw === '__th' && !cm.frameworks_th.length) return false;
    if (fw === '__intl' && !cm.frameworks_intl.length) return false;
    if (fw && fw.indexOf('__') !== 0 &&
        !cm.frameworks_th.includes(fw) && !cm.frameworks_intl.includes(fw)) return false;
    if (q) {
      const hay = [t.name, t.category, t.id, t.license, t.capabilities.join(' '),
        t.enterprise_alt.join(' '), t.oss_alt.join(' '), t.note_th,
        cm.frameworks_th_text, cm.frameworks_intl_text,
        (cm.controls_full || []).join(' '), (cm.controls_partial || []).join(' ')]
        .join(' ').toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
  $('#catalogCount').textContent = 'แสดง ' + rows.length + ' จาก ' + CAT.tools.length + ' เครื่องมือ';
  $('#catalogTbl').innerHTML =
    '<thead><tr><th class="ctr">St</th><th>เครื่องมือ</th><th>หมวด</th><th class="ctr">Core</th>' +
    '<th class="num">min<br>vCPU</th><th class="num">min<br>RAM</th><th class="num">min<br>Disk</th>' +
    '<th class="num">rec<br>vCPU</th><th class="num">rec<br>RAM</th><th class="num">rec<br>Disk</th>' +
    '<th class="ctr">Resident</th><th class="num">Idle<br>RAM</th><th class="ctr">กลุ่ม</th>' +
    '<th class="ctr">ความถี่</th><th class="ctr">w</th><th class="num">GB/<br>วัน</th>' +
    '<th class="num">Reten<br>tion</th><th class="capcol">Capabilities</th>' +
    '<th class="fw-th">มาตรฐานไทยที่ช่วยตอบ</th><th class="fw-intl">มาตรฐานสากลที่ช่วยตอบ</th>' +
    '<th class="rulecol">ตอบครบด้วยตัวเอง</th><th class="rulecol">ช่วยตอบบางส่วน</th>' +
    '<th>License</th><th>ทางเลือก Enterprise-Grade</th><th>ทางเลือก OSS อื่น</th>' +
    '<th>ที่มาของตัวเลข</th><th>ข้อสังเกต</th></tr></thead><tbody>' +
    rows.map(t => {
      const cm = t.compliance || {};
      return '<tr><td class="ctr"><span class="stage-pill st' + t.stage + '">' + t.stage +
      '</span></td><td><b>' + esc(t.name) + '</b><div class="hint mono">' + esc(t.id) +
      '</div></td><td>' + esc(t.category) + '</td><td class="ctr"><span class="badge ' +
      (t.core === 'Core' ? 'core' : 'opt') + '">' + esc(t.core) + '</span></td>' +
      '<td class="num">' + t.min.vcpu + '</td><td class="num">' + t.min.ram_gb +
      '</td><td class="num">' + t.min.disk_os_gb + '</td><td class="num">' + t.rec.vcpu +
      '</td><td class="num">' + t.rec.ram_gb + '</td><td class="num">' + t.rec.disk_os_gb +
      '</td><td class="ctr">' + (t.resident ? '✔' : '–') + '</td><td class="num">' +
      t.idle_ram_gb + '</td><td class="ctr"><span class="chip">' + esc(t.conc_group) +
      '</span></td><td class="ctr hint">' + esc(P.freqById.get(t.freq).label_th) +
      '</td><td class="ctr"><b>' + Math.round(P.dutyWeight(t.freq) * 100) + '%</b></td>' +
      '<td class="num">' + fmt(t.storage.data_daily_gb, 2) + '</td><td class="num">' +
      fmt(t.storage.retention_days) + '</td><td class="capcol">' +
      t.capabilities.map(x => '<span class="chip">' + esc(x) + '</span>').join(' ') +
      '</td><td class="hint fw-th">' + ((cm.frameworks_th || []).length
        ? cm.frameworks_th.map(f => '<span class="chip on">' + esc(fwShort(f)) + '</span>').join(' ')
        : '–') + '</td><td class="hint fw-intl">' + ((cm.frameworks_intl || []).length
        ? cm.frameworks_intl.map(f => '<span class="chip">' + esc(fwShort(f)) + '</span>').join(' ')
        : '–') + '</td><td class="hint mono rulecol">' +
      ((cm.controls_full || []).join(', ') || '–') + '</td><td class="hint mono rulecol">' +
      ((cm.controls_partial || []).join(', ') || '–') + '</td><td class="hint">' +
      esc(t.license) + '<div class="hint">' + esc(t.license_class) + '</div></td>' +
      '<td class="hint">' + esc(t.enterprise_alt.join('; ')) + '</td><td class="hint">' +
      esc(t.oss_alt.join('; ')) + '</td><td class="hint">' + esc(t.sizing_ref) +
      '</td><td class="hint">' + esc(t.note_th) + '</td></tr>';
    }).join('') + '</tbody>';
}

function fwShort(id) {
  const f = CAT.frameworks.find(x => x.id === id);
  return f ? f.short_th : id;
}

/* --------------------------------------------- method tab --------------- */
function buildMethodPanel() {
  $('#freqTbl').innerHTML =
    '<thead><tr><th>freq_id</th><th>ความถี่การรัน</th><th class="ctr">ครั้ง/วัน</th>' +
    '<th class="num">activity_index</th><th class="num">น้ำหนัก w</th>' +
    '<th>เหตุผล / ข้อควรระวัง</th></tr></thead><tbody>' +
    CAT.freq_classes.map(f => '<tr><td class="mono">' + esc(f.id) + '</td><td>' +
      esc(f.label_th) + '</td><td class="ctr">' + esc(f.runs_per_day) + '</td><td class="num">' +
      f.activity_index.toFixed(2) + '</td><td class="num"><b>' +
      Math.round(f.weight * 100) + '%</b></td><td class="hint">' + esc(f.note_th) +
      '</td></tr>').join('') + '</tbody>';

  const ladder = CAT.model.w_cross_ladder || [];
  const xt = $('#crossTbl');
  if (xt) {
    xt.innerHTML = '<thead><tr><th class="ctr">n เครื่องมือบน VM</th>' +
      ladder.map((_, i) => '<th class="ctr">' + (i + 1) + (i === ladder.length - 1 ? '+' : '') +
        '</th>').join('') + '</tr></thead><tbody><tr><td>w_max (เพดาน)</td>' +
      ladder.map(x => '<td class="ctr"><b>' + Math.round(x * 100) + '%</b></td>').join('') +
      '</tr><tr><td>resident ที่ n นั้น</td>' +
      ladder.map(x => '<td class="ctr">' + Math.round(x * 100) + '%</td>').join('') +
      '</tr></tbody>';
  }

  const m = CAT.model;
  const rowsM = [
    ['w_base', m.w_base, 'น้ำหนักต่ำสุด = 20%'],
    ['w_span', m.w_span, 'ช่วงเดี่ยว ทำให้สูงสุด = 0.20 + 0.40 = 0.60 (60%) เมื่ออยู่เครื่องเดียว'],
    ['w_cross_ladder', (m.w_cross_ladder || []).map(x => Math.round(x * 100) + '%').join(', '),
      'เพดานน้ำหนักตามจำนวนเครื่องมือ self-hosted บน VM (n=1…8+)'],
    ['w_cross_cap', m.w_cross_cap || 8, 'เมื่อถึงจำนวนนี้แล้ว w_max หยุดที่ 20%'],
    ['os_reserve_vcpu', m.os_reserve_vcpu, 'vCPU ที่กันให้ OS + Container Runtime'],
    ['os_reserve_ram_gb', m.os_reserve_ram_gb, 'RAM ที่กันให้ OS + Docker/containerd'],
    ['os_reserve_disk_gb', m.os_reserve_disk_gb, 'Disk ที่กันให้ระบบปฏิบัติการ + swap + log ระบบ'],
    ['disk_free_ratio', m.disk_free_ratio, 'ต้องเหลือว่าง 25% — Docker/Elasticsearch หยุดทำงานเมื่อ disk ใกล้เต็ม'],
    ['scale (คิดจากปริมาณงาน)', '0.55×(build/10) + 0.30×(แอป/2) + 0.15×(ทีม/10)',
      'ค่าฐาน 1.0 = 10 builds/วัน, 2 แอป, ทีม 10 คน'],
    ['airgap mirror', AIRGAP_MIRROR_GB + ' GB',
      'เพิ่มใน Disk OS ของเครื่องที่มี Registry/Scanner เมื่อเป็นเครือข่ายปิด'],
    ['HA', '×2', 'บริการที่รันค้างถูกคูณ 2 ชุดเมื่อเปิดโหมด High Availability'],
    ['vcpu_ladder', m.vcpu_ladder.join(', '), 'ขั้นการจัดสรร vCPU (ปัดขึ้นเสมอ)'],
    ['ram_ladder', m.ram_ladder.join(', '), 'ขั้นการจัดสรร RAM (GB)'],
    ['disk_ladder', m.disk_ladder.join(', '), 'ขั้นการจัดสรร Disk (GB)'],
    ['horizons', m.horizons.join(', '), 'ช่วงเวลาประเมินผลลัพธ์ระยะยาว (เดือน)'],
  ];
  $('#modelTbl').innerHTML =
    '<thead><tr><th>พารามิเตอร์</th><th>ค่า</th><th>ความหมาย</th></tr></thead><tbody>' +
    rowsM.map(r => '<tr><td class="mono">' + esc(r[0]) + '</td><td><b>' + esc(r[1]) +
      '</b></td><td class="hint">' + esc(r[2]) + '</td></tr>').join('') +
    '<tr><td class="mono">conc_groups</td><td colspan="2">' +
    Object.entries(CAT.conc_groups).map(([k, v]) => '<div><span class="chip on">' + esc(k) +
      '</span> ' + esc(v) + '</div>').join('') + '</td></tr>' +
    '<tr><td class="mono">license_classes</td><td colspan="2">' +
    Object.entries(CAT.license_classes).map(([k, v]) => '<div><span class="chip">' + esc(k) +
      '</span> ' + esc(v) + '</div>').join('') + '</td></tr></tbody>';

  $('#srcList').innerHTML = [
    'CI/CD Service Blueprint V0.2 — โครงสร้าง 6 Stage, รายชื่อเครื่องมือ Enterprise/OSS, ' +
      'ตารางบทบาทบุคลากร และช่วงต้นทุนต่อปีตามประเภทโครงการ',
    'แนวปฏิบัติการพัฒนาซอฟต์แวร์ กฎระเบียบเกี่ยวข้องทางไซเบอร์และสถาปัตยกรรมระบบที่มั่นคงปลอดภัย V0.2 — ' +
      'กฎหมายและมาตรฐานไทย, OWASP Top 10:2025, DevSecOps, Defense in Depth, Zero Trust',
    'เอกสารติดตั้ง (sizing guide) ของผู้พัฒนาแต่ละเครื่องมือ — ดูคอลัมน์ "ที่มาของตัวเลข" ในแท็บ 2',
    'ค่าที่พบจากการใช้งานจริงระดับ UAT/Production ขนาดเล็ก ใช้เป็นค่าฐานของปริมาณข้อมูลต่อวัน',
    'แบบฟอร์มนี้เป็นแบบกลาง ไม่มีข้อมูลเฉพาะโครงการใดฝังอยู่',
  ].map(x => '<li>' + esc(x) + '</li>').join('');
}

/* --------------------------------------------- meta / charts ------------ */
function refreshMeta() {
  const pj = ST.project || {};
  const label = [pj.name, pj.org, pj.env].filter(Boolean).join(' · ');
  const ph = $('#printHead');
  if (ph) {
    ph.innerHTML = '<h2 style="margin:0 0 4px">' + esc(pj.name || '(ยังไม่ระบุชื่อโครงการ)') +
      '</h2><div class="hint">' +
      esc([pj.org, 'สภาพแวดล้อม ' + (pj.env || '-')].filter(Boolean).join(' · ')) + '</div>' +
      (pj.note ? '<div class="hint">ข้อจำกัด: ' + esc(pj.note) + '</div>' : '') +
      '<div class="hint" style="margin-top:6px">ประเภทโครงการ ' +
      esc(P.profileById.get(ST.profile).name_th) + ' · ระดับผลกระทบ ' + esc(ST.impact) +
      ' · โหมด ' + esc(ST.mode) + ' · มาตรฐานที่เลือก ' + ST.frameworks.length +
      ' ฉบับ · มาตรการ ' + (D ? D.ctrls.length : 0) + ' รายการ · Storage ที่ ' +
      ST.horizon + ' เดือน · Scale ' + (D ? D.scale.toFixed(1) : '1.0') + '×' +
      (ST.retention ? ' · retention ' + ST.retention + ' วัน' : '') + '</div>';
  }
  $('#footMeta').textContent = (label ? 'โครงการ: ' + label + ' — ' : '') +
    'Catalog schema ' + CAT.schema_version + ' · ' + CAT.tools.length + ' เครื่องมือ · ' +
    CAT.frameworks.length + ' มาตรฐาน · ' + CAT.controls.length + ' มาตรการ · ' +
    Object.keys(CAT.capabilities).length + ' capability';
  document.title = (pj.name ? pj.name + ' — ' : '') + 'CI/CD Resource & Compliance Planner';
}

function legend(items) {
  return '<div class="legend">' + items.map(it => '<span><i style="background:' + it[1] +
    '"></i>' + esc(it[0]) + '</span>').join('') + '</div>';
}

function groupedBars(caption, data, unit, showB) {
  if (!data.length) return '';
  if (showB === undefined) showB = true;
  const W = 780, labelW = 168, valW = 62, padTop = 26, barH = 10, gap = 2;
  const rowH = showB ? 30 : 20;
  const barArea = W - labelW - valW;
  const H = padTop + data.length * rowH + 10;
  const maxVal = Math.max(...data.flatMap(d => (showB ? [d.a, d.b] : [d.a])), 1);
  const t = v => (v > 0 ? fmt(v) : '0');
  const bars = data.map((d, i) => {
    const y = padTop + i * rowH;
    const wa = Math.max((d.a / maxVal) * barArea, 2);
    const wb = Math.max((d.b / maxVal) * barArea, 2);
    const rowB = showB ? '<rect class="bar" x="' + labelW + '" y="' + (y + 1 + barH + gap) +
      '" width="' + wb.toFixed(1) + '" height="' + barH + '" fill="var(--series-2)"><title>' +
      esc(d.label) + ' — spec ' + t(d.b) + ' ' + esc(unit) + '</title></rect>' +
      '<text class="val-text" x="' + (labelW + wb + 5).toFixed(1) + '" y="' +
      (y + 2 * barH + gap) + '">' + t(d.b) + '</text>' : '';
    return '<text class="axis-text" x="0" y="' + (y + (showB ? rowH / 2 + 3 : barH)) + '">' +
      esc(String(d.label).slice(0, 26)) + '</text><rect class="bar" x="' + labelW + '" y="' +
      (y + 1) + '" width="' + wa.toFixed(1) + '" height="' + barH +
      '" fill="var(--series-1)"><title>' + esc(d.label) + ' — ต้องจัดสรร ' + t(d.a) + ' ' +
      esc(unit) + '</title></rect><text class="val-text" x="' + (labelW + wa + 5).toFixed(1) +
      '" y="' + (y + barH - 1) + '">' + t(d.a) + '</text>' + rowB;
  }).join('');
  const ticks = [0, .25, .5, .75, 1].map(f => {
    const x = (labelW + f * barArea).toFixed(1);
    return '<line class="grid-line" x1="' + x + '" y1="' + (padTop - 6) + '" x2="' + x +
      '" y2="' + (H - 6) + '"/><text class="axis-text" x="' + x + '" y="' + (padTop - 10) +
      '" text-anchor="middle">' + fmt(maxVal * f) + '</text>';
  }).join('');
  return '<figure style="margin:6px 0 14px"><figcaption class="hint" ' +
    'style="font-weight:700;color:var(--text-primary);margin-bottom:2px">' + esc(caption) +
    ' <span style="font-weight:400;color:var(--text-muted)">(หน่วย: ' + esc(unit) +
    ')</span></figcaption><svg class="chart" viewBox="0 0 ' + W + ' ' + H +
    '" role="img" aria-label="' + esc(caption) + '" style="width:100%;max-width:' + W +
    'px;height:auto" preserveAspectRatio="xMinYMin meet">' + ticks + bars + '</svg></figure>';
}

/* --------------------------------------------- export ------------------- */
function exportPlan() {
  return {
    project: ST.project,
    settings: {
      profile: ST.profile, impact: ST.impact, mode: ST.mode,
      horizon_months: ST.horizon, scale_factor: D.scale, scale_auto: ST.scaleAuto,
      workload: ST.workload, retention_days: ST.retention,
      frameworks: D.fws, license_blocklist: D.licBlock,
      environment: ST.env, external_caps: D.extCaps,
    },
    controls_required: D.ctrls.map(c => ({ control_id: c.control_id, severity: c.severity,
      title_th: c.title_th, caps: c.caps, refs: c.refs })),
    tools: ST.tools,
    pipeline: {
      flavor: ST.pipelineFlavor || currentIR().flavors[0],
      ir: currentIR(),
      files: {
        gitlab: emitGitlab(currentIR()),
        github: emitGithub(currentIR()),
      },
    },
    plan: {
      totals: PLAN.totals,
      compliance: {
        score: PLAN.compliance.score, passed: PLAN.compliance.passed,
        total: PLAN.compliance.total_rules, failed_count: PLAN.compliance.failed_count,
        by_framework: PLAN.compliance.by_framework,
        failed: PLAN.compliance.results.filter(r => r.status !== 'pass')
          .map(r => ({ control_id: r.control_id, status: r.status, missing: r.missing })),
        gaps: PLAN.compliance.gaps, uncovered_caps: PLAN.compliance.uncovered_caps,
        recommendations: PLAN.compliance.recommendations.map(r => r.tool_id),
        verify_needed: PLAN.compliance.verify_needed,
      },
      vms: PLAN.vms.map(v => ({
        name: v.name, role: v.role, tools: v.tools, executors: v.executors,
        extra_install_gb: v.extraInstallGb || 0, spec: v.spec, verdict: v.verdict, gap: v.gap,
        method_a: v.calc.method_a, method_b1: v.calc.method_b, method_b2: v.calc.method_b2,
        method_c: v.calc.method_c, governing: v.calc.governing,
        required: v.calc.required, allocated: v.calc.allocated, storage: v.calc.storage,
      })),
    },
  };
}

function buildCsv() {
  const q = s => '"' + String(s === undefined || s === null ? '' : s).replace(/"/g, '""') + '"';
  const L = [];
  const pj = ST.project || {};
  L.push(['# CI/CD Resource Plan'].map(q).join(','));
  L.push(['# โครงการ', pj.name || '-', 'หน่วยงาน', pj.org || '-',
          'สภาพแวดล้อม', pj.env || '-'].map(q).join(','));
  if (pj.note) L.push(['# ข้อจำกัด', pj.note].map(q).join(','));
  L.push(['# profile=' + ST.profile, 'impact=' + ST.impact, 'mode=' + ST.mode,
          'horizon=' + ST.horizon + 'm', 'scale=' + D.scale + 'x',
          'retention=' + (ST.retention || 'per-tool'),
          'license_block=' + (D.licBlock.join('|') || 'none'),
          'external_caps=' + (D.extCaps.join('|') || 'none')].map(q).join(','));
  L.push(['# มาตรฐานที่เลือก'].concat(D.fws).map(q).join(','));
  L.push('');
  L.push(['VM', 'บทบาท', 'จำนวนเครื่องมือ', 'A vCPU', 'A RAM', 'B1 vCPU', 'B1 RAM',
          'B2 vCPU', 'B2 RAM', 'C vCPU', 'C RAM', 'ตัวกำหนด vCPU', 'ตัวกำหนด RAM',
          'จัดสรร vCPU', 'จัดสรร RAM', 'จัดสรร Disk OS', 'จัดสรร Disk Data',
          'spec vCPU', 'spec RAM', 'spec Disk OS', 'spec Disk Data',
          'ส่วนต่าง vCPU', 'ส่วนต่าง RAM', 'ผลประเมิน', 'เครื่องมือ'].map(q).join(','));
  PLAN.vms.forEach(v => {
    const c = v.calc, s = v.spec || {};
    L.push([v.name, v.role, v.tools.length,
      c.method_a.vcpu, c.method_a.ram_gb, c.method_b.vcpu, c.method_b.ram_gb,
      c.method_b2.vcpu, c.method_b2.ram_gb, c.method_c.vcpu, c.method_c.ram_gb,
      c.governing.vcpu, c.governing.ram,
      c.allocated.vcpu, c.allocated.ram_gb, c.allocated.disk_os_gb, c.allocated.disk_data_gb,
      s.vcpu, s.ram_gb, s.disk_os_gb, s.disk_data_gb,
      v.gap && v.gap.vcpu, v.gap && v.gap.ram_gb, VERDICT[v.verdict].th,
      v.tools.join(' | ')].map(q).join(','));
  });
  L.push('');
  L.push(['# คะแนนแยกตามมาตรฐาน'].map(q).join(','));
  L.push(['framework', 'ชื่อย่อ', 'ขอบเขต', 'ผ่าน', 'ทั้งหมด', 'คะแนน %',
          'มาตรการที่ไม่ผ่าน', 'ต้องตรวจเลขที่ประกาศ'].map(q).join(','));
  Object.values(PLAN.compliance.by_framework).forEach(f => L.push(
    [f.framework, f.short_th, f.region === 'th' ? 'ไทย' : 'สากล', f.passed, f.total, f.score,
     f.failed.join(' | '), f.verify ? 'ใช่' : ''].map(q).join(',')));
  L.push('');
  L.push(['# มาตรการที่ต้องทำ'].map(q).join(','));
  L.push(['control', 'กลุ่ม', 'ระดับ', 'สถานะ', 'capability ที่ขาด', 'มาตรการ',
          'อ้างจากมาตรฐาน'].map(q).join(','));
  PLAN.compliance.results.forEach(r => L.push(
    [r.control_id, CAT.control_groups[r.group], r.severity, r.status, r.missing.join(' | '),
     r.title_th, Object.entries(r.refs).map(kv => kv[0] + ':' + kv[1]).join(' | ')].map(q).join(',')));
  L.push('');
  L.push(['# Storage long-term (GB)'].map(q).join(','));
  L.push(['VM'].concat(CAT.model.horizons.map(h => 'Data @' + h + 'm'))
    .concat(CAT.model.horizons.map(h => 'Provision @' + h + 'm')).map(q).join(','));
  PLAN.vms.forEach(v => L.push([v.name]
    .concat(v.calc.storage.long_term.map(x => x.data_gb))
    .concat(v.calc.storage.long_term.map(x => x.provisioned_gb)).map(q).join(',')));
  L.push('');
  L.push(['# เครื่องมือที่แนะนำให้เพิ่ม'].map(q).join(','));
  L.push(['tool', 'stage', 'ปิด capability', 'มาตรการ', '+vCPU', '+RAM', '+Disk',
          'license', 'license class'].map(q).join(','));
  PLAN.compliance.recommendations.forEach(r => L.push(
    [r.name, r.stage, r.closes.join(' | '), r.controls.join(' | '),
     r.add_vcpu, r.add_ram_gb, r.add_disk_gb, r.license, r.license_class].map(q).join(',')));
  return '﻿' + L.join('\n');
}

function fileStem() {
  const raw = (ST.project && ST.project.name) || 'cicd-plan';
  const n = raw.replace(/[^฀-๿a-zA-Z0-9_-]+/g, '-')
    .replace(/^-+|-+$/g, '').slice(0, 60) || 'cicd-plan';
  const env = (ST.project && ST.project.env) ? '-' + ST.project.env.replace(/[^\w]/g, '') : '';
  return n + env;
}

function download(name, text, mime) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: mime }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}

boot().catch(e => {
  document.body.insertAdjacentHTML('afterbegin',
    '<div style="padding:20px;color:#b00">โหลดข้อมูลไม่สำเร็จ: ' + esc(e.message) + '<br>' +
    '<span style="font-size:12px">รีเฟรชแบบข้ามแคช (Ctrl+F5) หรือเปิดไฟล์ <code>index.html</code> ' +
    'ที่รากโปรเจกต์หลังรัน <code>python scripts/build_standalone.py</code></span></div>');
  console.error(e);
});
