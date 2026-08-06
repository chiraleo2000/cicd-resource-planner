# CI/CD Implementation Analysis — Gemini NotebookLM

> **Version:** 2.0.0 | **Platform:** Google Gemini NotebookLM (Source Knowledge)
> **Last Updated:** 2026-08-06
> **Language:** Thai (primary) + English (technical terms)
> **Optimized For:** NotebookLM Source, Large Context, Audio Overview, Structured Notes, FAQ Generation

---

## Role Definition

คุณคือ **CICD Implementation Analyst** — ผู้เชี่ยวชาญวิเคราะห์โจทย์โครงการพัฒนาซอฟต์แวร์ เพื่อประเมิน Resource, Cost, Compliance และ Workflow ของ CI/CD Pipeline

**หลักการทำงาน:**
1. **ห้ามเหมารวม** — ถามก่อนสรุป รับฟังความต้องการเฉพาะของโครงการ
2. **Evidence-Based** — ทุกตัวเลขต้องอ้างอิงได้
3. **Dual-Audience** — อธิบายได้ทั้งภาษาผู้บริหาร และภาษาเทคนิค
4. **Minimum First** — เสนอขั้นต่ำที่ใช้ได้จริงก่อน แล้วค่อยเสนอ recommended/optimal

---

## NotebookLM-Specific Instructions

### Source Knowledge (ไฟล์นี้)
- ไฟล์นี้คือ source document ที่ถูก add เข้า NotebookLM notebook
- NotebookLM จะใช้ข้อมูลในไฟล์นี้เป็น grounded knowledge — ตอบตาม source เท่านั้น
- ทุกคำตอบต้อง cite กลับมาที่ข้อมูลใน source documents

### Multi-Source Cross-Reference
- Add เอกสารหลายฉบับเป็น sources (TOR, Spec, UAT, แนวปฏิบัติ)
- NotebookLM จะ cross-reference ระหว่าง sources อัตโนมัติ
- ถามได้: "เปรียบเทียบ requirements ใน TOR กับ spec ข้อ 2.1"
- อ้างอิง source + หน้า/section ที่เจาะจงได้

### Audio Overview
- สร้าง Audio Overview สรุปเนื้อหาทั้ง notebook เป็น podcast-style
- เหมาะสำหรับสรุปให้ผู้บริหารฟังระหว่างเดินทาง
- ครอบคลุม: สรุปโครงการ, ต้นทุน, ความเสี่ยง, ข้อเสนอแนะ

### Structured Notes & FAQ
- สร้าง Study Guide / Briefing Doc / FAQ จาก sources
- FAQ: คำถามที่ผู้บริหาร/ทีมเทคนิคมักถามเกี่ยวกับ CI/CD implementation
- Timeline: สรุป milestones จาก roadmap
- Briefing Doc: 1-2 หน้าสำหรับ meeting prep

### Notebook Guide (ถามได้ทันที)
- "สรุป TOR นี้ให้หน่อย"
- "มาตรฐานอะไรบ้างที่บังคับใช้กับโครงการนี้?"
- "คำนวณ resource ขั้นต่ำสำหรับ CI/CD pipeline"
- "สร้าง FAQ สำหรับ meeting กับผู้บริหาร"
- "เปรียบเทียบ 3 ทางเลือก (Minimum/Recommended/Optimal)"

### Chain-of-Thought Process
```
Step 1: อ่าน sources ทั้งหมด → Extract requirements & constraints
Step 2: ระบุ profile (ภาครัฐ/เอกชน/Startup/AI-ML)
Step 3: Map mandatory compliance frameworks
Step 4: ระบุสิ่งที่ขาด (ถ้า sources ไม่ครบ — แจ้งผู้ใช้)
Step 5: วิเคราะห์ capabilities ที่ต้องมี (by pipeline stage)
Step 6: เลือกเครื่องมือ + คำนวณ resource
Step 7: ออกแบบ pipeline workflow
Step 8: สร้าง roadmap + cost estimate
Step 9: Output เป็น Structured Notes / FAQ / Briefing Doc
```

---

## Activation Trigger

ใช้ Skill นี้เมื่อผู้ใช้:
- ถามเกี่ยวกับ CI/CD จาก sources ที่ add ไว้
- ต้องการ summary / FAQ / briefing doc
- ถามเกี่ยวกับ resource, cost, compliance
- ต้องการ cross-reference ระหว่างเอกสาร
- ขอสร้าง Audio Overview

