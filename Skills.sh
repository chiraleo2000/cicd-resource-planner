#!/usr/bin/env bash
# ============================================================================
# Skills.sh — CI/CD Implementation Analysis Automation Script
# Version: 1.0.0 | Date: 2026-08-05
# Description: Companion script for Skills.md
#   - Generates report templates (Markdown, DOCX-ready, Excel CSV)
#   - Organizes output directory structure
#   - Validates project inputs
#   - Extracts data from planner catalog
#
# Usage:
#   chmod +x Skills.sh
#   ./Skills.sh <command> [options]
#
# Commands:
#   init <project-name>    Create project analysis directory structure
#   report <project-dir>   Generate report templates from project config
#   catalog [filter]       Extract tool catalog data (optional: stage/category)
#   compliance <profile>   List compliance requirements for a profile
#   estimate <config>      Calculate resource estimates from config YAML
#   export <project-dir>   Export all reports to final formats
#   help                   Show this help message
# ============================================================================

set -euo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLANNER_HTML="${SCRIPT_DIR}/planner-standalone.html"
SKILLS_MD="${SCRIPT_DIR}/Skills.md"
OUTPUT_BASE="${SCRIPT_DIR}/analysis-output"
VERSION="1.0.0"
DATE_NOW="$(date '+%Y-%m-%d')"
TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# --- Helper Functions ---
log_info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_step()  { echo -e "${CYAN}[STEP]${NC} ${BOLD}$*${NC}"; }

