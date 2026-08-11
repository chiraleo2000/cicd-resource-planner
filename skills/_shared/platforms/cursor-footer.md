## Cursor outputs

- `.gitlab-ci.yml` / `.github/workflows/cicd.yml` / `Jenkinsfile`
- `Dockerfile` + `docker-compose.yml` + scanner config
- `terraform/` + `ansible/` + `k8s/`
- `reports/cicd-analysis-report.md` + `reports/resource-tables.md`
- `docs/diagrams/pipeline.mmd`

### Setup

1. Project skill: `.cursor/skills/cicd-analyst/SKILL.md` (auto-discovered)
2. Optional root `.cursorrules` (this file) for always-on context
3. Rebuild knowledge after catalog edits: `python skills/compile_skills.py`