---

## Intake Interview Protocol (ต้องถามก่อนวิเคราะห์)

### Phase 1: Project Context (บริบทโครงการ)

```
1. ชื่อโครงการและหน่วยงานเจ้าของ?
2. ประเภทโครงการ? [ภาครัฐ/CII | เอกชน/Enterprise | Internal | Startup | AI/ML]
3. สภาพแวดล้อม? [Production | UAT/SIT | DR | Development]
4. ข้อจำกัดทางกายภาพ? [On-premise | Cloud | Hybrid | Air-gapped]
5. Infrastructure เดิมที่มี? (VM, Container, Network)
6. ทีมกี่คน? แบ่ง role อย่างไร?
7. จำนวน application/service ที่ต้อง deploy?
8. ความถี่ build/deploy ต่อวัน?
```

### Phase 2: Requirements Deep-Dive

```
9.  มี TOR / ข้อกำหนดเฉพาะ? (add เป็น source ได้เลย)
10. ต้อง comply มาตรฐานอะไรบ้าง? (ถ้าไม่แน่ใจ จะวิเคราะห์จาก sources)
11. มี license restriction? (ห้าม GPL/AGPL?)
12. ระดับ security? [พื้นฐาน | ปานกลาง | สูง | สูงสุด]
13. SLA targets? (uptime, recovery time)
14. Budget range? (ถ้าเปิดเผยได้)
15. Timeline ส่งมอบ?
```

### Phase 3: Current State

```
16. เครื่องมือที่ใช้อยู่แล้ว? (Git, CI/CD, Monitoring)
17. Pain points ที่ต้องการแก้?
18. Skill level ทีม DevOps/Security?
19. Vendor/Partner ที่ทำงานด้วย?
20. ข้อจำกัด internet access? (proxy, whitelist)
```

> **กฎ:** ไม่จำเป็นต้องถามทุกข้อพร้อมกัน — ถามตามบริบท
> ถ้าข้อมูลไม่พอ ให้ระบุ "**สมมติฐานที่ใช้:**" ชัดเจน + แนะนำให้ add source เพิ่ม

---

## Compliance Standards Register (v4 — 155+ มาตรฐาน/กฎหมาย)

> **แหล่งข้อมูล:** `Compliance_Standards_Register_CICD_v4.xlsx` — รวม 155 มาตรฐาน/กฎหมาย + 28 ข้อกำหนด WASS + 18 ประเภทการสแกน + 12 เกณฑ์ Severity Gate

### หมวด 1: กฎหมายไทยหลัก (TH-01 ถึง TH-11)

| รหัส | ชื่อ | หน่วยงาน | สาระสำคัญ |
|------|------|----------|-----------|
| TH-01 | พ.ร.บ. ไซเบอร์ 2562 | สกมช. | CII 7 ภาคส่วน, Identify-Protect-Detect-Respond-Recover |
| TH-02 | PDPA 2562 | PDPC | มาตรการ ม.37; RoPA ม.39; แจ้งเหตุ 72 ชม. |
| TH-03 | พ.ร.บ. คอมพิวเตอร์ 2550/2560 | ETDA | Log retention 90 วัน |
| TH-04 | พ.ร.บ. บริการภาครัฐดิจิทัล 2562 | DGA | Open Data, e-Service |
| TH-05 | มาตรฐานขั้นต่ำ 2566 | สกมช. | Security Categorization ต่ำ/กลาง/สูง |
| TH-06 | มาตรฐานคลาวด์ 2567 | สกมช. | Cloud First, Shared Responsibility |
| TH-07 | มาตรฐานเว็บไซต์ 2568 | สกมช. | Website Security Governance + Technical |
| TH-09 | มสพร. 11-2566 | DGA | เว็บภาครัฐ 3.0, WCAG AA |

### หมวด 1b: กฎหมายลำดับรอง (TX-01 ถึง TX-24)

| รหัส | ประเภท | สาระสำคัญ |
|------|--------|-----------|
| TX-01 | ประกาศ PDPC | มาตรการ CIA, Defense-in-Depth |
| TX-02 | ประกาศ PDPC | แจ้งเหตุละเมิด 72 ชม. |
| TX-05 | ประกาศ PDPC | โอนข้อมูลต่างประเทศ (SCCs/BCRs) |
| TX-07 | สกมช. | Zero Trust ตาม NIST 800-207 |
| TX-08 | สกมช. | AI Security Guidelines |
| TX-09 | สกมช. | Post-Quantum / Crypto-Agility |
| TX-11 | กมช. | กรอบ Identify-Protect-Detect-Respond-Recover |

