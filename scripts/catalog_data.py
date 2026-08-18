# -*- coding: utf-8 -*-
"""
แหล่งข้อมูลกลาง (Single Source of Truth) สำหรับ CI/CD Resource Planner
- FREQ_CLASSES : ชั้นความถี่การรัน -> Duty Weight 20-60% + บันไดร่วมเครื่อง
- CAPABILITIES : ความสามารถที่ระบบ CI/CD ต้องมี (ใช้ map compliance)
- FRAMEWORKS   : กฎหมาย/มาตรฐานที่เกี่ยวข้อง
- RULES        : ข้อกำหนดที่ต้องปฏิบัติ -> ต้องมี capability อะไร
- PROFILES     : ประเภทโครงการ 5 แบบ
- TOOLS        : ตารางเครื่องมือ + Resource Requirements (Minimum)

หมายเหตุเรื่องตัวเลข Minimum:
ตัวเลขในคอลัมน์ min_* คือ "ค่าต่ำสุดที่เครื่องมือทำงานได้จริงในระดับ Production/UAT ขนาดเล็ก"
อ้างอิงจากเอกสารติดตั้งของผู้พัฒนา (vendor sizing guide) และค่าที่พบจากการใช้งานจริงในระดับ UAT/Production ขนาดเล็ก
ค่า rec_* คือค่าที่แนะนำเมื่อรับงานจริงต่อเนื่อง (steady state)
"""

SCHEMA_VERSION = "1.3.0"
GENERATED_FOR = "CI/CD Service Blueprint V0.2 — Generic Edition (ใช้ได้กับทุกประเภทโครงการ)"

# ---------------------------------------------------------------------------
# 1) ชั้นความถี่การรัน  ->  Duty Weight เดี่ยว (w_solo) = 0.20 + 0.40 * activity_index
#    ช่วง 20-60% เมื่อเครื่องมืออยู่เครื่องเดียว
#    เมื่อรวมหลายเครื่องมือบน VM เดียวกัน ใช้ w_max(n) ladder แทนเพดาน 60%
# ---------------------------------------------------------------------------
FREQ_CLASSES = [
    dict(id="resident",   label_th="รันค้างตลอดเวลา 24/7 (Resident Daemon)",
         runs_per_day="ตลอดเวลา", activity_index=1.00,
         note_th="น้ำหนักสูงสุด 60% เมื่ออยู่เครื่องเดียว ลดตามจำนวนเครื่องมือร่วมเครื่องลงถึงพื้น 20%"),
    dict(id="per_commit", label_th="ทุก Commit / Push (10-30 ครั้ง/วัน)",
         runs_per_day="10-30", activity_index=0.80,
         note_th="Trigger บ่อย ยังซ้อนทับได้ แต่ถูกจำกัดด้วยเพดาน w_max(n) ของเครื่องนั้น"),
    dict(id="per_build",  label_th="ทุก Build / Merge (5-15 ครั้ง/วัน)",
         runs_per_day="5-15", activity_index=0.65,
         note_th="รันเป็นช่วง ๆ ระหว่างวันทำงาน มีโอกาสซ้อนทับปานกลาง"),
    dict(id="per_pr",     label_th="ทุก Pull Request / Quality Gate (3-10 ครั้ง/วัน)",
         runs_per_day="3-10", activity_index=0.55,
         note_th="ผูกกับรอบ Review ของทีม"),
    dict(id="nightly",    label_th="รอบกลางคืน / วันละครั้ง (Nightly)",
         runs_per_day="1", activity_index=0.35,
         note_th="เช่น DAST Full Scan, Dependency-Check ที่ใช้เวลานาน ย้ายไปรันหลังบ้าน"),
    dict(id="weekly",     label_th="รายสัปดาห์ (1-2 ครั้ง/สัปดาห์)",
         runs_per_day="0.15-0.3", activity_index=0.15,
         note_th="เช่น Performance/Load Test รอบใหญ่, License Audit"),
    dict(id="on_demand",  label_th="ตามคำสั่ง / รอบ Release (ไม่กี่ครั้ง/เดือน)",
         runs_per_day="<0.1", activity_index=0.00,
         note_th="บวกที่ 20% ซึ่งเป็นค่าต่ำสุดของช่วงที่กำหนด เพราะยังต้องกันที่ไว้ให้รันได้"),
]

# ---------------------------------------------------------------------------
# 2) Capabilities — หน่วยย่อยที่ใช้เชื่อมเครื่องมือกับข้อกำหนดมาตรฐาน
# ---------------------------------------------------------------------------
CAPABILITIES = {
    "git_scm":            "Version Control / Source Code Management",
    "webhook":            "Webhook / Event Trigger",
    "branch_protection":  "Branch Protection & Code Review Enforcement",
    "pipeline":           "Pipeline Orchestration",
    "sast":               "Static Application Security Testing",
    "secret_scan":        "Secret / Credential Scanning",
    "sca":                "Software Composition Analysis (CVE)",
    "license":            "License Compliance",
    "code_quality":       "Code Quality / Technical Debt",
    "build":              "Build & Compilation",
    "image_build":        "Container Image Build",
    "container_scan":     "Container Image Vulnerability Scan",
    "iac_scan":           "Infrastructure as Code / Policy-as-Code Scan",
    "artifact_sign":      "Artifact / Image Signing & Verification",
    "unit_test":          "Unit Test + Coverage",
    "integration_test":   "Integration / Contract Test",
    "dast":               "Dynamic Application Security Testing",
    "api_security":       "API Security Testing",
    "perf_test":          "Performance / Load Test",
    "registry":           "Private Container / Artifact Registry",
    "version_tag":        "Version Tagging / Release Management",
    "sbom":               "Software Bill of Materials",
    "audit_trail":        "Audit Trail (ใครทำอะไรเมื่อไหร่)",
    "log_mgmt":           "Centralized Log Management (เก็บ >= 90 วัน)",
    "siem_alert":         "SIEM / Security Alerting",
    "quality_gate":       "Quality Gate & Approval Workflow",
    "deploy_strategy":    "Deployment Strategy (Rolling/Blue-Green/Canary)",
    "orchestration":      "Container Orchestration",
    "runtime_security":   "Runtime Security Monitoring",
    "monitoring":         "Observability / Metrics & Alerting",
    "secret_mgmt":        "Secret Management / Key Rotation",
    "config_mgmt":        "Configuration Management / Hardening Baseline",
    "waf":                "Web Application Firewall",
    "tls_check":          "TLS / Cipher Configuration Validation",
    "accessibility":      "Web Accessibility Test (WCAG 2.1/2.2 AA)",
    "cspm":               "Cloud / Infra Security Posture Scan",
    "backup_dr":          "Backup & Restore / Disaster Recovery",
    "iam_mfa":            "Identity, SSO & MFA",
    "crypto_agility":     "Crypto Inventory / Post-Quantum Readiness",
    "vapt":               "Vulnerability Assessment & Penetration Test",
    "notify":             "Notification / Incident Escalation",
}

# ---------------------------------------------------------------------------
# 3) กฎหมาย / มาตรฐาน  -> อยู่ใน scripts/standards_data.py แบบรายฉบับ
#    FRAMEWORKS = มาตรฐานรายฉบับ แยกไทย/สากล
#    CONTROLS   = มาตรการที่ระบบต้องทำ ผูกกับ capabilities
#    มาตรฐานหลายฉบับอ้าง control เดียวกันได้ พร้อมเลขข้อของตัวเอง
# ---------------------------------------------------------------------------
from standards_data import (  # noqa: E402
    CONTROLS, CONTROL_GROUPS, FRAMEWORKS, FRAMEWORK_FAMILIES,
    FRAMEWORK_PRESETS, PRESET_LABELS,
)

CONTROL_BY_ID = {c["id"]: c for c in CONTROLS}
FRAMEWORK_BY_ID = {f["id"]: f for f in FRAMEWORKS}
SEV_RANK = {"recommended": 0, "conditional": 1, "mandatory": 2}

# ตรวจความสมบูรณ์ของการอ้างอิงตอน import (ผิดพลาดรู้ทันที ไม่รอถึงตอน build)
for _f in FRAMEWORKS:
    assert _f["family"] in FRAMEWORK_FAMILIES, f"{_f['id']} family ไม่รู้จัก"
    _f.setdefault("region", FRAMEWORK_FAMILIES[_f["family"]]["region"])
    _bad = [c for c in _f["controls"] if c not in CONTROL_BY_ID]
    assert not _bad, f"{_f['id']} อ้าง control ที่ไม่มี: {_bad}"
for _c in CONTROLS:
    assert _c["group"] in CONTROL_GROUPS, f"{_c['id']} group ไม่รู้จัก: {_c['group']}"
for _k, _ids in FRAMEWORK_PRESETS.items():
    _bad = [i for i in _ids if i not in FRAMEWORK_BY_ID]
    assert not _bad, f"preset {_k} อ้างมาตรฐานที่ไม่มี: {_bad}"


def framework_refs(control_id: str, framework_ids=None) -> dict:
    """คืน {framework_id: เลขข้ออ้างอิง} ของมาตรฐานที่อ้าง control นี้"""
    out = {}
    for f in FRAMEWORKS:
        if framework_ids is not None and f["id"] not in framework_ids:
            continue
        ref = f["controls"].get(control_id)
        if ref is None:
            continue
        out[f["id"]] = ref["clause"] if isinstance(ref, dict) else ref
    return out


def control_severity(control_id: str, framework_ids=None) -> str:
    """ระดับบังคับที่เข้มที่สุดในบรรดามาตรฐานที่เลือกซึ่งอ้าง control นี้

    ถ้ามาตรฐานฉบับใดระบุ severity ไว้เอง (เช่น มสพร. 11-2566 ให้ WAF เป็น 'แนะนำ')
    จะใช้ค่านั้น ไม่ใช้ค่าเริ่มต้นของ control
    """
    base = CONTROL_BY_ID[control_id]["severity"]
    sevs = []
    for f in FRAMEWORKS:
        if framework_ids is not None and f["id"] not in framework_ids:
            continue
        ref = f["controls"].get(control_id)
        if ref is None:
            continue
        sevs.append(ref.get("severity", base) if isinstance(ref, dict) else base)
    return max(sevs, key=lambda x: SEV_RANK[x]) if sevs else base


# ---------------------------------------------------------------------------
# 4) ประเภทโครงการ (Profile)
# ---------------------------------------------------------------------------
PROFILES = [
    dict(id="gov", name_th="ภาครัฐ / CII", grade_pref="oss",
         impact="high", security="สูงสุด", automate_th="6-12 ชั่วโมง/รอบ",
         cost_yr_thb="5,250,000 - 17,500,000+",
         framework_preset="gov",
         log_retention_days=90, audit_retention_days=2555,
         notes_th="On-premise/Air-gapped, ห้าม GPL/AGPL, Critical = 0, Coverage > 80%, เก็บ Audit Trail 7+ ปี"),
    dict(id="enterprise", name_th="เอกชน / Enterprise", grade_pref="mixed",
         impact="medium", security="สูง", automate_th="60-95 นาที/รอบ",
         cost_yr_thb="1,050,000 - 5,250,000",
         framework_preset="enterprise",
         log_retention_days=90, audit_retention_days=365,
         notes_th="Cloud + OSS ผสมได้, Canary/A-B Testing, Auto-remediation ผ่าน PR"),
    dict(id="internal", name_th="Internal Dev / R&D", grade_pref="oss",
         impact="low", security="ปานกลาง", automate_th="22-35 นาที/รอบ",
         cost_yr_thb="0 - 175,000",
         framework_preset="internal",
         log_retention_days=30, audit_retention_days=90,
         notes_th="ใช้ OSS เกือบทั้งหมด, Self-hosted, Monitoring พื้นฐาน"),
    dict(id="startup", name_th="Startup / Fast-paced", grade_pref="saas",
         impact="low", security="พื้นฐาน", automate_th="15-25 นาที/รอบ",
         cost_yr_thb="0 - 84,000",
         framework_preset="startup",
         log_retention_days=14, audit_retention_days=90,
         notes_th="Managed/Serverless, Zero maintenance, เพิ่ม Security เมื่อ Scale"),
    dict(id="aiml", name_th="AI/ML Engineering", grade_pref="oss",
         impact="medium", security="สูง (Data + Model)", automate_th="70-135 นาที/รอบ (+Training)",
         cost_yr_thb="1,750,000 - 7,000,000+",
         framework_preset="aiml",
         log_retention_days=90, audit_retention_days=730,
         notes_th="ต้องมี GPU Scheduling, Model Registry, Data Versioning, Drift Detection"),
]


# ---------------------------------------------------------------------------
# 4.5) การจำแนกประเภทลิขสิทธิ์ (License Class)
#      ใช้กรองเครื่องมือตามนโยบายของโครงการ เช่น "ห้ามใช้ GPL/AGPL"
#      สำคัญ: LGPL เป็น weak copyleft ไม่ใช่ GPL — การกรองด้วยการค้นคำว่า "GPL"
#      จะตัด LGPL ทิ้งไปด้วยโดยไม่ควร จึงต้องจำแนกเป็นชั้นก่อน
# ---------------------------------------------------------------------------
LICENSE_CLASSES = {
    "permissive":       "อนุญาตกว้าง (MIT, Apache-2.0, BSD, PostgreSQL) — ใช้ได้ทุกกรณี",
    "weak-copyleft":    "Copyleft อ่อน (LGPL, MPL, EPL) — ใช้เป็นไลบรารี/บริการแยกได้ ไม่ลาม",
    "strong-copyleft":  "Copyleft เข้ม (GPL) — ผลงานดัดแปลงต้องเปิดซอร์ส",
    "network-copyleft": "Copyleft ผ่านเครือข่าย (AGPL) — ให้บริการผ่านเน็ตก็ต้องเปิดซอร์ส",
    "source-available": "เปิดซอร์สแบบมีเงื่อนไข (BUSL, SSPL, Elastic, RSAL) — ไม่ใช่ OSI-approved",
    "n/a":              "ไม่ใช่ซอฟต์แวร์ที่มีลิขสิทธิ์เดียว (เช่น โหนดฮาร์ดแวร์/บริการภายนอก)",
}


def classify_license(lic: str) -> str:
    """จำแนกข้อความ license เป็นชั้น — ตรวจ AGPL และ SSPL/BUSL ก่อน LGPL ก่อน GPL"""
    u = (lic or "").upper()
    if not u or u == "N/A":
        return "n/a"
    if "PROPRIETARY" in u or "SAAS" in u:
        return "n/a"
    if "SSPL" in u or "BUSL" in u or "ELASTIC LICENSE" in u or "RSAL" in u:
        return "source-available"
    if "AGPL" in u:
        return "network-copyleft"
    if "LGPL" in u:
        return "weak-copyleft"
    if "GPL" in u:
        return "strong-copyleft"
    if "MPL" in u or "EPL" in u:
        return "weak-copyleft"
    return "permissive"


# ---------------------------------------------------------------------------
# 5) ตารางเครื่องมือ + Resource Requirements
# ---------------------------------------------------------------------------
FIT_LABELS = {
    "all": "ทั้งหมด",
    "cloud": "Cloud",
    "hybrid": "Hybrid",
    "private": "Private / On-prem",
    "local": "Local / Dev",
}


def T(id, name, stage, cat, caps, grade, license, core, ent,
      min_vcpu, min_ram, min_disk_os,
      rec_vcpu, rec_ram, rec_disk_os,
      resident, idle_ram, freq,
      data_daily_gb, retention_days, index_overhead, growth_yr,
      profiles, sizing_ref, note_th, oss_alt=None, gpu=False, managed=False,
      fit=None, install=None):
    """สร้าง record เครื่องมือ 1 ตัว

    min_*  = ค่าต่ำสุดที่รันได้จริง (peak ระหว่างทำงาน)
    idle_ram = RAM ที่ถูกจองค้างไว้แม้ไม่มีงาน (0 = ephemeral)
    data_daily_gb = ปริมาณข้อมูลใหม่เฉลี่ยต่อวันในสภาวะใช้งานปกติ (GB/วัน)
    index_overhead = ส่วนเกินสำหรับ index/replica/metadata (สัดส่วน)
    growth_yr = อัตราการโตของปริมาณข้อมูลต่อปี (สัดส่วน)
    fit = สภาพแวดล้อมที่ติดตั้งได้ (cloud / hybrid / private / local)
    """
    return dict(
        id=id, name=name, stage=stage, category=cat, capabilities=caps,
        grade=grade, license=license, core=core, enterprise_alt=ent, oss_alt=oss_alt or [],
        min=dict(vcpu=min_vcpu, ram_gb=min_ram, disk_os_gb=min_disk_os),
        rec=dict(vcpu=rec_vcpu, ram_gb=rec_ram, disk_os_gb=rec_disk_os),
        resident=resident, idle_ram_gb=idle_ram, freq=freq, gpu=gpu,
        storage=dict(install_gb=min_disk_os, data_daily_gb=data_daily_gb,
                     retention_days=retention_days, index_overhead=index_overhead,
                     growth_yr=growth_yr),
        profiles=profiles, sizing_ref=sizing_ref, note_th=note_th,
        managed=managed,
        fit=list(fit or []),
        install=dict(install or {}),
    )