header() {
    echo ""
    echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║  CI/CD Implementation Analysis — Skills Automation v${VERSION}   ║${NC}"
    echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_deps() {
    local missing=()
    for cmd in python3 pandoc; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_warn "Optional dependencies not found: ${missing[*]}"
        log_warn "Some export features may be limited."
        log_warn "Install with: sudo apt install ${missing[*]} (Linux) or brew install ${missing[*]} (macOS)"
    fi
}

# ============================================================================
# COMMAND: init — Create project analysis directory structure
# ============================================================================
cmd_init() {
    local project_name="${1:-}"
    if [[ -z "$project_name" ]]; then
        log_error "Usage: $0 init <project-name>"
        log_error "Example: $0 init MOC-HS-2567"
        exit 1
    fi

    local project_dir="${OUTPUT_BASE}/${project_name}"

    if [[ -d "$project_dir" ]]; then
        log_warn "Directory already exists: ${project_dir}"
        read -rp "Overwrite templates? (y/N): " confirm
        [[ "$confirm" != "y" && "$confirm" != "Y" ]] && exit 0
    fi

    log_step "Creating project directory: ${project_dir}"

    mkdir -p "${project_dir}"/{input,analysis,reports/{markdown,docx,excel},diagrams,archive}

    # Create project config template
    cat > "${project_dir}/project-config.yaml" << YAML
# CI/CD Implementation Analysis — Project Configuration
# Generated: ${DATE_NOW}
# Instructions: Fill in all fields, then run: ./Skills.sh report ${project_dir}

project:
  name: "${project_name}"
  organization: ""          # หน่วยงาน/บริษัท
  environment: "Production" # Production | UAT | DR | Development
  notes: ""                 # ข้อจำกัดพิเศษ

profile:
  type: "gov"               # gov | enterprise | internal | startup | aiml
  impact_level: "high"      # low | medium | high
  calculation_mode: "strict" # strict | realistic

team:
  size: 10                  # จำนวนทีม
  devops_count: 2           # จำนวน DevOps/SRE
  security_count: 1         # จำนวน Security engineer

workload:
  applications: 3           # จำนวน application
  builds_per_day: 10        # จำนวน build ต่อวัน
  scale_factor: 1.0         # 1.0 = baseline, 5.0 = enterprise scale

infrastructure:
  deployment: "on-premise"  # on-premise | cloud | hybrid | air-gapped
  existing_tools: []        # เครื่องมือที่มีอยู่แล้ว
  internet_access: "proxy"  # full | proxy | air-gapped
  gpu_available: false

constraints:
  license_restriction: "no-gpl"  # none | no-gpl | no-agpl | commercial-only
  budget_range_thb: ""           # เช่น "5000000-10000000"
  timeline_months: 12
  log_retention_days: 90
  audit_retention_days: 2555     # 7 ปีสำหรับภาครัฐ

compliance:
  frameworks: []  # จะถูก auto-fill ตาม profile type
  # ตัวอย่าง: [CYBER2562, PDPA2562, MIN2566, MSPR11, WEB2568, OWASP2025]

documents:
  tor: ""           # path to TOR document
  requirements: ""  # path to requirements spec
  comments: ""      # path to review comments
YAML

    # Create intake checklist
    cat > "${project_dir}/intake-checklist.md" << 'CHECKLIST'
# Intake Checklist — Project Analysis

## Phase 1: Project Context
- [ ] ชื่อโครงการและหน่วยงาน
- [ ] ประเภทโครงการ (ภาครัฐ/เอกชน/Internal/Startup/AI-ML)
- [ ] สภาพแวดล้อม (Production/UAT/DR/Dev)
- [ ] ข้อจำกัดทางกายภาพ (On-premise/Cloud/Air-gapped)
- [ ] Infrastructure เดิม
- [ ] ขนาดทีมและ role

## Phase 2: Requirements
- [ ] เอกสาร TOR / Spec (อัปโหลดใน input/)
- [ ] มาตรฐานที่ต้อง comply
- [ ] License restrictions
- [ ] Security level requirement
- [ ] SLA targets
- [ ] Budget range
- [ ] Timeline

## Phase 3: Current State
- [ ] เครื่องมือปัจจุบัน
- [ ] Pain points
- [ ] Team skill level
- [ ] Vendor/Partner
- [ ] Internet/Network constraints

## Status
- Started: ____
- Completed: ____
- Analyst: ____
CHECKLIST

    log_ok "Project initialized: ${project_dir}"
    log_info "Next steps:"
    echo "  1. Copy TOR/Spec documents to: ${project_dir}/input/"
    echo "  2. Fill in: ${project_dir}/project-config.yaml"
    echo "  3. Complete: ${project_dir}/intake-checklist.md"
    echo "  4. Run: $0 report ${project_dir}"
}

# ============================================================================
# COMMAND: report — Generate report templates from project config
# ============================================================================
cmd_report() {
    local project_dir="${1:-}"
    if [[ -z "$project_dir" || ! -d "$project_dir" ]]; then
        log_error "Usage: $0 report <project-dir>"
        log_error "Run '$0 init <name>' first to create a project directory."
        exit 1
    fi

    local config="${project_dir}/project-config.yaml"
    if [[ ! -f "$config" ]]; then
        log_error "Config not found: ${config}"
        exit 1
    fi

    log_step "Generating reports for: ${project_dir}"

    # Extract basic info from config (simple grep-based for portability)
    local pj_name pj_org pj_env profile_type impact
    pj_name=$(grep '^\s*name:' "$config" | head -1 | sed 's/.*name:\s*"\?\([^"]*\)"\?.*/\1/')
    pj_org=$(grep '^\s*organization:' "$config" | head -1 | sed 's/.*organization:\s*"\?\([^"]*\)"\?.*/\1/')
    pj_env=$(grep '^\s*environment:' "$config" | head -1 | sed 's/.*environment:\s*"\?\([^"]*\)"\?.*/\1/')
    profile_type=$(grep '^\s*type:' "$config" | head -1 | sed 's/.*type:\s*"\?\([^"]*\)"\?.*/\1/')
    impact=$(grep '^\s*impact_level:' "$config" | head -1 | sed 's/.*impact_level:\s*"\?\([^"]*\)"\?.*/\1/')

    [[ -z "$pj_name" ]] && pj_name="Unnamed Project"
    [[ -z "$pj_org" ]] && pj_org="(ไม่ระบุ)"
    [[ -z "$pj_env" ]] && pj_env="Production"
    [[ -z "$profile_type" ]] && profile_type="gov"
    [[ -z "$impact" ]] && impact="high"

    log_info "Project: ${pj_name} | Org: ${pj_org} | Profile: ${profile_type} | Impact: ${impact}"

    # --- Generate Markdown Technical Report Template ---
    generate_md_report "$project_dir" "$pj_name" "$pj_org" "$pj_env" "$profile_type" "$impact"

    # --- Generate Excel CSV Templates ---
    generate_excel_templates "$project_dir" "$pj_name"

    # --- Generate DOCX-ready Markdown (for pandoc conversion) ---
    generate_docx_template "$project_dir" "$pj_name" "$pj_org" "$profile_type"

    log_ok "All report templates generated in: ${project_dir}/reports/"
    log_info "Review and fill in the [TODO] sections, then run: $0 export ${project_dir}"
}

generate_md_report() {
    local dir="$1" name="$2" org="$3" env="$4" profile="$5" impact="$6"
    local outfile="${dir}/reports/markdown/technical-report.md"

    cat > "$outfile" << EOF
# CI/CD Implementation Analysis Report

| Field | Value |
|-------|-------|
| **Project** | ${name} |
| **Organization** | ${org} |
| **Environment** | ${env} |
| **Profile** | ${profile} |
| **Impact Level** | ${impact} |
| **Date** | ${DATE_NOW} |
| **Analyst** | [TODO] |

---

## Executive Summary (สรุปสำหรับผู้บริหาร)

> [TODO: สรุป 3-5 ประเด็นหลัก ใช้ภาษาที่ผู้บริหารเข้าใจ]

- **ต้นทุนโดยประมาณ:** [TODO] บาท/ปี
- **ระยะเวลาดำเนินการ:** [TODO] เดือน
- **ระดับความเสี่ยง:** [TODO: ต่ำ/กลาง/สูง]
- **ข้อเสนอแนะหลัก:** [TODO]

---

## 1. Requirements Analysis

### 1.1 Functional Requirements (ความต้องการเชิงหน้าที่)

| # | Requirement | Priority | Source | Status |
|---|-------------|----------|--------|--------|
| 1 | [TODO] | Must | TOR ข้อ _ | [  ] |
| 2 | [TODO] | Should | TOR ข้อ _ | [  ] |

### 1.2 Non-Functional Requirements (ความต้องการที่ไม่ใช่หน้าที่)

| Category | Requirement | Target | Source |
|----------|-------------|--------|--------|
| Performance | [TODO] | [TODO] | |
| Availability | [TODO] | 99._% | |
| Security | [TODO] | | |
| Scalability | [TODO] | | |

### 1.3 Gap Analysis

| Current State | Required State | Gap | Priority | Effort |
|---------------|----------------|-----|----------|--------|
| [TODO] | [TODO] | [TODO] | [H/M/L] | [TODO] |

---

## 2. Compliance Assessment

### 2.1 Applicable Frameworks

| Framework | Mandatory | Applicable Rules | Status |
|-----------|-----------|-----------------|--------|
$(case "$profile" in
    gov) echo "| CYBER2562 | Yes | [TODO] | [  ] |
| PDPA2562 | Yes | [TODO] | [  ] |
| MIN2566 | Yes | [TODO] | [  ] |
| MSPR11 | Yes | [TODO] | [  ] |
| WEB2568 | Yes | [TODO] | [  ] |
| OWASP2025 | Yes | [TODO] | [  ] |";;
    enterprise) echo "| PDPA2562 | Yes | [TODO] | [  ] |
| OWASP2025 | Yes | [TODO] | [  ] |
| ISO27001 | Yes | [TODO] | [  ] |
| CLOUD2567 | Yes | [TODO] | [  ] |";;
    *) echo "| OWASP2025 | Yes | [TODO] | [  ] |";;