### หมวด 1c: กฎเกณฑ์รายภาคส่วน (S-01 ถึง S-15)

| รหัส | ภาคส่วน | กฎหมาย | หน่วยงาน |
|------|---------|--------|----------|
| S-01 | การเงิน | IT Risk Management | ธปท. |
| S-03 | ตลาดทุน | IT Security | ก.ล.ต. |
| S-05 | โทรคมนาคม | Cybersecurity | กสทช. |
| S-06 | สาธารณสุข | โรงพยาบาลรัฐ 2567 | สกมช. |
| S-09 | การชำระเงิน | PCI DSS | ธปท. |
| S-12 | ลิขสิทธิ์ | ห้าม GPL/AGPL ภาครัฐ | กรมทรัพย์สินฯ |

### หมวด 2: มาตรฐานสากล (IN + IX)

| รหัส | กลุ่ม | ชื่อ | สาระสำคัญ |
|------|------|------|-----------|
| IN-01 | OWASP | Top 10 (2025) | A01-A10 + Supply Chain + PQC |
| IN-05 | OWASP | CI/CD Top 10 Risks | Pipeline-specific risks |
| IN-07 | NIST | SP 800-218 SSDF | Secure Dev Framework |
| IN-08 | NIST | SP 800-207 Zero Trust | PE/PA/PEP |
| IN-11 | NIST | CSF 2.0 | 6 Functions framework |
| IN-14 | ISO | 27001:2022 | ISMS Controls |
| IN-20 | CIS | Benchmarks | Hardening |
| IN-22 | W3C | WCAG 2.2 AA | Accessibility |
| IX-08 | ISO | 42001 AI Mgmt | AI/ML Pipeline |
| IX-36 | CISA | KEV Catalog | Exploited vulns |
| IX-43 | DORA | Metrics | CI/CD performance |

### หมวด 3: Cloud-Native & Supply Chain (CN-01 ถึง CN-29)

| รหัส | ชื่อ | สาระสำคัญ |
|------|------|-----------|
| CN-01 | SLSA | Supply chain Levels 1-4, provenance |
| CN-02 | Sigstore | Artifact Signing (บังคับภาครัฐ) |
| CN-04 | Notary v2 | Image signing & verification |
| CN-05 | CycloneDX/SPDX | SBOM formats |

### หมวด 4: OWASP Top 10:2025 → Pipeline Mapping

| รหัส | ช่องโหว่ | แนวทางใน Pipeline |
|------|---------|------------------|
| A01 | Broken Access Control (รวม SSRF) | RBAC/ABAC, deny-by-default |
| A02 | Security Misconfiguration | IaC + Policy-as-Code |
| A03 | Supply Chain Failures (NEW) | SBOM, SCA, signing |
| A04 | Cryptographic Failures | TLS 1.3, key rotation |
| A05 | Injection | SAST, parameterized queries |
| A06 | Insecure Design | Threat Modeling (STRIDE) |
| A07 | Authentication Failures | MFA, Argon2/bcrypt |
| A08 | Integrity Failures | Signed artifacts, SLSA |
| A09 | Logging & Monitoring | SIEM, Log 90d+ |
| A10 | Exceptional Conditions (NEW) | Error handling SAST |

### หมวด 5: CI/CD Stage Compliance

| Stage | ชื่อ | เครื่องมือ | เกณฑ์ภาครัฐ |
|-------|------|-----------|------------|
| 1 | Source Code Mgmt | Git, Branch Protection | Audit Log, On-premise |
| 2 | Check & Scan | SonarQube, Semgrep, GitLeaks | Critical=0, ห้าม GPL, Cov>80% |
| 3 | Build & Sign | Kaniko, Trivy, Cosign | Rootless, Sign, Scan layers |
| 4 | Test | ZAP, Burp, K6 | DAST Mandatory |
| 5 | Delivery | Harbor, SBOM, Cosign verify | SBOM+Sig บังคับ |
| 6 | Operate | Prometheus, Wazuh, SIEM | Log 90d+, IR Plan |

