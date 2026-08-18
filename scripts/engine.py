# -*- coding: utf-8 -*-
"""
เครื่องคำนวณทรัพยากร (Reference Implementation ภาษา Python)
ต้องให้ผลลัพธ์ตรงกับ assets/engine.js ทุกกรณี — มีเทสต์เทียบใน scripts/verify.py

โมเดลการคำนวณกรณี "เครื่องเดียวแชร์หลายเครื่องมือ" (Co-location)
================================================================
เงื่อนไขที่ 1  Method A : Peak-Max  =  max( minimum ของแต่ละเครื่องมือ )
              ตีความว่า "ณ เวลาใดเวลาหนึ่งมีเครื่องมือเพียงตัวเดียวที่ทำงานหนักสุด"
              เป็นค่าต่ำสุดที่ต้องมีเพื่อให้เครื่องมือที่หนักที่สุด "รันผ่าน" ได้

เงื่อนไขที่ 2  Method B : Weighted-Sum 20-60% + บันไดร่วมเครื่อง
              w_solo = 0.20 + 0.40 x activity_index(freq_i)     -> ช่วงเดี่ยว 0.20 - 0.60
              w_max(n) = ladder[min(n,8)-1]   60% … 20% เมื่อมี n เครื่องมือ self-hosted
              w_i = 0.20 + (w_max(n) - 0.20) x activity_index
              B   = ผลรวมของ ( minimum_i x w_i ) ทุกเครื่องมือ

ตัวตรวจความเป็นไปได้  Method C : Resident Floor
              C = MAX(idle) + w_max(n) x (Σ idle - MAX(idle))
              กัน daemon ที่หนักที่สุดเต็ม และลดส่วนที่ซ้อนของตัวอื่นตามบันไดเดียวกัน

ผลลัพธ์สุดท้าย (ตามที่กำหนด "ต้องเป็นค่าที่มากสุดสำหรับ minimum เท่านั้น")
              REQUIRED = max(A, B, C)  +  OS/Runtime Reserve  ->  ปัดขึ้นตาม Allocation Ladder
"""
from __future__ import annotations
import math
import sys as _sys

from catalog_data import (FREQ_CLASSES, TOOLS, MODEL, PROFILES, CAPABILITIES,
                          CONTROLS, CONTROL_BY_ID, CONTROL_GROUPS,
                          FRAMEWORKS, FRAMEWORK_BY_ID, FRAMEWORK_FAMILIES,
                          FRAMEWORK_PRESETS, SEV_RANK,
                          framework_refs, control_severity)

_EPS = _sys.float_info.epsilon   # 2.220446049250313e-16 = Number.EPSILON ของ JavaScript


def jsround(v: float, n: int) -> float:
    """ปัดเศษให้ผลลัพธ์เหมือน `Math.round(v * 10**n + Number.EPSILON) / 10**n` ของ JavaScript

    ห้ามใช้ round() ของ Python ในไฟล์นี้ เพราะ round() ใช้ banker's rounding
    (ปัดครึ่งไปเลขคู่) ซึ่งให้ผลต่างจาก JS ที่ปัดครึ่งขึ้น เช่น 0.7925 -> Python 0.792 แต่ JS 0.793
    ความต่างระดับ 0.001 จะสะสมจนตัวเลขสองฝั่งไม่ตรงกัน
    """
    p = 10.0 ** n
    return math.floor(v * p + _EPS + 0.5) / p


FREQ_BY_ID = {f["id"]: f for f in FREQ_CLASSES}
TOOL_BY_ID = {t["id"]: t for t in TOOLS}
PROFILE_BY_ID = {p["id"]: p for p in PROFILES}
DAYS_PER_MONTH = 30.44


# --------------------------------------------------------------------------- #
# helper
# --------------------------------------------------------------------------- #
def duty_weight(freq_id: str) -> float:
    """น้ำหนักเดี่ยว (เครื่องมืออยู่เครื่องเดียว) ช่วง 0.20 - 0.60"""
    a = FREQ_BY_ID[freq_id]["activity_index"]
    return jsround(MODEL["w_base"] + MODEL["w_span"] * a, 4)


