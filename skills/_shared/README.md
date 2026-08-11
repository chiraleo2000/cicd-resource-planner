# Shared skill source

Edit these files, then run:

```bash
python skills/_shared/_dump_from_sources.py   # refresh Excel + catalog dumps
python skills/compile_skills.py               # write every tool pack
```

| File | Content |
|------|---------|
| `methodology.md` | Role, intake, 6 stages, resource model, profiles |
| `compliance-register.md` | Full dump of `Compliance_Standards_Register_CICD_v4.xlsx` |
| `tool-catalog.md` | Full dump of `data/catalog.json` (72 tools) |
| `documents.md` | Blueprint, guidelines, TOR folders |
| `platforms/*.md` | Per-tool wrappers (Claude, ChatGPT, Gemini, Cursor, VS Code, Kiro) |
