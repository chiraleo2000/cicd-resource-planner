# CI/CD Implementation Analysis — Kiro Agent Skill

> **Version:** 3.0.0 | **Platform:** Kiro IDE
> **Optimized For:** Workspace context, steering, hooks, spec-driven workflow

## Kiro-specific behaviour

- Read TOR/spec and existing CI/CD from the workspace before asking.
- Write reports to `reports/`, diagrams to `docs/diagrams/`, and real pipeline/IaC files to the repo root.
- Use Spec mode (Requirements → Design → Tasks) for large implementations.
- Suggested steering: `.kiro/steering/cicd-standards.md`, `.kiro/steering/project-context.md`.
- Hooks: lint pipeline YAML on save; validate generated Terraform; security check before infra edits.
