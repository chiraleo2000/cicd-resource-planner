# AI skill packs

Shared knowledge lives in `_shared/`. Compile into every tool:

```bash
python skills/_shared/_dump_from_sources.py
python skills/compile_skills.py
```

| Tool | Compiled file |
|------|----------------|
| Claude | `claude/SKILL.md` |
| ChatGPT | `chatgpt/knowledge-files/instructions.md` |
| Gemini | `gemini/SKILL.md` |
| Cursor | `cursor/.cursorrules` and `../.cursor/skills/cicd-analyst/SKILL.md` |
| VS Code Copilot | `vscode/.github/copilot-instructions.md` |
| Kiro | `../.kiro/skills/cicd-analyst/SKILL.md` |

Each pack includes the same methodology, full compliance register dump, 72-tool catalog, and document index. Only the wrapper (how to talk to that product) differs.