esac)

### 2.2 Compliance Gap Matrix

| Rule ID | Requirement | Required Capabilities | Met? | Remediation |
|---------|-------------|----------------------|------|-------------|
| [TODO] | [TODO] | [TODO] | [  ] | [TODO] |

---

## 3. Resource Specification

### 3.1 VM/Server Layout (Minimum)

| VM | Role | vCPU | RAM (GB) | OS Disk | Data Disk | Tools |
|----|------|------|----------|---------|-----------|-------|
| VM-01 | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] | [TODO] |

### 3.2 Storage Projection

| Period | Total Data (GB) | Required Disk (GB) | Notes |
|--------|-----------------|-------------------|-------|
| 12 months | [TODO] | [TODO] | |
| 24 months | [TODO] | [TODO] | |
| 36 months | [TODO] | [TODO] | |

### 3.3 Calculation Method

- Method A (Peak-Max): [TODO] GB
- Method B (Weighted-Sum ${profile == "gov" && echo "strict" || echo "realistic"}): [TODO] GB
- Method C (Resident Floor): [TODO] GB
- **Final = MAX(A,B,C) + OS Reserve:** [TODO] GB

---

## 4. Tool Selection

### 4.1 Recommended Tools

| Stage | Tool | Category | License | Core/Opt | Justification |
|-------|------|----------|---------|----------|---------------|
| 1 | [TODO] | Git/Pipeline | [TODO] | Core | [TODO] |
| 2 | [TODO] | Security | [TODO] | Core | [TODO] |
| 3 | [TODO] | Build/Test | [TODO] | Core | [TODO] |
| 4 | [TODO] | Artifact | [TODO] | Core | [TODO] |
| 5 | [TODO] | Monitor | [TODO] | Core | [TODO] |

### 4.2 Alternatives Comparison

| Need | Option A (OSS) | Option B (Commercial) | Recommendation |
|------|---------------|---------------------|----------------|
| [TODO] | [TODO] | [TODO] | [TODO] |

---

## 5. Pipeline Workflow

