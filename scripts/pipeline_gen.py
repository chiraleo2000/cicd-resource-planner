# -*- coding: utf-8 -*-
"""PipelineIR + YAML / mermaid emitters.

ต้องให้ผลลัพธ์ตรงกับ assets/pipeline.js ทุกกรณี — มีเทสต์ใน scripts/verify.py
ห้ามใส่ URL แบบ http(s):// ในสตริงที่ฝั่ง JS จะคัดลอก (air-gap lint)
"""
from __future__ import annotations

SCHEMA = "1.2.0"

STAGES = [
    dict(id="source", n=1, label="Source Code"),
    dict(id="check", n=2, label="Check & Scan"),
    dict(id="build", n=3, label="Build & Sign"),
    dict(id="test", n=4, label="Test"),
    dict(id="store", n=5, label="Store & Version"),
    dict(id="deploy", n=6, label="Deploy & Operate"),
]

# id, stage, tool preference list, needs, when, env, gates, title, script lines
JOB_SPECS = [
    ("policy", "source", ["opa-conftest"], [], "pr", None, ["G-12"],
     "Policy-as-Code (OPA/Conftest)", ["conftest test policy/"]),
    ("secret-scan", "check", ["gitleaks"], [], "commit", None, ["G-07"],
     "Secret scan (GitLeaks)", ["gitleaks detect --redact --exit-code 1"]),
    ("sast-semgrep", "check", ["semgrep"], [], "commit", None, ["G-01"],
     "SAST (Semgrep)", ["semgrep scan --error --metrics=off"]),
    ("sast-sonar", "check", ["sonarqube"], [], "commit", None, ["G-09"],
     "SAST + Quality Gate (SonarQube)", ["sonar-scanner -Dsonar.qualitygate.wait=true"]),
    ("lint", "check", ["linters"], [], "commit", None, [],
     "Linters", ["echo run project linters"]),
    ("sca-trivy", "check", ["trivy"], [], "build", None, ["G-01", "G-05"],
     "SCA + image scan (Trivy)", ["trivy fs --exit-code 1 --severity CRITICAL,HIGH ."]),
    ("sca-owasp", "check", ["dependency-check"], [], "build", None, ["G-01"],
     "SCA (OWASP Dependency-Check)", ["dependency-check.sh --scan . --failOnCVSS 9"]),
    ("license", "check", ["scancode", "fossology"], [], "build", None, ["G-08"],
     "License compliance", ["scancode --license --json-pp license-report.json ."]),
    ("compile", "build", ["maven-gradle"], ["lint"], "commit", None, [],
     "Compile / package", ["echo compile with project build tool"]),
    ("image", "build", ["docker-buildkit"], ["compile"], "build", None, [],
     "Container image (rootless BuildKit)", ["buildctl build --frontend dockerfile.v0 --local context=."]),
    ("iac", "build", ["checkov"], [], "build", None, ["G-02"],
     "IaC scan (Checkov)", ["checkov -d . --quiet --compact"]),
    ("sbom", "build", ["syft"], ["image", "compile"], "build", None, ["G-10"],
     "SBOM (Syft / CycloneDX)", ["syft dir:. -o cyclonedx-json > sbom.json"]),
    ("sign", "build", ["cosign"], ["sbom", "image"], "build", None, ["G-11"],
     "Sign artifact (Cosign)", ["cosign sign --yes ${IMAGE_REF}"]),
    ("unit", "test", ["unit-test-runner"], ["compile"], "commit", None, ["G-09"],
     "Unit test + coverage", ["echo unit tests --coverage"]),
    ("integration", "test", ["testcontainers"], ["unit"], "build", None, [],
     "Integration / contract test", ["echo integration tests"]),
    ("dast", "test", ["owasp-zap"], ["deploy-dev"], "release", "uat", ["G-01", "G-02"],
     "DAST (OWASP ZAP) on UAT", ["zap-baseline.py -t ${UAT_URL} -I"]),
    ("api-dast", "test", ["nuclei"], ["deploy-dev"], "release", "uat", ["G-01"],
     "API / template scan (Nuclei)", ["nuclei -u ${UAT_URL} -severity critical,high"]),
    ("a11y", "test", ["playwright-a11y"], ["deploy-dev"], "nightly", "uat", [],
     "Accessibility (Playwright + axe)", ["echo playwright a11y"]),
    ("tls", "test", ["testssl", "cbomkit"], ["deploy-dev"], "weekly", "uat", [],
     "TLS / crypto check", ["echo tls scan on UAT"]),
    ("load", "test", ["locust"], ["deploy-uat"], "weekly", "uat", [],
     "Load test (Locust)", ["echo locust -f locustfile.py"]),
    ("push-registry", "store",
     ["harbor", "azure-container-registry", "aws-ecr", "gcp-artifact-registry"],
     ["image", "sign", "sbom"], "build", None, ["G-10", "G-11"],
     "Push image + SBOM to registry", ["echo crane push ${IMAGE_REF}"]),
    ("verify-sign", "store", ["cosign"], ["push-registry"], "release", None, ["G-11"],
     "Verify signature before deploy", ["cosign verify ${IMAGE_REF}"]),
]