TOOLS = [
# ======================= STAGE 1: SOURCE CODE ==============================
T("gitlab-ce", "GitLab Community Edition (Self-hosted Git)", 1, "Git Repository",
  ["git_scm","webhook","branch_protection","pipeline","audit_trail"], "oss", "MIT", "Core",
  ["GitLab Enterprise Edition","GitHub Enterprise Server","Bitbucket Data Center","Azure DevOps Server"],
  4, 8, 40, 8, 16, 200, True, 5.0, "resident",
  0.50, 3650, 0.20, 0.25, ["gov", "enterprise", "internal", "aiml"],
  "GitLab docs: 4 vCPU / 4 GB (แนะนำ 8 GB) รองรับได้ถึง ~500 users; Puma+Sidekiq+Gitaly+PostgreSQL+Redis รวมในเครื่องเดียว",
  "ทางเลือกหลักของภาครัฐที่ต้องการ Git แบบ On-premise เต็มรูปแบบ กินทรัพยากรมากเพราะรวมหลาย service; ถ้าต้องการเบาให้ใช้ Gitea",
  oss_alt=["Gitea","Forgejo","Gogs","Onedev"]),

T("gitea", "Gitea / Forgejo (Lightweight Git)", 1, "Git Repository",
  ["git_scm","webhook","branch_protection","audit_trail"], "oss", "MIT", "Core",
  ["GitLab Enterprise Edition","GitHub Enterprise Server","Bitbucket Data Center"],
  1, 1, 10, 2, 4, 100, True, 0.5, "resident",
  0.20, 3650, 0.10, 0.25, ["gov", "internal", "startup", "aiml"],
  "Gitea docs: 2 CPU cores / 1 GB RAM เพียงพอสำหรับทีมขนาดเล็ก-กลาง; binary เดียว + SQLite/PostgreSQL",
  "ตัวเลือกเบาสำหรับเครื่องที่ต้องแชร์กับเครื่องมืออื่น กินแค่ ~300-500 MB RAM ตอน idle"),

T("github-actions-runner", "GitHub Actions Self-hosted Runner", 1, "Pipeline Orchestration",
  ["pipeline","webhook","build"], "oss", "MIT", "Core",
  ["GitHub Actions Enterprise","GitHub Enterprise Server"],
  2, 4, 60, 4, 8, 150, False, 0.2, "per_commit",
  0.60, 30, 0.05, 0.20, ["gov","enterprise","internal","startup","aiml"],
  "GitHub-hosted standard runner = 2 vCPU / 7 GB / 14 GB SSD — ใช้เป็นเกณฑ์เทียบขั้นต่ำของ self-hosted runner",
  "รูปแบบที่ประหยัดที่สุดคือให้ Runner ของผู้ให้บริการ Git ทำงานเบา (Lint / Unit Test) แล้วส่ง Webhook เข้า Orchestrator ในองค์กร จึงไม่ต้องใช้ VM ของหน่วยงานในขั้นนี้; ถ้าอยู่หลัง Proxy ต้อง whitelist โดเมนของผู้ให้บริการ (เช่น *.github.com, *.ghcr.io, *.githubusercontent.com)"),

T("jenkins-master", "Jenkins Master / Controller", 1, "Pipeline Orchestration",
  ["pipeline","webhook","quality_gate","audit_trail","notify"], "oss", "MIT", "Core",
  ["CloudBees CI","Jenkins Enterprise","Azure DevOps Server","GitLab Ultimate Self-Managed"],
  2, 4, 20, 4, 8, 100, True, 2.0, "resident",
  0.30, 180, 0.10, 0.15, ["gov","enterprise","internal","aiml"],
  "Jenkins docs: absolute min 256 MB RAM / 1 GB disk; 'small team' 1 GB+ RAM / 50 GB disk — ภาครัฐที่ลง plugin RBAC/Audit/Pipeline ควรเริ่ม 2 vCPU / 4 GB (JVM heap 2 GB)",
  "ห้ามรัน Build บน Master (Controller) — ให้สั่ง Agent เท่านั้น เพื่อกัน Master ล่มและกันช่องโหว่ Script Approval",
  oss_alt=["Argo Workflows","Tekton Pipelines","Woodpecker CI","Drone CI","Concourse CI"]),

T("jenkins-agent", "Jenkins Agent / Build Executor (ต่อ 1 Executor)", 1, "Pipeline Orchestration",
  ["pipeline","build","unit_test"], "oss", "MIT", "Core",
  ["CloudBees CI Agent","Azure Pipelines Agent"],
  2, 4, 60, 4, 8, 200, False, 0.3, "per_commit",
  1.20, 14, 0.05, 0.20, ["gov","enterprise","internal","aiml"],
  "1 Executor = 1 build พร้อมกัน; ประสบการณ์ทั่วไป 1 vCPU + 2 GB ต่อ executor เป็นขั้นต่ำ, 2 vCPU + 4 GB เมื่อ build Java/Node ที่มี dependency มาก",
  "จำนวน Executor = จำนวน build ที่รันขนานได้ ให้คำนวณ vCPU/RAM แบบคูณจำนวน executor; Workspace ควรมี disk 60-200 GB และตั้ง cleanup ทุกรอบ"),

T("argo-workflows", "Argo Workflows (CNCF Graduated)", 1, "Pipeline Orchestration",
  ["pipeline","webhook","audit_trail"], "oss", "Apache-2.0", "Core",
  ["Azure DevOps","CloudBees CI","Harness"],
  1, 2, 10, 2, 4, 40, True, 1.0, "resident",
  0.15, 90, 0.10, 0.20, ["gov","enterprise","aiml"],
  "Argo Workflows controller ทั่วไปตั้ง request 100m CPU / 128Mi และ limit ~500m / 1Gi; ต้องมี Kubernetes อยู่แล้ว",
  "เหมาะเมื่อมี Kubernetes แล้ว — เบากว่า Jenkins มาก แต่ต้องนับ resource ของ K8s control plane เพิ่ม"),

T("tekton", "Tekton Pipelines (CI บน Kubernetes)", 1, "Pipeline Orchestration",
  ["pipeline","webhook","quality_gate"], "oss", "Apache-2.0", "Optional",
  ["Jenkins","GitLab CI","Argo Workflows","Azure DevOps"],
  1, 2, 15, 2, 4, 40, True, 0.8, "resident",
  0.10, 90, 0.10, 0.20, ["gov", "enterprise", "internal", "aiml"],
  "Tekton controller + webhook ใช้ประมาณ 0.5-1 vCPU / 1-2 GB; งาน build ไปลง Task pod ตาม spec ของแต่ละ Pipeline",
  "CI แบบ cloud-native รันบนคลัสเตอร์เดียวกันได้ทั้ง AKS/EKS/GKE และ K3s/kubeadm — ไม่ผูกกับ SaaS",
  oss_alt=["Argo Workflows","Jenkins","Woodpecker CI"],
  fit=["cloud", "hybrid", "private", "local"]),

T("woodpecker", "Woodpecker CI (Lightweight CI คู่ Gitea/Forgejo)", 1, "Pipeline Orchestration",
  ["pipeline","webhook","build"], "oss", "Apache-2.0", "Optional",
  ["GitHub Actions","GitLab CI","Jenkins"],
  1, 2, 10, 2, 4, 30, True, 0.5, "resident",
  0.05, 90, 0.10, 0.15, ["gov", "enterprise", "internal", "startup", "aiml"],
  "Woodpecker server + agent กิน RAM ประมาณ 200-500 MB idle; ใช้ container runtime ของเครื่อง agent",
  "ทางเลือก CI เบาเมื่อใช้ Gitea/Forgejo แทน GitLab — ติดตั้งได้ทั้ง private และ local",
  oss_alt=["Jenkins","Forgejo Actions","Drone CI"],
  fit=["private", "hybrid", "local"]),

T("opa-conftest", "Open Policy Agent / Conftest (Policy-as-Code Gate)", 1, "Branch Protection",
  ["branch_protection","iac_scan","quality_gate"], "oss", "Apache-2.0", "Optional",
  ["GitHub Enterprise Branch Protection","GitLab Premium Protected Branches","Azure Branch Policies"],
  1, 1, 5, 1, 2, 10, False, 0.0, "per_pr",
  0.01, 90, 0.05, 0.10, ["gov", "enterprise", "internal", "aiml"],
  "OPA binary เดียว ใช้ RAM หลักสิบ MB ตอนประเมิน policy; ค่าขั้นต่ำ 1 vCPU / 1 GB คือการกันที่ให้ container",
  "ใช้บังคับกฎ 'ต้องมี 2 Approvers' และตรวจ Terraform/K8s YAML ก่อน Merge ตาม CORE-R1"),

T("nginx-gateway", "Nginx (Reverse Proxy / Webhook Relay)", 1, "Webhook Trigger",
  ["webhook","tls_check"], "oss", "BSD-2", "Core",
  ["F5 BIG-IP","Azure Application Gateway","AWS ALB"],
  1, 1, 10, 2, 4, 40, True, 0.3, "resident",
  0.10, 90, 0.10, 0.20, ["gov", "enterprise", "internal", "aiml"],
  "Nginx worker กิน RAM หลักสิบ MB ต่อ worker; 1 vCPU / 1 GB รองรับหลักพัน req/s ของ webhook ได้",
  "โดยทั่วไปวาง Reverse Proxy แยกเครื่อง (2 vCPU / 4 GB เพียงพอสำหรับ traffic ระดับหน่วยงาน); บนเครื่อง CI ใช้เพียง relay webhook ผ่าน Proxy Whitelist จึงกินทรัพยากรน้อยมาก"),

# ======================= STAGE 2: CHECK & SCAN =============================
T("sonarqube", "SonarQube Community Edition", 2, "SAST + Code Quality",
  ["sast","code_quality","quality_gate"], "oss", "LGPL-3.0", "Core",
  ["SonarQube Enterprise","Checkmarx SAST","Fortify SCA","Veracode Static Analysis"],
  2, 4, 30, 4, 8, 100, True, 3.5, "resident",
  0.25, 365, 0.30, 0.20, ["gov","enterprise","internal","aiml"],
  "SonarQube docs: ขั้นต่ำ 2 GB RAM ว่างสำหรับ server + 1 GB สำหรับ OS; ตัว server รัน 3 process (Web + Compute Engine + Elasticsearch) จึงควรมี 4 GB ขึ้นไป และตั้ง vm.max_map_count=524288",
  "เป็นหัวใจของ Quality Gate; ต้องมี PostgreSQL แยก (ห้ามใช้ embedded H2 ใน production) และมี Embedded Elasticsearch อยู่ในตัว ทำให้ RAM เป็นค่าคงค้างตลอดเวลา ไม่ใช่ค่าชั่วคราว — เป็นเหตุผลหลักที่เครื่อง Orchestrator มักต้องการ RAM มากกว่าที่ประเมินไว้ตอนแรก",
  oss_alt=["Semgrep","SpotBugs","Bandit","gosec","Brakeman","ESLint Security"]),

T("postgresql-tools", "PostgreSQL (ฐานข้อมูลของเครื่องมือ CI/CD)", 2, "Supporting Database",
  ["audit_trail"], "oss", "PostgreSQL License", "Core",
  ["Azure Database for PostgreSQL","AWS RDS","Oracle Database"],
  2, 4, 20, 4, 8, 100, True, 3.0, "resident",
  0.20, 2555, 0.35, 0.20, ["gov","enterprise","internal","aiml"],
  "PostgreSQL ทำงานได้ที่ 1 GB แต่ shared_buffers 25% ของ RAM + work_mem ต่อ connection ทำให้ 4 GB เป็นค่าที่ปลอดภัยเมื่อรองรับ SonarQube + Jenkins",
  "SonarQube ต้องมี PostgreSQL แยก (ห้ามใช้ embedded H2 ใน production); ถ้าเก็บ Audit Trail 7 ปีตามภาครัฐ ต้องวางแผน partition + archive"),

T("semgrep", "Semgrep (SAST แบบ Rule-based)", 2, "SAST",
  ["sast"], "oss", "LGPL-2.1", "Core",
  ["Semgrep Enterprise","Checkmarx SAST","Fortify SCA","CodeQL (GitHub Advanced Security)"],
  2, 4, 5, 4, 8, 20, False, 0.0, "per_commit",
  0.02, 180, 0.05, 0.15, ["gov","enterprise","internal","startup","aiml"],
  "Semgrep แนะนำ ~4 GB RAM สำหรับ repo ขนาดกลาง; RAM ขึ้นกับขนาดไฟล์ที่ใหญ่สุด ไม่ใช่จำนวนไฟล์",
  "เร็วกว่า SonarQube หลายเท่า เหมาะรันทุก commit เป็น Fast Gate แล้วปล่อย SonarQube รันรอบ nightly"),

T("gitleaks", "GitLeaks / TruffleHog (Secret Scanning)", 2, "Secret Scanning",
  ["secret_scan"], "oss", "MIT", "Core",
  ["GitHub Advanced Security Secret Scanning","GitLab Ultimate Secret Detection","HashiCorp Vault Radar"],
  1, 2, 3, 2, 4, 10, False, 0.0, "per_commit",
  0.01, 365, 0.05, 0.10, ["gov","enterprise","internal","startup","aiml"],
  "GitLeaks เป็น Go binary สแกน git history ด้วย regex/entropy; RAM ~200-500 MB ต่อ repo ขนาดกลาง",
  "ต้องตั้งเป็น Blocking Gate (พบ = หยุด Pipeline) ตาม PDPA-R3; ควรติดตั้ง pre-commit hook ที่ฝั่ง Developer ด้วย"),

T("dependency-check", "OWASP Dependency-Check (SCA)", 2, "Software Composition Analysis",
  ["sca","sbom"], "oss", "Apache-2.0", "Optional",
  ["Snyk Enterprise","BlackDuck (Synopsys)","JFrog Xray","Sonatype Nexus Lifecycle","Mend (WhiteSource)"],
  2, 4, 15, 4, 8, 40, False, 0.5, "nightly",
  0.05, 365, 0.10, 0.15, ["gov", "enterprise", "internal", "startup", "aiml"],
  "Dependency-Check ต้องดาวน์โหลดและ cache NVD CVE Database (~2-8 GB) และแนะนำ JVM heap 4 GB; รอบแรกใช้เวลา 20-60 นาที",
  "ควรย้ายไปรันรอบ nightly เพราะช้า และตั้ง NVD_API_KEY + local mirror เพื่อรองรับ Air-gapped ตามภาครัฐ",
  oss_alt=["Trivy","Grype (Anchore)","Dependency-Track","OSV-Scanner"]),

T("dependency-track", "OWASP Dependency-Track (SCA Dashboard)", 2, "Software Composition Analysis",
  ["sca","sbom","audit_trail","quality_gate"], "oss", "Apache-2.0", "Optional",
  ["Snyk Enterprise","Mend","JFrog Xray","Sonatype Lifecycle"],
  2, 4, 40, 4, 8, 80, True, 2.0, "resident",
  0.10, 730, 0.20, 0.20, ["gov", "enterprise", "internal", "aiml"],
  "Dependency-Track เป็น Java + PostgreSQL; docs แนะนำ 4 GB heap สำหรับทีมเล็ก และเก็บ SBOM ระยะยาว",
  "ใช้ติดตาม CVE ต่อเนื่องหลัง pipeline จบ ไม่ใช่แค่สแกนรอบเดียว — รับ CycloneDX จาก Syft/Trivy",
  oss_alt=["Trivy Operator","Grype","OSV-Scanner"],
  fit=["private", "hybrid", "local"]),

T("trivy", "Trivy (SCA + Container + IaC + Secret ในตัวเดียว)", 2, "Multi-purpose Scanner",
  ["sca","container_scan","iac_scan","secret_scan","sbom"], "oss", "Apache-2.0", "Core",
  ["Aqua Container Security","Prisma Cloud (Twistlock)","Snyk Container","JFrog Xray"],
  2, 2, 10, 2, 4, 30, False, 0.0, "per_build",
  0.03, 365, 0.05, 0.15, ["gov","enterprise","internal","startup","aiml"],
  "Trivy เป็น Go binary; vulnerability DB cache ~1-3 GB, Java DB เพิ่มอีก ~1-2 GB; RAM ปกติ < 1 GB แต่ image ใหญ่อาจถึง 2 GB",
  "คุ้มค่าที่สุดต่อ resource เพราะทำได้ 5 หน้าที่ในตัวเดียว ลดจำนวนเครื่องมือที่ต้องแชร์เครื่อง — แนะนำเป็นตัวหลักเมื่อ VM จำกัด"),

T("fossology", "FOSSology / ScanCode (License Compliance)", 2, "License Compliance",
  ["license"], "oss", "GPL-2.0", "Optional",
  ["BlackDuck License Compliance","FOSSA Enterprise","Mend (WhiteSource)","Snyk License"],
  4, 8, 30, 4, 8, 100, True, 2.0, "weekly",
  0.05, 730, 0.20, 0.10, ["gov", "enterprise", "aiml"],
  "FOSSology เป็น web app + PostgreSQL + scheduler; เอกสารแนะนำ 4 GB RAM ขึ้นไป และ CPU มากขึ้นตามจำนวน agent ที่รันขนาน",
  "ภาครัฐบังคับ 'ห้ามใช้ GPL/AGPL' — ควรรัน ScanCode Toolkit (เบากว่า, ephemeral) ทุก build และเก็บ FOSSology ไว้ทำ audit รายสัปดาห์แทน",
  oss_alt=["ScanCode Toolkit","License Finder","Licensee","REUSE"]),

T("linters", "Linters (ESLint / Pylint / golangci-lint / RuboCop)", 2, "Code Quality",
  ["code_quality"], "oss", "MIT", "Optional",
  ["SonarQube Enterprise","CodeClimate Enterprise","Codacy Enterprise"],
  1, 2, 3, 2, 4, 10, False, 0.0, "per_commit",
  0.01, 90, 0.05, 0.10, ["gov","enterprise","internal","startup","aiml"],
  "Linter ทำงานใน process เดียว ใช้ RAM 200 MB - 1 GB ตามขนาด codebase; golangci-lint อาจถึง 2 GB บน monorepo",
  "ควรรันบน Runner ของผู้ให้บริการ Git ก่อนส่ง Webhook เข้า Orchestrator ในองค์กร เพื่อไม่กินทรัพยากร VM ที่หน่วยงานต้องจัดหาเอง"),

# ======================= STAGE 3: BUILD & RUN ==============================
T("maven-gradle", "Maven / Gradle / npm / pip (Build & Compilation)", 3, "Build & Compilation",
  ["build"], "oss", "Apache-2.0", "Core",
  ["JFrog Artifactory (with Maven/Gradle)","Azure DevOps Build","AWS CodeBuild","CloudBees Build"],
  2, 4, 40, 4, 8, 120, False, 0.0, "per_commit",
  0.80, 30, 0.05, 0.20, ["gov","enterprise","internal","startup","aiml"],
  "Gradle daemon ตั้ง heap 1-2 GB โดยปริยาย; Maven fork JVM ต่อ module; local cache ~/.m2 หรือ ~/.gradle โต 5-20 GB และ node_modules 1-3 GB ต่อโปรเจกต์",
  "อย่าลืมกัน disk ให้ dependency cache — เป็นสาเหตุ 'disk full' อันดับ 1 บนเครื่อง Agent; ควรตั้ง cache cleanup รายสัปดาห์"),

T("docker-buildkit", "Docker Engine / BuildKit (Container Image Builder)", 3, "Container Image Builder",
  ["image_build","build"], "oss", "Apache-2.0", "Core",
  ["Google Cloud Build","Azure Container Registry Build","Red Hat Quay Build","AWS CodeBuild"],
  2, 4, 100, 4, 8, 300, True, 0.5, "per_commit",
  2.50, 30, 0.10, 0.25, ["gov","enterprise","internal","startup","aiml"],
  "Docker daemon idle ~200-400 MB; multi-stage build ของ Java/Node ใช้ 2-4 GB ตอน compile layer; image layer cache เป็นตัวกิน disk หลัก",
  "จุดเสี่ยงหลักคือ Disk ไม่ใช่ RAM — layer cache + dangling image โต 2-5 GB/วัน ต้องตั้ง `docker system prune` เป็น cron; ถ้าต้องการ Rootless Build ตามข้อกำหนดภาครัฐให้ใช้ Kaniko/Buildah แทน",
  oss_alt=["Kaniko","Buildah","Podman","Cloud Native Buildpacks","img","ko"]),

T("podman-buildah", "Podman / Buildah / Kaniko (Rootless Image Build)", 3, "Container Image Builder",
  ["image_build","build"], "oss", "Apache-2.0", "Optional",
  ["Docker BuildKit","Google Cloud Build","AWS CodeBuild"],
  2, 4, 80, 4, 8, 200, False, 0.0, "per_commit",
  2.00, 21, 0.10, 0.20, ["gov", "enterprise", "internal", "startup", "aiml"],
  "Buildah/Kaniko ไม่ต้องใช้ Docker daemon; RAM ใกล้เคียง Docker ตอน build (2-4 GB) แต่ idle เป็น 0 เพราะเป็น CLI/job",
  "เหมาะกับภาครัฐ/air-gap ที่ห้าม Docker daemon และอยาก build ใน Kubernetes job — ใช้ร่วมกับ Helm ได้ทุกสภาพแวดล้อม",
  oss_alt=["Docker BuildKit","img","ko"],
  fit=["cloud", "hybrid", "private", "local"]),

T("checkov", "Checkov / tfsec / KubeLinter (IaC Validation)", 3, "IaC Validation",
  ["iac_scan"], "oss", "Apache-2.0", "Optional",
  ["Prisma Cloud IaC Scanning","Snyk IaC Enterprise","Bridgecrew"],
  1, 2, 5, 2, 4, 15, False, 0.0, "per_build",
  0.01, 365, 0.05, 0.10, ["gov","enterprise","internal","aiml"],
  "Checkov เป็น Python CLI ใช้ RAM 300 MB - 1.5 GB ตามจำนวนไฟล์ Terraform/K8s; ephemeral ทั้งหมด",
  "ภาครัฐกำหนดเป็น Mandatory (ตาม OWASP A02 + CLOUD2567-R1) — ตรวจ Security Group เปิดกว้าง, ไม่มี Resource Limits, ไม่ได้เข้ารหัส Volume"),

T("cosign", "Sigstore Cosign / Notary v2 (Artifact Signing)", 3, "Artifact Signing",
  ["artifact_sign"], "oss", "Apache-2.0", "Optional",
  ["Azure Code Signing","AWS Signer","Venafi CodeSign Protect","Google Binary Authorization"],
  1, 2, 5, 1, 2, 10, False, 0.0, "per_build",
  0.01, 2555, 0.05, 0.10, ["gov","enterprise","aiml"],
  "Cosign เป็น Go binary ใช้ RAM < 300 MB; ต้องมีที่เก็บ key อย่างปลอดภัย (KMS/Vault) และ Rekor transparency log ถ้าต้องการ",
  "ภาครัฐกำหนด Mandatory ตาม OWASP A08 + NIST SSDF — ต้อง Verify signature ก่อน Pull มา Deploy ทุกครั้ง ไม่ใช่แค่ Sign"),

T("syft", "Syft / CycloneDX CLI (SBOM Generation)", 3, "SBOM",
  ["sbom"], "oss", "Apache-2.0", "Optional",
  ["JFrog Xray SBOM","Snyk SBOM","BlackDuck SBOM","Google Cloud SBOM"],
  1, 2, 5, 2, 4, 20, False, 0.0, "per_build",
  0.02, 2555, 0.05, 0.15, ["gov","enterprise","aiml"],
  "Syft สแกน image layer สร้าง SBOM; RAM ~500 MB - 2 GB ตามขนาด image; ไฟล์ SBOM 1-10 MB ต่อ artifact",
  "ภาครัฐกำหนด Mandatory ตาม OWASP A03 + NIST SP 800-161; SBOM ต้องเก็บคู่กับ artifact และเก็บนานเท่ากับอายุการใช้งานระบบ (7+ ปี)"),

# ======================= STAGE 4: TEST RUNNING =============================
T("unit-test-runner", "pytest / Jest / JUnit / Go test (Unit Test)", 4, "Unit Test",
  ["unit_test","code_quality"], "oss", "MIT", "Core",
  ["Visual Studio Test Professional","TestNG Enterprise","NCrunch","JUnit (IntelliJ Ultimate)"],
  2, 4, 20, 4, 8, 60, False, 0.0, "per_commit",
  0.10, 90, 0.05, 0.15, ["gov","enterprise","internal","startup","aiml"],
  "Test runner แบบขนาน (pytest-xdist / Jest workers) ใช้ RAM ≈ 500 MB ต่อ worker; 4 worker ≈ 2-4 GB",
  "ภาครัฐบังคับ Coverage > 80% — coverage instrumentation ทำให้ใช้ RAM และเวลาเพิ่ม ~30-50% ต้องเผื่อไว้"),

T("testcontainers", "Testcontainers / WireMock / Pact (Integration Test)", 4, "Integration Test",
  ["integration_test"], "oss", "MIT", "Core",
  ["Tricentis Tosca","SmartBear ReadyAPI","Parasoft SOAtest","Postman Enterprise"],
  4, 8, 40, 4, 8, 100, False, 0.0, "per_build",
  0.15, 90, 0.05, 0.15, ["gov","enterprise","internal","aiml"],
  "Integration test ที่ spin ฐานข้อมูล/queue จริงเป็น container ต้องบวก RAM ของ PostgreSQL (~1 GB) + Redis (~0.5 GB) + RabbitMQ (~1 GB) เข้าไปในตอนรัน",
  "เป็นขั้นที่กิน RAM สูงสุดใน Stage 4 เพราะรัน dependency จริงพร้อมกัน — อย่าให้ทับเวลากับ DAST Full Scan"),

T("owasp-zap", "OWASP ZAP (DAST + API Security)", 4, "DAST",
  ["dast","api_security","vapt"], "oss", "Apache-2.0", "Optional",
  ["Veracode Dynamic Analysis","Burp Suite Professional","Acunetix","Rapid7 InsightAppSec","StackHawk"],
  2, 4, 20, 4, 8, 60, False, 0.0, "nightly",
  0.30, 730, 0.10, 0.15, ["gov","enterprise","internal","aiml"],
  "ZAP เป็น Java app ค่าปริยาย heap ~25% ของ RAM เครื่อง; Full Scan/AJAX Spider บนเว็บใหญ่ควรตั้ง -Xmx 4 GB ขึ้นไป และ session file โต 1-10 GB ต่อรอบ",
  "แนวปฏิบัติที่ดีคือติดตั้ง ZAP บนเครื่องหนึ่งแล้วยิงสแกนข้ามเครื่องไปยัง Target ที่รันอยู่ (ห้ามยิงตัวเองเพราะจะแย่ง CPU กันจนผลเพี้ยน); การติดตั้งแบบ Native บน Host แทนการรันใน Docker ช่วยลด RAM ได้ประมาณ 15-20% เมื่อทรัพยากรจำกัด",
  oss_alt=["Nikto","w3af","Nuclei","Arachni","RESTler","Schemathesis"]),

T("nuclei", "Nuclei (Template-based Vulnerability Scan)", 4, "DAST",
  ["dast","api_security","vapt","tls_check"], "oss", "MIT", "Optional",
  ["Rapid7 InsightAppSec","Tenable.io","Qualys WAS"],
  2, 2, 10, 2, 4, 20, False, 0.0, "nightly",
  0.05, 365, 0.05, 0.15, ["gov","enterprise","internal","startup"],
  "Nuclei เป็น Go binary รัน template ขนานสูง; RAM 500 MB - 2 GB ตามจำนวน concurrency ที่ตั้ง",
  "เบากว่า ZAP มาก เหมาะรันทุกวันเป็น Fast Security Gate แล้วปล่อย ZAP Full Scan รอบสัปดาห์"),

T("locust", "Locust (Performance / Load Test)", 4, "Performance Test",
  ["perf_test"], "oss", "MIT", "Optional",
  ["BlazeMeter","LoadRunner Enterprise","NeoLoad","Gatling Enterprise"],
  4, 8, 20, 8, 16, 60, False, 0.0, "weekly",
  0.20, 730, 0.10, 0.15, ["gov","enterprise","internal","aiml"],
  "Locust ใช้ ~1 CPU core ต่อ ~1,000 concurrent users (แบบ single-process) จึงต้องรัน master + workers; แนะนำ 1 worker ต่อ core และ RAM ~1 GB ต่อ 1,000 users",
  "ข้อควรระวังสำคัญ: ถ้ารัน Load Generator บนเครื่องเดียวกับระบบที่กำลังทดสอบ ผลการวัดจะเพี้ยน เพราะแย่ง CPU กันเอง ควรแยกเครื่องหรือแยกช่วงเวลาให้ชัดเจน และต้องกันทรัพยากรไว้เต็มจำนวนในช่วงที่รัน",
  oss_alt=["K6","Apache JMeter","Gatling","Artillery","Vegeta","wrk"]),

T("playwright-a11y", "Playwright + axe-core / pa11y-ci / Lighthouse CI (Accessibility)", 4, "Accessibility Test",
  ["accessibility","integration_test"], "oss", "Apache-2.0", "Optional",
  ["Deque axe DevTools Pro","Siteimprove","Level Access"],
  2, 4, 15, 4, 8, 40, False, 0.0, "nightly",
  0.05, 365, 0.05, 0.10, ["gov","enterprise"],
  "Headless Chromium ใช้ RAM ~300-700 MB ต่อ browser context; 4 context ขนาน ≈ 2-3 GB",
  "จำเป็นสำหรับ .go.th ตาม มสพร. 11-2566 (WCAG 2.1/2.2 AA) — เป็นข้อที่โครงการภาครัฐมักตกเพราะไม่มีใน Pipeline; ต้องเก็บผลเป็นหลักฐาน Self-Assessment ตาม WEB2568-R4"),

T("testssl", "testssl.sh / sslyze / CBOMkit (TLS + Crypto Inventory)", 4, "TLS & Crypto Validation",
  ["tls_check","crypto_agility"], "oss", "GPL-2.0", "Optional",
  ["Qualys SSL Labs API","Venafi TLS Protect","Entrust"],
  1, 2, 5, 2, 2, 10, False, 0.0, "weekly",
  0.01, 365, 0.05, 0.10, ["gov", "enterprise", "aiml"],
  "testssl.sh เป็น bash + openssl ใช้ RAM < 300 MB; ใช้เวลา 2-10 นาทีต่อ endpoint",
  "ตรวจว่า TLS 1.2/1.3 เท่านั้น ไม่มี Self-signed ตาม มสพร. 11-2566 และ WEB2568-R1; CBOMkit ใช้ทำ Crypto Bill of Materials เตรียม Post-Quantum ตาม OWASP-PQC"),

# ======================= STAGE 5: STORE & VERSIONING =======================
T("harbor", "Harbor (Private Container Registry, CNCF Graduated)", 5, "Container Registry",
  ["registry","container_scan","artifact_sign","audit_trail","version_tag"], "oss", "Apache-2.0", "Core",
  ["JFrog Artifactory Enterprise","Amazon ECR","Azure Container Registry","Google Artifact Registry"],
  2, 4, 60, 4, 8, 200, True, 3.0, "resident",
  1.50, 365, 0.20, 0.30, ["gov", "enterprise", "internal", "aiml"],
  "Harbor docs: minimum 2 CPU / 4 GB RAM / 40 GB disk; recommended 4 CPU / 8 GB RAM / 160 GB disk — ประกอบด้วย core, registry, jobservice, PostgreSQL, Redis, Trivy",
  "รองรับ Air-gapped ตามข้อกำหนดภาครัฐ + มี Vulnerability Scan และ Cosign verification ในตัว; ต้องตั้ง Retention Policy ไม่งั้น disk โตไม่หยุด (2-5 GB/วัน จาก image tag ใหม่)",
  oss_alt=["Zot","Quay.io","Distribution (Docker Registry)","GitLab Container Registry"]),

T("minio", "MinIO (S3-compatible Object Storage)", 5, "Artifact Storage",
  ["registry","backup_dr","audit_trail"], "oss", "AGPL-3.0", "Core",
  ["Amazon S3","Azure Blob Storage","NetApp StorageGRID","Dell ECS"],
  2, 4, 20, 4, 8, 500, True, 1.5, "resident",
  2.00, 730, 0.15, 0.30, ["gov","enterprise","internal","aiml"],
  "MinIO ขั้นต่ำใช้งานได้ที่ 2 vCPU / 4 GB (เอกสารแนะนำ 32 GB สำหรับ production ที่โหลดสูง เพราะ cache metadata ใน RAM); erasure coding ต้องมี 4 drive ขึ้นไปถ้าต้องการ HA",
  "ใช้เป็นคลังเก็บ Container Image, Source Archive และ Report ที่เข้าถึงแบบ S3 API ได้ ต้องแยก Data Disk ออกจาก OS Disk เสมอ — ข้อควรระวัง License เป็น AGPL-3.0 ซึ่งขัดกับข้อห้าม ใช้ GPL/AGPL ของโครงการภาครัฐบางแห่ง ต้องตรวจว่าเข้าเงื่อนไข 'ไม่แก้ไข source และไม่ให้บริการต่อสาธารณะ' หรือขอ Commercial License"),

T("elasticsearch", "Elasticsearch (Log / Audit Trail Index)", 5, "Log & Audit Store",
  ["log_mgmt","audit_trail","siem_alert"], "oss", "SSPL / Elastic License", "Core",
  ["Splunk Enterprise","Datadog","Sumo Logic","Microsoft Sentinel"],
  2, 4, 40, 8, 16, 500, True, 3.5, "resident",
  4.00, 90, 0.45, 0.35, ["gov","enterprise","internal","aiml"],
  "Elasticsearch แนะนำ JVM heap ไม่เกิน 50% ของ RAM และไม่เกิน ~31 GB; ที่ 4 GB RAM ต้องตั้ง ES_JAVA_OPTS=-Xms2g -Xmx2g; index overhead รวม replica + doc_values ประมาณ 30-50% ของ raw log",
  "เป็นตัวกิน RAM และ Disk มากที่สุดในระบบ CI/CD — ถ้าต้องแชร์เครื่องกับ Orchestrator หรือ SAST ให้จำกัด heap ด้วย ES_JAVA_OPTS (เช่น 2-4 GB) เพื่อรักษาเสถียรภาพของเครื่อง; มาตรฐานขั้นต่ำ พ.ศ. 2566 บังคับเก็บ Log อย่างน้อย 90 วัน ซึ่งเป็นตัวกำหนดขนาด Data Disk โดยตรง"),

T("logstash", "Logstash (Log Pipeline / Parser)", 5, "Log Ingest",
  ["log_mgmt"], "oss", "SSPL / Elastic License", "Optional",
  ["Splunk Forwarder","Datadog Agent","Cribl Stream"],
  2, 4, 15, 2, 4, 40, True, 1.5, "resident",
  0.10, 30, 0.05, 0.20, ["gov","enterprise","internal","aiml"],
  "Logstash ค่าปริยาย heap 1 GB (แนะนำ 4-8 GB เมื่อ throughput สูง); ทุก pipeline worker กิน RAM เพิ่ม",
  "ถ้า RAM จำกัด ให้ตัด Logstash ออกและใช้ Filebeat -> Elasticsearch Ingest Pipeline โดยตรง ประหยัดได้ 1.5-4 GB ต่อเครื่อง"),

T("kibana", "Kibana (Log Visualization / Audit Review)", 5, "Log UI",
  ["log_mgmt","audit_trail","siem_alert"], "oss", "SSPL / Elastic License", "Core",
  ["Splunk Dashboards","Datadog","Grafana Enterprise"],
  1, 2, 10, 2, 4, 30, True, 1.2, "resident",
  0.05, 90, 0.05, 0.15, ["gov","enterprise","internal","aiml"],
  "Kibana เป็น Node.js app ค่าปริยาย heap ~1 GB (ปรับผ่าน NODE_OPTIONS --max-old-space-size)",
  "ใช้ตรวจ Access Log และ Audit Log ก่อนกด Approve ขึ้น Production ซึ่งเป็นหลักฐานประกอบการตรวจสอบระบบตาม พ.ร.บ. ไซเบอร์ ม.54-57"),

T("filebeat", "Filebeat (Log Shipper ต่อเครื่อง)", 5, "Log Agent",
  ["log_mgmt"], "oss", "SSPL / Elastic License", "Core",
  ["Splunk Universal Forwarder","Datadog Agent","Fluent Bit"],
  1, 1, 5, 1, 1, 10, True, 0.15, "resident",
  0.02, 7, 0.05, 0.20, ["gov","enterprise","internal","aiml"],
  "Filebeat เป็น Go binary กิน RAM 50-150 MB ต่อ instance; ต้องลงทุกเครื่องที่ต้องการเก็บ log",
  "ทั้ง 2 โครงการใช้ Filebeat ส่ง Log เข้า Elasticsearch แบบ Real-time; ต้องนับ 1 instance ต่อ 1 VM ในการคำนวณ (เล็กแต่คูณจำนวนเครื่อง)"),

T("wazuh", "Wazuh (SIEM / HIDS + Alerting)", 5, "SIEM",
  ["siem_alert","log_mgmt","audit_trail","runtime_security","config_mgmt"], "oss", "GPL-2.0", "Optional",
  ["Splunk Enterprise Security","Microsoft Sentinel","IBM QRadar","Elastic Security"],
  4, 8, 50, 8, 16, 300, True, 6.0, "resident",
  2.00, 90, 0.40, 0.30, ["gov", "enterprise", "aiml"],
  "Wazuh docs: server ขั้นต่ำ 2 vCPU / 4 GB สำหรับ < 25 agents แต่แนะนำ 4 vCPU / 8 GB ขึ้นไปเมื่อรวม Indexer; Indexer เป็น OpenSearch จึงกิน RAM แบบเดียวกับ Elasticsearch",
  "จำเป็นสำหรับ CYBER2562-R2 (เฝ้าระวัง + รายงาน สกมช. ทันที) และ PDPA-R2 (แจ้งเหตุใน 72 ชม.); ถ้ามี ELK อยู่แล้วให้พิจารณา Elastic Security แทนเพื่อไม่ต้องรัน OpenSearch ซ้อน"),

T("vault", "HashiCorp Vault / OpenBao (Secret Management)", 5, "Secret Management",
  ["secret_mgmt","iam_mfa","audit_trail"], "oss", "BUSL-1.1 / MPL-2.0", "Optional",
  ["HashiCorp Vault Enterprise","Azure Key Vault","AWS Secrets Manager","CyberArk Conjur"],
  2, 4, 20, 2, 4, 60, True, 1.0, "resident",
  0.05, 2555, 0.10, 0.15, ["gov", "enterprise", "internal", "aiml"],
  "Vault แนะนำ 2 vCPU / 4-8 GB สำหรับ production ขนาดเล็ก (มี in-memory cache + audit log); ต้องมี storage backend (Raft/Consul)",
  "ตอบ PDPA-R1 (การเข้ารหัส + Key Rotation) และ OWASP-A04; ห้ามเก็บ Credential ใน Jenkins Credentials อย่างเดียวเพราะไม่มี Rotation/Lease — Vault ต้องเปิด Audit Device ตลอดเวลา",
  oss_alt=["OpenBao","Infisical","SOPS + age","Sealed Secrets"]),

# ======================= STAGE 6: DEPLOY & UPDATE ==========================
T("k3s-control", "K3s (Lightweight Kubernetes, ต่อ 1 Node)", 6, "Container Orchestration",
  ["orchestration","deploy_strategy","iam_mfa"], "oss", "Apache-2.0", "Core",
  ["Red Hat OpenShift","Rancher Enterprise","VMware Tanzu","Google GKE Enterprise","Azure AKS"],
  2, 4, 40, 4, 8, 100, True, 2.5, "resident",
  0.30, 90, 0.15, 0.20, ["gov", "enterprise", "internal", "aiml"],
  "K3s docs: server node ขั้นต่ำ 2 vCPU / 2 GB (แนะนำ 4 GB); เหมาะกับ private / hybrid / local ไม่ใช่ managed cloud control plane",
  "ทางเลือกหลักสำหรับติดตั้ง Kubernetes เองในเครื่องหรือศูนย์ข้อมูลปิด — ใช้ Helm/Kustomize ร่วมเพื่อแพ็กเกจงานขึ้นคลัสเตอร์",
  oss_alt=["MicroK8s","K0s","kubeadm","kind","k3d"],
  fit=["private", "hybrid", "local"]),

T("kubernetes-kubeadm", "Kubernetes kubeadm (Self-managed Control Plane)", 6, "Container Orchestration",
  ["orchestration","deploy_strategy","iam_mfa"], "oss", "Apache-2.0", "Optional",
  ["Red Hat OpenShift","Rancher","VMware Tanzu","Google GKE Enterprise"],
  4, 8, 80, 8, 16, 200, True, 4.0, "resident",
  0.40, 90, 0.15, 0.20, ["gov", "enterprise", "internal", "aiml"],
  "kubeadm control plane ขั้นต่ำ 2 vCPU / 2 GB แต่ etcd + apiserver ที่โหลดจริงควรมี 4 vCPU / 8 GB ขึ้นไปต่อ node",
  "Kubernetes เต็มรูปแบบสำหรับ private/hybrid ที่ต้องการเวอร์ชัน upstream และส่วนขยายของระบบนิเวศครบ — หนักกว่า K3s",
  oss_alt=["K3s","MicroK8s","RKE2"],
  fit=["private", "hybrid"]),

T("kind-k3d", "kind / k3d (Kubernetes ใน Docker สำหรับ Local CI)", 6, "Local Kubernetes",
  ["orchestration","deploy_strategy"], "oss", "Apache-2.0", "Optional",
  ["Docker Desktop Kubernetes","Minikube","Rancher Desktop"],
  2, 8, 40, 4, 16, 80, True, 3.0, "resident",
  0.10, 14, 0.10, 0.10, ["gov", "enterprise", "internal", "startup", "aiml"],
  "kind รัน node เป็น container; แนะนำ 8 GB RAM เพราะรวม Docker engine + control plane + workload บนเครื่องพัฒนา/agent",
  "ใช้ทดสอบ pipeline และ Helm chart ในเครื่องหรือใน job CI ไม่แทนคลัสเตอร์ Production",
  oss_alt=["minikube","MicroK8s","K3s"],
  fit=["local"]),

T("microk8s", "MicroK8s (Local / Private Kubernetes)", 6, "Container Orchestration",
  ["orchestration","deploy_strategy"], "oss", "Apache-2.0", "Optional",
  ["K3s","kubeadm","Red Hat OpenShift Local"],
  2, 4, 40, 4, 8, 100, True, 2.5, "resident",
  0.25, 90, 0.15, 0.20, ["gov", "enterprise", "internal", "startup", "aiml"],
  "MicroK8s docs: เครื่องพัฒนา 4 GB ขึ้นไป; production เล็กใช้ 4 vCPU / 8 GB เมื่อเปิด dns, storage, ingress, helm",
  "ติดตั้งแบบ snap บน Ubuntu ได้ทั้ง local และ private — ทางเลือกเมื่อหน่วยงานล็อกไว้ที่ Ubuntu",
  oss_alt=["K3s","kubeadm","k0s"],
  fit=["local", "private"]),

T("helm", "Helm 3 (Kubernetes Package Manager)", 6, "Deployment Packaging",
  ["deploy_strategy","config_mgmt","version_tag"], "oss", "Apache-2.0", "Core",
  ["HashiCorp Waypoint","Rancher Apps","OpenShift Templates"],
  1, 1, 5, 1, 2, 10, False, 0.0, "per_build",
  0.02, 365, 0.05, 0.10, ["gov", "enterprise", "internal", "startup", "aiml"],
  "Helm เป็น Go CLI กิน RAM น้อย (< 200 MB); ใช้ได้กับทุกคลัสเตอร์ ทั้ง cloud managed, hybrid, private และ kind/k3d",
  "จำเป็นเมื่อต้องติดตั้งแอปเป็น chart ซ้ำได้ทุกสภาพแวดล้อม — คู่กับ kubectl/Kustomize ไม่แทน GitOps ถ้าต้องการ audit จาก Git โดยตรง",
  oss_alt=["Kustomize","carvel kapp","Helmfile"],
  fit=["cloud", "hybrid", "private", "local"]),

T("kustomize", "Kustomize (Overlay / GitOps แบบไฟล์)", 6, "Deployment Packaging",
  ["deploy_strategy","config_mgmt"], "oss", "Apache-2.0", "Optional",
  ["Helm","Jsonnet","cdk8s"],
  1, 1, 5, 1, 2, 10, False, 0.0, "per_build",
  0.01, 365, 0.05, 0.10, ["gov", "enterprise", "internal", "startup", "aiml"],
  "Kustomize รวมใน kubectl อยู่แล้ว; binary แยกใช้ RAM < 150 MB ต่อรอบ build",
  "เหมาะกับ private/air-gap ที่ไม่ต้องการ template engine ของ Helm — วาง overlay ตาม dev/uat/prod",
  oss_alt=["Helm","kustomize-controller (Flux)"],
  fit=["cloud", "hybrid", "private", "local"]),

T("argocd", "Argo CD (GitOps Continuous Delivery)", 6, "Deployment Strategy",
  ["deploy_strategy","audit_trail","quality_gate","version_tag"], "oss", "Apache-2.0", "Core",
  ["Harness CD","Spinnaker Enterprise","GitLab Premium Auto DevOps","LaunchDarkly"],
  2, 4, 20, 4, 8, 60, True, 2.0, "resident",
  0.10, 365, 0.10, 0.15, ["gov", "enterprise", "internal", "aiml"],
  "Argo CD ประกอบด้วย api-server, repo-server, application-controller, Redis; รวมกันขั้นต่ำ ~2 vCPU / 2-4 GB สำหรับ < 50 applications",
  "ให้ Git เป็น Single Source of Truth = ได้ Audit Trail และ Rollback; ใช้ได้ทั้งคลัสเตอร์ cloud และที่ติดตั้งเอง",
  oss_alt=["Flux CD","Rancher Fleet"]),

T("flux-cd", "Flux CD (GitOps, CNCF Graduated)", 6, "Deployment Strategy",
  ["deploy_strategy","audit_trail","version_tag","config_mgmt"], "oss", "Apache-2.0", "Optional",
  ["Argo CD","Harness CD","Spinnaker"],
  1, 2, 10, 2, 4, 30, True, 0.8, "resident",
  0.05, 365, 0.10, 0.15, ["gov", "enterprise", "internal", "startup", "aiml"],
  "Flux controllers (source, kustomize, helm, notification) รวมกันประมาณ 0.5-1.5 vCPU / 1-2 GB สำหรับคลัสเตอร์ขนาดเล็ก",
  "ทางเลือก GitOps ที่เบากว่า Argo CD และทำงานแบบ pull บนคลัสเตอร์ — เหมาะกับ private/hybrid ที่จำกัด RAM",
  oss_alt=["Argo CD","Rancher Fleet"]),

T("falco", "Falco (Runtime Security Monitoring, ต่อ Node)", 6, "Runtime Security",
  ["runtime_security","siem_alert"], "oss", "Apache-2.0", "Optional",
  ["Aqua Runtime Security","Prisma Cloud Runtime Defense","Sysdig Secure","Lacework"],
  1, 2, 10, 2, 4, 30, True, 0.8, "resident",
  0.50, 90, 0.20, 0.25, ["gov", "enterprise", "aiml"],
  "Falco ใช้ eBPF/kernel module ดักจับ syscall; RAM ~200-500 MB ต่อ node แต่ CPU เพิ่มขึ้นตาม syscall rate (ปกติ 5-15% ของ 1 core)",
  "ภาครัฐกำหนด 'Mandatory Real-time' — ต้องลงทุก node ที่รัน container; ระวัง event flood ทำให้ Elasticsearch โตเร็วกว่าที่ประเมิน ให้ตั้ง rule ให้แคบก่อนเปิดใช้จริง",
  oss_alt=["Tetragon","KubeArmor","Tracee","Osquery"]),

T("kyverno", "Kyverno (Kubernetes Policy / Admission)", 6, "Policy Enforcement",
  ["config_mgmt","iac_scan","quality_gate"], "oss", "Apache-2.0", "Optional",
  ["OPA Gatekeeper","HashiCorp Sentinel","Prisma Cloud"],
  1, 2, 10, 2, 4, 20, True, 0.6, "resident",
  0.05, 90, 0.10, 0.15, ["gov", "enterprise", "internal", "aiml"],
  "Kyverno admission controller แนะนำ 0.5-1 vCPU / 512 MB - 2 GB ตามจำนวน policy และขนาดคลัสเตอร์",
  "บังคับ policy บนคลัสเตอร์ (image signed, no latest tag, resource limits) ได้ทั้ง private และ cloud managed",
  oss_alt=["OPA Gatekeeper","jsPolicy"],
  fit=["cloud", "hybrid", "private", "local"]),

T("sealed-secrets", "Sealed Secrets / kubeseal (GitOps Secrets)", 5, "Secret Management",
  ["secret_mgmt"], "oss", "Apache-2.0", "Optional",
  ["HashiCorp Vault","External Secrets Operator","SOPS"],
  1, 1, 5, 1, 2, 10, True, 0.2, "resident",
  0.01, 365, 0.05, 0.10, ["gov", "enterprise", "internal", "startup", "aiml"],
  "controller ใช้ RAM ประมาณ 64-256 MB; kubeseal เป็น CLI บนเครื่องผู้พัฒนา/pipeline",
  "เข้ารหัส secret เก็บใน Git ได้ เหมาะกับ private GitOps และ air-gap ที่ยังไม่พร้อม Vault ทั้งชุด",
  oss_alt=["SOPS + age","External Secrets Operator","OpenBao"],
  fit=["hybrid", "private", "local"]),

T("prometheus", "Prometheus (Metrics & Alerting)", 6, "Monitoring",
  ["monitoring","siem_alert","notify"], "oss", "Apache-2.0", "Core",
  ["Datadog","Dynatrace","New Relic","Splunk","AppDynamics"],
  2, 4, 40, 4, 8, 200, True, 2.5, "resident",
  1.20, 180, 0.10, 0.30, ["gov","enterprise","internal","aiml"],
  "Prometheus ใช้ RAM ประมาณ 2-4 KB ต่อ active time series; 500,000 series ≈ 2-4 GB; disk ≈ 1.5-2 bytes ต่อ sample (scrape 15s = ~5,760 sample/series/วัน)",
  "สูตรประมาณ disk: series × 5,760 × 2 bytes × retention_days; 200,000 series เก็บ 180 วัน ≈ 400 GB — ถ้า disk ไม่พอให้ลด retention เป็น 30 วันแล้วส่งต่อไป Thanos/VictoriaMetrics",
  oss_alt=["VictoriaMetrics","Mimir","Zabbix","OpenTelemetry Collector"]),

T("grafana", "Grafana (Dashboard)", 6, "Monitoring UI",
  ["monitoring"], "oss", "AGPL-3.0", "Core",
  ["Datadog Dashboards","Grafana Enterprise","New Relic One"],
  1, 2, 10, 2, 4, 30, True, 0.6, "resident",
  0.02, 365, 0.05, 0.15, ["gov","enterprise","internal","aiml"],
  "Grafana เป็น Go binary กิน RAM 150-500 MB; ใช้ SQLite ในตัวหรือ PostgreSQL ภายนอก",
  "License เป็น AGPL-3.0 — เช่นเดียวกับ MinIO ต้องตรวจข้อห้าม GPL/AGPL ของภาครัฐก่อนใช้เชิงพาณิชย์/ให้บริการต่อ"),

T("grafana-loki", "Grafana Loki (Log Aggregation)", 5, "Log Store",
  ["log_mgmt","monitoring"], "oss", "AGPL-3.0", "Optional",
  ["Splunk","Datadog Logs","Elasticsearch","OpenSearch"],
  2, 4, 40, 4, 8, 200, True, 2.0, "resident",
  1.00, 90, 0.20, 0.25, ["gov", "enterprise", "internal", "aiml"],
  "Loki เก็บ index เล็กกว่า Elasticsearch; ทีมเล็กใช้ 2 vCPU / 4 GB + object storage (MinIO/S3) สำหรับ chunks",
  "ทางเลือก log สำหรับ private/hybrid ที่ใช้ Grafana อยู่แล้ว — License เป็น AGPL-3.0 ต้องตรวจนโยบายภาครัฐก่อน",
  oss_alt=["OpenSearch","VictoriaLogs","Graylog Open"],
  fit=["hybrid", "private", "local"]),

T("zabbix", "Zabbix Server (Infrastructure Monitoring)", 6, "Monitoring",
  ["monitoring","notify","siem_alert"], "oss", "AGPL-3.0", "Optional",
  ["Datadog","SolarWinds","Nagios XI","PRTG"],
  2, 4, 30, 4, 8, 150, True, 2.0, "resident",
  0.60, 365, 0.25, 0.20, ["gov","enterprise"],
  "Zabbix server ขั้นต่ำ 2 vCPU / 2 GB สำหรับ < 100 hosts แต่ต้องรวม MySQL/PostgreSQL อีก 2-4 GB; disk โตตาม history + trends",
  "ถ้าหน่วยงานมีระบบ Monitoring ส่วนกลางอยู่แล้ว (สังเกตได้จากพอร์ต 10051 ที่เปิดรออยู่บนเครื่อง) ให้ประสานส่ง metric เข้าระบบเดิม ไม่ติดตั้ง Prometheus ซ้อนอีกชุด เพื่อไม่ให้เสีย RAM ซ้ำซ้อน"),

T("ansible-chef", "Ansible / Chef Client (Config Management & Hardening)", 6, "Configuration Management",
  ["config_mgmt","iac_scan","backup_dr"], "oss", "GPL-3.0 / Apache-2.0", "Optional",
  ["Red Hat Ansible Automation Platform","Chef Enterprise Automate","Puppet Enterprise"],
  1, 2, 15, 2, 4, 40, False, 0.1, "nightly",
  0.05, 365, 0.10, 0.15, ["gov","enterprise","internal"],
  "Ansible controller ใช้ RAM ~100 MB ต่อ fork; 10 forks ≈ 1-2 GB; Chef Client บน node กิน ~300-500 MB ต่อรอบ converge",
  "ใช้ตรวจและบังคับ Configuration Baseline อัตโนมัติ เช่น Dual-Stack IPv4/IPv6, Kernel Parameter, Firewall Rule, การปิด service ที่ไม่ใช้ — ตอบข้อ Hardening Baseline ของ OWASP A02 และ MIN2566-R2"),

T("modsecurity", "ModSecurity / Coraza (Web Application Firewall)", 6, "WAF",
  ["waf","tls_check"], "oss", "Apache-2.0", "Optional",
  ["F5 Advanced WAF","Cloudflare WAF","Imperva","Azure Application Gateway WAF","AWS WAF"],
  2, 4, 15, 4, 8, 60, True, 1.0, "resident",
  0.80, 90, 0.15, 0.25, ["gov", "enterprise", "aiml"],
  "ModSecurity + OWASP CRS ทำงานเป็น module ของ Nginx/Apache; เพิ่ม RAM ~500 MB - 1 GB และ CPU ~10-30% ต่อ request เมื่อเปิด rule set เต็ม",
  "มสพร. 11-2566 'แนะนำ' แต่มาตรฐานเว็บไซต์ พ.ศ. 2568 'บังคับ' ให้ติดตั้ง WAF — ควรวางไว้ที่ Reverse Proxy หรือ API Gateway ไม่ใช่บนเครื่อง CI/CD เพราะจะกิน CPU ของ Pipeline"),

T("keycloak", "Keycloak (SSO / MFA / Identity)", 6, "Identity & Access",
  ["iam_mfa","audit_trail"], "oss", "Apache-2.0", "Optional",
  ["Microsoft Entra ID","Okta","PingFederate","ForgeRock"],
  2, 4, 20, 4, 8, 60, True, 1.5, "resident",
  0.10, 2555, 0.15, 0.20, ["gov", "enterprise", "internal", "aiml"],
  "Keycloak เป็น Quarkus app แนะนำ heap 1-2 GB สำหรับ < 10,000 users; ต้องมี PostgreSQL ภายนอกใน production",
  "ตอบ WEB2568-R1 (MFA บังคับสำหรับบัญชีสำคัญ) และ OWASP-A07 — ถ้าองค์กรมี SSO ส่วนกลางอยู่แล้ว ให้เชื่อมต่อผ่าน OIDC/SAML แทนการติดตั้งใหม่ ซึ่งประหยัดทั้ง RAM และภาระการดูแล"),

T("velero-restic", "Velero / restic / pgBackRest (Backup & DR)", 6, "Backup & DR",
  ["backup_dr"], "oss", "Apache-2.0", "Optional",
  ["Veeam","Commvault","Rubrik","Azure Backup"],
  1, 2, 20, 2, 4, 60, False, 0.2, "nightly",
  3.00, 90, 0.05, 0.25, ["gov", "enterprise", "internal", "aiml"],
  "restic/Velero ใช้ RAM ~500 MB - 2 GB ตอน backup (dedup index อยู่ใน RAM); ปริมาณ backup = ขนาดข้อมูล × จำนวน full copy + incremental",
  "MIN2566-R4 บังคับซ้อมแผน BCP ทุกปี และ CYBER2562-R3 บังคับแผนกู้คืนสำหรับ CII — Backup ต้องเก็บแยกเครื่อง/แยก site และต้องทดสอบ Restore จริง ไม่ใช่แค่ Backup ผ่าน"),

T("prowler", "Prowler / ScoutSuite (Cloud & Infra Posture Scan)", 6, "CSPM",
  ["cspm","iac_scan","config_mgmt"], "oss", "Apache-2.0", "Optional",
  ["Prisma Cloud","Wiz","Orca Security","Microsoft Defender for Cloud"],
  2, 4, 15, 2, 4, 40, False, 0.0, "weekly",
  0.05, 730, 0.10, 0.15, ["enterprise","aiml","gov"],
  "Prowler เป็น Python CLI เรียก API ของ cloud provider; RAM 1-2 GB, เวลารัน 10-60 นาทีตามขนาด account",
  "ตอบ CLOUD2567-R1 — Prowler ออกแบบมาสำหรับ Cloud API ถ้าระบบเป็น On-premise ล้วน ให้ใช้ CIS Benchmark scanner เช่น OpenSCAP หรือ Lynis แทน"),

# ======================= AI/ML SPECIFIC ===================================
T("mlflow", "MLflow (Experiment Tracking + Model Registry)", 5, "Model Registry",
  ["version_tag","registry","audit_trail","artifact_sign"], "oss", "Apache-2.0", "Core",
  ["Azure ML","AWS SageMaker Model Registry","Databricks Model Registry","Weights & Biases","Neptune.ai"],
  2, 4, 20, 4, 8, 200, True, 1.5, "resident",
  1.00, 730, 0.15, 0.40, ["aiml"],
  "MLflow tracking server เป็น Flask/Gunicorn ใช้ RAM ~500 MB - 2 GB; artifact store ควรชี้ไป MinIO/S3 ไม่ใช่ local disk",
  "จำเป็นเมื่อต้อง Track Experiment และ Model Version; ถ้าโครงการมีขั้นตอนประเมินผลโมเดล (Model / LLM Evaluation) ควรผูกผลการประเมินเข้ากับ Model Registry เพื่อตรวจย้อนหลังได้ว่า เวอร์ชันไหนผ่านเกณฑ์อะไร"),

T("llm-eval", "LLM Evaluation Runner (AI/LLM Eval Harness)", 4, "AI Model Evaluation",
  ["unit_test","integration_test","quality_gate"], "oss", "MIT", "Optional",
  ["Azure ML Quality Gates","SageMaker Model Monitor","Databricks Model Serving"],
  4, 8, 40, 8, 16, 120, False, 0.0, "per_build",
  0.50, 730, 0.10, 0.30, ["aiml"],
  "การประเมิน LLM ผ่าน API ภายนอกใช้ CPU/RAM ไม่มาก (I/O bound) แต่ถ้ารัน model ในเครื่องต้องมี GPU; batch eval ขนาดกลางใช้ 4 vCPU / 8 GB",
  "ถ้าใช้ AI Model-as-a-Service ภายนอก งานนี้จะเป็น I/O bound ใช้ CPU/RAM ไม่มาก แต่ต้อง whitelist ปลายทางที่ Proxy; ข้อควรระวังคือมักถูกวางรวมกับ Load Test, Search Engine และ Object Storage บนเครื่องเดียว จึงต้องคุมด้วยตารางเวลาไม่ให้รันทับกัน",
  gpu=False),

T("gpu-training", "GPU Training Node (Model Training / Fine-tune)", 3, "AI Model Training",
  ["build"], "oss", "N/A", "Optional",
  ["Azure ML Compute","AWS SageMaker Training","Google Vertex AI","Databricks"],
  8, 16, 200, 16, 64, 1000, False, 0.0, "weekly",
  10.00, 365, 0.10, 0.40, ["aiml"],
  "Training node ต้องมี GPU (เช่น H100/A100) + RAM >= 2 เท่าของ VRAM + NVMe สำหรับ dataset; CPU 8 core ขึ้นไปเพื่อป้อนข้อมูลไม่ให้ GPU รอ",
  "สภาพแวดล้อมของหน่วยงานหลายแห่งไม่รองรับ GPU ทำให้ต้องแยก Training Node ออกไปภายนอก — ข้อจำกัดนี้ต้องระบุใน TOR ให้ชัดว่าใครรับผิดชอบจัดหา GPU และเชื่อมต่อกันอย่างไร ไม่งั้นจะกลายเป็นข้อพิพาทตอนส่งมอบ",
  gpu=True),

# ======================= SUPPORTING / SHARED ==============================
T("redis", "Redis (Cache สำหรับเครื่องมือ CI/CD)", 5, "Supporting Cache",
  ["monitoring"], "oss", "RSALv2 / SSPL", "Optional",
  ["Azure Cache for Redis","AWS ElastiCache","Redis Enterprise"],
  1, 2, 10, 2, 4, 30, True, 1.0, "resident",
  0.05, 30, 0.10, 0.20, ["gov","enterprise","internal","aiml"],
  "Redis เก็บข้อมูลใน RAM ทั้งหมด — ขนาด RAM = ขนาด dataset × 1.5 (เผื่อ fragmentation + COW ตอน BGSAVE); ต้องตั้ง maxmemory-policy",
  "Harbor, Argo CD และ GitLab ต่างต้องใช้ Redis — ควรใช้ instance เดียวแล้วแยก database index แทนการรัน 3 instance ซึ่งประหยัด RAM ได้ 2-3 GB"),

T("rabbitmq", "RabbitMQ (Message Queue)", 5, "Supporting Queue",
  ["monitoring"], "oss", "MPL-2.0", "Optional",
  ["Azure Service Bus","AWS SQS","IBM MQ"],
  2, 4, 15, 2, 4, 60, True, 1.5, "resident",
  0.10, 30, 0.10, 0.20, ["gov","enterprise","aiml"],
  "RabbitMQ ต้องมี disk free >= 1-2 GB (disk_free_limit) ไม่งั้นจะ block publisher; RAM watermark ค่าปริยาย 40% ของ RAM เครื่อง",
  "โดยปกติเป็นของฝั่ง Application ไม่ใช่ CI/CD แต่ต้องนับรวมถ้าถูกวางบนเครื่องเดียวกับ Pipeline เพราะ RAM watermark ค่าปริยาย 40% ของเครื่องจะกินโควตาของงาน Build ไปด้วย"),

T("sftp-nfs", "SFTP / NFS File Server", 5, "File Transfer",
  ["backup_dr","registry"], "oss", "BSD", "Optional",
  ["Azure Files","AWS EFS","NetApp"],
  1, 2, 20, 2, 4, 500, True, 0.3, "resident",
  1.00, 365, 0.05, 0.25, ["gov","enterprise"],
  "sshd/nfsd กิน RAM น้อย (< 300 MB) แต่ throughput ขึ้นกับ disk I/O และ network; ต้องเผื่อ page cache",
  "มักถูกวางรวมกับ Object Storage และ Container Runtime บนเครื่องเดียว ต้องตรวจว่า RAM เหลือพอ สำหรับ metadata cache ของ Object Storage หรือไม่ เพราะ page cache ของ NFS แย่งพื้นที่เดียวกัน"),

T("scancode", "ScanCode Toolkit / License Finder (License Compliance แบบ Permissive)", 2,
  "License Compliance", ["license", "sbom"], "oss", "Apache-2.0", "Optional",
  ["BlackDuck License Compliance", "FOSSA Enterprise", "Mend (WhiteSource)", "Snyk License"],
  2, 4, 15, 2, 4, 40, False, 0.0, "per_build",
  0.02, 730, 0.05, 0.10, ["gov", "enterprise", "internal", "aiml"],
  "ScanCode เป็น Python CLI สแกนไฟล์หา license expression; RAM 1-2 GB ต่อ repo ขนาดกลาง ทำงานแบบ ephemeral",
  "ทางเลือกแทน FOSSology เมื่อโครงการห้ามใช้ GPL/AGPL — ScanCode เองเป็น Apache-2.0 จึงใช้ได้ และเบากว่ามากเพราะไม่ต้องมี web app กับฐานข้อมูลแยก",
  oss_alt=["License Finder", "Licensee", "REUSE", "Trivy license scan"]),

T("cbomkit", "CBOMkit / Crypto Inventory Scanner (Crypto Bill of Materials)", 4,
  "Crypto Inventory", ["crypto_agility", "sbom"], "oss", "Apache-2.0", "Optional",
  ["Venafi TLS Protect", "Entrust Crypto Discovery", "Keyfactor Command"],
  2, 4, 10, 2, 4, 20, False, 0.0, "weekly",
  0.02, 730, 0.05, 0.10, ["gov", "enterprise", "aiml"],
  "สแกนซอร์สโค้ดและ artifact หาอัลกอริทึมเข้ารหัสที่ใช้อยู่ แล้วออกเป็น CBOM รูปแบบ CycloneDX; RAM 1-2 GB ต่อรอบ ทำงานแบบ ephemeral",
  "ตอบข้อ Post-Quantum / Crypto-Agility โดยตรง และเป็น Apache-2.0 จึงใช้ได้ในโครงการที่ห้าม GPL (ต่างจาก testssl.sh ที่เป็น GPL-2.0) — ควรรันคู่กับการตรวจ TLS ที่ปลายทาง",
  oss_alt=["Trivy CBOM", "cryptography-inventory", "sonar-cryptography"]),


T("opensearch", "OpenSearch + OpenSearch Dashboards (Log & SIEM แบบ Apache-2.0)", 5,
  "Log & Audit Store", ["log_mgmt", "audit_trail", "siem_alert"], "oss", "Apache-2.0", "Core",
  ["Splunk Enterprise", "Datadog", "Microsoft Sentinel", "Sumo Logic"],
  4, 8, 50, 8, 16, 500, True, 6.0, "resident",
  1.50, 90, 0.45, 0.30, ["gov", "enterprise", "internal", "aiml"],
  "OpenSearch เป็น fork ของ Elasticsearch 7.10 ภายใต้ Apache-2.0; heap ไม่ควรเกิน 50% ของ RAM และไม่เกิน 31 GB "
  "ตัวเลขนี้รวม Dashboards (Node.js ~1 GB) ไว้ในเครื่องเดียวกันแล้ว",
  "ทางเลือกแทน Elasticsearch/Kibana เมื่อโครงการห้ามใช้ License แบบ source-available (SSPL / Elastic License) "
  "ซึ่งเป็นเงื่อนไขที่พบในโครงการภาครัฐบางแห่ง — มี Security Analytics plugin ทำหน้าที่ SIEM ได้ในตัว",
  oss_alt=["VictoriaLogs", "Graylog Open", "Loki (AGPL)", "Quickwit"]),

T("openbao", "OpenBao (Secret Management แบบ MPL-2.0)", 5,
  "Secret Management", ["secret_mgmt", "iam_mfa", "audit_trail"], "oss", "MPL-2.0", "Optional",
  ["HashiCorp Vault Enterprise", "Azure Key Vault", "AWS Secrets Manager", "CyberArk Conjur"],
  2, 4, 20, 2, 4, 60, True, 1.0, "resident",
  0.05, 2555, 0.10, 0.15, ["gov", "enterprise", "internal", "aiml"],
  "OpenBao เป็น fork ของ Vault 1.14 ภายใต้ MPL-2.0 ใช้ resource เท่ากัน; ต้องมี storage backend (Raft) และเปิด Audit Device",
  "ทางเลือกแทน HashiCorp Vault เมื่อโครงการห้ามใช้ License แบบ source-available (BUSL) — "
  "MPL-2.0 เป็น copyleft อ่อน ใช้เป็นบริการแยกได้โดยไม่ลามไปยังโค้ดของโครงการ",
  oss_alt=["Infisical", "SOPS + age", "Sealed Secrets"]),


# ======================= CLOUD MANAGED (SaaS — no local VM) =============
T("azure-devops", "Azure DevOps (Cloud CI/CD Platform)", 1, "Cloud CI/CD Platform",
  ["git_scm", "webhook", "branch_protection", "pipeline", "audit_trail", "quality_gate", "deploy_strategy"], "commercial", "Proprietary (SaaS)", "Core",
  ["GitHub Enterprise Cloud", "GitLab SaaS Ultimate"],
  0, 0, 0, 0, 0, 0,
  False, 0, "per_commit",
  0.02, 365, 0.1, 0.2,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed service — no self-hosted resource needed; pricing per user/pipeline minute",
  "CI/CD แบบ managed ของ Microsoft รวม Git, Boards, Pipelines, Artifacts, Test Plans ในที่เดียว รองรับ hybrid agent สำหรับ on-premise build",
  oss_alt=["GitLab CE", "Gitea + Jenkins"], managed=True),
T("github-actions", "GitHub Actions (Cloud CI/CD)", 1, "Cloud CI/CD Platform",
  ["pipeline", "webhook", "build", "deploy_strategy", "audit_trail"], "commercial", "Proprietary (SaaS / Free tier)", "Core",
  ["Azure DevOps", "AWS CodePipeline", "GitLab SaaS"],
  0, 0, 0, 0, 0, 0,
  False, 0, "per_commit",
  0.02, 90, 0.1, 0.2,
  ["enterprise", "internal", "aiml"],
  "Managed — 2,000 free minutes/month (public repos unlimited); supports self-hosted runners for on-prem builds",
  "CI/CD ของ GitHub; ecosystem ใหญ่ที่สุด (Marketplace 20K+ actions), รองรับ matrix builds, reusable workflows, OIDC federation",
  oss_alt=["Woodpecker CI", "Forgejo Actions", "Jenkins"], managed=True),
T("aws-codecommit-pipeline", "AWS CodePipeline + CodeBuild + CodeCommit", 1, "Cloud CI/CD Platform",
  ["git_scm", "webhook", "pipeline", "build", "deploy_strategy", "audit_trail"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure DevOps", "GitLab SaaS Ultimate", "GitHub Enterprise Cloud"],
  0, 0, 0, 0, 0, 0,
  False, 0, "per_commit",
  0.02, 365, 0.1, 0.2,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed — pay per pipeline execution minute and build compute; integrates with all AWS services",
  "CI/CD suite ของ AWS รวม source repo, build, deploy pipeline; รองรับ cross-account deployment, CloudFormation/CDK integration",
  oss_alt=["GitLab CE + Jenkins", "Gitea + Woodpecker"], managed=True),
T("gcp-cloud-build", "Google Cloud Build + Source Repositories", 1, "Cloud CI/CD Platform",
  ["pipeline", "build", "webhook", "image_build", "deploy_strategy"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure DevOps", "AWS CodePipeline", "GitLab SaaS"],
  0, 0, 0, 0, 0, 0,
  False, 0, "per_commit",
  0.02, 365, 0.1, 0.2,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed — 120 free build-minutes/day; supports custom workers, multi-step builds, and Cloud Deploy for CD",
  "CI/CD ของ GCP รองรับ Buildpacks, kaniko builds, Binary Authorization integration, Cloud Deploy สำหรับ progressive delivery",
  oss_alt=["Jenkins + Gitea", "Tekton + Gitea"], managed=True),
T("azure-container-registry", "Azure Container Registry (ACR)", 4, "Cloud Container Registry",
  ["registry", "container_scan", "artifact_sign"], "commercial", "Proprietary (SaaS)", "Core",
  ["AWS ECR", "Google Artifact Registry", "JFrog Artifactory Cloud"],
  0, 0, 0, 0, 0, 0,
  False, 0, "per_build",
  0.5, 365, 0.1, 0.3,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed registry — pricing per storage GB + network egress; Premium SKU supports geo-replication and private link",
  "Container registry ของ Azure รองรับ Helm charts, OCI artifacts, content trust (Notary), integrated vulnerability scanning",
  oss_alt=["Harbor", "GitLab Container Registry"], managed=True),
T("aws-ecr", "Amazon Elastic Container Registry (ECR)", 4, "Cloud Container Registry",
  ["registry", "container_scan"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure Container Registry", "Google Artifact Registry", "JFrog Artifactory Cloud"],
  0, 0, 0, 0, 0, 0,
  False, 0, "per_build",
  0.5, 365, 0.1, 0.3,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed registry — pricing per storage GB; supports image scanning, lifecycle policies, cross-region replication",
  "Container registry ของ AWS รองรับ ECR Enhanced Scanning (Inspector), lifecycle policies, cross-account access",
  oss_alt=["Harbor", "Zot"], managed=True),
T("gcp-artifact-registry", "Google Artifact Registry (GAR)", 4, "Cloud Container Registry",
  ["registry", "container_scan", "artifact_sign"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure Container Registry", "AWS ECR", "JFrog Artifactory Cloud"],
  0, 0, 0, 0, 0, 0,
  False, 0, "per_build",
  0.5, 365, 0.1, 0.3,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed registry — supports Docker, Maven, npm, Python, Apt, Yum packages; integrates with Binary Authorization",
  "Artifact registry ของ GCP รองรับ multi-format (ไม่ใช่แค่ container), Vulnerability scanning (On-Demand/Automatic), SLSA provenance",
  oss_alt=["Harbor", "Zot"], managed=True),
T("azure-kubernetes-service", "Azure Kubernetes Service (AKS)", 5, "Cloud Container Orchestration",
  ["orchestration", "deploy_strategy", "runtime_security", "monitoring"], "commercial", "Proprietary (SaaS)", "Core",
  ["AWS EKS", "Google GKE", "Red Hat OpenShift Dedicated"],
  0, 0, 0, 0, 0, 0,
  False, 0, "resident",
  0.1, 90, 0.1, 0.25,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed K8s — control plane free, pay for worker nodes; supports spot/burstable VMs",
  "Kubernetes managed ของ Azure รองรับ Azure Policy, Azure AD integration, KEDA auto-scaling, Defender for Containers",
  oss_alt=["K3s", "MicroK8s", "Kubernetes (self-managed)"], managed=True),
T("aws-eks", "Amazon Elastic Kubernetes Service (EKS)", 5, "Cloud Container Orchestration",
  ["orchestration", "deploy_strategy", "runtime_security", "monitoring"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure AKS", "Google GKE", "Red Hat OpenShift on AWS (ROSA)"],
  0, 0, 0, 0, 0, 0,
  False, 0, "resident",
  0.1, 90, 0.1, 0.25,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed K8s — control plane $0.10/hr, pay for worker nodes (EC2/Fargate); supports Karpenter auto-scaling",
  "Kubernetes managed ของ AWS รองรับ Fargate (serverless pods), GuardDuty EKS Protection, IAM Roles for Service Accounts (IRSA)",
  oss_alt=["K3s", "Kubernetes (self-managed on EC2)"], managed=True),
T("gcp-gke", "Google Kubernetes Engine (GKE)", 5, "Cloud Container Orchestration",
  ["orchestration", "deploy_strategy", "runtime_security", "monitoring"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure AKS", "AWS EKS", "Red Hat OpenShift Dedicated"],
  0, 0, 0, 0, 0, 0,
  False, 0, "resident",
  0.1, 90, 0.1, 0.25,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed K8s — Autopilot mode (fully managed nodes) or Standard mode; supports GKE Sandbox, Binary Authorization",
  "Kubernetes managed ของ GCP เป็น original contributor; GKE Autopilot จัดการ node อัตโนมัติ, รองรับ Anthos สำหรับ multi-cloud",
  oss_alt=["K3s", "Kubernetes (self-managed on GCE)"], managed=True),
T("azure-key-vault", "Azure Key Vault", 5, "Cloud Secret Management",
  ["secret_mgmt", "crypto_agility", "tls_check"], "commercial", "Proprietary (SaaS)", "Core",
  ["AWS Secrets Manager + KMS", "Google Secret Manager + Cloud KMS", "HashiCorp Vault Enterprise"],
  0, 0, 0, 0, 0, 0,
  False, 0, "resident",
  0.01, 2555, 0.05, 0.1,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed — pricing per 10K operations + HSM-backed keys; supports FIPS 140-2 Level 2/3",
  "Secret/Key management ของ Azure; HSM-backed, auto-rotation, Azure RBAC integration, supports certificates management",
  oss_alt=["OpenBao", "Infisical"], managed=True),
T("aws-secrets-manager", "AWS Secrets Manager + KMS", 5, "Cloud Secret Management",
  ["secret_mgmt", "crypto_agility"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure Key Vault", "Google Secret Manager", "HashiCorp Vault Enterprise"],
  0, 0, 0, 0, 0, 0,
  False, 0, "resident",
  0.01, 2555, 0.05, 0.1,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed — $0.40/secret/month + $0.05/10K API calls; KMS supports FIPS 140-2 Level 3 (CloudHSM)",
  "Secret management ของ AWS; auto-rotation สำหรับ RDS/Redshift/DocumentDB, CloudHSM สำหรับ compliance สูง",
  oss_alt=["OpenBao", "SOPS + age"], managed=True),
T("azure-monitor", "Azure Monitor + Log Analytics + Application Insights", 6, "Cloud Monitoring",
  ["monitoring", "log_mgmt", "siem_alert", "audit_trail"], "commercial", "Proprietary (SaaS)", "Core",
  ["AWS CloudWatch + X-Ray", "Google Cloud Operations", "Datadog", "Splunk Cloud"],
  0, 0, 0, 0, 0, 0,
  False, 0, "resident",
  1.0, 90, 0.1, 0.3,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed — pricing per GB ingested + retention; supports 30-day to 2-year retention in workspace",
  "Observability suite ของ Azure รวม metrics, logs, traces, alerts ในที่เดียว; รองรับ Microsoft Sentinel (SIEM) add-on",
  oss_alt=["Prometheus + Grafana + Loki", "ELK Stack"], managed=True),
T("aws-cloudwatch", "Amazon CloudWatch + CloudTrail + X-Ray", 6, "Cloud Monitoring",
  ["monitoring", "log_mgmt", "audit_trail", "siem_alert"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure Monitor", "Google Cloud Operations", "Datadog", "Splunk Cloud"],
  0, 0, 0, 0, 0, 0,
  False, 0, "resident",
  1.0, 90, 0.1, 0.3,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed — CloudWatch Logs pricing per GB ingested; CloudTrail free for management events",
  "Monitoring + audit ของ AWS; CloudTrail จับ API calls ทุก action, CloudWatch Logs เก็บ application logs, X-Ray สำหรับ distributed tracing",
  oss_alt=["Prometheus + Grafana + Loki", "OpenSearch"], managed=True),
T("gcp-cloud-operations", "Google Cloud Operations (Logging + Monitoring + Trace)", 6, "Cloud Monitoring",
  ["monitoring", "log_mgmt", "audit_trail", "siem_alert"], "commercial", "Proprietary (SaaS)", "Core",
  ["Azure Monitor", "AWS CloudWatch", "Datadog", "Splunk Cloud"],
  0, 0, 0, 0, 0, 0,
  False, 0, "resident",
  1.0, 90, 0.1, 0.3,
  ["gov", "enterprise", "internal", "aiml"],
  "Managed — first 50 GB/month free for logs; integrates with Chronicle SIEM for security operations",
  "Observability ของ GCP; Cloud Logging + Cloud Monitoring + Cloud Trace; รองรับ Chronicle (SIEM) และ Security Command Center",
  oss_alt=["Prometheus + Grafana + Loki", "OpenSearch"], managed=True),

]


# ---------------------------------------------------------------------------
# 6) ARCHETYPES — ผังเครื่องอ้างอิงแบบทั่วไป (ไม่ผูกกับโครงการใด)
#    ใช้เป็นจุดตั้งต้นแล้วปรับตามสภาพจริง; ช่อง spec เว้นเป็น 0 ไว้ให้กรอกเอง
#    (โปรแกรมจะแสดงค่าที่ควรขอให้ แล้วกดปุ่มเติม spec ตามค่าที่คำนวณได้)
# ---------------------------------------------------------------------------
_BLANK = dict(vcpu=0, ram_gb=0, disk_os_gb=0, disk_data_gb=0)

# ชุดเครื่องมือตามบทบาทหน้าที่ (Role Bundle) — ใช้ประกอบเป็นผังต่าง ๆ
BUNDLES = {
    "edge": dict(
        role_th="Edge / Reverse Proxy: รับ traffic ขาเข้า, WAF, TLS Termination, SSO",
        tools=["nginx-gateway", "modsecurity", "keycloak", "filebeat"]),
    "ci_control": dict(
        role_th="CI Control: Git Repository, Pipeline Orchestration, SAST และ Quality Gate",
        tools=["gitea", "jenkins-master", "sonarqube", "postgresql-tools",
               "opa-conftest", "filebeat"]),
    "build_agent": dict(
        role_th="Build Agent: Compile, Container Build, Unit/Integration Test และสแกนใน Pipeline",
        tools=["jenkins-agent", "maven-gradle", "docker-buildkit", "unit-test-runner",
               "testcontainers", "semgrep", "gitleaks", "trivy", "checkov",
               "cosign", "syft", "scancode", "linters", "filebeat"]),
    "sec_test": dict(
        role_th="Security & Performance Test: DAST, API Security, Accessibility, TLS, Load Test",
        tools=["owasp-zap", "nuclei", "dependency-check", "playwright-a11y",
               "testssl", "locust", "prowler", "filebeat"]),
    "store_log": dict(
        role_th="Store & Log: Container Registry, Object Storage, Secret Management, Log และ Audit Trail",
        tools=["harbor", "minio", "elasticsearch", "logstash", "kibana",
               "vault", "redis", "filebeat"]),
    "deploy_mon": dict(
        role_th="Deploy & Monitor: Orchestration, Helm, GitOps, Runtime Security, Observability, Backup",
        tools=["k3s-control", "helm", "kustomize", "argocd", "prometheus", "grafana", "falco",
               "ansible-chef", "velero-restic", "filebeat"]),
    "small_control": dict(
        role_th="Control (ขนาดเล็ก): Git, Pipeline, SAST และฐานข้อมูลของเครื่องมือรวมในเครื่องเดียว",
        tools=["gitea", "jenkins-master", "sonarqube", "postgresql-tools",
               "nginx-gateway", "vault", "filebeat"]),
    "small_worker": dict(
        role_th="Worker (ขนาดเล็ก): Build, Test, Registry, Storage, Log และ Scan รวมในเครื่องเดียว",
        tools=["jenkins-agent", "maven-gradle", "docker-buildkit", "unit-test-runner",
               "semgrep", "gitleaks", "trivy", "cosign", "syft", "scancode",
               "minio", "elasticsearch", "kibana", "owasp-zap", "locust", "filebeat"]),
    "ml_train": dict(
        role_th="ML Training: Fine-tune / Train โมเดล (ต้องมี GPU)",
        tools=["gpu-training", "filebeat"]),
    "ml_registry": dict(
        role_th="ML Registry & Evaluation: Experiment Tracking, Model Registry, Model/LLM Evaluation",
        tools=["mlflow", "llm-eval", "minio", "filebeat"]),
}


def _vm(name, bundle_key, extra=None, drop=None):
    b = BUNDLES[bundle_key]
    tools = [t for t in b["tools"] if t not in (drop or [])]
    tools += [t for t in (extra or []) if t not in tools]
    return dict(host=name, role_th=b["role_th"], tools=tools, spec=dict(_BLANK))


ARCHETYPES = [
    dict(id="arch-2vm", name_th="ผัง 2 เครื่อง — ขนาดเล็ก / UAT / Internal Dev", profile="internal",
         network_th="เหมาะกับทีม 5-15 คน, 1-3 แอปพลิเคชัน, ~10 builds/วัน — ยอมรับความเสี่ยงที่ Build "
                    "กับ Log แย่งทรัพยากรกันได้ในบางช่วง",
         vms=[_vm("CI-CONTROL-01", "small_control"),
              _vm("WORKER-STORE-01", "small_worker",
                  extra=["testcontainers", "prometheus", "grafana", "ansible-chef",
                         "prowler", "argocd", "k3s-control", "cbomkit"])]),

    dict(id="arch-4vm", name_th="ผัง 4 เครื่อง — มาตรฐาน (เอกชน / Enterprise)", profile="enterprise",
         network_th="แยกงานที่รันค้าง 24/7 ออกจากงาน Build ที่ burst และแยกที่เก็บข้อมูลออกจาก Compute "
                    "ทำให้ประเมินทรัพยากรและขยายได้ตรงจุด",
         vms=[_vm("CI-CONTROL-01", "ci_control", extra=["nginx-gateway", "modsecurity", "keycloak"]),
              _vm("BUILD-AGENT-01", "build_agent",
                  extra=["owasp-zap", "nuclei", "dependency-check", "locust",
                         "playwright-a11y", "testssl", "prowler"]),
              _vm("STORE-LOG-01", "store_log"),
              _vm("DEPLOY-MON-01", "deploy_mon")]),

    dict(id="arch-6vm-gov", name_th="ผัง 6 เครื่อง — ภาครัฐ / CII ครบตามมาตรฐานบังคับ", profile="gov",
         network_th="On-premise หรือ Air-gapped, แยก Edge ที่มี WAF และ SSO ออกมา และแยกเครื่อง "
                    "Security/Performance Test ไม่ให้ทับเวลากับ Pipeline หลัก",
         vms=[_vm("EDGE-01", "edge"),
              _vm("CI-CONTROL-01", "ci_control"),
              _vm("BUILD-AGENT-01", "build_agent"),
              _vm("SEC-TEST-01", "sec_test"),
              _vm("STORE-LOG-01", "store_log"),
              _vm("DEPLOY-MON-01", "deploy_mon")]),

    dict(id="arch-aiml", name_th="ผัง 5 เครื่อง — AI/ML Engineering", profile="aiml",
         network_th="เพิ่ม Model Registry และ Evaluation แยกจาก Pipeline ปกติ และแยก Training Node "
                    "ที่ต้องมี GPU ออกไป (สภาพแวดล้อมหลายแห่งไม่รองรับ GPU จึงต้องระบุผู้รับผิดชอบใน TOR)",
         vms=[_vm("CI-CONTROL-01", "ci_control", extra=["nginx-gateway", "keycloak"]),
              _vm("BUILD-AGENT-01", "build_agent",
                  extra=["owasp-zap", "nuclei", "dependency-check", "locust", "prowler"]),
              _vm("ML-REGISTRY-01", "ml_registry",
                  extra=["elasticsearch", "kibana", "vault", "testssl"]),
              _vm("ML-TRAIN-01", "ml_train"),
              _vm("DEPLOY-MON-01", "deploy_mon")]),
]

# ชื่อเดิมที่โค้ดส่วนอื่นเรียกใช้
PRESETS = ARCHETYPES

# ---------------------------------------------------------------------------
# 7) ค่าคงที่ของโมเดลการคำนวณ
# ---------------------------------------------------------------------------
MODEL = dict(
    # Duty Weight เดี่ยว w_solo = W_BASE + W_SPAN * activity_index  -> ช่วง 20% - 60%
    # เมื่อรวม n เครื่องมือ self-hosted บน VM เดียวกัน เพดานเหลือ w_max(n) ตาม ladder
    w_base=0.20,
    w_span=0.40,
    w_cross_ladder=[0.60, 0.54, 0.48, 0.42, 0.36, 0.30, 0.24, 0.20],
    w_cross_cap=8,
    # ทรัพยากรที่ต้องกันไว้ให้ OS + Container Runtime ของทุก VM
    os_reserve_vcpu=1,
    os_reserve_ram_gb=2,
    os_reserve_disk_gb=20,
    # กันที่ว่างของ Disk ไม่ให้เต็ม (ต้องเหลือว่าง 25%)
    disk_free_ratio=0.25,
    # ขั้นการจัดสรร (Allocation Ladder) — ปัดขึ้นเสมอ
    vcpu_ladder=[2, 4, 6, 8, 12, 16, 24, 32, 48, 64],
    ram_ladder=[2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256],
    disk_ladder=[20, 40, 60, 80, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000],
    # ช่วงเวลาที่ใช้ประเมินผลลัพธ์ระยะยาว (เดือน)
    horizons=[12, 24, 36, 60],
)


# ---------------------------------------------------------------------------
# 8) กลุ่มการทำงานพร้อมกัน (Concurrency Group)
#    ใช้ในเงื่อนไขที่ 2 แบบ B2 (Serialized) — ภายในกลุ่มเดียวกันถือว่า "รันต่อกันเป็นลำดับ"
#    จึงใช้ค่าสูงสุดของกลุ่ม ส่วนระหว่างกลุ่มถือว่า "ทับซ้อนกันได้" จึงบวกกัน
#      resident = process ที่ค้างอยู่ตลอด ต้องบวกทุกตัว
#      ci_seq   = ขั้นตอนภายใน Pipeline รอบเดียวกัน ทำงานเรียงต่อกัน
#      async    = งานหลังบ้าน (nightly/weekly) ที่ตั้งเวลาไม่ให้ทับ Pipeline
#      load     = งานทดสอบภาระ/ประมวลผลหนักที่ต้องจองเครื่องทั้งรอบ
# ---------------------------------------------------------------------------
CONC_GROUP = {
    # resident daemons
    "gitlab-ce": "resident", "gitea": "resident", "jenkins-master": "resident",
    "jenkins-agent": "resident", "argo-workflows": "resident", "nginx-gateway": "resident",
    "sonarqube": "resident", "postgresql-tools": "resident", "harbor": "resident",
    "minio": "resident", "elasticsearch": "resident", "logstash": "resident",
    "kibana": "resident", "filebeat": "resident", "wazuh": "resident", "vault": "resident",
    "k3s-control": "resident", "kubernetes-kubeadm": "resident", "kind-k3d": "resident",
    "microk8s": "resident", "argocd": "resident", "flux-cd": "resident", "falco": "resident",
    "prometheus": "resident", "grafana": "resident", "grafana-loki": "resident",
    "zabbix": "resident", "kyverno": "resident", "sealed-secrets": "resident",
    "modsecurity": "resident", "keycloak": "resident", "mlflow": "resident",
    "redis": "resident", "rabbitmq": "resident", "sftp-nfs": "resident",
    "fossology": "resident", "tekton": "resident", "woodpecker": "resident",
    "dependency-track": "resident",
    # ขั้นตอนใน Pipeline (เรียงต่อกัน)
    "github-actions-runner": "ci_seq", "opa-conftest": "ci_seq", "semgrep": "ci_seq",
    "gitleaks": "ci_seq", "trivy": "ci_seq", "linters": "ci_seq",
    "maven-gradle": "ci_seq", "docker-buildkit": "ci_seq", "podman-buildah": "ci_seq",
    "checkov": "ci_seq",
    "cosign": "ci_seq", "syft": "ci_seq", "unit-test-runner": "ci_seq",
    "testcontainers": "ci_seq", "helm": "ci_seq", "kustomize": "ci_seq",
    # งานหลังบ้าน
    "dependency-check": "async", "owasp-zap": "async", "nuclei": "async",
    "playwright-a11y": "async", "testssl": "async", "ansible-chef": "async",
    "velero-restic": "async", "prowler": "async",
    # งานภาระหนัก
    "locust": "load", "llm-eval": "load", "gpu-training": "load",
    "scancode": "ci_seq", "cbomkit": "async",
    "opensearch": "resident", "openbao": "resident",
    # cloud managed
    "azure-devops": "ci_seq", "github-actions": "ci_seq", "aws-codecommit-pipeline": "ci_seq", "gcp-cloud-build": "ci_seq", "azure-container-registry": "ci_seq", "aws-ecr": "ci_seq", "gcp-artifact-registry": "ci_seq", "azure-kubernetes-service": "resident", "aws-eks": "resident", "gcp-gke": "resident", "azure-key-vault": "resident", "aws-secrets-manager": "resident", "azure-monitor": "resident", "aws-cloudwatch": "resident", "gcp-cloud-operations": "resident",
}

# ---------------------------------------------------------------------------
# 9) การปรับเทียบปริมาณข้อมูล (Storage Calibration)
#    ค่าฐาน = สภาพแวดล้อม UAT / Production ขนาดเล็ก
#             ~10 builds/วัน, 1-3 แอปพลิเคชัน, ทีม 5-15 คน
#    ใช้ scale_factor ในโปรแกรมเพื่อขยายไปสู่องค์กรที่ใหญ่ขึ้น
# ---------------------------------------------------------------------------
STORAGE_BASELINE_TH = ("ค่าฐานอ้างอิงสภาพแวดล้อม UAT/Production ขนาดเล็ก: "
                       "ประมาณ 10 builds/วัน, 1-3 แอปพลิเคชัน, ทีม 5-15 คน, "
                       "log ระดับ INFO — ใช้ Scale Factor ในโปรแกรมเพื่อขยายตามขนาดจริง")

STORAGE_CAL = {
    "elasticsearch":    dict(data_daily_gb=1.50, retention_days=90,   index_overhead=0.45, growth_yr=0.30),
    "minio":            dict(data_daily_gb=1.00, retention_days=180,  index_overhead=0.15, growth_yr=0.25),
    "harbor":           dict(data_daily_gb=1.00, retention_days=180,  index_overhead=0.20, growth_yr=0.25),
    "docker-buildkit":  dict(data_daily_gb=2.00, retention_days=21,   index_overhead=0.10, growth_yr=0.20),
    "jenkins-agent":    dict(data_daily_gb=0.80, retention_days=7,    index_overhead=0.05, growth_yr=0.20),
    "jenkins-master":   dict(data_daily_gb=0.15, retention_days=180,  index_overhead=0.10, growth_yr=0.15),
    "maven-gradle":     dict(data_daily_gb=0.30, retention_days=30,   index_overhead=0.05, growth_yr=0.20),
    "postgresql-tools": dict(data_daily_gb=0.05, retention_days=2555, index_overhead=0.35, growth_yr=0.20),
    "gitlab-ce":        dict(data_daily_gb=0.05, retention_days=3650, index_overhead=0.20, growth_yr=0.25),
    "gitea":            dict(data_daily_gb=0.02, retention_days=3650, index_overhead=0.10, growth_yr=0.25),
    "sonarqube":        dict(data_daily_gb=0.10, retention_days=365,  index_overhead=0.30, growth_yr=0.20),
    "locust":           dict(data_daily_gb=0.05, retention_days=365,  index_overhead=0.10, growth_yr=0.15),
    "owasp-zap":        dict(data_daily_gb=0.15, retention_days=730,  index_overhead=0.10, growth_yr=0.15),
    "prometheus":       dict(data_daily_gb=0.80, retention_days=90,   index_overhead=0.10, growth_yr=0.30),
    "wazuh":            dict(data_daily_gb=1.00, retention_days=90,   index_overhead=0.40, growth_yr=0.30),
    "velero-restic":    dict(data_daily_gb=2.00, retention_days=90,   index_overhead=0.05, growth_yr=0.25),
    "sftp-nfs":         dict(data_daily_gb=0.50, retention_days=180,  index_overhead=0.05, growth_yr=0.25),
    "mlflow":           dict(data_daily_gb=0.50, retention_days=730,  index_overhead=0.15, growth_yr=0.40),
    "llm-eval":         dict(data_daily_gb=0.20, retention_days=365,  index_overhead=0.10, growth_yr=0.30),
    "gpu-training":     dict(data_daily_gb=5.00, retention_days=180,  index_overhead=0.10, growth_yr=0.40),
    "falco":            dict(data_daily_gb=0.30, retention_days=90,   index_overhead=0.20, growth_yr=0.25),
    "modsecurity":      dict(data_daily_gb=0.40, retention_days=90,   index_overhead=0.15, growth_yr=0.25),
    "zabbix":           dict(data_daily_gb=0.40, retention_days=365,  index_overhead=0.25, growth_yr=0.20),
}


# ---------------------------------------------------------------------------
# 9.5) การเพิ่ม profile ให้เครื่องมือ (แก้ที่นี่ ปลอดภัยกว่าการแก้ในบรรทัด T(...))
#      profile = "ประเภทโครงการที่แนะนำให้ใช้เครื่องมือนี้"
#      ต้องครอบคลุมให้ทุกประเภทโครงการหาเครื่องมือปิด capability ที่มาตรฐานเรียกร้องได้
# ---------------------------------------------------------------------------
PROFILE_EXTRA = {
    "cbomkit":         ["internal", "startup"],
    "scancode":        ["startup"],
    "cosign":          ["internal", "startup"],
    "syft":            ["internal", "startup"],
    "harbor":          ["startup"],
    "prometheus":      ["startup"],
    "grafana":         ["startup"],
    "keycloak":        ["internal", "startup"],
    "argocd":          ["internal", "startup"],
    "flux-cd":         ["internal", "startup"],
    "k3s-control":     ["internal", "startup"],
    "helm":            ["internal", "startup"],
    "kustomize":       ["internal", "startup"],
    "kind-k3d":        ["internal", "startup"],
    "tekton":          ["internal", "startup"],
    "woodpecker":      ["startup"],
    "podman-buildah":  ["startup"],
    "kyverno":         ["internal", "startup"],
    "sealed-secrets":  ["internal", "startup"],
    "dependency-track": ["internal", "startup"],
    "filebeat":        ["startup"],
    "opensearch":      ["startup"],
    "openbao":         ["startup"],
    "vault":           ["internal"],
    "velero-restic":   ["internal", "startup"],
    "modsecurity":     ["internal", "startup"],
    "playwright-a11y": ["internal", "startup"],
    "locust":          ["startup"],
    "checkov":         ["startup"],
    "testcontainers":  ["startup"],
    "opa-conftest":    ["startup"],
    "prowler":         ["internal", "startup"],
    "falco":           ["internal", "startup"],
    "ansible-chef":    ["startup"],
    "logstash":        ["startup"],
    "kibana":          ["startup"],
    "elasticsearch":   ["startup"],
    "postgresql-tools": ["startup"],
    "jenkins-master":  ["startup"],
    "jenkins-agent":   ["startup"],
    "sonarqube":       ["startup"],
    "minio":           ["startup"],
    "redis":           ["startup"],
    "nginx-gateway":   ["startup"],
    "nuclei":          ["aiml"],
    "dependency-check": ["startup", "aiml"],
    "grafana-loki":    ["internal", "startup"],
    "kubernetes-kubeadm": ["internal"],
    "microk8s":        ["internal", "startup"],
}
_PROFILE_ORDER = ["gov", "enterprise", "internal", "startup", "aiml"]

# ---- apply -----------------------------------------------------------------
_bad_extra = [k for k in PROFILE_EXTRA if k not in {t["id"] for t in TOOLS}]
assert not _bad_extra, f"PROFILE_EXTRA อ้างเครื่องมือที่ไม่มี: {_bad_extra}"

for _t in TOOLS:
    _t["conc_group"] = CONC_GROUP.get(_t["id"], "ci_seq")
    _t["license_class"] = classify_license(_t["license"])
    _merged = set(_t["profiles"]) | set(PROFILE_EXTRA.get(_t["id"], []))
    _t["profiles"] = [p for p in _PROFILE_ORDER if p in _merged]
    if _t["id"] in STORAGE_CAL:
        _t["storage"].update(STORAGE_CAL[_t["id"]])
_missing = [t["id"] for t in TOOLS if t["id"] not in CONC_GROUP]
assert not _missing, f"tools ไม่ได้กำหนด CONC_GROUP: {_missing}"

# ---------------------------------------------------------------------------
# 10) สภาพแวดล้อมที่ติดตั้งได้ + สูตรติดตั้ง (ใช้สร้าง .sh ต่อเครื่อง)
# ---------------------------------------------------------------------------
FIT_ALL = ["cloud", "hybrid", "private", "local"]
FIT_SELFHOST = ["private", "hybrid", "local"]
FIT_MANAGED = ["cloud", "hybrid"]
FIT_OVERRIDE = {
    "helm": FIT_ALL, "kustomize": FIT_ALL, "podman-buildah": FIT_ALL,
    "tekton": FIT_ALL, "kyverno": FIT_ALL, "checkov": FIT_ALL, "cosign": FIT_ALL,
    "syft": FIT_ALL, "trivy": FIT_ALL, "gitleaks": FIT_ALL, "semgrep": FIT_ALL,
    "kind-k3d": ["local"], "microk8s": ["local", "private"],
    "kubernetes-kubeadm": ["private", "hybrid"],
    "k3s-control": ["private", "hybrid", "local"],
    "woodpecker": ["private", "hybrid", "local"],
    "sealed-secrets": ["hybrid", "private", "local"],
    "grafana-loki": ["hybrid", "private", "local"],
    "dependency-track": ["private", "hybrid", "local"],
    "flux-cd": FIT_ALL, "argocd": FIT_ALL,
}


def _inst(family, packages=None, *lines):
    return dict(family=family, packages=list(packages or []), lines=list(lines))


INSTALL = {
    "gitlab-ce": _inst("binary", ["curl", "openssh-server", "ca-certificates"],
                       'need_cmd gitlab-ctl || install_from_mirror gitlab-ce gitlab-ce.deb'),
    "gitea": _inst("binary", ["git", "ca-certificates"],
                   'need_cmd gitea || install_from_mirror gitea gitea'),
    "github-actions-runner": _inst("binary", ["ca-certificates"],
                                   'need_cmd config.sh || install_from_mirror actions-runner actions-runner.tar.gz'),
    "jenkins-master": _inst("apt", ["openjdk-17-jre-headless"],
                            'need_cmd jenkins || install_from_mirror jenkins jenkins.deb'),
    "jenkins-agent": _inst("apt", ["openjdk-17-jre-headless", "git"],
                           'need_cmd agent.jar || install_from_mirror jenkins-agent agent.jar'),
    "argo-workflows": _inst("k8s", None,
                            'need_cmd argo || install_from_mirror argo argo',
                            'kubectl apply -k "$MIRROR/argo-workflows" 2>/dev/null || log "วาง manifests ของ Argo Workflows ใน $MIRROR/argo-workflows"'),
    "tekton": _inst("k8s", None,
                    'need_cmd tkn || install_from_mirror tkn tkn',
                    'kubectl apply -k "$MIRROR/tekton" 2>/dev/null || log "วาง manifests ของ Tekton ใน $MIRROR/tekton"'),
    "woodpecker": _inst("binary", ["ca-certificates"],
                        'need_cmd woodpecker-server || install_from_mirror woodpecker woodpecker-server'),
    "opa-conftest": _inst("binary", None, 'need_cmd conftest || install_from_mirror conftest conftest'),
    "nginx-gateway": _inst("apt", ["nginx"],),
    "sonarqube": _inst("apt", ["openjdk-17-jre-headless"],
                       'need_cmd sonar.sh || install_from_mirror sonarqube sonarqube.zip'),
    "postgresql-tools": _inst("apt", ["postgresql", "postgresql-contrib"],),
    "semgrep": _inst("binary", ["python3", "python3-pip"],
                     'need_cmd semgrep || install_from_mirror semgrep semgrep'),
    "gitleaks": _inst("binary", None, 'need_cmd gitleaks || install_from_mirror gitleaks gitleaks'),
    "dependency-check": _inst("binary", ["openjdk-17-jre-headless"],
                              'need_cmd dependency-check.sh || install_from_mirror dependency-check dependency-check.zip'),
    "dependency-track": _inst("binary", ["openjdk-17-jre-headless"],
                              'need_cmd java || true',
                              'install_from_mirror dependency-track dependency-track.jar || log "วาง dependency-track.jar ใน $MIRROR"'),
    "trivy": _inst("binary", None, 'need_cmd trivy || install_from_mirror trivy trivy'),
    "fossology": _inst("apt", ["fossology"],),
    "linters": _inst("apt", ["python3", "python3-pip", "nodejs", "npm"],
                     'need_cmd eslint || log "ติดตั้ง eslint/pylint/golangci-lint จาก $MIRROR ตามภาษาของโครงการ"'),
    "maven-gradle": _inst("apt", ["openjdk-17-jdk", "maven"],
                          'need_cmd gradle || install_from_mirror gradle gradle.zip'),
    "docker-buildkit": _inst("binary", ["uidmap", "dbus-user-session"],
                             'need_cmd docker || install_from_mirror docker docker.tgz',
                             'need_cmd buildctl || install_from_mirror buildkit buildkit.tgz'),
    "podman-buildah": _inst("apt", ["podman", "buildah", "skopeo"],),
    "checkov": _inst("binary", ["python3", "python3-pip"],
                     'need_cmd checkov || install_from_mirror checkov checkov'),
    "cosign": _inst("binary", None, 'need_cmd cosign || install_from_mirror cosign cosign'),
    "syft": _inst("binary", None, 'need_cmd syft || install_from_mirror syft syft'),
    "unit-test-runner": _inst("apt", ["python3", "python3-pip", "nodejs"],
                              'log "ติดตั้ง pytest/jest/junit ตามภาษาของโครงการจาก $MIRROR"'),
    "testcontainers": _inst("binary", None,
                            'log "Testcontainers ใช้ Docker/Podman ที่ติดตั้งบนเครื่องนี้"'),
    "owasp-zap": _inst("binary", ["openjdk-17-jre-headless"],
                       'need_cmd zap.sh || install_from_mirror zap zap.tar.gz'),
    "nuclei": _inst("binary", None, 'need_cmd nuclei || install_from_mirror nuclei nuclei'),
    "locust": _inst("binary", ["python3", "python3-pip"],
                    'need_cmd locust || install_from_mirror locust locust'),
    "playwright-a11y": _inst("apt", ["nodejs", "npm"],
                             'need_cmd playwright || install_from_mirror playwright playwright'),
    "testssl": _inst("apt", ["openssl", "bsdmainutils"],
                     'need_cmd testssl.sh || install_from_mirror testssl testssl.sh'),
    "harbor": _inst("binary", ["docker.io", "docker-compose"],
                    'install_from_mirror harbor harbor.tgz || log "วาง Harbor installer ใน $MIRROR"'),
    "minio": _inst("binary", None, 'need_cmd minio || install_from_mirror minio minio'),
    "elasticsearch": _inst("apt", ["elasticsearch"],),
    "logstash": _inst("apt", ["logstash"],),
    "kibana": _inst("apt", ["kibana"],),
    "filebeat": _inst("apt", ["filebeat"],),
    "wazuh": _inst("binary", None, 'install_from_mirror wazuh wazuh-manager.deb || log "วาง Wazuh package ใน $MIRROR"'),
    "vault": _inst("binary", None, 'need_cmd vault || install_from_mirror vault vault'),
    "openbao": _inst("binary", None, 'need_cmd bao || install_from_mirror openbao bao'),
    "opensearch": _inst("binary", None, 'install_from_mirror opensearch opensearch.tar.gz || log "วาง OpenSearch ใน $MIRROR"'),
    "k3s-control": _inst("k8s", None,
                         'need_cmd k3s || install_from_mirror k3s k3s',
                         'if [ ! -e /usr/local/bin/kubectl ]; then ln -sf /usr/local/bin/k3s /usr/local/bin/kubectl 2>/dev/null || true; fi'),
    "kubernetes-kubeadm": _inst("k8s", ["conntrack", "socat"],
                                'need_cmd kubeadm || install_from_mirror kubeadm kubeadm',
                                'need_cmd kubelet || install_from_mirror kubelet kubelet',
                                'need_cmd kubectl || install_from_mirror kubectl kubectl'),
    "kind-k3d": _inst("binary", ["docker.io"],
                      'need_cmd kind || install_from_mirror kind kind',
                      'need_cmd k3d || install_from_mirror k3d k3d'),
    "microk8s": _inst("apt", ["snapd"],
                      'need_cmd microk8s || log "ติดตั้ง MicroK8s จาก snap ที่ mirror ของหน่วยงาน: snap install microk8s --classic"'),
    "helm": _inst("binary", None, 'need_cmd helm || install_from_mirror helm helm'),
    "kustomize": _inst("binary", None,
                       'need_cmd kustomize || install_from_mirror kustomize kustomize',
                       'need_cmd kubectl || install_from_mirror kubectl kubectl'),
    "argocd": _inst("k8s", None,
                    'need_cmd argocd || install_from_mirror argocd argocd',
                    'kubectl apply -k "$MIRROR/argocd" 2>/dev/null || log "วาง manifests ของ Argo CD ใน $MIRROR/argocd"'),
    "flux-cd": _inst("k8s", None,
                     'need_cmd flux || install_from_mirror flux flux',
                     'log "flux install --components-extra=image-reflector-controller --export > flux.yaml แล้ว apply จาก $MIRROR"'),
    "falco": _inst("apt", ["dkms"],
                   'need_cmd falco || install_from_mirror falco falco.deb'),
    "kyverno": _inst("k8s", None,
                     'need_cmd kyverno || install_from_mirror kyverno kyverno',
                     'kubectl apply -k "$MIRROR/kyverno" 2>/dev/null || log "วาง manifests ของ Kyverno ใน $MIRROR/kyverno"'),
    "prometheus": _inst("binary", None, 'need_cmd prometheus || install_from_mirror prometheus prometheus'),
    "grafana": _inst("apt", ["grafana"],),
    "grafana-loki": _inst("binary", None, 'need_cmd loki || install_from_mirror loki loki'),
    "zabbix": _inst("apt", ["zabbix-server-pgsql", "zabbix-frontend-php"],),
    "ansible-chef": _inst("apt", ["ansible"],),
    "modsecurity": _inst("apt", ["libmodsecurity3", "nginx"],),
    "keycloak": _inst("binary", ["openjdk-17-jre-headless"],
                      'install_from_mirror keycloak keycloak.tar.gz || log "วาง Keycloak ใน $MIRROR"'),
    "velero-restic": _inst("binary", None,
                           'need_cmd velero || install_from_mirror velero velero',
                           'need_cmd restic || install_from_mirror restic restic'),
    "prowler": _inst("binary", ["python3", "python3-pip"],
                     'need_cmd prowler || install_from_mirror prowler prowler'),
    "mlflow": _inst("binary", ["python3", "python3-pip"],
                    'need_cmd mlflow || install_from_mirror mlflow mlflow'),
    "llm-eval": _inst("binary", ["python3"],
                      'log "วาง harness ประเมินโมเดลใน $MIRROR/llm-eval"'),
    "gpu-training": _inst("binary", None, 'log "โหนด GPU — ติดตั้ง CUDA/driver ตามคู่มือของหน่วยงาน"'),
    "redis": _inst("apt", ["redis-server"],),
    "rabbitmq": _inst("apt", ["rabbitmq-server"],),
    "sftp-nfs": _inst("apt", ["openssh-server", "nfs-kernel-server"],),
    "scancode": _inst("binary", ["python3", "python3-pip"],
                      'need_cmd scancode || install_from_mirror scancode scancode'),
    "cbomkit": _inst("binary", None, 'need_cmd cbomkit || install_from_mirror cbomkit cbomkit'),
    "sealed-secrets": _inst("k8s", None,
                            'need_cmd kubeseal || install_from_mirror kubeseal kubeseal',
                            'kubectl apply -k "$MIRROR/sealed-secrets" 2>/dev/null || log "วาง controller ใน $MIRROR/sealed-secrets"'),
}

for _t in TOOLS:
    if not _t.get("fit"):
        _t["fit"] = list(FIT_OVERRIDE.get(_t["id"]) or (FIT_MANAGED if _t.get("managed") else FIT_SELFHOST))
    else:
        _t["fit"] = list(_t["fit"])
    if not _t.get("install"):
        if _t.get("managed"):
            _t["install"] = _inst("managed", None,
                                  'log "managed service — ไม่ติดตั้งบน VM (' + _t["id"] + ')"')
        else:
            _t["install"] = INSTALL.get(_t["id"]) or _inst(
                "binary", None,
                'need_cmd ' + _t["id"] + ' || install_from_mirror ' + _t["id"] + ' ' + _t["id"])
    bad_fit = [x for x in _t["fit"] if x not in FIT_LABELS]
    assert not bad_fit, f"{_t['id']} fit ไม่รู้จัก: {bad_fit}"
    assert _t["install"].get("family") in ("apt", "binary", "k8s", "managed"), (
        f"{_t['id']} install.family ไม่รู้จัก")
_bad_install = [k for k in INSTALL if k not in {t["id"] for t in TOOLS}]
assert not _bad_install, f"INSTALL อ้างเครื่องมือที่ไม่มี: {_bad_install}"
