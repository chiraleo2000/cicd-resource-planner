# -*- coding: utf-8 -*-
"""Compliance Gate — ใช้เป็นด่านใน CI/CD Pipeline

อ่านไฟล์แผน (plan JSON) แล้วตรวจ 2 เรื่องพร้อมกัน
  1. ทรัพยากร  : spec ที่ขอไว้พอกับเครื่องมือที่วางบนเครื่องนั้นหรือไม่
  2. Compliance: ชุดเครื่องมือครอบคลุมข้อกำหนดกฎหมาย/มาตรฐานครบหรือไม่
     ถ้าไม่ครบ จะเสนอเครื่องมือที่ควรเพิ่ม (Automation เลือกเครื่องมือให้ผ่านมาตรฐาน)

รูปแบบไฟล์แผน
-------------
{
  "profile": "gov",           // gov | enterprise | internal | startup | aiml
  "impact": "high",           // low | medium | high
  "mode": "strict",           // strict | realistic
  "horizon_months": 36,
  "scale_factor": 1.0,
  "retention_days": null,     // null = ใช้ค่าของแต่ละเครื่องมือ
  "frameworks": ["TH-CCA-2560", "..."],        // null/ไม่ระบุ = ใช้ชุดสำเร็จของ profile
  "license_blocklist": ["strong-copyleft"],    // ชั้นลิขสิทธิ์ที่ห้ามใช้
  "external_caps": ["iam_mfa", "waf"],         // capability ที่มีระบบส่วนกลางรองรับแล้ว
  "min_score": 100,           // คะแนน compliance ขั้นต่ำที่ยอมรับ (%)
  "allow_resource_gap": false,
  "vms": [
    {"name": "...", "role": "...", "tools": ["jenkins-master", "..."],
     "executors": {"jenkins-agent": 2},
     "spec": {"vcpu": 8, "ram_gb": 16, "disk_os_gb": 60, "disk_data_gb": 500}}
  ]
}

รัน
---
python3 scripts/check_compliance.py plans/mochs-uat.json
python3 scripts/check_compliance.py plans/*.json --summary $GITHUB_STEP_SUMMARY
Exit code 0 = ผ่าน, 1 = ไม่ผ่าน (ทำให้ Pipeline หยุด)
"""
from __future__ import annotations
import argparse, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import engine as E          # noqa: E402
import catalog_data as C    # noqa: E402

SEV_TH = {"mandatory": "บังคับ", "conditional": "บังคับเมื่อผลกระทบสูง", "recommended": "แนะนำ"}


def evaluate(plan: dict) -> dict:
    profile = plan.get("profile", "gov")
    impact = plan.get("impact")
    mode = plan.get("mode", "strict")
    horizon = int(plan.get("horizon_months", 36))
    scale = float(plan.get("scale_factor", 1.0))
    retention = plan.get("retention_days")
    frameworks = plan.get("frameworks")
    lic_block = plan.get("license_blocklist")
    ext_caps = plan.get("external_caps")

    unknown = sorted({t for vm in plan["vms"] for t in vm["tools"]} - set(E.TOOL_BY_ID))
    vms = []
    for vm in plan["vms"]:
        tools = [t for t in vm["tools"] if t in E.TOOL_BY_ID]
        calc = E.colocate(tools, horizon_months=horizon, mode=mode, scale_factor=scale,
                          retention_override=retention, executors=vm.get("executors") or {},
                          extra_install_gb=float(vm.get("extra_install_gb") or 0))
        spec = vm.get("spec") or {}
        gap = None
        verdict = "unknown"
        if spec.get("vcpu"):
            gap = {k: (spec.get(k, 0) or 0) - calc["allocated"][k]
                   for k in ("vcpu", "ram_gb", "disk_os_gb", "disk_data_gb")}
            if gap["vcpu"] < 0 or gap["ram_gb"] < 0:
                verdict = "insufficient"
            elif gap["disk_os_gb"] < 0 or gap["disk_data_gb"] < 0:
                verdict = "disk-risk"
            else:
                verdict = "ok"
        vms.append(dict(name=vm.get("name", "?"), role=vm.get("role", ""), tools=tools,
                        spec=spec, calc=calc, gap=gap, verdict=verdict))

    all_tools = sorted({t for vm in vms for t in vm["tools"]})
    comp = E.compliance_check(all_tools, profile, impact, frameworks, lic_block, ext_caps)
    return dict(profile=profile, impact=comp["impact"], mode=mode, horizon=horizon,
                scale=scale, retention=retention, vms=vms, compliance=comp,
                frameworks=comp["frameworks"], license_blocklist=lic_block or [],
                external_caps=comp["external_caps"], unknown_tools=unknown)


