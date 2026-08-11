## Claude output pack

1. Artifact — Technical Report (`CICD Technical Report — [project]`)
2. Artifact — Mermaid pipeline
3. Artifact — Executive report (DOCX-ready Markdown + YAML frontmatter)
4. Artifact — Excel-ready tables (VM spec, tools, compliance, cost, timeline)

Convert with `pandoc executive-report.md -o executive-report.docx`.

Update the same Artifact when the user adds facts. Do not spawn duplicates.

### Folder

```
skills/claude/
├── SKILL.md
├── assets/          # exported artifacts
└── references/      # PDFs + xlsx to upload with this skill
```