### หมวด 6: WASS Scanning & Severity Gates

#### ประเภทการสแกน (SC-01 ถึง SC-18)

| รหัส | ประเภท | เครื่องมือ | ความถี่ | เกณฑ์ |
|------|--------|-----------|--------|------|
| SC-01 | SAST | SonarQube, Semgrep | ทุก commit | Critical=0 |
| SC-02 | SCA | Dep-Check, Trivy | ทุก build+วัน | CVSS>=7 block |
| SC-03 | Secret | GitLeaks, TruffleHog | Pre-commit | Zero tolerance |
| SC-04 | DAST | ZAP, Burp, Nuclei | ทุก release | No Crit/High |
| SC-06 | API | 42Crunch, Schemathesis | ทุก release | API Top 10 |
| SC-07 | Container | Trivy, Grype | ทุก build | No Critical |
| SC-08 | IaC | Checkov, tfsec | ทุก commit | No High |
| SC-12 | Network | Nmap, Nessus | เดือน+90d | ปิดพอร์ตไม่จำเป็น |
| SC-14 | Accessibility | axe, Lighthouse | ปี | AA บังคับ |
| SC-17 | Pen Test | OSCP/CREST | ปี+Go-Live | Report+Retest |
| SC-18 | EASM | Amass, Shodan | ต่อเนื่อง | Unknown=0 |

#### Severity Gate & SLA (G-01 ถึง G-12)

| รหัส | เกณฑ์ | Action | SLA |
|------|-------|--------|-----|
| G-01 | Critical CVSS 9-10 | **Block** | 7d |
| G-02 | High CVSS 7-8.9 | Block Prod | 30d |
| G-03 | Medium CVSS 4-6.9 | Warning | 90d |
| G-05 | CISA KEV | **Block ทันที** | 7d |
| G-07 | Secret หลุด | **Block+Revoke** | 24h |
| G-08 | GPL/AGPL | Block | ก่อนส่งมอบ |
| G-10 | ไม่มี SBOM | **Block (ภาครัฐ)** | ก่อน release |
| G-11 | ไม่มี Signature | **Block** | Sign ใหม่ |

#### แผนรอบการสแกน

| รอบ | กิจกรรม | ผู้รับผิดชอบ |
|-----|---------|------------|
| ทุก Commit/PR | SAST, Secret, Lint | ทีมพัฒนา |
| ทุก Build | SCA, Container, IaC, SBOM | DevSecOps |
| ทุก Release | DAST, API, Headers, Sig Verify | DevSecOps+CISO |
| รายวัน | Re-scan, Malware, Threat Intel | SOC |
| รายสัปดาห์ | SCA re-scan, EASM | DevSecOps |
| รายเดือน | Network, WAF, Patch | Security Eng |
| 90 วัน | Full VA, TLS, CIS, Privacy | Security Eng |
| รายปี (บังคับ) | Pen Test, แบบฟอร์ม ค., Accessibility | CISO+Auditor |

**วิธี Map Compliance:**
1. ระบุประเภทโครงการ → mandatory frameworks
2. ระดับผลกระทบ (Low/Medium/High) → กรองข้อกำหนดตามระดับ
3. Required capabilities → map เข้ากับเครื่องมือจาก Stage 1-6
4. Gap analysis: สิ่งที่มี vs สิ่งที่ต้องมี
5. ตรวจ Severity Gate (G-01 ถึง G-12) ว่าตรงเกณฑ์ภาครัฐ
6. ตรวจ Scanning Schedule ว่าครบตามรอบบังคับ

---

## Resource Calculation Model

### 3 Methods

```
A = Peak-Max: MAX(minimum ของทุกเครื่องมือบน VM นั้น)
    → พื้นขั้นต่ำที่ต้องมี

B = Weighted-Sum (25-75%):
    weight = 0.25 + 0.50 × activity_index
    B = Σ(minimum_i × weight_i)

C = Resident Floor: Σ idle_ram ของเครื่องมือ 24/7
    → ตรวจความเป็นไปได้ทางกายภาพ

ผลลัพธ์ = MAX(A, B, C) + OS Reserve → ปัดขึ้นตาม Allocation Ladder
```

### Allocation Ladder
- vCPU: 2, 4, 6, 8, 12, 16, 24, 32, 48, 64
- RAM (GB): 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128
- Disk (GB): 20, 40, 60, 80, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000

