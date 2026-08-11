/* =============================================================================
 * engine.js — เครื่องคำนวณทรัพยากร CI/CD
 * ต้องให้ผลลัพธ์ตรงกับ scripts/engine.py ทุกกรณี (มีเทสต์เทียบใน scripts/verify.py)
 *
 * โมเดล
 *   A  Peak-Max          = MAX( minimum ของแต่ละเครื่องมือ )
 *   B1 Weighted-Sum      = Σ ( minimum_i × w_i )              , w = 0.50 + 0.45 × activity
 *   B2 Weighted-Serialized = Σ resident(w×min) + MAX ต่อกลุ่ม ci_seq / async / load
 *   C  Resident Floor    = Σ idle_ram ของเครื่องมือที่รันค้าง 24/7
 *   REQUIRED = MAX(A, B, C) + OS Reserve  ->  ปัดขึ้นตาม Allocation Ladder
 * ========================================================================== */
'use strict';

const DAYS_PER_MONTH = 30.44;

export class Planner {
  constructor(catalog) {
    this.c = catalog;
    this.model = catalog.model;
    this.toolById = new Map(catalog.tools.map(t => [t.id, t]));
    this.freqById = new Map(catalog.freq_classes.map(f => [f.id, f]));
    this.profileById = new Map(catalog.profiles.map(p => [p.id, p]));
    this.controlById = new Map(catalog.controls.map(c => [c.id, c]));
    this.frameworkById = new Map(catalog.frameworks.map(f => [f.id, f]));
  }

  /* ---------------------------------------------------- standards helpers */
  /** เลขข้ออ้างอิงของมาตรฐานที่อ้าง control นี้ (กรองเฉพาะชุดที่เลือกได้) */
  frameworkRefs(controlId, frameworkIds = null) {
    const out = {};
    for (const f of this.c.frameworks) {
      if (frameworkIds && !frameworkIds.has(f.id)) continue;
      const ref = f.controls[controlId];
      if (ref == null) continue;
      out[f.id] = typeof ref === 'object' ? ref.clause : ref;
    }
    return out;
  }

  /** ระดับบังคับที่เข้มที่สุดในบรรดามาตรฐานที่เลือกซึ่งอ้าง control นี้ */
  controlSeverity(controlId, frameworkIds = null) {
    const RANK = { recommended: 0, conditional: 1, mandatory: 2 };
    const base = this.controlById.get(controlId).severity;
    const sevs = [];
    for (const f of this.c.frameworks) {
      if (frameworkIds && !frameworkIds.has(f.id)) continue;
      const ref = f.controls[controlId];
      if (ref == null) continue;
      sevs.push(typeof ref === 'object' ? (ref.severity || base) : base);
    }
    if (!sevs.length) return base;
    return sevs.reduce((a, b) => (RANK[b] > RANK[a] ? b : a));
  }

  /** ถ้าไม่ระบุมาตรฐาน ให้ใช้ชุดสำเร็จของประเภทโครงการนั้น */
  resolveFrameworks(profileId = 'gov', frameworks = null) {
    if (frameworks && frameworks.length) return frameworks.filter(f => this.frameworkById.has(f));
    const prof = this.profileById.get(profileId) || this.profileById.get('gov');
    return [...(this.c.framework_presets[prof.framework_preset || 'gov'] || [])];
  }

  /** รวม control ที่ต้องทำจากมาตรฐานที่เลือก แล้วกรองตามระดับผลกระทบ */
  requiredControls(frameworks, impact = 'high') {
    const RANK = { recommended: 0, conditional: 1, mandatory: 2 };
    const fset = new Set(frameworks);
    const out = [];
    for (const c of this.c.controls) {
      const refs = this.frameworkRefs(c.id, fset);
      if (!Object.keys(refs).length) continue;
      if (!c.impact.includes(impact)) continue;
      out.push({
        control_id: c.id, group: c.group, group_th: this.c.control_groups[c.group],
        title_th: c.title_th, detail_th: c.detail_th || '',
        caps: c.caps, param: c.param || {},
        severity: this.controlSeverity(c.id, fset), refs,
      });
    }
    out.sort((a, b) => (RANK[b.severity] - RANK[a.severity]) ||
      a.group.localeCompare(b.group) || a.control_id.localeCompare(b.control_id));
    return out;
  }

