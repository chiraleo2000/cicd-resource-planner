# Pipeline design (planner IR → mermaid + YAML)

Use this when the user asks for CI/CD architecture, pipeline structure, or working YAML.
Do **not** invent jobs for tools that were not selected. Cite tool ids and gate ids (G-01–G-12).

## PipelineIR

Build an intermediate graph from the current plan, then render mermaid and YAML from that graph only.

```
selected tools + VM packing + profile + disabled jobs
        → PipelineIR
        → mermaid (flow / VMs / envs)
        → .gitlab-ci.yml | .github/workflows/cicd.yml | azure-pipelines.yml | Jenkinsfile
```

Source of truth in this repo: `assets/pipeline.js` and `scripts/pipeline_gen.py` (must stay identical).

IR fields:

- `orchestrator`: `gitlab` if `gitlab-ce`; `github` if `github-actions` / `github-actions-runner`; `jenkins` if `jenkins-master` / `jenkins-agent`; `azure` if `azure-devops`; else `generic` (emit GitHub + GitLab)
- `envs`: `dev`, `uat`, `prod` (+ `dr` when profile is `gov`)
- `jobs[]`: `{id, stage, tool_id, name, needs, when, env, gates, script, enabled}`
- A job is included **only** if at least one of its tools is selected
- Last stage always includes `deploy-dev` (auto) → `deploy-uat` (DAST + quality gate) → `deploy-prod` (manual). `deploy-dr` for `gov`

## Stage → job map (emit only when the tool is selected)

| Stage | Job id | Tools (first match) | Gates |
|------|--------|---------------------|-------|
| 1 source | `policy` | `opa-conftest` | G-12 |
| 2 check | `secret-scan` | `gitleaks` | G-07 |
| 2 check | `sast-semgrep` | `semgrep` | G-01 |
| 2 check | `sast-sonar` | `sonarqube` | G-09 |
| 2 check | `lint` | `linters` | |
| 2 check | `sca-trivy` | `trivy` | G-01 G-05 |
| 2 check | `sca-owasp` | `dependency-check` | G-01 |
| 2 check | `license` | `scancode` then `fossology` | G-08 |
| 3 build | `compile` | `maven-gradle` | |
| 3 build | `image` | `docker-buildkit` | |
| 3 build | `iac` | `checkov` | G-02 |
| 3 build | `sbom` | `syft` | G-10 |
| 3 build | `sign` | `cosign` | G-11 |
| 4 test | `unit` | `unit-test-runner` | G-09 |
| 4 test | `integration` | `testcontainers` | |
| 4 test | `dast` | `owasp-zap` (UAT) | G-01 G-02 |
| 4 test | `api-dast` | `nuclei` (UAT) | G-01 |
| 4 test | `a11y` | `playwright-a11y` | |
| 4 test | `tls` | `testssl` then `cbomkit` | |
| 4 test | `load` | `locust` | |
| 5 store | `push-registry` | `harbor` / cloud registry | G-10 G-11 |
| 5 store | `verify-sign` | `cosign` | G-11 |
| 6 deploy | `deploy-dev` / `deploy-uat` / `deploy-prod` / `deploy-dr` | `argocd` / `k3s-control` / cloud K8s | G-01 G-11 |
| 6 deploy | `waf-review` / `runtime` / `backup` | `modsecurity` / `falco` / `velero-restic` | |

`needs` are filtered to jobs that actually exist.

## Mermaid

Always emit copyable mermaid (`flowchart LR` for stages, `flowchart TB` for VMs).
In the planner UI the same IR is drawn as offline SVG — do **not** call a CDN.

## YAML files

- GitLab: `.gitlab-ci.yml` — `stages:` then one job per enabled IR job; `when: manual` on prod
- GitHub Actions: `.github/workflows/cicd.yml` — `needs:` from IR; prod uses `environment`
- Azure: `azure-pipelines.yml` — one stage per Blueprint stage
- Jenkins: `Jenkinsfile` (declarative) when Jenkins tools are selected

Working configs, not stubs. Match selected scanners, registry, and deploy tool.

## Planner pages

The web planner (schema 1.2.0+) has:

1. Resource plan (W% 20–60% + per-VM ladder)
2. Tool catalog
3. Compliance
4. Storage
5. Method
6. Architecture (mermaid + automation requirements)
7. Pipeline YAML (job on/off + download)