### OS Reserve: 1 vCPU, 2 GB RAM, 20 GB Disk

### Frequency Classes

| Class | ความถี่ | Activity Index | Weight |
|-------|---------|---------------|--------|
| Resident (24/7) | ตลอดเวลา | 1.0 | 0.75 |
| Per-Commit | 10-30/วัน | 0.8 | 0.65 |
| Per-Build | 5-15/วัน | 0.65 | 0.575 |
| Per-PR | 3-10/วัน | 0.55 | 0.525 |
| Nightly | 1/วัน | 0.35 | 0.425 |
| Weekly | 1-2/สัปดาห์ | 0.15 | 0.325 |
| On-Demand | <0.1/วัน | 0.0 | 0.25 |

### Storage Estimation

```
Disk_OS = (OS_Reserve + Σ Install) / (1 - 0.25)
Data(h) = GB/วัน × Scale × (1 + Growth)^(h/12) × MIN(Retention, h×30.44) × 1.15
Disk_Data = Data(h) / (1 - 0.25)
```

---

## Project Profiles

### ภาครัฐ / CII
```yaml
impact_level: high
security: สูงสุด
mandatory_frameworks: [CYBER2562, PDPA2562, MIN2566, MSPR11, WEB2568, OWASP2025]
license_restriction: ห้าม GPL/AGPL (ต้องตรวจ)
log_retention: 90 วัน (minimum by law)
audit_retention: 7+ ปี (2,555 วัน)
coverage_target: ">80%"
deployment: On-premise / Air-gapped
cost_range_yr: "5,250,000 - 17,500,000+ THB"
```

### เอกชน / Enterprise
```yaml
impact_level: medium
security: สูง
mandatory_frameworks: [PDPA2562, OWASP2025, ISO27001, CLOUD2567]
license_restriction: flexible
log_retention: 90 วัน
audit_retention: 1 ปี
coverage_target: ">70%"
deployment: Cloud + On-premise Hybrid
cost_range_yr: "1,050,000 - 5,250,000 THB"
```

### Internal Dev / Startup
```yaml
impact_level: low
security: พื้นฐาน-ปานกลาง
mandatory_frameworks: [OWASP2025]
license_restriction: none
log_retention: 14-30 วัน
coverage_target: ">50-60%"
deployment: Self-hosted / SaaS
cost_range_yr: "0 - 175,000 THB"
```

### AI/ML Engineering
```yaml
impact_level: medium
security: สูง (Data + Model)
mandatory_frameworks: [PDPA2562, OWASP2025, ISO27001]
additional: [Model Registry, Data Versioning, Drift Detection, GPU Scheduling]
cost_range_yr: "1,750,000 - 7,000,000+ THB"
```

---

## Agile Team Workflow & Sprint Workloads

### Agile CI/CD Team Structure

| Role | จำนวนขั้นต่ำ | ความรับผิดชอบ | Sprint Involvement |
|------|-------------|--------------|-------------------|
| Product Owner | 1 | Prioritize backlog, accept deliverables | Sprint Planning, Review |
| Scrum Master / Agile Coach | 1 | Remove blockers, facilitate ceremonies | All ceremonies |
| DevOps Engineer | 1-2 | Pipeline design, IaC, automation | Sprint Execution |
| Platform / SRE Engineer | 1-2 | Infrastructure, monitoring, reliability | Sprint Execution |
| Security Engineer (DevSecOps) | 1 | Security gates, vulnerability mgmt | Sprint Execution, Review |
| Developer (Backend/Frontend) | 2-5 | Feature development, unit tests, code review | Sprint Execution |
| QA / Test Engineer | 1-2 | Test automation, UAT, quality gates | Sprint Execution |

### Sprint Cadence (2-week sprints แนะนำ)

```yaml
ceremonies:
  sprint_planning: "2-4 ชม. — ทั้งทีม → Sprint backlog"
  daily_standup: "15 นาที — Yesterday/Today/Blockers"
  sprint_review: "1-2 ชม. — Demo pipeline + compliance status"
  sprint_retrospective: "1-1.5 ชม. — Process improvements"
  backlog_refinement: "1 ชม. กลาง sprint — PO + tech leads"
```

### CI/CD Implementation Roadmap (Sprint-based)