def host_tool_count(tool_ids: list) -> int:
    """นับเฉพาะเครื่องมือ self-hosted บน VM นั้น (managed ไม่กินโควตาและไม่นับใน n)"""
    n = 0
    for tid in tool_ids:
        t = TOOL_BY_ID.get(tid)
        if t and not t.get("managed"):
            n += 1
    return n


def cross_max(n: int) -> float:
    """เพดานน้ำหนักตามจำนวนเครื่องมือร่วมเครื่อง — หยุดที่ 20% เมื่อ n >= 8"""
    ladder = MODEL["w_cross_ladder"]
    cap = int(MODEL["w_cross_cap"])
    if n <= 0:
        return ladder[0]
    idx = min(n, cap) - 1
    return ladder[idx]


def colocate_weight(freq_id: str, n: int) -> float:
    """น้ำหนักจริงบน VM นั้น: ยึดเพดาน w_max(n) แล้วสเกลตามความถี่ อยู่ใน [0.20, 0.60]"""
    a = FREQ_BY_ID[freq_id]["activity_index"]
    w_max = cross_max(n)
    w = MODEL["w_base"] + (w_max - MODEL["w_base"]) * a
    if w < MODEL["w_base"]:
        w = MODEL["w_base"]
    if w > 0.60:
        w = 0.60
    return jsround(w, 4)


def ladder_up(value: float, ladder: list) -> int:
    """ปัดขึ้นตามขั้นการจัดสรร; ถ้าเกินขั้นสูงสุดให้ปัดขึ้นเป็นทวีคูณของขั้นสูงสุด"""
    for step in ladder:
        if value <= step + 1e-9:
            return step
    top = ladder[-1]
    return int(math.ceil(value / top) * top)


# --------------------------------------------------------------------------- #
# storage projection
# --------------------------------------------------------------------------- #
def project_tool_storage(tool: dict, horizon_months: int, retention_override=None,
                         scale_factor: float = 1.0) -> dict:
    """ประเมินพื้นที่จัดเก็บของเครื่องมือ 1 ตัว ณ เดือนที่ horizon_months

    data(h) = daily x scale x (1+growth)^(h/12) x min(retention_days, h x 30.44) x (1 + index_overhead)
    เหตุผล: ระบบจะเข้าสู่สภาวะคงตัวเมื่อถึงรอบ retention (ข้อมูลเก่าถูกลบเท่าที่ข้อมูลใหม่เข้ามา)
            แต่อัตราการผลิตข้อมูลต่อวันยังโตขึ้นทุกปีตาม growth_yr
    """
    s = tool["storage"]
    retention = retention_override if retention_override else s["retention_days"]
    window_days = min(retention, horizon_months * DAYS_PER_MONTH)
    growth_mult = (1.0 + s["growth_yr"]) ** (horizon_months / 12.0)
    daily = s["data_daily_gb"] * scale_factor
    data_gb = daily * growth_mult * window_days * (1.0 + s["index_overhead"])
    return dict(
        tool_id=tool["id"],
        install_gb=jsround(s["install_gb"], 2),
        data_gb=jsround(data_gb, 2),
        window_days=jsround(window_days, 1),
        growth_mult=jsround(growth_mult, 3),
        effective_daily_gb=jsround(daily * growth_mult, 3),
    )


