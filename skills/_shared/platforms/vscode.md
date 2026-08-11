# CI/CD Implementation Analysis — VS Code GitHub Copilot

> **Version:** 3.0.0 | **Platform:** VS Code + GitHub Copilot
> **Optimized For:** Copilot Chat, `@workspace`, `#file`, `/fix`, `/explain`, `/tests`

## Copilot-specific behaviour

- `@workspace` — find existing CI/CD, Docker, IaC, and security config first.
- `#file` — treat attached TOR/spec/pipeline as ground truth.
- Inline complete YAML, Dockerfile, Terraform, and Ansible — no `...` placeholders.
- `/fix` pipeline YAML, `/explain` a stage or rule ID, `/tests` for pipeline validation jobs.
