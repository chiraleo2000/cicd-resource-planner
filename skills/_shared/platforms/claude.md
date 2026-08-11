# CI/CD Implementation Analysis — Claude (Cowork / Chat)

> **Version:** 3.0.0 | **Platform:** Claude (Anthropic) — Cowork & Chat
> **Optimized For:** Document upload, Artifacts, Extended Thinking

## Claude-specific behaviour

- Accept TOR / spec / proposal / UAT as PDF, DOCX, XLSX uploads. Summarise findings first, then ask gaps.
- Put every output longer than ~20 lines in an Artifact.
- Use extended thinking for TOR analysis, the 3-method resource calc, and multi-standard crosswalks.

| Output | Artifact type |
|--------|----------------|
| Technical / executive report | `text/markdown` |
| Resource / cost / compliance tables | `text/markdown` (Excel-pasteable) |
| Pipeline diagram | `application/vnd.ant.mermaid` |

## Activation

Use this skill when the user uploads a TOR or asks about CI/CD resource, cost, compliance, roadmap, or DevSecOps gates.
