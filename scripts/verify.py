# -*- coding: utf-8 -*-
"""ตรวจสอบความถูกต้อง (verification suite)

1. ตรวจ invariant ของ catalog (id ไม่ซ้ำ, capability มีจริง, ทุก capability มีเครื่องมือรองรับ)
2. ตรวจว่าน้ำหนัก w อยู่ในช่วง 0.20-0.60 และบันไดร่วมเครื่องทำงาน
3. ตรวจว่า REQUIRED = MAX(A, B, C) + OS Reserve จริงทุกกรณี
4. ตรวจว่า engine.py และ assets/engine.js ให้ผลลัพธ์ตรงกันทุกกรณีทดสอบ
5. ตรวจว่า catalog.json ที่ commit ไว้ตรงกับ catalog_data.py

รัน:  python3 scripts/verify.py
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import catalog_data as C   # noqa: E402
import engine as E         # noqa: E402
import build_catalog       # noqa: E402
import pipeline_gen as PG  # noqa: E402

FAIL = []
OKN = [0]


def check(cond, msg):
    if cond:
        OKN[0] += 1
    else:
        FAIL.append(msg)
        print("  [FAIL] " + msg)


# --------------------------------------------------------------------------- #
def test_catalog_invariants():
    print("[1] catalog invariants")
    ids = [t["id"] for t in C.TOOLS]
    check(len(ids) == len(set(ids)), "tool id ซ้ำกัน")
    for need in ("helm", "k3s-control", "kind-k3d", "kubernetes-kubeadm",
                 "microk8s", "flux-cd", "tekton", "woodpecker", "podman-buildah",
                 "kyverno", "dependency-track", "grafana-loki", "sealed-secrets",
                 "nexus-repository", "zot"):
        check(need in ids, "ขาดเครื่องมือ " + need)
    nexus = next(t for t in C.TOOLS if t["id"] == "nexus-repository")
    check(nexus["stage"] == 5, "Nexus ต้องอยู่ในขั้น 5 Store & Versioning")
    check("package_repo" in nexus["capabilities"], "Nexus ต้องมี capability package_repo")
    check(next(t for t in C.TOOLS if t["id"] == "azure-container-registry")["stage"] == 5,
          "ACR ต้องอยู่ในขั้น Store ไม่ใช่ Test")
    check(next(t for t in C.TOOLS if t["id"] == "azure-kubernetes-service")["stage"] == 6,
          "AKS ต้องอยู่ในขั้น Deploy ไม่ใช่ Store")
    check(any(c["id"] == "C-SC-PKG" for c in C.CONTROLS), "ขาดมาตรการ C-SC-PKG")
    check(any(c["id"] == "C-SC-PROMOTE" for c in C.CONTROLS), "ขาดมาตรการ C-SC-PROMOTE")
    allcaps = set(C.CAPABILITIES)
    for t in C.TOOLS:
        bad = [c for c in t["capabilities"] if c not in allcaps]
        check(not bad, f"{t['id']} อ้าง capability ที่ไม่มี: {bad}")
        if t.get("managed"):
            check(t["min"]["vcpu"] == 0 and t["min"]["ram_gb"] == 0,
                  f"{t['id']} managed ต้องไม่กิน VM (min=0)")
        else:
            check(t["min"]["vcpu"] > 0 and t["min"]["ram_gb"] > 0, f"{t['id']} min เป็นศูนย์")
        check(t["rec"]["vcpu"] >= t["min"]["vcpu"], f"{t['id']} rec vCPU < min")
        check(t["rec"]["ram_gb"] >= t["min"]["ram_gb"], f"{t['id']} rec RAM < min")
        check(t["idle_ram_gb"] <= t["min"]["ram_gb"], f"{t['id']} idle RAM > min RAM")
        check(t["freq"] in {f["id"] for f in C.FREQ_CLASSES}, f"{t['id']} freq ไม่รู้จัก")
        check(t["conc_group"] in {"resident", "ci_seq", "async", "load"},
              f"{t['id']} conc_group ไม่รู้จัก")
        check(set(t.get("fit") or []) <= {"cloud", "hybrid", "private", "local"} and t.get("fit"),
              f"{t['id']} fit ไม่ครบหรือไม่รู้จัก: {t.get('fit')}")
        fam = (t.get("install") or {}).get("family")
        check(fam in {"apt", "binary", "k8s", "managed"}, f"{t['id']} install.family={fam}")
        check(t["storage"]["retention_days"] > 0, f"{t['id']} retention <= 0")
        check(0 <= t["storage"]["index_overhead"] <= 1, f"{t['id']} index_overhead นอกช่วง")
        check(bool(t["profiles"]), f"{t['id']} ไม่ระบุ profile")
        check(bool(t["sizing_ref"]), f"{t['id']} ไม่มีที่มาของตัวเลข (sizing_ref)")
    covered = set()
    for t in C.TOOLS:
        covered |= set(t["capabilities"])
    check(not (allcaps - covered), f"capability ที่ไม่มีเครื่องมือรองรับ: {sorted(allcaps - covered)}")
    for r in C.CONTROLS:
        bad = [c for c in r["caps"] if c not in allcaps]
        check(not bad, f"{r['id']} อ้าง capability ที่ไม่มี: {bad}")
        check(r["group"] in C.CONTROL_GROUPS, f"{r['id']} group ไม่รู้จัก")
        check(r["severity"] in ("mandatory", "conditional", "recommended"),
              f"{r['id']} severity ไม่รู้จัก")
        check(bool(r["impact"]), f"{r['id']} ไม่ระบุระดับผลกระทบ")
        check(bool(C.framework_refs(r["id"])),
              f"{r['id']} ไม่มีมาตรฐานฉบับใดอ้างถึงเลย — ควรลบหรือผูกกับมาตรฐาน")
    for p in C.PRESETS:
        for vm in p["vms"]:
            bad = [t for t in vm["tools"] if t not in set(ids)]
            check(not bad, f"preset {vm['host']} อ้างเครื่องมือที่ไม่มี: {bad}")


def test_weight_range():
    print("[2] ช่วงน้ำหนัก 20-60% และบันไดร่วมเครื่อง")
    for f in C.FREQ_CLASSES:
        w = E.duty_weight(f["id"])
        check(0.20 - 1e-9 <= w <= 0.60 + 1e-9, f"น้ำหนักเดี่ยวของ {f['id']} = {w} หลุดช่วง 0.20-0.60")
    check(abs(E.duty_weight("resident") - 0.60) < 1e-9, "resident เดี่ยวต้องได้ 0.60 พอดี")
    check(abs(E.duty_weight("on_demand") - 0.20) < 1e-9, "on_demand เดี่ยวต้องได้ 0.20 พอดี")
    check(abs(E.cross_max(1) - 0.60) < 1e-9, "w_max(1) ต้องเป็น 0.60")
    check(abs(E.cross_max(8) - 0.20) < 1e-9, "w_max(8) ต้องเป็น 0.20")
    check(abs(E.cross_max(20) - 0.20) < 1e-9, "w_max ต้องไม่ต่ำกว่า 0.20 เมื่อ n > 8")
    check(abs(E.colocate_weight("resident", 1) - 0.60) < 1e-9, "resident n=1 ต้อง 60%")
    check(abs(E.colocate_weight("resident", 8) - 0.20) < 1e-9, "resident n=8 ต้อง 20%")
    check(abs(E.colocate_weight("on_demand", 1) - 0.20) < 1e-9, "on_demand ต้องพื้น 20%")
    check(abs(E.colocate_weight("on_demand", 8) - 0.20) < 1e-9, "on_demand n=8 ยังพื้น 20%")
    self_hosted = [t["id"] for t in C.TOOLS if not t.get("managed")][:8]
    r1 = E.colocate(self_hosted[:1], mode="realistic")
    check(abs(r1["tools"][0]["weight"] - 0.60) < 1e-9 or r1["tools"][0]["freq"] != "resident",
          "เครื่องเดียวต้องใช้เพดาน 60% เมื่อเป็น resident (หรือน้อยกว่าถ้าไม่ใช่ resident)")
    r8 = E.colocate(self_hosted, mode="realistic")
    for row in r8["tools"]:
        check(0.20 - 1e-9 <= row["weight"] <= 0.60 + 1e-9,
              f"{row['tool_id']} w={row['weight']} หลุด 20-60 เมื่อ n=8")
    if r8["tools"]:
        idles = [x["idle_ram"] for x in r8["tools"] if x["resident"]]
        if idles:
            check(r8["method_c"]["ram_gb"] + 1e-9 >= max(idles),
                  "C ต้องไม่ต่ำกว่า idle ของ daemon ที่หนักที่สุด")


def test_max_rule():
    print("[3] REQUIRED = MAX(A,B,C) + OS Reserve")
    rnd = random.Random(20260805)
    ids = [t["id"] for t in C.TOOLS]
    for i in range(120):
        k = rnd.randint(1, 12)
        sel = rnd.sample(ids, k)
        for mode in ("strict", "realistic"):
            r = E.colocate(sel, horizon_months=36, mode=mode)
            b = r["method_b"] if mode == "strict" else r["method_b2"]
            exp_v = max(r["method_a"]["vcpu"], b["vcpu"], r["method_c"]["vcpu"])
            exp_r = max(r["method_a"]["ram_gb"], b["ram_gb"], r["method_c"]["ram_gb"])
            check(abs(r["raw"]["vcpu"] - exp_v) < 1e-6,
                  f"case {i} {mode}: raw vCPU {r['raw']['vcpu']} != MAX {exp_v}")
            check(abs(r["raw"]["ram_gb"] - exp_r) < 1e-6,
                  f"case {i} {mode}: raw RAM {r['raw']['ram_gb']} != MAX {exp_r}")
            check(r["required"]["vcpu"] == round(exp_v + C.MODEL["os_reserve_vcpu"], 3),
                  f"case {i} {mode}: required vCPU ไม่ได้บวก OS Reserve")
            check(r["allocated"]["vcpu"] >= r["required"]["vcpu"],
                  f"case {i} {mode}: allocated vCPU < required")
            check(r["allocated"]["ram_gb"] >= r["required"]["ram_gb"],
                  f"case {i} {mode}: allocated RAM < required")
            # B1 ต้อง >= B2 เสมอ (บวกทุกตัว >= บวกข้ามกลุ่ม)
            check(r["method_b"]["ram_gb"] >= r["method_b2"]["ram_gb"] - 1e-6,
                  f"case {i}: B1 RAM < B2 RAM ซึ่งเป็นไปไม่ได้")
            # storage ต้องโตขึ้นตามเวลา
            lt = r["storage"]["long_term"]
            for a, bb in zip(lt, lt[1:]):
                check(bb["data_gb"] >= a["data_gb"] - 1e-6,
                      f"case {i}: storage ลดลงเมื่อเวลาเพิ่ม ({a['months']}->{bb['months']})")


def test_js_parity():
    print("[4] engine.py กับ assets/engine.js ให้ผลตรงกัน")
    if subprocess.run(["node", "--version"], capture_output=True).returncode != 0:
        print("  [SKIP] ไม่มี node ในเครื่องนี้")
        return
    rnd = random.Random(4242)
    ids = [t["id"] for t in C.TOOLS]
    cases = []
    for p in C.PRESETS:
        for vm in p["vms"]:
            key = f'{p["id"]}/{vm["host"]}'
            cases.append(dict(id=key, tools=vm["tools"], horizon=36, mode="strict",
                              scale=1.0, retention=None, profile=p["profile"], impact="high",
                              frameworks=None, block=None, ext=[]))
            cases.append(dict(id=key + "/realistic", tools=vm["tools"], horizon=60,
                              mode="realistic", scale=3.5, retention=90,
                              profile=p["profile"], impact="high",
                              frameworks=E.resolve_frameworks(p["profile"]),
                              block=["strong-copyleft", "network-copyleft"], ext=["waf"]))
    for i in range(40):
        sel = rnd.sample(ids, rnd.randint(1, 14))
        cases.append(dict(id=f"rnd{i}", tools=sel,
                          horizon=rnd.choice([12, 24, 36, 60]),
                          mode=rnd.choice(["strict", "realistic"]),
                          scale=rnd.choice([0.5, 1.0, 2.5, 5.0]),
                          retention=rnd.choice([None, 90, 365]),
                          profile=rnd.choice([p["id"] for p in C.PROFILES]),
                          impact=rnd.choice(["low", "medium", "high"]),
                          executors={sel[0]: rnd.randint(1, 4)},
                          frameworks=rnd.sample([f["id"] for f in C.FRAMEWORKS],
                                                rnd.randint(1, 12)),
                          block=rnd.choice([None, ["strong-copyleft"],
                                            ["strong-copyleft", "network-copyleft"],
                                            ["source-available"]]),
                          ext=rnd.sample(sorted(C.CAPABILITIES), rnd.randint(0, 4))))
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(cases, fh, ensure_ascii=False)
        cpath = fh.name
    proc = subprocess.run(["node", os.path.join(HERE, "verify_engines.mjs"), cpath],
                          capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    if proc.returncode != 0:
        FAIL.append("รัน verify_engines.mjs ไม่สำเร็จ: " + proc.stderr[-2000:])
        print("  [FAIL] node error:\n" + proc.stderr[-2000:])
        return
    js = {x["id"]: x for x in json.loads(proc.stdout)}

    def near(a, b, tol=1e-6):
        if isinstance(a, list) and isinstance(b, list):
            return len(a) == len(b) and all(near(x, y, tol) for x, y in zip(a, b))
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return abs(a - b) <= tol * max(1.0, abs(a), abs(b))
        return a == b

    for c in cases:
        r = E.colocate(c["tools"], horizon_months=c["horizon"], mode=c["mode"],
                       scale_factor=c["scale"], retention_override=c["retention"],
                       executors=c.get("executors") or {})
        comp = E.compliance_check(c["tools"], c["profile"], c["impact"],
                                  c.get("frameworks"), c.get("block"), c.get("ext"))
        j = js.get(c["id"])
        check(j is not None, f"{c['id']}: JS ไม่คืนผล")
        if not j:
            continue
        check(near([r["method_a"]["vcpu"], r["method_a"]["ram_gb"]], j["a"]), f"{c['id']}: A ไม่ตรง {j['a']}")
        check(near([r["method_b"]["vcpu"], r["method_b"]["ram_gb"]], j["b1"]), f"{c['id']}: B1 ไม่ตรง {j['b1']}")
        check(near([r["method_b2"]["vcpu"], r["method_b2"]["ram_gb"]], j["b2"]), f"{c['id']}: B2 ไม่ตรง {j['b2']}")
        check(near([r["method_c"]["vcpu"], r["method_c"]["ram_gb"]], j["c"]), f"{c['id']}: C ไม่ตรง {j['c']}")
        check([r["governing"]["vcpu"], r["governing"]["ram"]] == j["governing"],
              f"{c['id']}: governing ไม่ตรง {j['governing']}")
        check(near([r["required"]["vcpu"], r["required"]["ram_gb"],
                    r["required"]["disk_os_gb"], r["required"]["disk_data_gb"]], j["required"], 1e-4),
              f"{c['id']}: required ไม่ตรง {j['required']}")
        check([r["allocated"]["vcpu"], r["allocated"]["ram_gb"],
               r["allocated"]["disk_os_gb"], r["allocated"]["disk_data_gb"]] == j["allocated"],
              f"{c['id']}: allocated ไม่ตรง {j['allocated']}")
        check(near([r["storage"]["install_gb"], r["storage"]["data_gb"]], j["storage"], 1e-4),
              f"{c['id']}: storage ไม่ตรง {j['storage']}")
        check(near([[x["months"], x["data_gb"], x["provisioned_gb"]] for x in r["storage"]["long_term"]],
                   j["long_term"], 1e-4), f"{c['id']}: long_term ไม่ตรง")
        check(near([comp["score"], comp["passed"], comp["total_rules"], comp["failed_count"]],
                   j["compliance"][:4]), f"{c['id']}: compliance ตัวเลขไม่ตรง {j['compliance'][:4]}")
        check(sorted(comp["gaps"]) == j["compliance"][4], f"{c['id']}: gaps ไม่ตรง")
        check(sorted(comp["by_framework"]) == sorted(j["compliance"][7]),
              f"{c['id']}: รายชื่อมาตรฐานใน by_framework ไม่ตรง")
        check({k: [v["passed"], v["total"]] for k, v in comp["by_framework"].items()} ==
              j["compliance"][8], f"{c['id']}: คะแนนแยกตามมาตรฐานไม่ตรง")
        check([x["tool_id"] for x in comp["recommendations"]] == j["compliance"][5],
              f"{c['id']}: recommendations ไม่ตรง")
        check(comp["uncovered_caps"] == j["compliance"][6], f"{c['id']}: uncovered_caps ไม่ตรง")
    os.unlink(cpath)


def test_catalog_json_fresh():
    print("[5] data/catalog.json ตรงกับ catalog_data.py")
    path = os.path.join(ROOT, "data", "catalog.json")
    check(os.path.exists(path), "ไม่พบ data/catalog.json — รัน scripts/build_catalog.py")
    if not os.path.exists(path):
        return
    on_disk = json.load(open(path, encoding="utf-8"))
    fresh = json.loads(json.dumps(build_catalog.build(), ensure_ascii=False))
    check(on_disk == fresh,
          "data/catalog.json ไม่ตรงกับ source — รัน `python3 scripts/build_catalog.py` แล้ว commit ใหม่")


PROJECT_PAT = None


def test_no_project_specific_content():
    """ต้องไม่มีข้อมูลเฉพาะโครงการฝังอยู่ในข้อมูลกลาง — ไฟล์นี้ต้องใช้กับโครงการใดก็ได้"""
    import re as _re
    print("[6] ไม่มีเนื้อหาผูกกับโครงการเฉพาะ")
    pat = _re.compile(r"MOC-?HS|OPDC-?KPI|OPS-HS-|\b172\.(?:16|24)\.\d+\.\d+", _re.I)
    for t in C.TOOLS:
        for k in ("name", "note_th", "sizing_ref", "category"):
            check(not pat.search(t[k]), f"{t['id']}.{k} มีเนื้อหาผูกโครงการเฉพาะ")
    for a in C.ARCHETYPES:
        check(not pat.search(a["name_th"] + a["network_th"]),
              f"archetype {a['id']} มีเนื้อหาผูกโครงการเฉพาะ")
        for vm in a["vms"]:
            check(not pat.search(vm["host"] + vm["role_th"]),
                  f"archetype {a['id']}/{vm['host']} มีเนื้อหาผูกโครงการเฉพาะ")
            check(not vm["spec"]["vcpu"], f"archetype {a['id']}/{vm['host']} ไม่ควรกำหนด spec ล่วงหน้า")


def test_archetypes_reach_compliance():
    """ผังอ้างอิงทุกผังต้องผ่าน compliance ของ profile ตัวเอง 100% เพื่อใช้เป็นจุดตั้งต้นที่เชื่อถือได้"""
    print("[7] ผังอ้างอิงผ่าน compliance ครบ")
    for a in C.ARCHETYPES:
        tools = sorted({t for vm in a["vms"] for t in vm["tools"]})
        r = E.compliance_check(tools, a["profile"])
        check(r["failed_count"] == 0,
              f"archetype {a['id']} ยังไม่ผ่าน {r['failed_count']} ข้อ: "
              f"{[x['control_id'] for x in r['results'] if x['status'] == 'fail']}")
        for vm in a["vms"]:
            c = E.colocate(vm["tools"], horizon_months=36, mode="realistic")
            check(c["allocated"]["vcpu"] <= 64 and c["allocated"]["ram_gb"] <= 128,
                  f"archetype {a['id']}/{vm['host']} ต้องการทรัพยากรสูงเกินจริง "
                  f"({c['allocated']['vcpu']}c/{c['allocated']['ram_gb']}G) — ควรกระจายเครื่องมือเพิ่ม")


def test_tool_compliance_mapping():
    """ทุกเครื่องมือต้องมีการจับคู่ compliance และต้องแยกไทย/สากลได้"""
    print("[8] การจับคู่ compliance ต่อเครื่องมือ")
    tools = build_catalog.enrich_tools()
    fw = C.FRAMEWORK_BY_ID
    for t in tools:
        cm = t.get("compliance")
        check(cm is not None, f"{t['id']} ไม่มีข้อมูล compliance")
        if not cm:
            continue
        check(cm["control_count"] == len(cm["controls_full"]) + len(cm["controls_partial"]),
              f"{t['id']} control_count ไม่ตรงกับจำนวนมาตรการ")
        check(not (set(cm["controls_full"]) & set(cm["controls_partial"])),
              f"{t['id']} มีมาตรการซ้ำทั้งใน full และ partial")
        for x in cm["frameworks_th"]:
            check(fw[x]["region"] == "th", f"{t['id']} จัด {x} เป็นมาตรฐานไทยผิด")
        for x in cm["frameworks_intl"]:
            check(fw[x]["region"] == "intl", f"{t['id']} จัด {x} เป็นมาตรฐานสากลผิด")
        caps = set(t["capabilities"])
        for cid in cm["controls_full"]:
            check(set(C.CONTROL_BY_ID[cid]["caps"]) <= caps,
                  f"{t['id']} อ้าง {cid} เป็น full แต่ caps ไม่ครบ")
    covered = {x for t in tools
               for x in t["compliance"]["controls_full"] + t["compliance"]["controls_partial"]}
    missing = {r["id"] for r in C.CONTROLS} - covered
    check(not missing, f"มาตรการที่ไม่มีเครื่องมือใดรองรับเลย: {sorted(missing)}")


def test_frameworks_granular():
    """ทะเบียนมาตรฐานรายฉบับต้องสมบูรณ์และแยกไทย/สากลได้ถูกต้อง"""
    print("[8.1] ทะเบียนมาตรฐานรายฉบับ")
    ids = [f["id"] for f in C.FRAMEWORKS]
    check(len(ids) == len(set(ids)), "framework id ซ้ำกัน")
    for f in C.FRAMEWORKS:
        for k in ("name_th", "short_th", "authority", "scope_th", "family"):
            check(bool(f.get(k)), f"{f['id']} ขาดข้อมูล {k}")
        check(f["region"] in ("th", "intl"), f"{f['id']} region ไม่ถูกต้อง")
        check(len(f["controls"]) >= 1, f"{f['id']} ไม่ผูกกับมาตรการใดเลย")
        for cid, ref in f["controls"].items():
            check(cid in C.CONTROL_BY_ID, f"{f['id']} อ้างมาตรการที่ไม่มี: {cid}")
            if isinstance(ref, dict):
                check("clause" in ref, f"{f['id']}/{cid} dict ต้องมี clause")
                check(ref.get("severity", "mandatory") in
                      ("mandatory", "conditional", "recommended"),
                      f"{f['id']}/{cid} severity ไม่ถูกต้อง")
            else:
                check(isinstance(ref, str) and ref, f"{f['id']}/{cid} clause ต้องเป็นข้อความ")
    nth = sum(1 for f in C.FRAMEWORKS if f["region"] == "th")
    check(nth >= 10, f"มาตรฐานไทยน้อยเกินไป ({nth} ฉบับ)")
    check(len(C.FRAMEWORKS) - nth >= 20, "มาตรฐานสากลน้อยเกินไป")
    # ระดับบังคับที่ลดลงเฉพาะฉบับต้องทำงาน
    check(C.control_severity("C-APP-WAF", {"TH-DGA-MSPR11-2566"}) == "recommended",
          "การลดระดับบังคับเฉพาะฉบับ (มสพร. 11-2566 / WAF) ไม่ทำงาน")
    check(C.control_severity("C-APP-WAF", {"TH-NCSA-WEB-2568"}) == "mandatory",
          "มาตรฐานเว็บไซต์ 2568 ต้องบังคับ WAF")


def test_license_classes():
    """การจำแนกลิขสิทธิ์ต้องไม่สับสน LGPL กับ GPL"""
    print("[8.2] การจำแนกชั้นลิขสิทธิ์")
    cases = {
        "MIT": "permissive", "Apache-2.0": "permissive", "BSD": "permissive",
        "PostgreSQL License": "permissive",
        "LGPL-3.0": "weak-copyleft", "LGPL-2.1": "weak-copyleft",
        "MPL-2.0": "weak-copyleft",
        "GPL-2.0": "strong-copyleft", "GPL-3.0 / Apache-2.0": "strong-copyleft",
        "AGPL-3.0": "network-copyleft",
        "EPL-1.0": "weak-copyleft",
        "SSPL / Elastic License": "source-available", "BUSL-1.1 / MPL-2.0": "source-available",
        "RSALv2 / SSPL": "source-available", "N/A": "n/a",
    }
    for lic, want in cases.items():
        got = C.classify_license(lic)
        check(got == want, f"classify_license('{lic}') = {got} ควรเป็น {want}")
    for t in C.TOOLS:
        check(t["license_class"] in C.LICENSE_CLASSES,
              f"{t['id']} license_class ไม่รู้จัก: {t['license_class']}")


def test_every_preset_reaches_full_coverage():
    """ทุกชุดมาตรฐานสำเร็จ x ทุกนโยบายลิขสิทธิ์ ต้องหาเครื่องมือครอบคลุมได้ 100%"""
    print("[8.3] ชุดมาตรฐานสำเร็จหาเครื่องมือครบทุกกรณี")
    prof_for = {"gov": "gov", "enterprise": "enterprise", "internal": "internal",
                "startup": "startup", "aiml": "aiml", "cloud": "enterprise",
                "payment": "enterprise", "supplychain": "enterprise"}
    blocks = [None, ["strong-copyleft", "network-copyleft"],
              ["strong-copyleft", "network-copyleft", "source-available"]]
    for pk, pid in prof_for.items():
        for blk in blocks:
            r = E.required_tools(C.FRAMEWORK_PRESETS[pk], pid, "high", license_blocklist=blk)
            check(r["compliance"]["score"] == 100.0,
                  f"ชุด {pk} + ห้าม {blk} ได้เพียง {r['compliance']['score']}% "
                  f"(ขาด {r['uncovered_caps']})")
            for tid in r["tools"]:
                cls = E.TOOL_BY_ID[tid]["license_class"]
                check(not blk or cls not in blk,
                      f"ชุด {pk}: แนะนำ {tid} ({cls}) ที่ขัดนโยบาย {blk}")


def test_standalone_bundle():
    """ไฟล์ HTML แบบไฟล์เดียวต้อง bundle ได้และไม่มีสิ่งที่ทำให้ module พัง"""
    print("[8.4] ไฟล์ HTML แบบ standalone")
    import importlib
    bs = importlib.import_module("build_standalone")
    out = os.path.join(ROOT, "dist", "_verify_standalone.html")
    argv = sys.argv
    sys.argv = ["build_standalone.py", out]
    try:
        bs.main()
    except SystemExit as e:
        check(not e.code, f"build_standalone ออกด้วย exit code {e.code}")
    finally:
        sys.argv = argv
    check(os.path.exists(out), "สร้างไฟล์ standalone ไม่สำเร็จ")
    if not os.path.exists(out):
        return
    html = open(out, encoding="utf-8").read()
    i = html.find('<script id="cicd-app">')
    j = html.find("</script>", i)
    check(i > 0 and j > i, "ไม่พบ app script ในไฟล์ standalone")
    body = html[i:j]
    check('id="cicd-catalog"' in html, "ไม่ได้ฝัง catalog script")
    check("window.__STANDALONE__" in html, "ไม่ได้ตั้ง __STANDALONE__")
    # ห้ามมี HTML comment ในสคริปต์ — ทำให้เบราว์เซอร์ตัดสคริปต์กลางทาง
    # ลูกศร mermaid " --> " ในสตริงใช้ได้ จึงไม่บล็อกลำพัง
    check("<!--" not in body, "มี HTML comment อยู่ในสคริปต์ — หน้าจะพังทันที")
    import re as _re
    check(not _re.search(r"^\s*import\s+[\w{*]", body, _re.M),
          "ยังมี import statement หลงเหลือใน bundle")
    check(not _re.search(r"^\s*export\s+", body, _re.M),
          "ยังมี export statement หลงเหลือใน bundle")
    check("window.__CATALOG__" in html, "ไม่ได้ฝัง catalog ลงในไฟล์")
    check("panel-architecture" in html and "panel-pipeline" in html,
          "standalone ไม่มีหน้าสถาปัตยกรรม / Pipeline YAML")
    check("function buildPipelineIR" in html, "ไม่ได้ bundle pipeline.js")
    bad = [u for u in __import__("re").findall(r'(?:src|href)="([^"]+)"', html)
           if u.startswith(("http://", "https://", "//"))]
    check(not bad, f"ไฟล์ standalone ยังอ้างอิงภายนอก: {bad}")
    # catalog ที่ฝังต้องเป็น JSON ใช้ได้ — นี่คือจุดที่หน้าเคยพังรอบที่แล้ว
    m = _re.search(r"window\.__CATALOG__=(.+?);</script>", html)
    check(bool(m), "ไม่พบ window.__CATALOG__=... ใน standalone")
    if m:
        try:
            cat = json.loads(m.group(1))
            check(isinstance(cat.get("tools"), list) and len(cat["tools"]) >= 70,
                  f"catalog ที่ฝังมีเครื่องมือ {len(cat.get('tools') or [])} รายการ")
            check(cat.get("schema_version") == C.SCHEMA_VERSION,
                  f"schema ที่ฝัง {cat.get('schema_version')} != {C.SCHEMA_VERSION}")
            check(cat.get("model", {}).get("w_base") == 0.20, "catalog ที่ฝังยังเป็น w_base เก่า")
        except Exception as exc:
            check(False, "parse catalog ที่ฝังไม่สำเร็จ: " + str(exc)[:200])
    os.unlink(out)


def test_compliance_sanity():
    print("[9] compliance sanity")
    # ชุดเครื่องมือว่าง -> ต้องไม่ผ่านข้อบังคับ และต้องมีข้อเสนอแนะ
    r = E.compliance_check([], "gov", "high")
    check(r["failed_count"] > 0, "ชุดเครื่องมือว่างแต่ compliance ไม่ fail")
    check(len(r["recommendations"]) > 0, "ชุดเครื่องมือว่างแต่ไม่มีข้อเสนอแนะเครื่องมือ")
    # ใส่ทุกเครื่องมือของ profile gov -> ควรผ่านเกือบทั้งหมด
    all_gov = [t["id"] for t in C.TOOLS if "gov" in t["profiles"]]
    r2 = E.compliance_check(all_gov, "gov", "high")
    check(r2["failed_count"] == 0,
          f"ติดตั้งทุกเครื่องมือของ profile gov แล้วยังไม่ผ่าน {r2['failed_count']} ข้อ: "
          f"{[x['control_id'] for x in r2['results'] if x['status'] == 'fail']}")
    check(not r2["uncovered_caps"],
          f"capability ที่ไม่มีเครื่องมือ gov รองรับ: {r2['uncovered_caps']}")
    # recommendations ต้องไม่แนะนำเครื่องมือที่มีอยู่แล้ว
    some = all_gov[:6]
    r3 = E.compliance_check(some, "gov", "high")
    check(not (set(x["tool_id"] for x in r3["recommendations"]) & set(some)),
          "แนะนำเครื่องมือที่ติดตั้งอยู่แล้ว")


def test_pipeline_parity():
    print("[10] PipelineIR / YAML / mermaid ตรงกันระหว่าง Python กับ JS")
    if subprocess.run(["node", "--version"], capture_output=True).returncode != 0:
        print("  [SKIP] ไม่มี node ในเครื่องนี้")
        return
    fixtures = [
        dict(id="gov-core", tools=["gitea", "jenkins-master", "gitleaks", "semgrep",
                                   "trivy", "docker-buildkit", "syft", "cosign",
                                   "owasp-zap", "harbor", "nexus-repository", "argocd"],
             profile="gov", disabled=[], vms=[]),
        dict(id="ent-gh", tools=["github-actions", "gitleaks", "trivy", "unit-test-runner"],
             profile="enterprise", disabled=["secret-scan"], vms=[]),
        dict(id="empty", tools=[], profile="internal", disabled=[], vms=[]),
        dict(id="helm-k3s", tools=["helm", "k3s-control", "kustomize"],
             profile="gov", disabled=[],
             vms=[{"name": "DEPLOY-01", "role": "deploy",
                   "tools": ["k3s-control", "helm", "kustomize"]}]),
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(fixtures, fh, ensure_ascii=False)
        cpath = fh.name
    proc = subprocess.run(["node", os.path.join(HERE, "verify_pipeline.mjs"), cpath],
                          capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    if proc.returncode != 0:
        FAIL.append("รัน verify_pipeline.mjs ไม่สำเร็จ: " + (proc.stderr or proc.stdout)[-2000:])
        print("  [FAIL] node error:\n" + (proc.stderr or proc.stdout)[-2000:])
        os.unlink(cpath)
        return
    js = {x["id"]: x for x in json.loads(proc.stdout)}
    for fx in fixtures:
        ir = PG.build_pipeline_ir(fx["tools"], vms=fx.get("vms") or [],
                                  profile=fx["profile"], disabled=fx["disabled"])
        files = PG.emit_all(ir)
        pack = PG.build_install_pack(ir)
        j = js.get(fx["id"])
        check(j is not None, f"{fx['id']}: JS ไม่คืนผล")
        if not j:
            continue
        check([x["id"] for x in ir["jobs"]] == j["job_ids"], f"{fx['id']}: ลำดับ job ไม่ตรง")
        check([x["enabled"] for x in ir["jobs"]] == j["enabled"], f"{fx['id']}: enabled ไม่ตรง")
        check(files["gitlab"] == j["gitlab"], f"{fx['id']}: GitLab YAML ไม่ตรง")
        check(files["github"] == j["github"], f"{fx['id']}: GitHub YAML ไม่ตรง")
        check(files["mermaid_flow"] == j["mermaid_flow"], f"{fx['id']}: mermaid flow ไม่ตรง")
        check(pack == j["install"], f"{fx['id']}: สคริปต์ติดตั้งไม่ตรง")
        if fx["id"] == "helm-k3s":
            yml = files["gitlab"]
            check("helm upgrade --install" in yml, "helm-k3s ต้องมี helm upgrade")
            check("install/all.sh" in pack, "ต้องมี install/all.sh")
            check(any("k3s" in (pack[k] or "") for k in pack), "สคริปต์เครื่องต้องกล่าวถึง k3s")
        if ir["jobs"]:
            check(any(x["id"] == "deploy-uat" for x in ir["jobs"]),
                  f"{fx['id']}: ต้องมี deploy-uat")
            check(any(x["id"] == "deploy-prod" for x in ir["jobs"]),
                  f"{fx['id']}: ต้องมี deploy-prod")
        job_tools = {x["tool_id"] for x in ir["jobs"] if x["tool_id"]}
        check(job_tools <= set(fx["tools"]),
              f"{fx['id']}: มี tool ใน IR ที่ไม่ได้เลือก: {sorted(job_tools - set(fx['tools']))}")
    os.unlink(cpath)


def main():
    print("=" * 72)
    print("CI/CD Resource Planner — verification suite")
    print("=" * 72)
    test_catalog_invariants()
    test_weight_range()
    test_max_rule()
    test_js_parity()
    test_catalog_json_fresh()
    test_no_project_specific_content()
    test_frameworks_granular()
    test_license_classes()
    test_every_preset_reaches_full_coverage()
    test_standalone_bundle()
    test_archetypes_reach_compliance()
    test_tool_compliance_mapping()
    test_compliance_sanity()
    test_pipeline_parity()
    print("-" * 72)
    print(f"ผ่าน {OKN[0]} assertion · ล้มเหลว {len(FAIL)}")
    if FAIL:
        print("\nรายการที่ล้มเหลว:")
        for f in FAIL[:40]:
            print("  - " + f)
        sys.exit(1)
    print("ผลการตรวจ: ผ่านทั้งหมด")


if __name__ == "__main__":
    main()