ORCH_TOOLS = [
    ("gitlab-ce", "gitlab"),
    ("github-actions", "github"),
    ("github-actions-runner", "github"),
    ("jenkins-master", "jenkins"),
    ("jenkins-agent", "jenkins"),
    ("azure-devops", "azure"),
]

DEPLOY_TOOLS = [
    "argocd", "k3s-control",
    "azure-kubernetes-service", "aws-eks", "gcp-gke",
]


def _pick(tool_set: set, prefs: list) -> str | None:
    for tid in prefs:
        if tid in tool_set:
            return tid
    return None


def detect_orchestrator(tool_ids: list) -> str:
    s = set(tool_ids)
    for tid, flavor in ORCH_TOOLS:
        if tid in s:
            return flavor
    return "generic"


def flavors_for(orch: str) -> list:
    if orch == "generic":
        return ["github", "gitlab"]
    return [orch]


def build_pipeline_ir(tool_ids, vms=None, profile="gov", disabled=None, project=None):
    """สร้าง PipelineIR จากเครื่องมือที่เลือก — job ถูกใส่เฉพาะเมื่อมีเครื่องมือนั้น"""
    tools = list(tool_ids or [])
    tset = set(tools)
    disabled = list(disabled or [])
    off = set(disabled)
    vms = list(vms or [])
    project = project or {}
    orch = detect_orchestrator(tools)
    envs = ["dev", "uat", "prod"]
    if profile == "gov":
        envs.append("dr")

    jobs = []
    for spec in JOB_SPECS:
        jid, stage, prefs, needs, when, env, gates, title, script = spec
        tid = _pick(tset, prefs)
        if not tid:
            continue
        jobs.append(dict(
            id=jid, stage=stage, tool_id=tid, name=title,
            needs=list(needs), when=when, env=env, gates=list(gates),
            script=list(script), enabled=(jid not in off),
        ))

    deploy_tool = _pick(tset, DEPLOY_TOOLS)
    deploy_name = {
        "argocd": "GitOps deploy (Argo CD)",
        "k3s-control": "Deploy to K3s",
        "azure-kubernetes-service": "Deploy to AKS",
        "aws-eks": "Deploy to EKS",
        "gcp-gke": "Deploy to GKE",
    }.get(deploy_tool, "Deploy (GitOps / orchestrator)")

    deploy_jobs = [
        ("deploy-dev", "dev", "auto", ["verify-sign", "push-registry", "image", "compile"],
         [], "Deploy DEV (auto)"),
        ("deploy-uat", "uat", "release", ["deploy-dev", "dast", "verify-sign"],
         ["G-01", "G-02"], "Deploy UAT + quality gate"),
        ("deploy-prod", "prod", "manual", ["deploy-uat"],
         ["G-01", "G-11"], "Deploy PROD (manual approval)"),
    ]
    if "dr" in envs:
        deploy_jobs.append(
            ("deploy-dr", "dr", "manual", ["deploy-prod"], ["G-11"], "Deploy DR")
        )
    extra = []
    if "modsecurity" in tset:
        extra.append(("waf-review", "deploy", "modsecurity", ["deploy-uat"], "monthly", "prod",
                      [], "WAF rule review", ["echo review WAF rules"]))
    if "falco" in tset:
        extra.append(("runtime", "deploy", "falco", ["deploy-prod"], "resident", "prod",
                      [], "Runtime security (Falco)", ["echo falco is resident on nodes"]))
    if "velero-restic" in tset:
        extra.append(("backup", "deploy", "velero-restic", ["deploy-prod"], "nightly", "prod",
                      [], "Backup / restore drill", ["echo velero backup create nightly"]))

    for jid, env, when, needs, gates, title in deploy_jobs:
        jobs.append(dict(
            id=jid, stage="deploy", tool_id=deploy_tool, name=title,
            needs=list(needs), when=when, env=env, gates=list(gates),
            script=["echo " + title], enabled=(jid not in off),
        ))
    for row in extra:
        jid, stage, tid, needs, when, env, gates, title, script = row
        jobs.append(dict(
            id=jid, stage=stage, tool_id=tid, name=title,
            needs=list(needs), when=when, env=env, gates=list(gates),
            script=list(script), enabled=(jid not in off),
        ))

    present = {j["id"] for j in jobs}
    for j in jobs:
        j["needs"] = [x for x in j["needs"] if x in present]
    jobs.sort(key=lambda j: (next(s["n"] for s in STAGES if s["id"] == j["stage"]), j["id"]))

    return dict(
        schema=SCHEMA,
        orchestrator=orch,
        flavors=flavors_for(orch),
        profile=profile,
        envs=envs,
        stages=list(STAGES),
        jobs=jobs,
        tools=sorted(tset),
        vms=[{"name": v.get("name", "VM"), "role": v.get("role", ""),
              "tools": list(v.get("tools") or [])} for v in vms],
        disabled=sorted(off),
        project=dict(name=project.get("name") or "", org=project.get("org") or "",
                     env=project.get("env") or ""),
    )