```
Phase 1: Foundation (Sprint 1-3)
├── Sprint 1: Git + Basic Pipeline + Team Onboarding
├── Sprint 2: Container + Registry + Basic Security
└── Sprint 3: Automated Deploy + Environments

Phase 2: Security Integration (Sprint 4-6)
├── Sprint 4: SAST + SCA + Quality Gate
├── Sprint 5: Container Scan + Image Signing + SBOM
└── Sprint 6: DAST + API Security + Compliance Gate

Phase 3: Operations (Sprint 7-9)
├── Sprint 7: Centralized Logging + SIEM
├── Sprint 8: Monitoring + Alerting + Incident Response
└── Sprint 9: Backup/DR + Performance Testing

Phase 4: Optimization (Sprint 10-12)
├── Sprint 10: Advanced Deploy (Blue-Green/Canary)
├── Sprint 11: Chaos Engineering + Resilience
└── Sprint 12: Optimization + Documentation + Handover
```

### DORA Metrics & Sprint Velocity

| Metric | เป้าหมาย | วัดจาก |
|--------|---------|--------|
| Deployment Frequency | ≥ 1/วัน | Pipeline runs to prod |
| Lead Time for Changes | < 1 วัน | Commit → Production |
| Change Failure Rate | < 15% | Failed / Total deploys |
| MTTR | < 1 ชั่วโมง | Incident → Resolution |
| Pipeline Success Rate | > 90% | Green / Total builds |
| Security Gate Pass | > 85% | Passed / Total scans |
| Test Coverage | > 80% (ภาครัฐ) | Code coverage % |

### Workload Distribution per Sprint

```yaml
ci_cd_implementation_sprints:
  pipeline_development: "30%"
  security_integration: "25%"
  infrastructure_automation: "20%"
  monitoring_observability: "15%"
  documentation_training: "10%"

steady_state_sprints:
  new_features: "40%"
  security_hardening: "20%"
  tech_debt: "15%"
  bug_fixes: "15%"
  learning: "10%"
```

### Definition of Done (CI/CD Tasks)

```yaml
definition_of_done:
  code: ["Code reviewed ≥1 peer", "Unit tests pass (≥80%)", "SAST no Critical/High", "No secrets detected", "No Critical CVE"]
  pipeline: ["Pipeline green end-to-end", "Deployed to UAT", "Documentation updated", "Runbook created"]
  compliance: ["Rule IDs mapped", "Audit trail captured", "Artifacts signed"]
```

---

## Cloud Deployment Options

### Cloud-Native CI/CD (Managed Services)

| Cloud | CI/CD Platform | Container Registry | Kubernetes | Monitoring | Secret Mgmt |
|-------|---------------|-------------------|------------|------------|-------------|
| **Azure** | Azure DevOps | ACR | AKS | Azure Monitor + Log Analytics | Azure Key Vault |
| **AWS** | CodePipeline + CodeBuild | ECR | EKS | CloudWatch + CloudTrail | Secrets Manager + KMS |
| **GCP** | Cloud Build + Cloud Deploy | Artifact Registry | GKE | Cloud Operations | Secret Manager + KMS |
| **GitHub** | GitHub Actions | GHCR | — | — | — |

### Cloud vs Self-Hosted Decision Matrix

| เกณฑ์ | Cloud Managed | Self-Hosted (OSS) | Self-Hosted (Enterprise) |
|--------|--------------|-------------------|--------------------------|
| ต้นทุนเริ่มต้น | ต่ำ (pay-as-you-go) | ต่ำ (free license) | สูง (license + infra) |
| ต้นทุนระยะยาว | ปานกลาง-สูง | ต่ำ (infra + people) | สูง (renewal) |
| ทีมดูแล | น้อย (1-2 คน) | มาก (2-4 คน) | ปานกลาง (2-3 คน) |
| Compliance | ✓ ISO 27001, SOC2 | ต้อง configure เอง | ✓ + support |
| Air-gapped | ✗ (hybrid agent) | ✓ | ✓ |
| Scalability | อัตโนมัติ | ต้อง plan | Semi-auto |
| Data Sovereignty | เลือก region | ✓ on-premise | ✓ on-premise |
| Vendor Lock-in | สูง | ไม่มี | ปานกลาง |

### Hybrid Architecture (แนะนำภาครัฐ)

```
Cloud Layer: CI/CD Orchestration + Registry + Monitoring
Hybrid Agent: Self-hosted Build Agent + Security Scanners + Cache
On-Premise: Production + Database + Log Storage (90d) + Backup/DR
```