  /** {capability: [control_id, ...]} ที่มาตรฐานที่เลือกเรียกร้อง */
  requiredCapabilities(frameworks, impact = 'high') {
    const need = {};
    for (const c of this.requiredControls(frameworks, impact)) {
      for (const cap of c.caps) (need[cap] ||= []).push(c.control_id);
    }
    return Object.fromEntries(Object.keys(need).sort()
      .map(k => [k, [...new Set(need[k])].sort()]));
  }

  /* ---------------------------------------------------------------- helpers */
  dutyWeight(freqId) {
    const f = this.freqById.get(freqId);
    if (!f) throw new Error('ไม่รู้จัก freq: ' + freqId);
    return round(this.model.w_base + this.model.w_span * f.activity_index, 4);
  }

  ladderUp(value, ladder) {
    for (const step of ladder) if (value <= step + 1e-9) return step;
    const top = ladder[ladder.length - 1];
    return Math.ceil(value / top) * top;
  }

  /* -------------------------------------------------------------- storage */
  projectToolStorage(tool, horizonMonths, retentionOverride, scaleFactor = 1) {
    const s = tool.storage;
    const retention = retentionOverride || s.retention_days;
    const windowDays = Math.min(retention, horizonMonths * DAYS_PER_MONTH);
    const growthMult = Math.pow(1 + s.growth_yr, horizonMonths / 12);
    const daily = s.data_daily_gb * scaleFactor;
    return {
      tool_id: tool.id,
      install_gb: round(s.install_gb, 2),
      data_gb: round(daily * growthMult * windowDays * (1 + s.index_overhead), 2),
      window_days: round(windowDays, 1),
      growth_mult: round(growthMult, 3),
      effective_daily_gb: round(daily * growthMult, 3),
    };
  }