# --------------------------------------------------------------------------- #
# core: co-location calculation
# --------------------------------------------------------------------------- #
def colocate(tool_ids: list, horizon_months: int = 36, retention_override=None,
             executors: dict | None = None, use_rec: bool = False,
             mode: str = "strict", scale_factor: float = 1.0,
             extra_install_gb: float = 0.0) -> dict:
    """คำนวณ resource ที่ต้องมีบน VM 1 เครื่องที่รวมเครื่องมือหลายตัว

    executors    : {"jenkins-agent": 4}  -> คูณจำนวน instance ของเครื่องมือนั้น
    use_rec      : True = ใช้ค่า recommended แทน minimum เป็นฐานการคำนวณ
    mode         : "strict"    -> ใช้ B1 (บวกทุกตัวถ่วงน้ำหนัก) ตามเงื่อนไขที่กำหนดมา
                   "realistic" -> ใช้ B2 (บวกข้ามกลุ่ม, ใช้ค่าสูงสุดภายในกลุ่มที่รันเรียงกัน)
    scale_factor : ตัวคูณปริมาณข้อมูล (1.0 = UAT/Production ขนาดเล็กตามค่าฐาน)
    extra_install_gb : พื้นที่ Disk OS ที่ต้องเพิ่มจากเงื่อนไขของโครงการ
                       (เช่น Air-gapped ต้องเก็บ mirror ของฐานข้อมูลช่องโหว่และ package ไว้ในเครื่อง)
    """
    executors = executors or {}
    key = "rec" if use_rec else "min"
    n_host = host_tool_count(tool_ids)
    w_max = cross_max(n_host)
    rows = []
    for tid in tool_ids:
        t = TOOL_BY_ID[tid]
        n = int(executors.get(tid, 1))
        w_solo = duty_weight(t["freq"])
        w = colocate_weight(t["freq"], n_host)
        st = project_tool_storage(t, horizon_months, retention_override, scale_factor)
        st["data_gb"] = jsround(st["data_gb"] * n, 2)
        st["install_gb"] = jsround(st["install_gb"] * n, 2)
        rows.append(dict(
            tool_id=tid, name=t["name"], stage=t["stage"], category=t["category"],
            instances=n, freq=t["freq"], freq_label=FREQ_BY_ID[t["freq"]]["label_th"],
            weight=w, weight_solo=w_solo, resident=t["resident"], conc_group=t["conc_group"],
            min_vcpu=t[key]["vcpu"] * n,
            min_ram=t[key]["ram_gb"] * n,
            idle_ram=t["idle_ram_gb"] * n,
            w_vcpu=jsround(t[key]["vcpu"] * n * w, 3),
            w_ram=jsround(t[key]["ram_gb"] * n * w, 3),
            storage=st,
            gpu=t["gpu"],
        ))

    # --- เงื่อนไขที่ 1 : Peak-Max ---
    a_vcpu = max((r["min_vcpu"] for r in rows), default=0)
    a_ram = max((r["min_ram"] for r in rows), default=0)
    a_driver_vcpu = max(rows, key=lambda r: r["min_vcpu"])["name"] if rows else "-"
    a_driver_ram = max(rows, key=lambda r: r["min_ram"])["name"] if rows else "-"

    # --- เงื่อนไขที่ 2 แบบ B1 : Weighted-Sum 20-60% + บันไดร่วมเครื่อง ---
    b_vcpu = jsround(sum(r["w_vcpu"] for r in rows), 3)
    b_ram = jsround(sum(r["w_ram"] for r in rows), 3)

    # --- เงื่อนไขที่ 2 แบบ B2 : Weighted-Sum ตามกลุ่มการทำงานพร้อมกัน ---
    groups = {}
    for r in rows:
        groups.setdefault(r["conc_group"], []).append(r)
    b2_vcpu, b2_ram, b2_detail = 0.0, 0.0, []
    for gname, grows in groups.items():
        if gname == "resident":                       # ค้างอยู่ตลอด -> บวกทุกตัว
            gv = sum(r["w_vcpu"] for r in grows)
            gr = sum(r["w_ram"] for r in grows)
            rule = "sum"
        else:                                          # รันเรียงต่อกัน -> ใช้ค่าสูงสุด
            gv = max(r["w_vcpu"] for r in grows)
            gr = max(r["w_ram"] for r in grows)
            rule = "max"
        b2_vcpu += gv
        b2_ram += gr
        b2_detail.append(dict(group=gname, rule=rule, count=len(grows),
                              vcpu=jsround(gv, 3), ram_gb=jsround(gr, 3)))
    b2_vcpu, b2_ram = jsround(b2_vcpu, 3), jsround(b2_ram, 3)

    # --- ตัวตรวจ : Resident Floor (กันตัวหนักสุดเต็ม + ลดส่วนซ้อนตามบันได) ---
    res_rows = [r for r in rows if r["resident"]]
    if res_rows:
        idles = [r["idle_ram"] for r in res_rows]
        max_idle = max(idles)
        c_ram = jsround(max_idle + w_max * (sum(idles) - max_idle), 3)
        vparts = [0.25 * r["instances"] for r in res_rows]
        max_v = max(vparts)
        c_vcpu = jsround(max_v + w_max * (sum(vparts) - max_v), 3)
    else:
        c_ram, c_vcpu = 0.0, 0.0

    # --- ผลลัพธ์ = ค่าที่มากสุด + OS Reserve -> ปัดขึ้น ---
    sel_vcpu = b_vcpu if mode == "strict" else b2_vcpu
    sel_ram = b_ram if mode == "strict" else b2_ram
    raw_vcpu = max(a_vcpu, sel_vcpu, c_vcpu)
    raw_ram = max(a_ram, sel_ram, c_ram)
    need_vcpu = raw_vcpu + MODEL["os_reserve_vcpu"]
    need_ram = raw_ram + MODEL["os_reserve_ram_gb"]
    alloc_vcpu = ladder_up(need_vcpu, MODEL["vcpu_ladder"])
    alloc_ram = ladder_up(need_ram, MODEL["ram_ladder"])

    # --- Storage ---
    install_sum = jsround(sum(r["storage"]["install_gb"] for r in rows) +
                          (extra_install_gb if rows else 0.0), 2)
    data_sum = jsround(sum(r["storage"]["data_gb"] for r in rows), 2)
    free = MODEL["disk_free_ratio"]
    need_os_disk = (MODEL["os_reserve_disk_gb"] + install_sum) / (1.0 - free)
    need_data_disk = data_sum / (1.0 - free) if data_sum > 0 else 0.0
    alloc_os_disk = ladder_up(need_os_disk, MODEL["disk_ladder"])
    alloc_data_disk = ladder_up(need_data_disk, MODEL["disk_ladder"]) if need_data_disk > 0 else 0

    # --- ผลลัพธ์ระยะยาว ---
    long_term = []
    for h in MODEL["horizons"]:
        d = jsround(sum(project_tool_storage(TOOL_BY_ID[r["tool_id"]], h, retention_override,
                                           scale_factor)["data_gb"] * r["instances"] for r in rows), 2)
        long_term.append(dict(
            months=h,
            data_gb=d,
            total_gb=jsround(install_sum + d, 2),
            provisioned_gb=ladder_up((MODEL["os_reserve_disk_gb"] + install_sum + d) / (1.0 - free),
                                     MODEL["disk_ladder"]),
        ))

    return dict(
        tools=rows,
        horizon_months=horizon_months,
        mode=mode, scale_factor=scale_factor,
        method_a=dict(vcpu=a_vcpu, ram_gb=a_ram,
                      driver_vcpu=a_driver_vcpu, driver_ram=a_driver_ram,
                      label_th="เงื่อนไข 1: Peak-Max (ค่า minimum ที่สูงสุด)"),
        method_b=dict(vcpu=b_vcpu, ram_gb=b_ram,
                      label_th="เงื่อนไข 2 (B1 Strict): Weighted-Sum 20-60% บวกทุกเครื่องมือ"),
        method_b2=dict(vcpu=b2_vcpu, ram_gb=b2_ram, detail=b2_detail,
                       label_th="เงื่อนไข 2 (B2 Realistic): บวกข้ามกลุ่ม / ใช้ค่าสูงสุดในกลุ่มที่รันเรียงกัน"),
        method_c=dict(vcpu=c_vcpu, ram_gb=c_ram,
                      label_th="ตัวตรวจ: Resident Floor (MAX idle + w_max(n) ของส่วนที่เหลือ)"),
        weight_model=dict(n_selfhosted=n_host, w_max=w_max),
        governing=dict(
            vcpu="A" if raw_vcpu == a_vcpu else ("B" if raw_vcpu == sel_vcpu else "C"),
            ram="A" if raw_ram == a_ram else ("B" if raw_ram == sel_ram else "C"),
        ),
        raw=dict(vcpu=jsround(raw_vcpu, 3), ram_gb=jsround(raw_ram, 3)),
        os_reserve=dict(vcpu=MODEL["os_reserve_vcpu"], ram_gb=MODEL["os_reserve_ram_gb"],
                        disk_gb=MODEL["os_reserve_disk_gb"]),
        required=dict(vcpu=jsround(need_vcpu, 3), ram_gb=jsround(need_ram, 3),
                      disk_os_gb=jsround(need_os_disk, 2), disk_data_gb=jsround(need_data_disk, 2)),
        allocated=dict(vcpu=alloc_vcpu, ram_gb=alloc_ram,
                       disk_os_gb=alloc_os_disk, disk_data_gb=alloc_data_disk),
        storage=dict(install_gb=install_sum, data_gb=data_sum,
                     free_ratio=free, long_term=long_term),
        gpu_required=any(r["gpu"] for r in rows),
    )