---

## Output Specifications (NotebookLM Formats)

### Output 1: Study Guide / Technical Summary

NotebookLM สร้าง Study Guide อัตโนมัติ ครอบคลุม:
- Key concepts: CI/CD stages, compliance requirements
- Terms & definitions: SAST, DAST, SCA, SBOM, etc.
- Key findings from sources
- Questions for review

### Output 2: Briefing Document (1-2 pages)

สำหรับ meeting prep กับผู้บริหาร:
```
1. สรุปโครงการ (1 paragraph)
2. มาตรฐานที่ต้อง comply (bullet list)
3. Resource ที่ต้องการ (ตาราง VM spec)
4. ต้นทุนรวม (ช่วงราคา 3 ทางเลือก)
5. Timeline แนะนำ
6. ความเสี่ยงหลัก 3 ข้อ
7. ข้อเสนอแนะ
```

### Output 3: FAQ (Frequently Asked Questions)

คำถามที่ stakeholders มักถาม:
```
Q: ต้องใช้ server กี่เครื่อง?
Q: ต้นทุนปีแรกเท่าไหร่?
Q: ใช้เวลา implement นานแค่ไหน?
Q: ต้อง comply มาตรฐานอะไรบ้าง?
Q: ใช้เครื่องมือ open-source ได้ไหม?
Q: ทีมต้องมี skill อะไรบ้าง?
Q: ความเสี่ยงหลักคืออะไร?
Q: เปรียบเทียบกับ cloud CI/CD service ยังไง?
```

### Output 4: Audio Overview

NotebookLM สร้าง podcast-style audio สรุป:
- สรุปโจทย์และ requirements
- Compliance ที่ต้องทำ
- Resource & cost overview
- Recommendations
- เหมาะสำหรับฟังระหว่างเดินทาง (10-15 นาที)

### Output 5: Timeline / Roadmap Notes

```
Phase 1 (เดือน 1-2): Foundation — Git, CI Server, Basic Pipeline
Phase 2 (เดือน 3-4): Security — SAST, SCA, Secret Scan, Image Scan
Phase 3 (เดือน 5-6): Quality — DAST, Performance Test, Quality Gate
Phase 4 (เดือน 7-8): Operations — Monitoring, SIEM, DR, Optimization
```

---

## Behavioral Rules

1. **ห้ามเหมารวม** — ต้องถามก่อนสรุป ถ้าข้อมูลไม่พอ ระบุ "สมมติฐาน" ชัดเจน
2. **Minimum First** — แนะนำ resource ขั้นต่ำที่ใช้งานได้จริง แล้วค่อยเสนอ recommended
3. **Compliance-Driven** — ทุก recommendation อ้างอิง rule ID ได้
4. **Dual-Audience** — อธิบายได้ทั้งผู้บริหาร (ต้นทุน/ความเสี่ยง) และเทคนิค (spec/config)
5. **Evidence-Based** — ตัวเลขอ้างอิงจาก sources เท่านั้น (grounded)
6. **Incremental** — roadmap เป็น phase ไม่ใช่ทำทุกอย่างพร้อมกัน
7. **Alternative Options** — เสนออย่างน้อย 2 ทาง (OSS vs Commercial, Minimal vs Full)
8. **Thai Context Aware** — เข้าใจกฎหมายไทย, หน่วยงาน, งบประมาณ, วัฒนธรรมองค์กร
9. **Source-Grounded** — ทุกคำตอบต้อง cite กลับมาที่ source document
10. **Suggest Missing Sources** — ถ้าข้อมูลไม่พอ แนะนำให้ add source เพิ่ม

---

## Workflow: End-to-End

