# CI/CD Implementation Analysis — Cursor Rules

> **Version:** 3.0.0 | **Platform:** Cursor IDE (`.cursorrules` + project skill)
> **Optimized For:** `@codebase`, Composer, terminal, multi-file edits

## Cursor-specific behaviour

- Scan the workspace for Jenkinsfile, `.gitlab-ci.yml`, `.github/workflows/`, Dockerfile, terraform/, ansible/, sonar/trivy config, and lockfiles before recommending anything.
- Use Composer to emit working configs (not stubs): pipeline + Dockerfile + compose + report + diagram together.
- Validate with `yamllint`, `hadolint`, `terraform validate`, and `python scripts/check_compliance.py` when those files exist.
- Prefer writing into `reports/`, `docs/diagrams/`, `.github/workflows/`, `terraform/`, `ansible/`.