def _nid(jid: str) -> str:
    return "N_" + jid.replace("-", "_")


def mermaid_flow(ir: dict) -> str:
    lines = ["flowchart LR"]
    for st in ir["stages"]:
        lines.append("  subgraph " + st["id"] + " [" + str(st["n"]) + " " + st["label"] + "]")
        shown = False
        for j in ir["jobs"]:
            if j["stage"] != st["id"] or not j["enabled"]:
                continue
            lines.append("    " + _nid(j["id"]) + "[" + j["name"].replace("]", "") + "]")
            shown = True
        if not shown:
            lines.append("    " + st["id"] + "_empty[ไม่มีงานที่เลือก]")
        lines.append("  end")
    for j in ir["jobs"]:
        if not j["enabled"]:
            continue
        for dep in j["needs"]:
            lines.append("  " + _nid(dep) + " --> " + _nid(j["id"]))
    return "\n".join(lines) + "\n"


def mermaid_vms(ir: dict) -> str:
    lines = ["flowchart TB"]
    if not ir["vms"]:
        lines.append("  empty[ยังไม่ได้จัดเครื่องมือลง VM]")
        return "\n".join(lines) + "\n"
    for i, vm in enumerate(ir["vms"]):
        vid = "VM" + str(i)
        lines.append("  subgraph " + vid + " [" + (vm["name"] or vid) + "]")
        tools = vm["tools"] or ["empty"]
        for tid in tools:
            lines.append("    " + vid + "_" + tid.replace("-", "_") + "[" + tid + "]")
        lines.append("  end")
    return "\n".join(lines) + "\n"


def mermaid_envs(ir: dict) -> str:
    lines = ["flowchart LR"]
    prev = None
    for env in ir["envs"]:
        nid = "E_" + env
        lines.append("  " + nid + "[" + env.upper() + "]")
        if prev:
            lines.append("  " + prev + " --> " + nid)
        prev = nid
    for j in ir["jobs"]:
        if j.get("env") and j["enabled"]:
            lines.append("  E_" + j["env"] + " --- " + _nid(j["id"]) + "[" + j["id"] + "]")
    return "\n".join(lines) + "\n"