# --------------------------------------------------------------------------- #
# compliance engine
# --------------------------------------------------------------------------- #
def covered_capabilities(tool_ids: list) -> set:
    caps = set()
    for tid in tool_ids:
        caps |= set(TOOL_BY_ID[tid]["capabilities"])
    return caps


def resolve_frameworks(profile_id: str = "gov", frameworks=None) -> list:
    """ถ้าไม่ระบุมาตรฐาน ให้ใช้ชุดสำเร็จของประเภทโครงการนั้น"""
    if frameworks:
        return [f for f in frameworks if f in FRAMEWORK_BY_ID]
    prof = PROFILE_BY_ID.get(profile_id) or PROFILE_BY_ID["gov"]
    return list(FRAMEWORK_PRESETS.get(prof.get("framework_preset", "gov"), []))


def required_controls(frameworks: list, impact: str = "high") -> list:
    """รวม control ที่ต้องทำจากมาตรฐานที่เลือก แล้วกรองตามระดับผลกระทบ

    control หนึ่งตัวอาจถูกอ้างจากหลายมาตรฐาน -> รวมเป็นรายการเดียวพร้อมเลขข้อของทุกฉบับ
    """
    fset = set(frameworks)
    out = []
    for c in CONTROLS:
        refs = framework_refs(c["id"], fset)
        if not refs:
            continue
        if impact not in c["impact"]:
            continue
        out.append(dict(
            control_id=c["id"], group=c["group"], group_th=CONTROL_GROUPS[c["group"]],
            title_th=c["title_th"], detail_th=c.get("detail_th", ""),
            caps=c["caps"], param=c.get("param", {}),
            severity=control_severity(c["id"], fset), refs=refs,
        ))
    out.sort(key=lambda x: (-SEV_RANK[x["severity"]], x["group"], x["control_id"]))
    return out


