# -*- coding: utf-8 -*-
"""Regenerate shared markdown from Excel + catalog.json. Called by humans / compile."""
from __future__ import annotations

import json
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def cell(v) -> str:
    if v is None:
        return ""
    return str(v).replace("\n", " ").replace("|", "/").strip()


def sheet_to_md(ws, max_cols: int = 8) -> str:
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        vals = [cell(c) for c in row[:max_cols]]
        if not any(vals):
            continue
        rows.append(vals)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    # first non-empty row that looks like a header: use it; else synthesize
    header = rows[0]
    # if first row is a title (mostly empty after col 0), skip to next
    if sum(1 for x in header[1:] if x) <= 1 and len(rows) > 1:
        title = header[0]
        body = rows[1:]
        header = body[0]
        data = body[1:]
        out = [f"**{title}**", ""]
    else:
        data = rows[1:]
        out = []
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join("---" for _ in header) + " |")
    for r in data:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def dump_compliance() -> str:
    wb = openpyxl.load_workbook(
        ROOT / "Compliance_Standards_Register_CICD_v4.xlsx",
        read_only=True, data_only=True,
    )
    parts = [
        "# Compliance Standards Register (v4 — full dump)",
        "",
        "> Compiled from `Compliance_Standards_Register_CICD_v4.xlsx`.",
        "> Cite rule IDs (TH-/TX-/S-/IN-/IX-/CN-/SC-/G-/W-) in every recommendation.",
        "",
    ]
    for ws in wb.worksheets:
        parts.append(f"## {ws.title}")
        parts.append("")
        parts.append(sheet_to_md(ws))
        parts.append("")
    wb.close()
    return "\n".join(parts)


def dump_tools() -> str:
    cat = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    stages = cat.get("stages") or {}
    parts = [
        "# CI/CD Tool Catalog (planner source of truth)",
        "",
        f"> Generated from `data/catalog.json` schema {cat.get('schema_version')} — "
        f"{len(cat['tools'])} tools, {len(cat['frameworks'])} frameworks, "
        f"{len(cat['controls'])} controls, {len(cat['capabilities'])} capabilities.",
        "",
        "## Capabilities",
        "",
        "| id | meaning |",
        "| --- | --- |",
    ]
    for k, v in cat["capabilities"].items():
        parts.append(f"| `{k}` | {v} |")

    parts += ["", "## Tools by stage", ""]
    by = {}
    for t in cat["tools"]:
        by.setdefault(str(t["stage"]), []).append(t)
    for st in sorted(by, key=lambda x: int(x)):
        parts.append(f"### Stage {st}: {stages.get(st, '')}")
        parts.append("")
        parts.append(
            "| id | name | category | grade | license | managed | min vCPU | min RAM | freq | capabilities |"
        )
        parts.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for t in by[st]:
            caps = ", ".join(t.get("capabilities") or [])
            managed = "yes" if t.get("managed") else ""
            parts.append(
                f"| `{t['id']}` | {t['name']} | {t.get('category','')} | {t.get('grade','')} | "
                f"{t.get('license','')} | {managed} | {t['min']['vcpu']} | {t['min']['ram_gb']} | "
                f"{t.get('freq','')} | {caps} |"
            )
        parts.append("")

    parts += [
        "## Profiles",
        "",
        "| id | name | impact | security | notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p in cat["profiles"]:
        parts.append(
            f"| `{p['id']}` | {p.get('name_th','')} | {p.get('impact','')} | "
            f"{p.get('security','')} | {str(p.get('notes_th') or p.get('automate_th') or '')[:160]} |"
        )

    parts += ["", "## Reference architectures", ""]
    for a in cat.get("archetypes") or []:
        parts.append(f"### {a.get('name_th') or a['id']}")
        parts.append("")
        parts.append(a.get("network_th") or "")
        parts.append("")
        for vm in a.get("vms") or []:
            tools = ", ".join(f"`{x}`" for x in vm.get("tools") or [])
            parts.append(f"- **{vm.get('host')}** — {vm.get('role_th')}: {tools}")
        parts.append("")
    return "\n".join(parts)


def main() -> None:
    (OUT / "compliance-register.md").write_text(dump_compliance(), encoding="utf-8", newline="\n")
    (OUT / "tool-catalog.md").write_text(dump_tools(), encoding="utf-8", newline="\n")
    print("dumped compliance-register.md and tool-catalog.md")


if __name__ == "__main__":
    main()