  /* ----------------------------------------------------------- co-location */
  colocate(toolIds, opts = {}) {
    const {
      horizonMonths = 36, retentionOverride = null, executors = {},
      useRec = false, mode = 'strict', scaleFactor = 1, extraInstallGb = 0,
    } = opts;
    const key = useRec ? 'rec' : 'min';
    const rows = toolIds.map(tid => {
      const t = this.toolById.get(tid);
      if (!t) throw new Error('ไม่รู้จักเครื่องมือ: ' + tid);
      const n = Math.max(1, parseInt(executors[tid] || 1, 10));
      const w = this.dutyWeight(t.freq);
      const st = this.projectToolStorage(t, horizonMonths, retentionOverride, scaleFactor);
      st.data_gb = round(st.data_gb * n, 2);
      st.install_gb = round(st.install_gb * n, 2);
      return {
        tool_id: tid, name: t.name, stage: t.stage, category: t.category,
        instances: n, freq: t.freq, freq_label: this.freqById.get(t.freq).label_th,
        weight: w, resident: t.resident, conc_group: t.conc_group,
        min_vcpu: t[key].vcpu * n,
        min_ram: t[key].ram_gb * n,
        idle_ram: t.idle_ram_gb * n,
        w_vcpu: round(t[key].vcpu * n * w, 3),
        w_ram: round(t[key].ram_gb * n * w, 3),
        storage: st, gpu: t.gpu, license: t.license, core: t.core,
      };
    });

    /* A : Peak-Max */
    const aVcpu = rows.length ? Math.max(...rows.map(r => r.min_vcpu)) : 0;
    const aRam = rows.length ? Math.max(...rows.map(r => r.min_ram)) : 0;
    const driverV = rows.length ? rows.reduce((a, b) => (b.min_vcpu > a.min_vcpu ? b : a)).name : '-';
    const driverR = rows.length ? rows.reduce((a, b) => (b.min_ram > a.min_ram ? b : a)).name : '-';

    /* B1 : Weighted-Sum ทุกตัว */
    const bVcpu = round(rows.reduce((s, r) => s + r.w_vcpu, 0), 3);
    const bRam = round(rows.reduce((s, r) => s + r.w_ram, 0), 3);

    /* B2 : resident บวก + กลุ่มอื่นใช้ค่าสูงสุด */
    const groups = {};
    rows.forEach(r => { (groups[r.conc_group] ||= []).push(r); });
    let b2Vcpu = 0, b2Ram = 0;
    const b2Detail = [];
    for (const [g, grows] of Object.entries(groups)) {
      let gv, gr, rule;
      if (g === 'resident') {
        gv = grows.reduce((s, r) => s + r.w_vcpu, 0);
        gr = grows.reduce((s, r) => s + r.w_ram, 0);
        rule = 'sum';
      } else {
        gv = Math.max(...grows.map(r => r.w_vcpu));
        gr = Math.max(...grows.map(r => r.w_ram));
        rule = 'max';
      }
      b2Vcpu += gv; b2Ram += gr;
      b2Detail.push({ group: g, rule, count: grows.length, vcpu: round(gv, 3), ram_gb: round(gr, 3) });
    }
    b2Vcpu = round(b2Vcpu, 3); b2Ram = round(b2Ram, 3);

    /* C : Resident Floor */
    const cRam = round(rows.filter(r => r.resident).reduce((s, r) => s + r.idle_ram, 0), 3);
    const cVcpu = round(rows.filter(r => r.resident).reduce((s, r) => s + 0.25 * r.instances, 0), 3);

    /* ผลลัพธ์ */
    const selVcpu = mode === 'strict' ? bVcpu : b2Vcpu;
    const selRam = mode === 'strict' ? bRam : b2Ram;
    const rawVcpu = Math.max(aVcpu, selVcpu, cVcpu);
    const rawRam = Math.max(aRam, selRam, cRam);
    const needVcpu = rawVcpu + this.model.os_reserve_vcpu;
    const needRam = rawRam + this.model.os_reserve_ram_gb;

    /* Storage */
    const installSum = round(rows.reduce((s, r) => s + r.storage.install_gb, 0) +
                             (rows.length ? extraInstallGb : 0), 2);
    const dataSum = round(rows.reduce((s, r) => s + r.storage.data_gb, 0), 2);
    const free = this.model.disk_free_ratio;
    const needOsDisk = (this.model.os_reserve_disk_gb + installSum) / (1 - free);
    const needDataDisk = dataSum > 0 ? dataSum / (1 - free) : 0;

    const longTerm = this.model.horizons.map(h => {
      const d = round(rows.reduce((s, r) => s +
        this.projectToolStorage(this.toolById.get(r.tool_id), h, retentionOverride, scaleFactor)
          .data_gb * r.instances, 0), 2);
      return {
        months: h, data_gb: d, total_gb: round(installSum + d, 2),
        provisioned_gb: this.ladderUp((this.model.os_reserve_disk_gb + installSum + d) / (1 - free),
                                      this.model.disk_ladder),
      };
    });

    return {
      tools: rows, horizon_months: horizonMonths, mode, scale_factor: scaleFactor,
      method_a: { vcpu: aVcpu, ram_gb: aRam, driver_vcpu: driverV, driver_ram: driverR,
                  label_th: 'เงื่อนไข 1: Peak-Max (ค่า minimum ที่สูงสุด)' },
      method_b: { vcpu: bVcpu, ram_gb: bRam,
                  label_th: 'เงื่อนไข 2 (B1 Strict): Weighted-Sum 50-95% บวกทุกเครื่องมือ' },
      method_b2: { vcpu: b2Vcpu, ram_gb: b2Ram, detail: b2Detail,
                   label_th: 'เงื่อนไข 2 (B2 Realistic): บวกข้ามกลุ่ม / ใช้ค่าสูงสุดในกลุ่มที่รันเรียงกัน' },
      method_c: { vcpu: cVcpu, ram_gb: cRam,
                  label_th: 'ตัวตรวจ: Resident Floor (RAM ที่ถูกจองค้างตลอด 24/7)' },
      governing: {
        vcpu: rawVcpu === aVcpu ? 'A' : (rawVcpu === selVcpu ? 'B' : 'C'),
        ram: rawRam === aRam ? 'A' : (rawRam === selRam ? 'B' : 'C'),
      },
      raw: { vcpu: round(rawVcpu, 3), ram_gb: round(rawRam, 3) },
      os_reserve: { vcpu: this.model.os_reserve_vcpu, ram_gb: this.model.os_reserve_ram_gb,
                    disk_gb: this.model.os_reserve_disk_gb },
      required: { vcpu: round(needVcpu, 3), ram_gb: round(needRam, 3),
                  disk_os_gb: round(needOsDisk, 2), disk_data_gb: round(needDataDisk, 2) },
      allocated: {
        vcpu: this.ladderUp(needVcpu, this.model.vcpu_ladder),
        ram_gb: this.ladderUp(needRam, this.model.ram_ladder),
        disk_os_gb: this.ladderUp(needOsDisk, this.model.disk_ladder),
        disk_data_gb: needDataDisk > 0 ? this.ladderUp(needDataDisk, this.model.disk_ladder) : 0,
      },
      storage: { install_gb: installSum, data_gb: dataSum, free_ratio: free, long_term: longTerm },
      gpu_required: rows.some(r => r.gpu),
    };
  }