def required_capabilities(frameworks: list, impact: str = "high") -> dict:
    """คืน {capability: [control_id, ...]} ที่มาตรฐานที่เลือกเรียกร้อง"""
    need = {}
    for c in required_controls(frameworks, impact):
        for cap in c["caps"]:
            need.setdefault(cap, []).append(c["control_id"])
    return {k: sorted(set(v)) for k, v in sorted(need.items())}


def tool_fits(t: dict, fit) -> bool:
    """True ถ้าไม่กรองสภาพแวดล้อม หรือเครื่องมือรองรับสภาพแวดล้อมนั้น"""
    if not fit or fit in ("all", ""):
        return True
    return fit in (t.get("fit") or [])


def compliance_check(tool_ids: list, profile_id: str = "gov", impact: str | None = None,
                     frameworks=None, license_blocklist=None, external_caps=None,
                     fit=None) -> dict:
    """ตรวจว่าชุดเครื่องมือที่เลือกครอบคลุมมาตรฐานที่เลือกครบหรือไม่
    และแนะนำเครื่องมือที่ควรเพิ่มเพื่อปิดช่องว่าง (Automation เลือกเครื่องมือให้ผ่านมาตรฐาน)

    frameworks        : รายการ framework id ที่ผู้ใช้ติ๊กเลือก (None = ใช้ชุดสำเร็จของ profile)
    license_blocklist : ชั้นลิขสิทธิ์ที่ห้ามใช้ เช่น ["strong-copyleft", "network-copyleft"]
                        (ค่าที่ใช้ได้ดูใน LICENSE_CLASSES) — ตัดเครื่องมือกลุ่มนั้นออกจากรายการที่แนะนำ
    external_caps     : capability ที่องค์กรมีระบบส่วนกลางรองรับอยู่แล้ว (เช่น SSO, WAF, Monitoring)
                        จะถือว่าครอบคลุมแล้วโดยไม่ต้องติดตั้งเครื่องมือเพิ่มในโครงการนี้
    """
    prof = PROFILE_BY_ID.get(profile_id) or PROFILE_BY_ID["gov"]
    imp = impact or prof["impact"]
    fws = resolve_frameworks(profile_id, frameworks)
    have = covered_capabilities(tool_ids) | set(external_caps or [])
    ctrls = required_controls(fws, imp)

    results, gaps = [], {}
    for c in ctrls:
        missing = [x for x in c["caps"] if x not in have]
        status = "pass" if not missing else ("warn" if c["severity"] == "recommended" else "fail")
        results.append(dict(c, missing=missing, status=status))
        for x in missing:
            gaps.setdefault(x, []).append(c["control_id"])

    # ---- คะแนนแยกตามมาตรฐานรายฉบับ ----
    by_fw = {}
    for fid in fws:
        rows = [r for r in results if fid in r["refs"]]
        passed = sum(1 for r in rows if r["status"] == "pass")
        f = FRAMEWORK_BY_ID[fid]
        by_fw[fid] = dict(
            framework=fid, short_th=f["short_th"], name_th=f["name_th"],
            family=f["family"], region=f["region"], verify=f.get("verify", False),
            authority=f.get("authority", ""),
            total=len(rows), passed=passed,
            score=jsround(100.0 * passed / len(rows), 1) if rows else 100.0,
            failed=[r["control_id"] for r in rows if r["status"] == "fail"],
        )

    # ---- Automation: greedy set cover เลือกเครื่องมือปิดช่องว่าง ----
    # กรองด้วย "ชั้นของลิขสิทธิ์" ไม่ใช่การค้นคำ เพราะการค้นคำว่า GPL จะตัด LGPL ทิ้งด้วย
    blocked = set(license_blocklist or [])

    def license_ok(t):
        return t.get("license_class", "permissive") not in blocked

    recommendations = []
    remaining = set(gaps)
    pool = [t for t in TOOLS
            if profile_id in t["profiles"] and t["id"] not in tool_ids
            and license_ok(t) and tool_fits(t, fit)]
    guard = 0
    while remaining and guard < 80:
        guard += 1
        best, best_hit = None, set()
        prefer_managed = (PROFILE_BY_ID.get(profile_id) or {}).get("grade_pref") == "saas"
        for t in pool:
            hit = set(t["capabilities"]) & remaining
            if not hit:
                continue
            if len(hit) > len(best_hit):
                best, best_hit = t, hit
                continue
            if len(hit) < len(best_hit) or not best:
                continue
            t_m, b_m = bool(t.get("managed")), bool(best.get("managed"))
            if t_m != b_m:
                if prefer_managed == t_m:
                    best, best_hit = t, hit
                continue
            if t["min"]["ram_gb"] < best["min"]["ram_gb"]:
                best, best_hit = t, hit
        if not best or not best_hit:
            break
        ctrl_ids = sorted({cid for cap in best_hit for cid in gaps[cap]})
        recommendations.append(dict(
            tool_id=best["id"], name=best["name"], stage=best["stage"], category=best["category"],
            closes=sorted(best_hit), controls=ctrl_ids,
            frameworks=sorted({fid for cid in ctrl_ids for fid in framework_refs(cid, set(fws))}),
            add_vcpu=best["min"]["vcpu"], add_ram_gb=best["min"]["ram_gb"],
            add_disk_gb=best["min"]["disk_os_gb"], freq=best["freq"],
            weight=duty_weight(best["freq"]), conc_group=best["conc_group"],
            license=best["license"], note_th=best["note_th"],
        ))
        remaining -= best_hit
        pool = [t for t in pool if t["id"] != best["id"]]

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "pass")
    return dict(
        profile=profile_id, impact=imp, frameworks=fws,
        external_caps=sorted(set(external_caps or [])),
        total_rules=total, passed=passed,
        score=jsround(100.0 * passed / total, 1) if total else 100.0,
        failed_count=sum(1 for r in results if r["status"] == "fail"),
        warn_count=sum(1 for r in results if r["status"] == "warn"),
        results=results, by_framework=by_fw,
        gaps={k: sorted(v) for k, v in sorted(gaps.items())},
        uncovered_caps=sorted(remaining),
        recommendations=recommendations,
        verify_needed=[fid for fid in fws if FRAMEWORK_BY_ID[fid].get("verify")],
    )


