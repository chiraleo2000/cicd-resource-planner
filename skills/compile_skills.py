# -*- coding: utf-8 -*-
"""Compile shared DevSecOps knowledge into each AI-tool skill pack.

Single source of truth:
  skills/_shared/*.md          — domain knowledge (compliance, tools, method, docs)
  skills/_shared/platforms/*.md — per-tool wrappers (role, output format, setup)

Run:  python skills/compile_skills.py
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = Path(__file__).resolve().parent / "_shared"
PLAT = SHARED / "platforms"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8").strip() + "\n"


def assemble(parts: list[Path]) -> str:
    return "\n\n".join(read(p).rstrip() for p in parts) + "\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"[ok] {path.relative_to(ROOT)}  ({len(text):,} chars)")


def main() -> None:
    core = [
        SHARED / "methodology.md",
        SHARED / "pipeline-design.md",
        SHARED / "compliance-register.md",
        SHARED / "tool-catalog.md",
        SHARED / "documents.md",
    ]
    for p in core + list(PLAT.glob("*.md")):
        if not p.exists():
            raise SystemExit(f"missing {p}")

    # Claude
    write(ROOT / "skills/claude/SKILL.md", assemble([
        PLAT / "claude.md", *core, PLAT / "claude-footer.md",
    ]))

    # ChatGPT Custom GPT
    write(ROOT / "skills/chatgpt/knowledge-files/instructions.md", assemble([
        PLAT / "chatgpt.md", *core, PLAT / "chatgpt-footer.md",
    ]))

    # Gemini / NotebookLM
    write(ROOT / "skills/gemini/SKILL.md", assemble([
        PLAT / "gemini.md", *core, PLAT / "gemini-footer.md",
    ]))

    # Cursor (legacy .cursorrules + modern project skill)
    cursor_body = assemble([PLAT / "cursor.md", *core, PLAT / "cursor-footer.md"])
    write(ROOT / "skills/cursor/.cursorrules", cursor_body)
    write(
        ROOT / ".cursorrules",
        "# CI/CD Implementation Analyst\n"
        "# Full rules: skills/cursor/.cursorrules\n"
        "# Project skill: .cursor/skills/cicd-analyst/SKILL.md\n"
        "# Rebuild: python skills/compile_skills.py\n"
        "\n"
        "When the user asks about CI/CD, DevSecOps, compliance, TOR analysis,\n"
        "pipeline design, or resource sizing, follow .cursor/skills/cicd-analyst/SKILL.md.\n"
        "Scan the workspace first. Cite rule IDs. Ask before assuming.\n"
        "Generate working configs, not stubs. Prefer OSS on government / air-gapped work.\n",
    )
    write(ROOT / ".cursor/skills/cicd-analyst/SKILL.md", assemble([
        PLAT / "cursor-skill.md", *core,
    ]))

    # VS Code Copilot
    write(ROOT / "skills/vscode/.github/copilot-instructions.md", assemble([
        PLAT / "vscode.md", *core, PLAT / "vscode-footer.md",
    ]))

    # Kiro
    write(ROOT / ".kiro/skills/cicd-analyst/SKILL.md", assemble([
        PLAT / "kiro.md", *core, PLAT / "kiro-footer.md",
    ]))

    # Refresh Excel copies used as skill assets
    src_matrix = ROOT / "dist" / "CICD_Tool_Resource_Matrix.xlsx"
    src_reg = ROOT / "Compliance_Standards_Register_CICD_v4.xlsx"
    for dest_dir in [
        ROOT / "skills/chatgpt/assets",
        ROOT / "skills/claude/assets",
        ROOT / "skills/gemini/assets",
    ]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if src_matrix.exists():
            shutil.copy2(src_matrix, dest_dir / "CICD_Tool_Resource_Matrix.xlsx")
        if src_reg.exists():
            shutil.copy2(src_reg, dest_dir / "Compliance_Standards_Register_CICD_v4.xlsx")

    # Drop the leftover Gemini folder name from another project
    stale = ROOT / "skills/gemini/partnership-intelligence-pre-mou-agent-knowledge"
    if stale.exists():
        shutil.rmtree(stale)
        print("[ok] removed stale", stale.relative_to(ROOT))

    print("[ok] skill compile complete")


if __name__ == "__main__":
    main()