\`\`\`mermaid
graph LR
    A[Source/Commit] --> B[Build]
    B --> C[Unit Test]
    C --> D[SAST/SCA]
    D --> E[Container Build]
    E --> F[Container Scan]
    F --> G[Deploy to UAT]
    G --> H[DAST/API Test]
    H --> I[Approval Gate]
    I --> J[Deploy to Prod]
    J --> K[Monitor/Alert]
\`\`\`

> [TODO: Customize pipeline stages per project requirements]

---

## 6. Implementation Roadmap

| Phase | Duration | Activities | Deliverables |
|-------|----------|-----------|--------------|
| 1: Foundation | Month 1-3 | [TODO] | [TODO] |
| 2: Security | Month 3-6 | [TODO] | [TODO] |
| 3: Automation | Month 6-9 | [TODO] | [TODO] |
| 4: Optimization | Month 9-12 | [TODO] | [TODO] |

---

## 7. Cost Estimation

| Category | Item | Quantity | Unit Cost (THB) | Annual (THB) | Notes |
|----------|------|----------|--------|-------|-------|
| Infrastructure | [TODO] | | | | |
| Software | [TODO] | | | | |
| Personnel | [TODO] | | | | |
| **Total** | | | | **[TODO]** | |

---

## 8. Risks & Mitigations

| # | Risk | Probability | Impact | Mitigation | Owner |
|---|------|-------------|--------|-----------|-------|
| 1 | [TODO] | [H/M/L] | [H/M/L] | [TODO] | [TODO] |

---

## Appendix

### A. Reference Documents
- TOR: [TODO: filename]
- Requirements Spec: [TODO: filename]
- Skills.md methodology reference

### B. Assumptions
- [TODO: List all assumptions made during analysis]

### C. Revision History
| Date | Version | Author | Changes |
|------|---------|--------|---------|
| ${DATE_NOW} | 0.1 | [TODO] | Initial draft |
EOF

    log_ok "  Technical report: ${outfile}"
}

generate_excel_templates() {
    local dir="$1" name="$2"
    local excel_dir="${dir}/reports/excel"

    # Sheet 1: VM Specification
    cat > "${excel_dir}/01-vm-specification.csv" << CSV
VM Name,Role,vCPU,RAM (GB),OS Disk (GB),Data Disk (GB),OS,Tools Installed,Frequency Class,Notes
VM-Orchestrator,CI/CD Core Services,,,,,Rocky Linux 9,,resident,
VM-Security,Security Scanning,,,,,Rocky Linux 9,,per_commit,
VM-Build,Build Agent,,,,,Rocky Linux 9,,per_commit,
VM-Monitor,Monitoring & Logging,,,,,Rocky Linux 9,,resident,
VM-Registry,Artifact Storage,,,,,Rocky Linux 9,,resident,
CSV

    # Sheet 2: Tool Inventory
    cat > "${excel_dir}/02-tool-inventory.csv" << CSV
Tool,Category,Stage,Core/Optional,License,Min vCPU,Min RAM (GB),Min Disk (GB),Frequency,Resident,Idle RAM (GB),Compliance Frameworks,Notes
GitLab CE,Git Repository,1,Core,MIT,4,8,40,resident,Yes,5.0,"CYBER2562;MIN2566;WEB2568",Self-hosted Git
Jenkins Master,Pipeline,1,Core,MIT,2,4,20,resident,Yes,2.0,"CYBER2562;MIN2566;PDPA2562;WEB2568",Controller only
SonarQube CE,SAST + Quality,2,Core,LGPL-3.0,2,4,30,resident,Yes,3.5,"CYBER2562;WEB2568",Needs PostgreSQL
Semgrep,SAST,2,Core,LGPL-2.1,2,4,5,per_commit,No,0.0,"CYBER2562;WEB2568",Rule-based scanner
TruffleHog,Secret Scan,2,Core,AGPL-3.0,1,2,5,per_commit,No,0.0,"PDPA2562;OWASP2025",Check GPL restriction
OWASP DependencyCheck,SCA,2,Core,Apache-2.0,2,4,10,per_build,No,0.0,"OWASP2025",CVE database
Trivy,Container Scan,3,Core,Apache-2.0,1,2,5,per_build,No,0.0,"OWASP2025",Image + IaC scan
Docker/Podman,Container Build,3,Core,Apache-2.0,2,4,40,per_build,No,0.0,"NIST",Build images
Harbor,Registry,4,Core,Apache-2.0,2,4,40,resident,Yes,2.0,"OWASP2025;NIST",Private registry
Cosign,Artifact Sign,4,Core,Apache-2.0,1,1,5,per_build,No,0.0,"NIST;OWASP2025",Keyless signing
ELK/OpenSearch,Log Management,5,Core,Apache-2.0,4,8,100,resident,Yes,6.0,"CYBER2562;PDPA2562;MIN2566",90-day retention
Prometheus+Grafana,Monitoring,5,Core,Apache-2.0,2,4,30,resident,Yes,2.0,"WEB2568;CYBER2562",Alerting
Wazuh,SIEM,5,Optional,GPL-2.0,4,8,50,resident,Yes,4.0,"CYBER2562;PDPA2562",Check GPL restriction
HashiCorp Vault,Secret Mgmt,5,Core,BUSL-1.1,2,4,20,resident,Yes,1.0,"PDPA2562;OWASP2025",Key rotation
PostgreSQL,Database,2,Core,PostgreSQL,2,4,20,resident,Yes,3.0,"CYBER2562;MIN2566",For SonarQube/GitLab
CSV

    # Sheet 3: Compliance Matrix
    cat > "${excel_dir}/03-compliance-matrix.csv" << CSV
Rule ID,Framework,Requirement (Thai),Severity,Impact Levels,Required Capabilities,Current Status,Gap,Remediation
CYBER2562-R1,พ.ร.บ.ไซเบอร์ 2562,ประเมินความเสี่ยงและตรวจสอบระบบเป็นประจำ,mandatory,"low;medium;high","vapt;audit_trail;sast;dast",,,
CYBER2562-R2,พ.ร.บ.ไซเบอร์ 2562,ระบบเฝ้าระวังภัยคุกคามและรายงาน สกมช.,mandatory,"medium;high","siem_alert;log_mgmt;notify;monitoring",,,
PDPA-R1,PDPA 2562,มาตรการรักษาความมั่นคงปลอดภัย,mandatory,"low;medium;high","secret_mgmt;iam_mfa;log_mgmt;tls_check",,,
PDPA-R3,PDPA 2562,ห้าม Credential รั่วไหลใน Source/Log,mandatory,"low;medium;high","secret_scan;secret_mgmt",,,
MIN2566-R1,มาตรฐานขั้นต่ำ 2566,เก็บ Log อย่างน้อย 90 วัน,mandatory,"low;medium;high","log_mgmt;audit_trail",,,
MIN2566-R3,มาตรฐานขั้นต่ำ 2566,ระดับสูง: VAPT + Third Party Mgmt + DR,conditional,high,"vapt;dast;sbom;sca;backup_dr",,,
WEB2568-R1,มาตรฐานเว็บไซต์ 2568,MFA + TLS 1.2+ + WAF,mandatory,"low;medium;high","iam_mfa;tls_check;waf",,,
WEB2568-R3,มาตรฐานเว็บไซต์ 2568,Penetration Testing + Secure Coding,mandatory,"low;medium;high","dast;api_security;sast;vapt",,,
OWASP-A03,OWASP Top 10:2025,Supply Chain: SBOM + SCA + Registry + Signing,mandatory,"low;medium;high","sbom;sca;registry;artifact_sign",,,
OWASP-A09,OWASP Top 10:2025,Logging & Alerting: centralized + SIEM,mandatory,"low;medium;high","log_mgmt;siem_alert;monitoring;audit_trail",,,
CSV

    # Sheet 4: Cost Breakdown
    cat > "${excel_dir}/04-cost-breakdown.csv" << CSV
Item,Category,Unit,Quantity,Unit Cost (THB),Total (THB),Frequency,Notes
VM Server,Infrastructure,VM,,,,"one-time",
Storage (SSD),Infrastructure,GB,,,,"one-time",
Network Equipment,Infrastructure,set,,,,"one-time",
OS License,Software,license,0,0,0,"annual",Rocky Linux = free
Commercial Tool License,Software,license,,,,"annual",If applicable
DevOps Engineer,Personnel,FTE,,,,"annual",
Security Engineer,Personnel,FTE,,,,"annual",
Training,Personnel,course,,,,"one-time",
Support Contract,Operation,contract,,,,"annual",
Cloud Hosting,Operation,month,,,,"monthly",If cloud
TOTAL,,,,,,"annual",
CSV

    # Sheet 5: Timeline
    cat > "${excel_dir}/05-timeline.csv" << CSV
Phase,Task,Start,End,Duration (weeks),Dependencies,Owner,Status,Notes
1-Foundation,Infrastructure Provisioning,,,,none,Infra Team,Not Started,
1-Foundation,Git Repository Setup,,,,Infra,DevOps,Not Started,
1-Foundation,Pipeline Orchestrator Setup,,,,Git,DevOps,Not Started,
1-Foundation,Basic CI Pipeline,,,,Pipeline,DevOps,Not Started,
2-Security,SAST Integration,,,,Basic CI,Security,Not Started,
2-Security,Secret Scanning,,,,Basic CI,Security,Not Started,
2-Security,SCA + License Check,,,,Basic CI,Security,Not Started,
2-Security,Container Scanning,,,,Basic CI,Security,Not Started,
3-Automation,Quality Gate Configuration,,,,SAST,DevOps,Not Started,
3-Automation,DAST Integration,,,,UAT Deploy,Security,Not Started,
3-Automation,Artifact Registry + Signing,,,,Container,DevOps,Not Started,
3-Automation,Deploy Automation,,,,Registry,DevOps,Not Started,
4-Optimize,Monitoring & Alerting,,,,Deploy,SRE,Not Started,
4-Optimize,SIEM Integration,,,,Monitoring,Security,Not Started,
4-Optimize,Performance Testing,,,,Deploy,QA,Not Started,
4-Optimize,DR & Backup Plan,,,,All,Infra,Not Started,
CSV

    log_ok "  Excel CSVs: ${excel_dir}/ (5 sheets)"
}

generate_docx_template() {
    local dir="$1" name="$2" org="$3" profile="$4"
    local outfile="${dir}/reports/docx/executive-report.md"

    cat > "$outfile" << EOF
---
title: "รายงานการวิเคราะห์ CI/CD Implementation"
subtitle: "${name}"
author: "[ชื่อผู้วิเคราะห์]"
date: "${DATE_NOW}"
organization: "${org}"
lang: th
toc: true
toc-depth: 3
geometry: "margin=2.5cm"
fontsize: 11pt
mainfont: "TH Sarabun New"
---

# บทสรุปผู้บริหาร

## ภาพรวมโครงการ

โครงการ **${name}** ต้องการระบบ CI/CD Pipeline เพื่อ [TODO: วัตถุประสงค์หลัก]

## ข้อเสนอแนะหลัก

1. [TODO: ข้อเสนอแนะที่ 1 — ใช้ภาษาที่ผู้บริหารเข้าใจ]
2. [TODO: ข้อเสนอแนะที่ 2]
3. [TODO: ข้อเสนอแนะที่ 3]

## งบประมาณโดยประมาณ

| รายการ | งบประมาณ (บาท) | หมายเหตุ |
|--------|---------------|---------|
| โครงสร้างพื้นฐาน | [TODO] | เครื่อง Server/Cloud |
| ซอฟต์แวร์ | [TODO] | License (ถ้ามี) |
| บุคลากร | [TODO] | ต่อปี |
| **รวม (ปีแรก)** | **[TODO]** | |
| **รวม (ต่อปีหลังจากนั้น)** | **[TODO]** | |

## ระยะเวลาดำเนินการ

ประมาณ **[TODO] เดือน** แบ่งเป็น 4 ระยะ

---

# บริบทและความต้องการ

## ที่มาของโครงการ

[TODO: อธิบายความเป็นมาและเหตุผลที่ต้องมี CI/CD]

## ความต้องการหลัก

1. [TODO]
2. [TODO]
3. [TODO]

## ข้อจำกัดที่ต้องพิจารณา

- [TODO: ข้อจำกัดทางกายภาพ/เครือข่าย]
- [TODO: ข้อจำกัดด้าน license]
- [TODO: ข้อจำกัดด้านบุคลากร]

---

# ทางเลือกที่เสนอ

## ทางเลือก A: Minimum (งบน้อยที่สุดที่ผ่านมาตรฐาน)

[TODO: อธิบายทางเลือกนี้ 3-5 บรรทัด]

| ด้าน | รายละเอียด |
|------|-----------|
| งบประมาณ | [TODO] บาท |
| เครื่องมือหลัก | [TODO] |
| ข้อดี | [TODO] |
| ข้อจำกัด | [TODO] |

## ทางเลือก B: Recommended (สมดุลระหว่างต้นทุนและคุณภาพ)

[TODO: อธิบาย]

## ทางเลือก C: Optimal (ครบทุกมิติ)

[TODO: อธิบาย]

## ตารางเปรียบเทียบ

| เกณฑ์ | Option A | Option B | Option C |
|-------|----------|----------|----------|
| งบประมาณ | [TODO] | [TODO] | [TODO] |
| ระยะเวลา | [TODO] | [TODO] | [TODO] |
| Compliance | [TODO] | [TODO] | [TODO] |
| Automation | [TODO] | [TODO] | [TODO] |
| Risk Level | [TODO] | [TODO] | [TODO] |

---

# แผนดำเนินงาน

## Phase 1: วางรากฐาน (เดือนที่ 1-3)
[TODO]

## Phase 2: Security Integration (เดือนที่ 3-6)
[TODO]

## Phase 3: Advanced Automation (เดือนที่ 6-9)
[TODO]

## Phase 4: Optimization & Handover (เดือนที่ 9-12)
[TODO]

---

# ความเสี่ยงและแนวทางบริหาร

| ความเสี่ยง | โอกาสเกิด | ผลกระทบ | แนวทางบริหาร |
|-----------|-----------|---------|-------------|
| [TODO] | [สูง/กลาง/ต่ำ] | [สูง/กลาง/ต่ำ] | [TODO] |

---

# ข้อเสนอแนะ

[TODO: สรุปข้อเสนอแนะสุดท้าย 3-5 ข้อ ภาษาผู้บริหาร]

---

# ภาคผนวก

## A. รายละเอียดทรัพยากรทางเทคนิค
(ดูรายละเอียดใน Excel: 01-vm-specification.csv)

## B. ตารางเครื่องมือทั้งหมด
(ดูรายละเอียดใน Excel: 02-tool-inventory.csv)

## C. Compliance Matrix ครบทุกข้อ
(ดูรายละเอียดใน Excel: 03-compliance-matrix.csv)

## D. วิธีคำนวณทรัพยากร
อ้างอิงจาก Skills.md — Resource Calculation Model (Peak-Max / Weighted-Sum / Resident Floor)
EOF

    log_ok "  Executive report (DOCX-ready): ${outfile}"
    log_info "  Convert to DOCX: pandoc ${outfile} -o ${dir}/reports/docx/executive-report.docx"
}

# ============================================================================
# COMMAND: catalog — Extract tool catalog data from planner
# ============================================================================
cmd_catalog() {
    local filter="${1:-all}"

    if [[ ! -f "$PLANNER_HTML" ]]; then
        log_error "Planner not found: ${PLANNER_HTML}"
        exit 1
    fi

    log_step "Extracting tool catalog (filter: ${filter})"

    # Use python3 to parse JSON from HTML if available
    if command -v python3 &>/dev/null; then
        python3 << 'PYEOF'
import json, re, sys

html_path = sys.argv[1] if len(sys.argv) > 1 else "planner-standalone.html"
filter_arg = sys.argv[2] if len(sys.argv) > 2 else "all"

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON catalog
match = re.search(r'window\.__CATALOG__\s*=\s*({.*?});\s*</script>', content, re.DOTALL)
if not match:
    # Try without semicolon
    match = re.search(r'window\.__CATALOG__\s*=\s*({.*?})\s*\n', content, re.DOTALL)

if not match:
    print("ERROR: Could not extract catalog JSON from HTML", file=sys.stderr)
    sys.exit(1)

try:
    catalog = json.loads(match.group(1))
except json.JSONDecodeError as e:
    print(f"ERROR: JSON parse failed: {e}", file=sys.stderr)
    sys.exit(1)

tools = catalog.get('tools', [])

# Apply filter
if filter_arg != "all":
    tools = [t for t in tools if
             str(t.get('stage','')) == filter_arg or
             filter_arg.lower() in t.get('category','').lower() or
             filter_arg.lower() in t.get('name','').lower()]

# Output as table
print(f"\n{'='*90}")
print(f"{'Tool':<35} {'Stage':<6} {'Category':<20} {'vCPU':<5} {'RAM':<5} {'Disk':<6} {'License':<12}")
print(f"{'='*90}")
for t in tools:
    mn = t.get('min', {})
    print(f"{t['name'][:34]:<35} {t.get('stage','?'):<6} {t.get('category','')[:19]:<20} "
          f"{mn.get('vcpu','?'):<5} {mn.get('ram_gb','?'):<5} {mn.get('disk_os_gb','?'):<6} "
          f"{t.get('license','')[:11]:<12}")
print(f"{'='*90}")
print(f"Total tools: {len(tools)}")
PYEOF
    else
        log_warn "python3 not available — showing raw tool count from HTML"
        local count
        count=$(grep -o '"id":"[^"]*"' "$PLANNER_HTML" | grep -c '' || echo "?")
        echo "Tool entries found in catalog: ~${count}"
        echo "Install python3 for full catalog extraction."
    fi
}

# ============================================================================
# COMMAND: compliance — List compliance requirements for a profile
# ============================================================================
cmd_compliance() {
    local profile="${1:-gov}"

    log_step "Compliance requirements for profile: ${profile}"
    echo ""

    case "$profile" in
        gov)
            echo "=== ภาครัฐ / CII ==="
            echo "Mandatory Frameworks:"
            echo "  - CYBER2562: พ.ร.บ. ไซเบอร์ 2562 (หน่วยงานรัฐ + CII)"
            echo "  - PDPA2562: พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล 2562"
            echo "  - MIN2566: มาตรฐานขั้นต่ำ พ.ศ. 2566 (ระดับสูง)"
            echo "  - MSPR11: มสพร. 11-2566 เว็บไซต์ภาครัฐ 3.0"
            echo "  - WEB2568: มาตรฐานเว็บไซต์ 2568"
            echo "  - OWASP2025: OWASP Top 10:2025"
            echo ""
            echo "Key Requirements (Impact: High):"
            echo "  - Log retention: >= 90 days"
            echo "  - Audit trail: >= 7 years (2,555 days)"
            echo "  - Coverage: > 80%"
            echo "  - VAPT: mandatory"
            echo "  - License: NO GPL/AGPL (check)"
            echo "  - MFA: mandatory for admin"
            echo "  - TLS: 1.2+ only"
            echo "  - WAF: mandatory"
            echo "  - DR plan: mandatory"
            ;;
        enterprise)
            echo "=== เอกชน / Enterprise ==="
            echo "Mandatory Frameworks:"
            echo "  - PDPA2562: พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล 2562"
            echo "  - OWASP2025: OWASP Top 10:2025"
            echo "  - ISO27001: ISO/IEC 27001 Annex A"
            echo "  - CLOUD2567: มาตรฐานคลาวด์ 2567"
            echo ""
            echo "Key Requirements (Impact: Medium):"
            echo "  - Log retention: >= 90 days"
            echo "  - Audit trail: >= 1 year"
            echo "  - Coverage: > 70%"
            echo "  - TLS: 1.2+"
            echo "  - Secret management: mandatory"
            ;;
        internal)
            echo "=== Internal Dev / R&D ==="
            echo "Mandatory Frameworks:"
            echo "  - OWASP2025: OWASP Top 10:2025"
            echo ""
            echo "Key Requirements (Impact: Low):"
            echo "  - Log retention: >= 30 days"
            echo "  - Coverage: > 60%"
            echo "  - Basic monitoring"
            ;;
        startup)
            echo "=== Startup / Fast-paced ==="
            echo "Mandatory Frameworks:"
            echo "  - OWASP2025: OWASP Top 10:2025"
            echo ""
            echo "Key Requirements (Impact: Low):"
            echo "  - Log retention: >= 14 days"
            echo "  - Coverage: > 50%"
            echo "  - Managed/SaaS preferred"
            ;;
        aiml)
            echo "=== AI/ML Engineering ==="
            echo "Mandatory Frameworks:"
            echo "  - PDPA2562: พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล 2562"
            echo "  - OWASP2025: OWASP Top 10:2025"
            echo "  - ISO27001: ISO/IEC 27001 Annex A"
            echo ""
            echo "Key Requirements (Impact: Medium):"
            echo "  - Log retention: >= 90 days"
            echo "  - Data versioning: mandatory"
            echo "  - Model registry: mandatory"
            echo "  - GPU scheduling: required"
            ;;
        *)
            log_error "Unknown profile: ${profile}"
            echo "Available profiles: gov | enterprise | internal | startup | aiml"
            exit 1
            ;;
    esac
}

# ============================================================================
# COMMAND: estimate — Quick resource estimate
# ============================================================================
cmd_estimate() {
    local config="${1:-}"

    if [[ -z "$config" ]]; then
        log_step "Quick Resource Estimate (Interactive)"
        echo ""
        read -rp "Profile type [gov/enterprise/internal/startup/aiml]: " profile
        read -rp "Number of CI/CD tools to deploy: " tool_count
        read -rp "Scale factor (1.0 = small team, 5.0 = large): " scale

        profile=${profile:-gov}
        tool_count=${tool_count:-15}
        scale=${scale:-1.0}
    else
        # Read from config file
        profile=$(grep '^\s*type:' "$config" | head -1 | sed 's/.*type:\s*"\?\([^"]*\)"\?.*/\1/')
        tool_count=15
        scale=$(grep '^\s*scale_factor:' "$config" | head -1 | sed 's/.*scale_factor:\s*\([0-9.]*\).*/\1/')
        profile=${profile:-gov}
        scale=${scale:-1.0}
    fi

    echo ""
    log_step "Estimating resources for: profile=${profile}, tools=${tool_count}, scale=${scale}"
    echo ""

    # Rough estimates based on profile
    case "$profile" in
        gov)
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║  RESOURCE ESTIMATE: ภาครัฐ (High Impact, Strict Mode)       ║"
            echo "╠══════════════════════════════════════════════════════════════╣"
            echo "║  Minimum Fleet:                                             ║"
            echo "║    VM-01 Orchestrator : 8 vCPU / 32 GB / 200 GB            ║"
            echo "║    VM-02 Build Agent  : 4 vCPU / 16 GB / 200 GB            ║"
            echo "║    VM-03 Security     : 4 vCPU / 16 GB / 100 GB            ║"
            echo "║    VM-04 Log/Monitor  : 8 vCPU / 32 GB / 500 GB            ║"
            echo "║    VM-05 Registry     : 4 vCPU / 8 GB  / 500 GB            ║"
            echo "║  ────────────────────────────────────────────────────────── ║"
            echo "║  Total Minimum: 28 vCPU / 104 GB RAM / 1,500 GB Disk       ║"
            echo "║  Cost Range: 5.25M - 17.5M+ THB/year                       ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            ;;
        enterprise)
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║  RESOURCE ESTIMATE: Enterprise (Medium Impact)              ║"
            echo "╠══════════════════════════════════════════════════════════════╣"
            echo "║  Minimum Fleet:                                             ║"
            echo "║    VM-01 Core+Build  : 8 vCPU / 24 GB / 200 GB             ║"
            echo "║    VM-02 Security    : 4 vCPU / 8 GB  / 100 GB             ║"
            echo "║    VM-03 Monitor+Log : 4 vCPU / 16 GB / 300 GB             ║"
            echo "║  ────────────────────────────────────────────────────────── ║"
            echo "║  Total Minimum: 16 vCPU / 48 GB RAM / 600 GB Disk          ║"
            echo "║  Cost Range: 1.05M - 5.25M THB/year                        ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            ;;
        internal|startup)
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║  RESOURCE ESTIMATE: Internal/Startup (Low Impact)           ║"
            echo "╠══════════════════════════════════════════════════════════════╣"
            echo "║  Minimum Fleet:                                             ║"
            echo "║    VM-01 All-in-One  : 4 vCPU / 16 GB / 150 GB             ║"
            echo "║    (or SaaS: GitHub Actions + managed services)             ║"
            echo "║  ────────────────────────────────────────────────────────── ║"
            echo "║  Total Minimum: 4 vCPU / 16 GB RAM / 150 GB Disk           ║"
            echo "║  Cost Range: 0 - 175K THB/year                             ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            ;;
        aiml)
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║  RESOURCE ESTIMATE: AI/ML Engineering (Medium-High)         ║"
            echo "╠══════════════════════════════════════════════════════════════╣"
            echo "║  Minimum Fleet:                                             ║"
            echo "║    VM-01 Core+Build  : 8 vCPU / 32 GB / 200 GB             ║"
            echo "║    VM-02 GPU Worker  : 8 vCPU / 32 GB / 500 GB + GPU       ║"
            echo "║    VM-03 Monitor+Log : 4 vCPU / 16 GB / 300 GB             ║"
            echo "║    VM-04 Model Reg   : 4 vCPU / 16 GB / 1000 GB            ║"
            echo "║  ────────────────────────────────────────────────────────── ║"
            echo "║  Total Minimum: 24 vCPU / 96 GB RAM / 2,000 GB + GPU       ║"
            echo "║  Cost Range: 1.75M - 7M+ THB/year                          ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            ;;
    esac

    echo ""
    log_info "This is a ROUGH estimate. Use 'Skills.md' methodology for precise calculation."
    log_info "Run '$0 report <project-dir>' for detailed project-specific analysis."
}

# ============================================================================
# COMMAND: export — Export reports to final formats
# ============================================================================
cmd_export() {
    local project_dir="${1:-}"
    if [[ -z "$project_dir" || ! -d "$project_dir" ]]; then
        log_error "Usage: $0 export <project-dir>"
        exit 1
    fi

    log_step "Exporting reports from: ${project_dir}"

    local docx_md="${project_dir}/reports/docx/executive-report.md"
    local docx_out="${project_dir}/reports/docx/executive-report.docx"

    # Convert Markdown to DOCX using pandoc
    if command -v pandoc &>/dev/null; then
        if [[ -f "$docx_md" ]]; then
            log_info "Converting executive report to DOCX..."
            pandoc "$docx_md" \
                -o "$docx_out" \
                --toc \
                --number-sections \
                -V geometry:margin=2.5cm \
                -V fontsize=11pt \
                2>/dev/null && log_ok "  DOCX: ${docx_out}" || log_warn "  DOCX conversion failed (font/template issue?)"
        fi
    else
        log_warn "pandoc not installed — skipping DOCX conversion"
        log_info "Install: sudo apt install pandoc (Linux) / brew install pandoc (macOS)"
        log_info "Then convert manually: pandoc ${docx_md} -o ${docx_out} --toc"
    fi

    # Convert CSVs to Excel using python3 + openpyxl
    if command -v python3 &>/dev/null; then
        local excel_dir="${project_dir}/reports/excel"
        local xlsx_out="${excel_dir}/CICD_Analysis_Report.xlsx"

        python3 << PYEOF
import sys
try:
    import openpyxl
except ImportError:
    print("WARN: openpyxl not installed. Run: pip3 install openpyxl", file=sys.stderr)
    sys.exit(0)

import csv
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

excel_dir = "${excel_dir}"
output = "${xlsx_out}"

wb = Workbook()
wb.remove(wb.active)

header_font = Font(bold=True, color="FFFFFF", size=10)
header_fill = PatternFill(start_color="1F3864", end_color="1F3864", fill_type="solid")
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

csv_files = sorted([f for f in os.listdir(excel_dir) if f.endswith('.csv')])

for csv_file in csv_files:
    sheet_name = csv_file.replace('.csv','').split('-',1)[-1][:31]
    ws = wb.create_sheet(title=sheet_name)

    with open(os.path.join(excel_dir, csv_file), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader, 1):
            for col_idx, value in enumerate(row, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = thin_border
                cell.alignment = Alignment(wrap_text=True, vertical='top')
                if row_idx == 1:
                    cell.font = header_font
                    cell.fill = header_fill

    # Auto-width columns
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max_length + 2, 40)

wb.save(output)
print(f"OK: Excel workbook saved: {output}")
PYEOF
        if [[ $? -eq 0 ]]; then
            log_ok "  Excel: ${xlsx_out}"
        fi
    else
        log_warn "python3 not available — CSVs remain as-is (open in Excel manually)"
    fi

    # Summary
    echo ""
    log_ok "Export complete!"
    echo ""
    echo "  Output files:"
    find "${project_dir}/reports" -type f \( -name "*.docx" -o -name "*.xlsx" -o -name "*.md" -o -name "*.csv" \) | sort | while read -r f; do
        echo "    $(basename "$f")"
    done
}

# ============================================================================
# COMMAND: help — Show usage
# ============================================================================
cmd_help() {
    header
    cat << 'HELP'
Usage: ./Skills.sh <command> [options]

Commands:
  init <project-name>     Create project analysis directory with templates
  report <project-dir>    Generate report templates from project config
  catalog [filter]        Extract tool catalog (filter by stage/name/category)
  compliance <profile>    Show compliance requirements (gov|enterprise|internal|startup|aiml)
  estimate [config]       Quick resource estimate (interactive or from config)
  export <project-dir>    Convert reports to DOCX + Excel (requires pandoc, openpyxl)
  help                    Show this help message

Examples:
  ./Skills.sh init MOC-HS-2567
  ./Skills.sh compliance gov
  ./Skills.sh estimate
  ./Skills.sh catalog security
  ./Skills.sh report ./analysis-output/MOC-HS-2567
  ./Skills.sh export ./analysis-output/MOC-HS-2567

Dependencies (optional):
  - python3       : catalog extraction, Excel generation
  - pandoc        : Markdown → DOCX conversion
  - openpyxl      : CSV → XLSX conversion (pip3 install openpyxl)

Workflow:
  1. init    → Create project structure
  2. (Fill in project-config.yaml + copy TOR to input/)
  3. report  → Generate all template files
  4. (Fill in [TODO] sections using AI analysis from Skills.md)
  5. export  → Convert to final DOCX + Excel formats

Reference:
  - Skills.md    : Full methodology and analysis framework
  - planner-standalone.html : Interactive tool catalog + compliance checker
HELP
}

# ============================================================================
# MAIN — Command Router
# ============================================================================
main() {
    local cmd="${1:-help}"
    shift 2>/dev/null || true

    header
    check_deps

    case "$cmd" in
        init)       cmd_init "$@" ;;
        report)     cmd_report "$@" ;;
        catalog)    cmd_catalog "$@" ;;
        compliance) cmd_compliance "$@" ;;
        estimate)   cmd_estimate "$@" ;;
        export)     cmd_export "$@" ;;
        help|--help|-h) cmd_help ;;
        *)
            log_error "Unknown command: ${cmd}"
            echo "Run '$0 help' for usage."
            exit 1
            ;;
    esac
}

main "$@"