def _header(ir: dict, flavor: str) -> str:
    pj = ir.get("project") or {}
    return (
        "# Generated by CI/CD Resource Planner " + SCHEMA + "\n"
        "# flavor=" + flavor + " profile=" + ir["profile"]
        + " orchestrator=" + ir["orchestrator"] + "\n"
        "# project=" + (pj.get("name") or "-") + " org=" + (pj.get("org") or "-") + "\n"
        "# tools=" + ",".join(ir["tools"]) + "\n"
    )


def emit_gitlab(ir: dict) -> str:
    L = [_header(ir, "gitlab"), "stages:"]
    for st in ir["stages"]:
        L.append("  - " + st["id"])
    L.append("")
    for j in ir["jobs"]:
        if not j["enabled"]:
            continue
        L.append(j["id"] + ":")
        L.append("  stage: " + j["stage"])
        if j["needs"]:
            L.append("  needs:")
            for n in j["needs"]:
                L.append("    - " + n)
        L.append("  script:")
        for s in j["script"]:
            L.append("    - " + s)
        if j["when"] == "manual":
            L.append("  when: manual")
            L.append("  allow_failure: false")
        if j.get("env"):
            L.append("  environment:")
            L.append("    name: " + j["env"])
        if j["gates"]:
            L.append("  variables:")
            L.append("    CICD_GATES: \"" + ",".join(j["gates"]) + "\"")
        L.append("")
    return "\n".join(L)


def emit_github(ir: dict) -> str:
    L = [_header(ir, "github"),
         "name: CI-CD\n",
         "on:\n  push:\n    branches: [main]\n  pull_request:\n\n",
         "jobs:\n"]
    for j in ir["jobs"]:
        if not j["enabled"]:
            continue
        L.append("  " + j["id"] + ":\n")
        L.append("    name: " + j["name"] + "\n")
        L.append("    runs-on: ubuntu-latest\n")
        if j["needs"]:
            L.append("    needs: [" + ", ".join(j["needs"]) + "]\n")
        if j["when"] == "manual":
            L.append("    if: github.ref == 'refs/heads/main'\n")
            L.append("    environment: " + (j.get("env") or "prod") + "\n")
        elif j.get("env"):
            L.append("    environment: " + j["env"] + "\n")
        L.append("    steps:\n")
        L.append("      - uses: actions/checkout@v4\n")
        for s in j["script"]:
            L.append("      - name: " + j["id"] + "\n")
            L.append("        run: " + s + "\n")
        L.append("\n")
    return "".join(L)


def emit_azure(ir: dict) -> str:
    L = [_header(ir, "azure"), "trigger:\n  - main\n\n", "stages:\n"]
    for st in ir["stages"]:
        jobs = [j for j in ir["jobs"] if j["enabled"] and j["stage"] == st["id"]]
        if not jobs:
            continue
        L.append("- stage: " + st["id"] + "\n")
        L.append("  displayName: " + st["label"] + "\n")
        L.append("  jobs:\n")
        for j in jobs:
            L.append("  - job: " + j["id"].replace("-", "_") + "\n")
            L.append("    displayName: " + j["name"] + "\n")
            L.append("    steps:\n")
            for s in j["script"]:
                L.append("    - script: " + s + "\n")
                L.append("      displayName: " + j["id"] + "\n")
        L.append("\n")
    return "".join(L)


def emit_jenkins(ir: dict) -> str:
    L = ["// Generated by CI/CD Resource Planner " + SCHEMA + "\n",
         "pipeline {\n  agent any\n  stages {\n"]
    for st in ir["stages"]:
        jobs = [j for j in ir["jobs"] if j["enabled"] and j["stage"] == st["id"]]
        if not jobs:
            continue
        L.append("    stage('" + st["label"] + "') {\n      steps {\n")
        for j in jobs:
            for s in j["script"]:
                L.append("        sh '" + s.replace("'", '"') + "'\n")
        L.append("      }\n    }\n")
    L.append("  }\n}\n")
    return "".join(L)


def emit_all(ir: dict) -> dict:
    return {
        "gitlab": emit_gitlab(ir),
        "github": emit_github(ir),
        "azure": emit_azure(ir),
        "jenkins": emit_jenkins(ir),
        "mermaid_flow": mermaid_flow(ir),
        "mermaid_vms": mermaid_vms(ir),
        "mermaid_envs": mermaid_envs(ir),
    }