def required_tools(frameworks: list, profile_id: str = "gov", impact: str = "high",
                   license_blocklist=None, seed_tools=None, external_caps=None,
                   fit=None) -> dict:
    """หาชุดเครื่องมือที่น้อยที่สุดที่ทำให้ผ่านมาตรฐานที่เลือก (ใช้สร้างแผนอัตโนมัติ)"""
    seed = list(seed_tools or [])
    r = compliance_check(seed, profile_id, impact, frameworks, license_blocklist,
                         external_caps, fit)
    tools = seed + [x["tool_id"] for x in r["recommendations"]]
    final = compliance_check(tools, profile_id, impact, frameworks, license_blocklist,
                             external_caps, fit)
    return dict(tools=tools, added=[x["tool_id"] for x in r["recommendations"]],
                compliance=final, uncovered_caps=final["uncovered_caps"])


def evaluate_preset(preset: dict, horizon_months: int = 36, mode: str = "realistic",
                    scale_factor: float = 1.0) -> dict:
    """เทียบ spec ที่ขอไว้จริง กับค่าที่โมเดลคำนวณได้"""
    out = dict(id=preset["id"], name_th=preset["name_th"], profile=preset["profile"],
               network_th=preset["network_th"], mode=mode, vms=[])
    all_tools = []
    for vm in preset["vms"]:
        calc = colocate(vm["tools"], horizon_months=horizon_months, mode=mode,
                        scale_factor=scale_factor)
        spec = vm["spec"]
        alloc = calc["allocated"]
        gap = dict(
            vcpu=spec["vcpu"] - alloc["vcpu"],
            ram_gb=spec["ram_gb"] - alloc["ram_gb"],
            disk_os_gb=spec["disk_os_gb"] - alloc["disk_os_gb"],
            disk_data_gb=spec["disk_data_gb"] - alloc["disk_data_gb"],
        )
        verdict = "ok"
        if gap["vcpu"] < 0 or gap["ram_gb"] < 0:
            verdict = "insufficient"
        elif gap["disk_os_gb"] < 0 or gap["disk_data_gb"] < 0:
            verdict = "disk-risk"
        out["vms"].append(dict(host=vm["host"], ip=vm["ip"], role_th=vm["role_th"],
                               tools=vm["tools"], spec=spec, calc=calc, gap=gap, verdict=verdict))
        all_tools += vm["tools"]
    out["compliance"] = compliance_check(sorted(set(all_tools)), preset["profile"])
    out["totals"] = dict(
        spec_vcpu=sum(v["spec"]["vcpu"] for v in out["vms"]),
        spec_ram_gb=sum(v["spec"]["ram_gb"] for v in out["vms"]),
        spec_disk_gb=sum(v["spec"]["disk_os_gb"] + v["spec"]["disk_data_gb"] for v in out["vms"]),
        calc_vcpu=sum(v["calc"]["allocated"]["vcpu"] for v in out["vms"]),
        calc_ram_gb=sum(v["calc"]["allocated"]["ram_gb"] for v in out["vms"]),
        calc_disk_gb=sum(v["calc"]["allocated"]["disk_os_gb"] + v["calc"]["allocated"]["disk_data_gb"]
                         for v in out["vms"]),
    )
    return out