  /* ------------------------------------------------------- compliance ---- */
  coveredCapabilities(toolIds) {
    const s = new Set();
    toolIds.forEach(id => (this.toolById.get(id)?.capabilities || []).forEach(c => s.add(c)));
    return s;
  }

  complianceCheck(toolIds, profileId = 'gov', impact = null, frameworks = null,
                  licenseBlocklist = null, externalCaps = null) {
    const prof = this.profileById.get(profileId) || this.profileById.get('gov');
    const imp = impact || prof.impact;
    const fws = this.resolveFrameworks(profileId, frameworks);
    const have = this.coveredCapabilities(toolIds);
    (externalCaps || []).forEach(c => have.add(c));
    const ctrls = this.requiredControls(fws, imp);

    const results = [], gaps = {};
    for (const c of ctrls) {
      const missing = c.caps.filter(x => !have.has(x));
      const status = missing.length === 0 ? 'pass'
        : (c.severity === 'recommended' ? 'warn' : 'fail');
      results.push({ ...c, missing, status });
      missing.forEach(x => { (gaps[x] ||= []).push(c.control_id); });
    }

    /* คะแนนแยกตามมาตรฐานรายฉบับ */
    const byFw = {};
    for (const fid of fws) {
      const rows = results.filter(r => fid in r.refs);
      const passed = rows.filter(r => r.status === 'pass').length;
      const f = this.frameworkById.get(fid);
      byFw[fid] = {
        framework: fid, short_th: f.short_th, name_th: f.name_th,
        family: f.family, region: f.region, verify: !!f.verify, authority: f.authority || '',
        total: rows.length, passed,
        score: rows.length ? round(100 * passed / rows.length, 1) : 100,
        failed: rows.filter(r => r.status === 'fail').map(r => r.control_id),
      };
    }

    /* Automation: greedy set cover — กรองด้วยชั้นลิขสิทธิ์ ไม่ใช่การค้นคำ */
    const blocked = new Set(licenseBlocklist || []);
    const licenseOk = (t) => !blocked.has(t.license_class || 'permissive');
    const recommendations = [];
    let remaining = new Set(Object.keys(gaps));
    let pool = this.c.tools.filter(t => t.profiles.includes(profileId) &&
      !toolIds.includes(t.id) && licenseOk(t));
    let guard = 0;
    while (remaining.size && guard++ < 80) {
      let best = null, bestHit = new Set();
      const preferManaged = (this.profileById.get(profileId) || {}).grade_pref === 'saas';
      for (const t of pool) {
        const hit = new Set(t.capabilities.filter(c => remaining.has(c)));
        if (!hit.size) continue;
        if (hit.size > bestHit.size) { best = t; bestHit = hit; continue; }
        if (hit.size < bestHit.size || !best) continue;
        const tM = !!t.managed, bM = !!best.managed;
        if (tM !== bM) {
          if (preferManaged === tM) { best = t; bestHit = hit; }
          continue;
        }
        if (t.min.ram_gb < best.min.ram_gb) { best = t; bestHit = hit; }
      }
      if (!best || bestHit.size === 0) break;
      const ctrlIds = [...new Set([...bestHit].flatMap(cap => gaps[cap]))].sort();
      const fwSet = new Set(fws);
      recommendations.push({
        tool_id: best.id, name: best.name, stage: best.stage, category: best.category,
        closes: [...bestHit].sort(), controls: ctrlIds,
        frameworks: [...new Set(ctrlIds.flatMap(cid =>
          Object.keys(this.frameworkRefs(cid, fwSet))))].sort(),
        add_vcpu: best.min.vcpu, add_ram_gb: best.min.ram_gb, add_disk_gb: best.min.disk_os_gb,
        freq: best.freq, weight: this.dutyWeight(best.freq), conc_group: best.conc_group,
        license: best.license, license_class: best.license_class, note_th: best.note_th,
      });
      bestHit.forEach(c => remaining.delete(c));
      pool = pool.filter(t => t.id !== best.id);
    }

    const total = results.length;
    const passed = results.filter(r => r.status === 'pass').length;
    return {
      profile: profileId, impact: imp, frameworks: fws,
      external_caps: [...new Set(externalCaps || [])].sort(),
      total_rules: total, passed,
      score: total ? round(100 * passed / total, 1) : 100,
      failed_count: results.filter(r => r.status === 'fail').length,
      warn_count: results.filter(r => r.status === 'warn').length,
      results, by_framework: byFw,
      gaps: mapSorted(gaps), uncovered_caps: [...remaining].sort(),
      recommendations,
      verify_needed: fws.filter(f => this.frameworkById.get(f).verify),
    };
  }