```
┌─────────────────────────────────────────────────────────────┐
│  1. SETUP NOTEBOOK                                           │
│  ├── Add SKILL.md เป็น source (ไฟล์นี้)                     │
│  ├── Add TOR / Requirements / Spec เป็น sources เพิ่ม       │
│  ├── Add CICD_Tool_Resource_Matrix.xlsx                     │
│  └── Add แนวปฏิบัติ/มาตรฐาน PDFs                            │
├─────────────────────────────────────────────────────────────┤
│  2. INTAKE (รับโจทย์)                                        │
│  ├── NotebookLM อ่าน sources ทั้งหมด                        │
│  ├── Cross-reference ระหว่างเอกสาร                           │
│  ├── ถามคำถาม Phase 1-3 (ตามบริบท)                          │
│  └── สรุป scope & constraints                               │
├─────────────────────────────────────────────────────────────┤
│  3. ANALYSIS (วิเคราะห์)                                     │
│  ├── Map project → profile                                   │
│  ├── Identify mandatory frameworks (cite sources)            │
│  ├── List required capabilities (by stage)                   │
│  ├── Select tools (Core + Optional)                          │
│  └── Calculate resources (from model in this file)           │
├─────────────────────────────────────────────────────────────┤
│  4. OUTPUT (ส่งมอบ — NotebookLM native formats)             │
│  ├── 📖 Study Guide: Technical summary                      │
│  ├── 📋 Briefing Doc: Executive summary (1-2 pages)         │
│  ├── ❓ FAQ: Stakeholder questions & answers                 │
│  ├── 🎧 Audio Overview: Podcast-style summary               │
│  └── 📝 Notes: Inline citations from all sources            │
└─────────────────────────────────────────────────────────────┘
```

---

## Example Interaction in NotebookLM

**User:** "สรุป TOR นี้ให้หน่อย ต้องใช้ CI/CD อะไรบ้าง?"

**NotebookLM Response:**

> จาก TOR [Source: TOR-โครงการ.pdf, หน้า 5-12] ระบุ requirements ดังนี้:
>
> **ขอบเขตโครงการ:**
> - [สรุปจาก source พร้อม citation]
>
> **มาตรฐานที่ TOR อ้างอิง:**
> - พ.ร.บ. ไซเบอร์ 2562 [Source: SKILL.md, Compliance Mapping]
> - มาตรฐานขั้นต่ำ 2566 ระดับสูง [Source: SKILL.md, MIN2566]
>
> **CI/CD Capabilities ที่ต้องมี:**
> - [list จาก cross-reference TOR + SKILL.md]
>
> **Resource ขั้นต่ำ (จากสูตรคำนวณใน SKILL.md):**
> - [calculated based on Resource Calculation Model]
>
> *ต้องการให้สร้าง Briefing Doc หรือ FAQ เพิ่มไหมครับ?*

---

## NotebookLM Setup Guide

### วิธี Deploy
1. เปิด NotebookLM (notebooklm.google.com)
2. สร้าง Notebook ใหม่ ชื่อ "CICD Implementation Analysis"
3. Add Sources:
   - `SKILL.md` (ไฟล์นี้) — เป็น knowledge base หลัก
   - `CICD_Tool_Resource_Matrix.xlsx` — ข้อมูลเครื่องมือ
   - TOR / Spec documents — โจทย์โครงการ
   - แนวปฏิบัติ PDFs — มาตรฐานอ้างอิง
4. ใช้ Notebook Guide ถามคำถามได้ทันที
5. สร้าง Audio Overview สำหรับสรุปภาพรวม

### Sources ที่แนะนำ
- `SKILL.md` (required) — ไฟล์นี้
- `CICD_Tool_Resource_Matrix.xlsx` — รายการเครื่องมือ + specs
- `CICD Blueprint Service V0.2.pdf` — blueprint อ้างอิง
- `CICD Internal Service Proposal.pdf` — proposal template
- `แนวปฏิบัติการพัฒนาซอฟต์แวร์ฯ.pdf` — มาตรฐาน cybersecurity
- TOR/Spec ของโครงการที่ต้องการวิเคราะห์

---

## Quick Reference

```
╔══════════════════════════════════════════════════════════════╗
║  CICD ANALYSIS — GEMINI NOTEBOOKLM EDITION                  ║
╠══════════════════════════════════════════════════════════════╣
║  1. ASK before ANALYZE (ห้ามเหมารวม)                        ║
║  2. Profile → Frameworks → Capabilities → Tools → Resources ║
║  3. Always MINIMUM + RECOMMENDED options                     ║
║  4. Always cite compliance rule IDs                          ║
║  5. Source-grounded — cite back to source documents          ║
║  6. Explain for BOTH executives AND engineers                ║
║  7. Provide OSS vs Commercial alternatives                   ║
║  8. Roadmap in phases (Phase 1-4)                            ║
║  9. Cross-reference multiple sources automatically           ║
║  10. Audio Overview for executive summary                    ║
╚══════════════════════════════════════════════════════════════╝
```
