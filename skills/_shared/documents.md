# Document index (this repository)

Use these as primary sources. Do not invent citations. Confidential TOR folders are local-only (gitignored) — analyse them when present, never copy project names, IPs, or personal data into generic templates.

## Core service documents (`Data/`)

| File | Use for |
|------|---------|
| `CICD Blueprint Service V0.2.pdf` / `.pptx` | 6-stage pipeline, Enterprise vs OSS tool lists, role chart, yearly cost bands by profile |
| `CICD Internal Service Proposal V0.1.pdf` / `.pptx` | Internal service offering, engagement model, deliverables |
| `แนวปฏิบัติการพัฒนาซอฟต์แวร์ กฎระเบียบเกี่ยวข้องทางไซเบอร์และสถาปัตยกรรมระบบที่มั่นคงปลอดภัย V0.2.pdf` | Thai cyber law mapping, OWASP Top 10:2025, DevSecOps, Defense-in-Depth, Zero Trust |
| `แนวปฏิบัติการพัฒนาซอฟต์แวร์และสถาปัตยกรรมระบบที่มั่นคงปลอดภัย V0.2.pdf` | Secure SDLC architecture companion |

Copies of the PDFs also live under `skills/*/references/` (Claude / ChatGPT / Gemini packs):

- `CICD Blueprint Service V0.2.pdf`
- `CICD Internal Service Proposal.pdf`
- `Cybersecurity-Guidelines-V0.2.pdf`
- `SecureDev-Architecture-V0.2.pdf`

## Registers and calculators (root)

| File | Use for |
|------|---------|
| `Compliance_Standards_Register_CICD_v4.xlsx` | 155+ laws/standards, WASS (28), scan types SC-01–18, gates G-01–12 |
| `CICD_Tool_Resource_Matrix.xlsx` / `dist/CICD_Tool_Resource_Matrix.xlsx` | Live Excel with formulas (sheets 00–11) |
| `data/catalog.json` | Same numbers the web planner uses |
| `scripts/catalog_data.py` + `scripts/standards_data.py` | Single source of truth — edit here, then rebuild |

## Web planner

| File | Use for |
|------|---------|
| `index.html` | Planner UI (needs `python -m http.server 8000`) |
| `planner-standalone.html` / `dist/planner-standalone.html` | Air-gapped / `file://` — catalog embedded |
| `plans/arch-*.json` | Reference architectures (2 / 4 / 6 VM + AI/ML) |

## AI / policy (`Standard/AI/`)

| File | Use for |
|------|---------|
| `Session 7 - Towards AI Regulation in Thailand.pdf` | Direction of Thai AI regulation |
| `ร่างพระราชบัญญัติว่าด้วยปัญญาประดิษฐ์.pdf` | Draft AI Act — relevant to AI/ML pipeline profile (ISO 42001, model registry, eval gates) |

## Sample assignments (`โจทย์/` — confidential, not in git)

When the folder exists locally:

- `โจทย์/MOC-HS&OPDC-KPI/` — Ministry of Commerce / OPDC KPI TOR, proposal, UAT specs
- `โจทย์/POLICE/` — Police CCIB forensic + integration TOR

Treat as **inputs to analyse**, not as content to republish. The planner and skills stay project-agnostic.

## How to attach sources per tool

| Tool | What to upload / add |
|------|----------------------|
| Claude | `SKILL.md` + references PDFs + both xlsx |
| ChatGPT Custom GPT | `instructions.md` as Knowledge + xlsx (Code Interpreter) + optional PDFs |
| Gemini NotebookLM | `SKILL.md` + PDFs + xlsx as notebook sources |
| Cursor | `.cursor/skills/cicd-analyst/SKILL.md` and/or `.cursorrules`; `@` the xlsx/PDF in chat |
| VS Code Copilot | `.github/copilot-instructions.md`; attach files with `#file` |
| Kiro | `.kiro/skills/cicd-analyst/SKILL.md` + steering if present |