  /** ชุดเครื่องมือที่น้อยที่สุดที่ทำให้ผ่านมาตรฐานที่เลือก (ใช้สร้างแผนอัตโนมัติ) */
  requiredTools(frameworks, profileId = 'gov', impact = 'high',
                licenseBlocklist = null, seedTools = null, externalCaps = null) {
    const seed = [...(seedTools || [])];
    const first = this.complianceCheck(seed, profileId, impact, frameworks, licenseBlocklist,
                                       externalCaps);
    const tools = seed.concat(first.recommendations.map(x => x.tool_id));
    const final = this.complianceCheck(tools, profileId, impact, frameworks, licenseBlocklist,
                                       externalCaps);
    return { tools, added: first.recommendations.map(x => x.tool_id),
             compliance: final, uncovered_caps: final.uncovered_caps };
  }

  /* ------------------------------------------------------------- fleet --- */
  planFleet(vms, opts = {}) {
    const { profileId = 'gov', impact = null, frameworks = null, licenseBlocklist = null,
            externalCaps = null } = opts;
    const out = vms.map(vm => {
      const calc = this.colocate(vm.tools, { ...opts, executors: vm.executors || {} });
      const spec = vm.spec || {};
      const has = spec.vcpu != null && spec.vcpu !== '' && spec.vcpu > 0;
      const gap = has ? {
        vcpu: num(spec.vcpu) - calc.allocated.vcpu,
        ram_gb: num(spec.ram_gb) - calc.allocated.ram_gb,
        disk_os_gb: num(spec.disk_os_gb) - calc.allocated.disk_os_gb,
        disk_data_gb: num(spec.disk_data_gb) - calc.allocated.disk_data_gb,
      } : null;
      let verdict = 'unknown';
      if (gap) {
        if (gap.vcpu < 0 || gap.ram_gb < 0) verdict = 'insufficient';
        else if (gap.disk_os_gb < 0 || gap.disk_data_gb < 0) verdict = 'disk-risk';
        else verdict = 'ok';
      }
      return { ...vm, calc, gap, verdict };
    });
    const allTools = [...new Set(vms.flatMap(v => v.tools))];
    const compliance = this.complianceCheck(allTools, profileId, impact, frameworks,
                                            licenseBlocklist, externalCaps);
    const sum = (f) => out.reduce((s, v) => s + f(v), 0);
    return {
      vms: out, compliance, all_tools: allTools,
      totals: {
        vm_count: out.length,
        alloc_vcpu: sum(v => v.calc.allocated.vcpu),
        alloc_ram_gb: sum(v => v.calc.allocated.ram_gb),
        alloc_disk_gb: sum(v => v.calc.allocated.disk_os_gb + v.calc.allocated.disk_data_gb),
        spec_vcpu: sum(v => num(v.spec?.vcpu)),
        spec_ram_gb: sum(v => num(v.spec?.ram_gb)),
        spec_disk_gb: sum(v => num(v.spec?.disk_os_gb) + num(v.spec?.disk_data_gb)),
        insufficient: out.filter(v => v.verdict === 'insufficient').length,
        disk_risk: out.filter(v => v.verdict === 'disk-risk').length,
        gpu_needed: out.some(v => v.calc.gpu_required),
        long_term: this.model.horizons.map((h, i) => ({
          months: h,
          gb: round(out.reduce((s, v) => s + v.calc.storage.long_term[i].data_gb, 0), 1),
          provisioned_gb: out.reduce((s, v) => s + v.calc.storage.long_term[i].provisioned_gb, 0),
        })),
      },
    };
  }
}

/* --------------------------------------------------------------- utils --- */
function round(v, n) { const p = Math.pow(10, n); return Math.round(v * p + Number.EPSILON) / p; }
function num(v) { const n = parseFloat(v); return Number.isFinite(n) ? n : 0; }
function mapSorted(o) {
  const r = {};
  Object.keys(o).sort().forEach(k => { r[k] = [...o[k]].sort(); });
  return r;
}
export { round, num, DAYS_PER_MONTH };