def report(name: str, plan: dict, res: dict) -> tuple[list, list, str]:
    """คืน (ปัญหาที่ทำให้ไม่ผ่าน, ข้อสังเกตที่ยกเว้นไว้, ข้อความ Markdown)"""
    problems, advisories, md = [], [], []
    min_score = float(plan.get("min_score", 100))
    allow_gap = bool(plan.get("allow_resource_gap", False))
    comp = res["compliance"]

    md.append(f"## แผน `{name}`")
    md.append(f"- ประเภทโครงการ: **{E.PROFILE_BY_ID[res['profile']]['name_th']}** "
              f"· ระดับผลกระทบ **{res['impact']}** · โหมด **{res['mode']}** "
              f"· ประเมินที่ **{res['horizon']} เดือน** · Scale **{res['scale']}×**")
    md.append(f"- คะแนน Compliance: **{comp['score']}%** "
              f"(ผ่าน {comp['passed']}/{comp['total_rules']} มาตรการ · ไม่ผ่าน {comp['failed_count']}) "
              f"· เกณฑ์ขั้นต่ำ {min_score}%")
    md.append(f"- มาตรฐานที่ตรวจ **{len(res['frameworks'])} ฉบับ**: " +
              ", ".join(C.FRAMEWORK_BY_ID[f]["short_th"] for f in res["frameworks"]))
    if res["license_blocklist"]:
        md.append("- นโยบายลิขสิทธิ์ที่ห้ามใช้: " + ", ".join(res["license_blocklist"]))
    if res["external_caps"]:
        md.append("- capability ที่ถือว่าระบบส่วนกลางรองรับแล้ว: " + ", ".join(res["external_caps"]))
    verify = comp.get("verify_needed") or []
    if verify:
        md.append("- ⚠ ควรตรวจเลขที่ประกาศ/ปีกับแหล่งทางการก่อนอ้างใน TOR: " +
                  ", ".join(C.FRAMEWORK_BY_ID[f]["short_th"] for f in verify))
    md.append("")

    if res["unknown_tools"]:
        problems.append(f"[{name}] อ้างเครื่องมือที่ไม่มีในตาราง: {res['unknown_tools']}")
        md.append(f"> เครื่องมือที่ไม่รู้จัก: `{'`, `'.join(res['unknown_tools'])}`")

    # ---- ตารางทรัพยากร ----
    md.append("### ทรัพยากรต่อเครื่อง")
    md.append("| VM | เครื่องมือ | A | B1 | B2 | C | ต้องจัดสรร | spec ที่ขอ | ผล |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for v in res["vms"]:
        c = v["calc"]
        a = f"{c['method_a']['vcpu']:.0f}c/{c['method_a']['ram_gb']:.0f}G"
        b1 = f"{c['method_b']['vcpu']:.1f}c/{c['method_b']['ram_gb']:.1f}G"
        b2 = f"{c['method_b2']['vcpu']:.1f}c/{c['method_b2']['ram_gb']:.1f}G"
        cc = f"{c['method_c']['ram_gb']:.1f}G"
        al = (f"{c['allocated']['vcpu']}c / {c['allocated']['ram_gb']}G / "
              f"{c['allocated']['disk_os_gb']}+{c['allocated']['disk_data_gb']}GB")
        sp = v["spec"]
        spt = (f"{sp.get('vcpu', '-')}c / {sp.get('ram_gb', '-')}G / "
               f"{sp.get('disk_os_gb', '-')}+{sp.get('disk_data_gb', '-')}GB") if sp else "–"
        mark = {"ok": "OK", "disk-risk": "DISK", "insufficient": "FAIL", "unknown": "–"}[v["verdict"]]
        md.append(f"| `{v['name']}` | {len(v['tools'])} | {a} | {b1} | {b2} | {cc} | "
                  f"**{al}** | {spt} | {mark} |")
        if v["verdict"] in ("insufficient", "disk-risk"):
            short = []
            if v["gap"]["vcpu"] < 0: short.append(f"{-v['gap']['vcpu']} vCPU")
            if v["gap"]["ram_gb"] < 0: short.append(f"{-v['gap']['ram_gb']} GB RAM")
            if v["gap"]["disk_os_gb"] < 0: short.append(f"{-v['gap']['disk_os_gb']} GB Disk OS")
            if v["gap"]["disk_data_gb"] < 0: short.append(f"{-v['gap']['disk_data_gb']} GB Disk Data")
            msg = f"[{name}] {v['name']}: ทรัพยากรไม่พอ ขาด {', '.join(short)}"
            (advisories if allow_gap else problems).append(msg)
    md.append("")

    # ---- compliance ----
    if comp["score"] < min_score - 1e-9:
        problems.append(f"[{name}] คะแนน Compliance {comp['score']}% ต่ำกว่าเกณฑ์ {min_score}%")
    elif comp["failed_count"]:
        advisories.append(f"[{name}] ยังมีข้อกำหนดที่ไม่ผ่าน {comp['failed_count']} ข้อ "
                          f"แต่เกณฑ์ที่ตั้งไว้ ({min_score}%) ยอมให้ผ่าน")
    # ---- คะแนนแยกตามมาตรฐานรายฉบับ ----
    fwrows = sorted(comp["by_framework"].values(), key=lambda x: (x["score"], x["short_th"]))
    if fwrows:
        md.append("### คะแนนแยกตามมาตรฐานรายฉบับ")
        md.append("| มาตรฐาน | ขอบเขต | ผ่าน | คะแนน | มาตรการที่ยังไม่ผ่าน |")
        md.append("|---|---|---|---|---|")
        for f in fwrows:
            md.append(f"| {f['short_th']}{' ⚠' if f['verify'] else ''} | "
                      f"{'ไทย' if f['region'] == 'th' else 'สากล'} | {f['passed']}/{f['total']} | "
                      f"**{f['score']}%** | {', '.join(f['failed']) or '–'} |")
        md.append("")

    fails = [r for r in comp["results"] if r["status"] == "fail"]
    if fails:
        md.append("### มาตรการที่ไม่ผ่าน")
        md.append("| control | กลุ่ม | ระดับ | Capability ที่ขาด | มาตรการ | อ้างจากมาตรฐาน |")
        md.append("|---|---|---|---|---|---|")
        for r in fails:
            refs = ", ".join(f'{C.FRAMEWORK_BY_ID[f]["short_th"]} {cl}'
                             for f, cl in r["refs"].items())
            md.append(f"| `{r['control_id']}` | {r['group_th']} | {SEV_TH[r['severity']]} | "
                      f"`{'`, `'.join(r['missing'])}` | {r['title_th']} | {refs} |")
        md.append("")
    if comp["recommendations"]:
        md.append("### เครื่องมือที่ควรเพิ่ม (เลือกอัตโนมัติด้วย greedy set-cover)")
        md.append("| เครื่องมือ | Stage | ปิด capability | มาตรการที่ปิดได้ | มาตรฐานที่เกี่ยว "
                  "| +vCPU | +RAM | +Disk | License (ชั้น) |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for r in comp["recommendations"]:
            md.append(f"| **{r['name']}** | {r['stage']} | `{'`, `'.join(r['closes'])}` | "
                      f"{', '.join(r['controls'])} | "
                      f"{', '.join(C.FRAMEWORK_BY_ID[f]['short_th'] for f in r['frameworks'])} | "
                      f"{r['add_vcpu']} | {r['add_ram_gb']} | {r['add_disk_gb']} | "
                      f"{r.get('license', '-')} ({r.get('license_class', '-')}) |")
        md.append("")
    if comp["uncovered_caps"]:
        problems.append(f"[{name}] ไม่มีเครื่องมือที่ใช้ได้ภายใต้เงื่อนไขนี้ "
                        f"(profile + นโยบายลิขสิทธิ์) สำหรับ capability: {comp['uncovered_caps']}")

    # ---- storage ----
    md.append("### พื้นที่จัดเก็บระยะยาว (GB ที่ต้องจัดสรร)")
    md.append("| VM | " + " | ".join(f"@{h} ด." for h in C.MODEL["horizons"]) + " | spec Data ที่ขอ |")
    md.append("|---|" + "---|" * (len(C.MODEL["horizons"]) + 1))
    for v in res["vms"]:
        cells = " | ".join(str(x["provisioned_gb"]) for x in v["calc"]["storage"]["long_term"])
        md.append(f"| `{v['name']}` | {cells} | {v['spec'].get('disk_data_gb', '–')} |")
    md.append("")
    return problems, advisories, "\n".join(md)


def main():
    ap = argparse.ArgumentParser(description="Compliance & Resource Gate สำหรับ CI/CD")
    ap.add_argument("plans", nargs="+", help="ไฟล์แผน JSON (รับ glob ได้)")
    ap.add_argument("--summary", help="ไฟล์ที่จะเขียนรายงาน Markdown (เช่น $GITHUB_STEP_SUMMARY)")
    ap.add_argument("--json-out", help="ไฟล์ที่จะเขียนผลลัพธ์แบบ JSON")
    ap.add_argument("--warn-only", action="store_true", help="รายงานแต่ไม่ทำให้ exit code ผิดพลาด")
    args = ap.parse_args()

    paths = []
    for pat in args.plans:
        paths += sorted(glob.glob(pat)) or [pat]

    all_problems, all_advisories, mds, results = [], [], [], {}
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            plan = json.load(fh)
        res = evaluate(plan)
        name = plan.get("name") or os.path.basename(path)
        probs, advs, md = report(name, plan, res)
        all_problems += probs
        all_advisories += advs
        mds.append(md)
        results[name] = dict(
            profile=res["profile"], impact=res["impact"], mode=res["mode"],
            frameworks=res["frameworks"],
            compliance_score=res["compliance"]["score"],
            by_framework={k: dict(passed=v["passed"], total=v["total"], score=v["score"],
                                  failed=v["failed"])
                          for k, v in res["compliance"]["by_framework"].items()},
            failed_controls=[r["control_id"] for r in res["compliance"]["results"]
                             if r["status"] == "fail"],
            recommendations=[r["tool_id"] for r in res["compliance"]["recommendations"]],
            vms={v["name"]: dict(verdict=v["verdict"], allocated=v["calc"]["allocated"],
                                 spec=v["spec"], gap=v["gap"]) for v in res["vms"]},
            problems=probs, advisories=advs,
        )

    head = ["# รายงาน Compliance & Resource Gate", ""]
    if all_problems:
        head.append(f"**ผลรวม: ไม่ผ่าน — พบ {len(all_problems)} ประเด็นที่ต้องแก้**")
        head.append("")
        head += [f"{i+1}. {p}" for i, p in enumerate(all_problems)]
        head.append("")
    else:
        head.append("**ผลรวม: ผ่านเกณฑ์ที่ตั้งไว้**")
        head.append("")
    if all_advisories:
        head.append(f"ข้อสังเกตที่ถูกยกเว้นตามเกณฑ์ในไฟล์แผน ({len(all_advisories)} รายการ) "
                    "— ยังควรแก้ไขแม้ Pipeline จะผ่าน:")
        head.append("")
        head += [f"- {a}" for a in all_advisories]
    head.append("")
    text = "\n".join(head + mds)

    print(text)
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=2)

    if all_problems and not args.warn_only:
        sys.exit(1)


if __name__ == "__main__":
    main()
