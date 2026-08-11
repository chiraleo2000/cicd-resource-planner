## Cursor outputs

- `.gitlab-ci.yml` / `.github/workflows/cicd.yml` / `Jenkinsfile` generated from selected tools (PipelineIR — see pipeline-design.md)
- `docs/diagrams/pipeline.mmd` mermaid of the same IR (6 stages + Dev/UAT/Prod)
- `Dockerfile` + `docker-compose.yml` + scanner config
- `terraform/` + `ansible/` + `k8s/`
- `reports/cicd-analysis-report.md` + `reports/resource-tables.md`

### Setup

1. Project skill: `.cursor/skills/cicd-analyst/SKILL.md` (auto-discovered)
2. Optional root `.cursorrules` (this file) for always-on context
3. Rebuild knowledge after catalog edits: `python skills/compile_skills.py`
