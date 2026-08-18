# -*- coding: utf-8 -*-
"""สร้าง data/catalog.json จาก catalog_data.py (Single Source of Truth)

รันคำสั่ง:  python3 scripts/build_catalog.py
GitHub Actions จะรันไฟล์นี้แล้วตรวจว่า catalog.json ที่ commit ไว้ตรงกับ source หรือไม่
"""
from __future__ import annotations
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import catalog_data as C  # noqa: E402
import engine as E        # noqa: E402


def enrich_tools() -> list:
    """เพิ่มข้อมูล compliance ให้เครื่องมือแต่ละตัว

    controls_full    = มาตรการที่เครื่องมือนี้ตอบได้ครบด้วยตัวเอง
    controls_partial = มาตรการที่ช่วยตอบได้บางส่วน (ต้องมีเครื่องมืออื่นประกอบ)
    frameworks_th / frameworks_intl = มาตรฐานรายฉบับที่อ้างมาตรการเหล่านั้น แยกไทย / สากล
    """
    out = []
    for t in C.TOOLS:
        caps = set(t["capabilities"])
        full, partial, fws = [], [], {}
        for ctl in C.CONTROLS:
            need = set(ctl["caps"])
            if not (need & caps):
                continue
            (full if need <= caps else partial).append(ctl["id"])
            for fid, clause in C.framework_refs(ctl["id"]).items():
                fws.setdefault(fid, []).append(ctl["id"])
        th = sorted(f for f in fws if C.FRAMEWORK_BY_ID[f]["region"] == "th")
        intl = sorted(f for f in fws if C.FRAMEWORK_BY_ID[f]["region"] == "intl")
        t = dict(t)
        t["compliance"] = dict(
            controls_full=sorted(full), controls_partial=sorted(partial),
            frameworks_th=th, frameworks_intl=intl,
            frameworks_th_text="; ".join(C.FRAMEWORK_BY_ID[f]["short_th"] for f in th),
            frameworks_intl_text="; ".join(C.FRAMEWORK_BY_ID[f]["short_th"] for f in intl),
            framework_controls={k: sorted(set(v)) for k, v in sorted(fws.items())},
            control_count=len(full) + len(partial),
            framework_count=len(fws),
        )
        out.append(t)
    return out


def build() -> dict:
    return {
        "schema_version": C.SCHEMA_VERSION,
        "generated_for": C.GENERATED_FOR,
        "storage_baseline_th": C.STORAGE_BASELINE_TH,
        "model": C.MODEL,
        "freq_classes": [dict(f, weight=E.duty_weight(f["id"])) for f in C.FREQ_CLASSES],
        "capabilities": C.CAPABILITIES,
        "license_classes": C.LICENSE_CLASSES,
        "control_groups": C.CONTROL_GROUPS,
        "controls": [dict(c, framework_refs=C.framework_refs(c["id"])) for c in C.CONTROLS],
        "framework_families": C.FRAMEWORK_FAMILIES,
        "frameworks": C.FRAMEWORKS,
        "framework_presets": C.FRAMEWORK_PRESETS,
        "framework_preset_labels": C.PRESET_LABELS,
        "profiles": C.PROFILES,
        "tools": enrich_tools(),
        "archetypes": C.ARCHETYPES,
        "bundles": C.BUNDLES,
        "presets": C.ARCHETYPES,
        "stages": {
            "1": "Source Code (รับโค้ดและควบคุม)",
            "2": "Check & Scan Programme (ตรวจสอบความปลอดภัยและคุณภาพ)",
            "3": "Build & Run (สร้างและยืนยันความถูกต้อง)",
            "4": "Test Running (ทดสอบระบบรอบด้าน)",
            "5": "Store & Versioning (จัดเก็บและจัดการเวอร์ชัน)",
            "6": "Deploy & Update (ขึ้นระบบและดูแลรักษา)",
        },
        "fit_labels": C.FIT_LABELS,
        "regions": {"th": "กฎหมายและมาตรฐานภายในประเทศไทย", "intl": "มาตรฐานสากล"},
        "severity_th": {"mandatory": "บังคับ", "conditional": "บังคับเมื่อผลกระทบสูง",
                        "recommended": "แนะนำ"},
        "conc_groups": {
            "resident": "รันค้างตลอด — บวกทุกตัว",
            "ci_seq": "ขั้นตอนใน Pipeline รอบเดียวกัน — ใช้ค่าสูงสุดของกลุ่ม",
            "async": "งานหลังบ้าน nightly/weekly — ใช้ค่าสูงสุดของกลุ่ม",
            "load": "งานทดสอบภาระ/ประมวลผลหนัก — ใช้ค่าสูงสุดของกลุ่ม",
        },
    }


def main():
    data = build()
    out = os.path.join(ROOT, "data", "catalog.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    txt = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(txt)
    digest = hashlib.sha256(txt.encode("utf-8")).hexdigest()[:16]
    print(f"[ok] {out}")
    print(f"     tools={len(data['tools'])} frameworks={len(data['frameworks'])} "
          f"controls={len(data['controls'])} capabilities={len(data['capabilities'])} "
          f"archetypes={len(data['archetypes'])} sha256={digest}")


if __name__ == "__main__":
    main()
