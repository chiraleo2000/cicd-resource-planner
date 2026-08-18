# CI/CD Tool Catalog (planner source of truth)

> Generated from `data/catalog.json` schema 1.3.1 — 87 tools, 48 frameworks, 52 controls, 42 capabilities.

## Capabilities

| id | meaning |
| --- | --- |
| `git_scm` | Version Control / Source Code Management |
| `webhook` | Webhook / Event Trigger |
| `branch_protection` | Branch Protection & Code Review Enforcement |
| `pipeline` | Pipeline Orchestration |
| `sast` | Static Application Security Testing |
| `secret_scan` | Secret / Credential Scanning |
| `sca` | Software Composition Analysis (CVE) |
| `license` | License Compliance |
| `code_quality` | Code Quality / Technical Debt |
| `build` | Build & Compilation |
| `image_build` | Container Image Build |
| `container_scan` | Container Image Vulnerability Scan |
| `iac_scan` | Infrastructure as Code / Policy-as-Code Scan |
| `artifact_sign` | Artifact / Image Signing & Verification |
| `unit_test` | Unit Test + Coverage |
| `integration_test` | Integration / Contract Test |
| `dast` | Dynamic Application Security Testing |
| `api_security` | API Security Testing |
| `perf_test` | Performance / Load Test |
| `registry` | Private Container / OCI Registry (Image + Helm) |
| `package_repo` | Private Package Repository + Upstream Proxy (Maven / npm / PyPI / NuGet / apt) |
| `version_tag` | Version Tagging / Release Management |
| `sbom` | Software Bill of Materials |
| `audit_trail` | Audit Trail (ใครทำอะไรเมื่อไหร่) |
| `log_mgmt` | Centralized Log Management (เก็บ >= 90 วัน) |
| `siem_alert` | SIEM / Security Alerting |
| `quality_gate` | Quality Gate & Approval Workflow |
| `deploy_strategy` | Deployment Strategy (Rolling/Blue-Green/Canary) |
| `orchestration` | Container Orchestration |
| `runtime_security` | Runtime Security Monitoring |
| `monitoring` | Observability / Metrics & Alerting |
| `secret_mgmt` | Secret Management / Key Rotation |
| `config_mgmt` | Configuration Management / Hardening Baseline |
| `waf` | Web Application Firewall |
| `tls_check` | TLS / Cipher Configuration Validation |
| `accessibility` | Web Accessibility Test (WCAG 2.1/2.2 AA) |
| `cspm` | Cloud / Infra Security Posture Scan |
| `backup_dr` | Backup & Restore / Disaster Recovery |
| `iam_mfa` | Identity, SSO & MFA |
| `crypto_agility` | Crypto Inventory / Post-Quantum Readiness |
| `vapt` | Vulnerability Assessment & Penetration Test |
| `notify` | Notification / Incident Escalation |

## Tools by stage

### Stage 1: Source Code (รับโค้ดและควบคุม)

| id | name | category | grade | license | managed | min vCPU | min RAM | freq | capabilities |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gitlab-ce` | GitLab Community Edition (Self-hosted Git) | Git Repository | oss | MIT |  | 4 | 8 | resident | git_scm, webhook, branch_protection, pipeline, audit_trail |
| `gitea` | Gitea / Forgejo (Lightweight Git) | Git Repository | oss | MIT |  | 1 | 1 | resident | git_scm, webhook, branch_protection, audit_trail |
| `github-actions-runner` | GitHub Actions Self-hosted Runner | Pipeline Orchestration | oss | MIT |  | 2 | 4 | per_commit | pipeline, webhook, build |
| `jenkins-master` | Jenkins Master / Controller | Pipeline Orchestration | oss | MIT |  | 2 | 4 | resident | pipeline, webhook, quality_gate, audit_trail, notify |
| `jenkins-agent` | Jenkins Agent / Build Executor (ต่อ 1 Executor) | Pipeline Orchestration | oss | MIT |  | 2 | 4 | per_commit | pipeline, build, unit_test |
| `argo-workflows` | Argo Workflows (CNCF Graduated) | Pipeline Orchestration | oss | Apache-2.0 |  | 1 | 2 | resident | pipeline, webhook, audit_trail |
| `tekton` | Tekton Pipelines (CI บน Kubernetes) | Pipeline Orchestration | oss | Apache-2.0 |  | 1 | 2 | resident | pipeline, webhook, quality_gate |
| `woodpecker` | Woodpecker CI (Lightweight CI คู่ Gitea/Forgejo) | Pipeline Orchestration | oss | Apache-2.0 |  | 1 | 2 | resident | pipeline, webhook, build |
| `opa-conftest` | Open Policy Agent / Conftest (Policy-as-Code Gate) | Branch Protection | oss | Apache-2.0 |  | 1 | 1 | per_pr | branch_protection, iac_scan, quality_gate |
| `nginx-gateway` | Nginx (Reverse Proxy / Webhook Relay) | Webhook Trigger | oss | BSD-2 |  | 1 | 1 | resident | webhook, tls_check |
| `azure-devops` | Azure DevOps (Cloud CI/CD Platform) | Cloud CI/CD Platform | commercial | Proprietary (SaaS) | yes | 0 | 0 | per_commit | git_scm, webhook, branch_protection, pipeline, audit_trail, quality_gate, deploy_strategy, package_repo |
| `github-actions` | GitHub Actions (Cloud CI/CD) | Cloud CI/CD Platform | commercial | Proprietary (SaaS / Free tier) | yes | 0 | 0 | per_commit | pipeline, webhook, build, deploy_strategy, audit_trail |
| `aws-codecommit-pipeline` | AWS CodePipeline + CodeBuild + CodeCommit | Cloud CI/CD Platform | commercial | Proprietary (SaaS) | yes | 0 | 0 | per_commit | git_scm, webhook, pipeline, build, deploy_strategy, audit_trail |
| `gcp-cloud-build` | Google Cloud Build + Source Repositories | Cloud CI/CD Platform | commercial | Proprietary (SaaS) | yes | 0 | 0 | per_commit | pipeline, build, webhook, image_build, deploy_strategy |

### Stage 2: Check & Scan Programme (ตรวจสอบความปลอดภัยและคุณภาพ)

| id | name | category | grade | license | managed | min vCPU | min RAM | freq | capabilities |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sonarqube` | SonarQube Community Edition | SAST + Code Quality | oss | LGPL-3.0 |  | 2 | 4 | resident | sast, code_quality, quality_gate |
| `postgresql-tools` | PostgreSQL (ฐานข้อมูลของเครื่องมือ CI/CD) | Supporting Database | oss | PostgreSQL License |  | 2 | 4 | resident | audit_trail |
| `semgrep` | Semgrep (SAST แบบ Rule-based) | SAST | oss | LGPL-2.1 |  | 2 | 4 | per_commit | sast |
| `gitleaks` | GitLeaks / TruffleHog (Secret Scanning) | Secret Scanning | oss | MIT |  | 1 | 2 | per_commit | secret_scan |
| `dependency-check` | OWASP Dependency-Check (SCA) | Software Composition Analysis | oss | Apache-2.0 |  | 2 | 4 | nightly | sca, sbom |
| `dependency-track` | OWASP Dependency-Track (SCA Dashboard) | Software Composition Analysis | oss | Apache-2.0 |  | 2 | 4 | resident | sca, sbom, audit_trail, quality_gate |
| `trivy` | Trivy (SCA + Container + IaC + Secret ในตัวเดียว) | Multi-purpose Scanner | oss | Apache-2.0 |  | 2 | 2 | per_build | sca, container_scan, iac_scan, secret_scan, sbom |
| `fossology` | FOSSology / ScanCode (License Compliance) | License Compliance | oss | GPL-2.0 |  | 4 | 8 | weekly | license |
| `linters` | Linters (ESLint / Pylint / golangci-lint / RuboCop) | Code Quality | oss | MIT |  | 1 | 2 | per_commit | code_quality |
| `scancode` | ScanCode Toolkit / License Finder (License Compliance แบบ Permissive) | License Compliance | oss | Apache-2.0 |  | 2 | 4 | per_build | license, sbom |

### Stage 3: Build & Run (สร้างและยืนยันความถูกต้อง)

| id | name | category | grade | license | managed | min vCPU | min RAM | freq | capabilities |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `maven-gradle` | Maven / Gradle / npm / pip (Build & Compilation) | Build & Compilation | oss | Apache-2.0 |  | 2 | 4 | per_commit | build |
| `docker-buildkit` | Docker Engine / BuildKit (Container Image Builder) | Container Image Builder | oss | Apache-2.0 |  | 2 | 4 | per_commit | image_build, build |
| `podman-buildah` | Podman / Buildah / Kaniko (Rootless Image Build) | Container Image Builder | oss | Apache-2.0 |  | 2 | 4 | per_commit | image_build, build |
| `checkov` | Checkov / tfsec / KubeLinter (IaC Validation) | IaC Validation | oss | Apache-2.0 |  | 1 | 2 | per_build | iac_scan |
| `cosign` | Sigstore Cosign / Notary v2 (Artifact Signing) | Artifact Signing | oss | Apache-2.0 |  | 1 | 2 | per_build | artifact_sign |
| `syft` | Syft / CycloneDX CLI (SBOM Generation) | SBOM | oss | Apache-2.0 |  | 1 | 2 | per_build | sbom |
| `gpu-training` | GPU Training Node (Model Training / Fine-tune) | AI Model Training | oss | N/A |  | 8 | 16 | weekly | build |

### Stage 4: Test Running (ทดสอบระบบรอบด้าน)

| id | name | category | grade | license | managed | min vCPU | min RAM | freq | capabilities |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `unit-test-runner` | pytest / Jest / JUnit / Go test (Unit Test) | Unit Test | oss | MIT |  | 2 | 4 | per_commit | unit_test, code_quality |
| `testcontainers` | Testcontainers / WireMock / Pact (Integration Test) | Integration Test | oss | MIT |  | 4 | 8 | per_build | integration_test |
| `owasp-zap` | OWASP ZAP (DAST + API Security) | DAST | oss | Apache-2.0 |  | 2 | 4 | nightly | dast, api_security, vapt |
| `nuclei` | Nuclei (Template-based Vulnerability Scan) | DAST | oss | MIT |  | 2 | 2 | nightly | dast, api_security, vapt, tls_check |
| `locust` | Locust (Performance / Load Test) | Performance Test | oss | MIT |  | 4 | 8 | weekly | perf_test |
| `playwright-a11y` | Playwright + axe-core / pa11y-ci / Lighthouse CI (Accessibility) | Accessibility Test | oss | Apache-2.0 |  | 2 | 4 | nightly | accessibility, integration_test |
| `testssl` | testssl.sh / sslyze / CBOMkit (TLS + Crypto Inventory) | TLS & Crypto Validation | oss | GPL-2.0 |  | 1 | 2 | weekly | tls_check, crypto_agility |
| `llm-eval` | LLM Evaluation Runner (AI/LLM Eval Harness) | AI Model Evaluation | oss | MIT |  | 4 | 8 | per_build | unit_test, integration_test, quality_gate |
| `cbomkit` | CBOMkit / Crypto Inventory Scanner (Crypto Bill of Materials) | Crypto Inventory | oss | Apache-2.0 |  | 2 | 4 | weekly | crypto_agility, sbom |

### Stage 5: Store & Versioning (จัดเก็บและจัดการเวอร์ชัน)

| id | name | category | grade | license | managed | min vCPU | min RAM | freq | capabilities |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `harbor` | Harbor (Private Container Registry, CNCF Graduated) | Container Registry | oss | Apache-2.0 |  | 2 | 4 | resident | registry, container_scan, artifact_sign, audit_trail, version_tag |
| `nexus-repository` | Sonatype Nexus Repository OSS (Maven / npm / PyPI / Docker / Helm) | Package & Artifact Repository | oss | EPL-1.0 |  | 4 | 8 | resident | package_repo, registry, version_tag, audit_trail |
| `zot` | Zot (OCI-native Registry, CNCF) | Container Registry | oss | Apache-2.0 |  | 1 | 2 | resident | registry, artifact_sign, version_tag, audit_trail |
| `minio` | MinIO (S3-compatible Object Storage) | Artifact Storage | oss | AGPL-3.0 |  | 2 | 4 | resident | registry, backup_dr, audit_trail |
| `elasticsearch` | Elasticsearch (Log / Audit Trail Index) | Log & Audit Store | oss | SSPL / Elastic License |  | 2 | 4 | resident | log_mgmt, audit_trail, siem_alert |
| `logstash` | Logstash (Log Pipeline / Parser) | Log Ingest | oss | SSPL / Elastic License |  | 2 | 4 | resident | log_mgmt |
| `kibana` | Kibana (Log Visualization / Audit Review) | Log UI | oss | SSPL / Elastic License |  | 1 | 2 | resident | log_mgmt, audit_trail, siem_alert |
| `filebeat` | Filebeat (Log Shipper ต่อเครื่อง) | Log Agent | oss | SSPL / Elastic License |  | 1 | 1 | resident | log_mgmt |
| `wazuh` | Wazuh (SIEM / HIDS + Alerting) | SIEM | oss | GPL-2.0 |  | 4 | 8 | resident | siem_alert, log_mgmt, audit_trail, runtime_security, config_mgmt |
| `vault` | HashiCorp Vault / OpenBao (Secret Management) | Secret Management | oss | BUSL-1.1 / MPL-2.0 |  | 2 | 4 | resident | secret_mgmt, iam_mfa, audit_trail |
| `sealed-secrets` | Sealed Secrets / kubeseal (GitOps Secrets) | Secret Management | oss | Apache-2.0 |  | 1 | 1 | resident | secret_mgmt |
| `grafana-loki` | Grafana Loki (Log Aggregation) | Log Store | oss | AGPL-3.0 |  | 2 | 4 | resident | log_mgmt, monitoring |
| `mlflow` | MLflow (Experiment Tracking + Model Registry) | Model Registry | oss | Apache-2.0 |  | 2 | 4 | resident | version_tag, registry, audit_trail, artifact_sign |
| `redis` | Redis (Cache สำหรับเครื่องมือ CI/CD) | Supporting Cache | oss | RSALv2 / SSPL |  | 1 | 2 | resident | monitoring |
| `rabbitmq` | RabbitMQ (Message Queue) | Supporting Queue | oss | MPL-2.0 |  | 2 | 4 | resident | monitoring |
| `sftp-nfs` | SFTP / NFS File Server | File Transfer | oss | BSD |  | 1 | 2 | resident | backup_dr, registry |
| `opensearch` | OpenSearch + OpenSearch Dashboards (Log & SIEM แบบ Apache-2.0) | Log & Audit Store | oss | Apache-2.0 |  | 4 | 8 | resident | log_mgmt, audit_trail, siem_alert |
| `openbao` | OpenBao (Secret Management แบบ MPL-2.0) | Secret Management | oss | MPL-2.0 |  | 2 | 4 | resident | secret_mgmt, iam_mfa, audit_trail |
| `azure-container-registry` | Azure Container Registry (ACR) | Cloud Container Registry | commercial | Proprietary (SaaS) | yes | 0 | 0 | per_build | registry, container_scan, artifact_sign |
| `aws-ecr` | Amazon Elastic Container Registry (ECR) | Cloud Container Registry | commercial | Proprietary (SaaS) | yes | 0 | 0 | per_build | registry, container_scan |
| `gcp-artifact-registry` | Google Artifact Registry (GAR) | Cloud Artifact Registry | commercial | Proprietary (SaaS) | yes | 0 | 0 | per_build | registry, package_repo, container_scan, artifact_sign, version_tag |
| `azure-key-vault` | Azure Key Vault | Cloud Secret Management | commercial | Proprietary (SaaS) | yes | 0 | 0 | resident | secret_mgmt, crypto_agility, tls_check |
| `aws-secrets-manager` | AWS Secrets Manager + KMS | Cloud Secret Management | commercial | Proprietary (SaaS) | yes | 0 | 0 | resident | secret_mgmt, crypto_agility |

### Stage 6: Deploy & Update (ขึ้นระบบและดูแลรักษา)

| id | name | category | grade | license | managed | min vCPU | min RAM | freq | capabilities |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `k3s-control` | K3s (Lightweight Kubernetes, ต่อ 1 Node) | Container Orchestration | oss | Apache-2.0 |  | 2 | 4 | resident | orchestration, deploy_strategy, iam_mfa |
| `kubernetes-kubeadm` | Kubernetes kubeadm (Self-managed Control Plane) | Container Orchestration | oss | Apache-2.0 |  | 4 | 8 | resident | orchestration, deploy_strategy, iam_mfa |
| `kind-k3d` | kind / k3d (Kubernetes ใน Docker สำหรับ Local CI) | Local Kubernetes | oss | Apache-2.0 |  | 2 | 8 | resident | orchestration, deploy_strategy |
| `microk8s` | MicroK8s (Local / Private Kubernetes) | Container Orchestration | oss | Apache-2.0 |  | 2 | 4 | resident | orchestration, deploy_strategy |
| `helm` | Helm 3 (Kubernetes Package Manager) | Deployment Packaging | oss | Apache-2.0 |  | 1 | 1 | per_build | deploy_strategy, config_mgmt, version_tag |
| `kustomize` | Kustomize (Overlay / GitOps แบบไฟล์) | Deployment Packaging | oss | Apache-2.0 |  | 1 | 1 | per_build | deploy_strategy, config_mgmt |
| `argocd` | Argo CD (GitOps Continuous Delivery) | Deployment Strategy | oss | Apache-2.0 |  | 2 | 4 | resident | deploy_strategy, audit_trail, quality_gate, version_tag |
| `flux-cd` | Flux CD (GitOps, CNCF Graduated) | Deployment Strategy | oss | Apache-2.0 |  | 1 | 2 | resident | deploy_strategy, audit_trail, version_tag, config_mgmt |
| `falco` | Falco (Runtime Security Monitoring, ต่อ Node) | Runtime Security | oss | Apache-2.0 |  | 1 | 2 | resident | runtime_security, siem_alert |
| `kyverno` | Kyverno (Kubernetes Policy / Admission) | Policy Enforcement | oss | Apache-2.0 |  | 1 | 2 | resident | config_mgmt, iac_scan, quality_gate |
| `prometheus` | Prometheus (Metrics & Alerting) | Monitoring | oss | Apache-2.0 |  | 2 | 4 | resident | monitoring, siem_alert, notify |
| `grafana` | Grafana (Dashboard) | Monitoring UI | oss | AGPL-3.0 |  | 1 | 2 | resident | monitoring |
| `zabbix` | Zabbix Server (Infrastructure Monitoring) | Monitoring | oss | AGPL-3.0 |  | 2 | 4 | resident | monitoring, notify, siem_alert |
| `ansible-chef` | Ansible / Chef Client (Config Management & Hardening) | Configuration Management | oss | GPL-3.0 / Apache-2.0 |  | 1 | 2 | nightly | config_mgmt, iac_scan, backup_dr |
| `modsecurity` | ModSecurity / Coraza (Web Application Firewall) | WAF | oss | Apache-2.0 |  | 2 | 4 | resident | waf, tls_check |
| `keycloak` | Keycloak (SSO / MFA / Identity) | Identity & Access | oss | Apache-2.0 |  | 2 | 4 | resident | iam_mfa, audit_trail |
| `velero-restic` | Velero / restic / pgBackRest (Backup & DR) | Backup & DR | oss | Apache-2.0 |  | 1 | 2 | nightly | backup_dr |
| `prowler` | Prowler / ScoutSuite (Cloud & Infra Posture Scan) | CSPM | oss | Apache-2.0 |  | 2 | 4 | weekly | cspm, iac_scan, config_mgmt |
| `azure-kubernetes-service` | Azure Kubernetes Service (AKS) | Cloud Container Orchestration | commercial | Proprietary (SaaS) | yes | 0 | 0 | resident | orchestration, deploy_strategy, runtime_security, monitoring |
| `aws-eks` | Amazon Elastic Kubernetes Service (EKS) | Cloud Container Orchestration | commercial | Proprietary (SaaS) | yes | 0 | 0 | resident | orchestration, deploy_strategy, runtime_security, monitoring |
| `gcp-gke` | Google Kubernetes Engine (GKE) | Cloud Container Orchestration | commercial | Proprietary (SaaS) | yes | 0 | 0 | resident | orchestration, deploy_strategy, runtime_security, monitoring |
| `azure-monitor` | Azure Monitor + Log Analytics + Application Insights | Cloud Monitoring | commercial | Proprietary (SaaS) | yes | 0 | 0 | resident | monitoring, log_mgmt, siem_alert, audit_trail |
| `aws-cloudwatch` | Amazon CloudWatch + CloudTrail + X-Ray | Cloud Monitoring | commercial | Proprietary (SaaS) | yes | 0 | 0 | resident | monitoring, log_mgmt, audit_trail, siem_alert |
| `gcp-cloud-operations` | Google Cloud Operations (Logging + Monitoring + Trace) | Cloud Monitoring | commercial | Proprietary (SaaS) | yes | 0 | 0 | resident | monitoring, log_mgmt, audit_trail, siem_alert |

## Profiles

| id | name | impact | security | notes |
| --- | --- | --- | --- | --- |
| `gov` | ภาครัฐ / CII | high | สูงสุด | On-premise/Air-gapped, ห้าม GPL/AGPL, Critical = 0, Coverage > 80%, เก็บ Audit Trail 7+ ปี |
| `enterprise` | เอกชน / Enterprise | medium | สูง | Cloud + OSS ผสมได้, Canary/A-B Testing, Auto-remediation ผ่าน PR |
| `internal` | Internal Dev / R&D | low | ปานกลาง | ใช้ OSS เกือบทั้งหมด, Self-hosted, Monitoring พื้นฐาน |
| `startup` | Startup / Fast-paced | low | พื้นฐาน | Managed/Serverless, Zero maintenance, เพิ่ม Security เมื่อ Scale |
| `aiml` | AI/ML Engineering | medium | สูง (Data + Model) | ต้องมี GPU Scheduling, Model Registry, Data Versioning, Drift Detection |

## Reference architectures

### ผัง 2 เครื่อง — ขนาดเล็ก / UAT / Internal Dev

เหมาะกับทีม 5-15 คน, 1-3 แอปพลิเคชัน, ~10 builds/วัน — ยอมรับความเสี่ยงที่ Build กับ Log แย่งทรัพยากรกันได้ในบางช่วง

- **CI-CONTROL-01** — Control (ขนาดเล็ก): Git, Pipeline, SAST และฐานข้อมูลของเครื่องมือรวมในเครื่องเดียว: `gitea`, `jenkins-master`, `sonarqube`, `postgresql-tools`, `nginx-gateway`, `vault`, `filebeat`
- **WORKER-STORE-01** — Worker (ขนาดเล็ก): Build, Test, Registry, Storage, Log และ Scan รวมในเครื่องเดียว: `jenkins-agent`, `maven-gradle`, `docker-buildkit`, `unit-test-runner`, `semgrep`, `gitleaks`, `trivy`, `cosign`, `syft`, `scancode`, `minio`, `nexus-repository`, `elasticsearch`, `kibana`, `owasp-zap`, `locust`, `filebeat`, `testcontainers`, `prometheus`, `grafana`, `ansible-chef`, `prowler`, `argocd`, `k3s-control`, `cbomkit`

### ผัง 4 เครื่อง — มาตรฐาน (เอกชน / Enterprise)

แยกงานที่รันค้าง 24/7 ออกจากงาน Build ที่ burst และแยกที่เก็บข้อมูลออกจาก Compute ทำให้ประเมินทรัพยากรและขยายได้ตรงจุด

- **CI-CONTROL-01** — CI Control: Git Repository, Pipeline Orchestration, SAST และ Quality Gate: `gitea`, `jenkins-master`, `sonarqube`, `postgresql-tools`, `opa-conftest`, `filebeat`, `nginx-gateway`, `modsecurity`, `keycloak`
- **BUILD-AGENT-01** — Build Agent: Compile, Container Build, Unit/Integration Test และสแกนใน Pipeline: `jenkins-agent`, `maven-gradle`, `docker-buildkit`, `unit-test-runner`, `testcontainers`, `semgrep`, `gitleaks`, `trivy`, `checkov`, `cosign`, `syft`, `scancode`, `linters`, `filebeat`, `owasp-zap`, `nuclei`, `dependency-check`, `locust`, `playwright-a11y`, `testssl`, `prowler`
- **STORE-LOG-01** — Store & Log: Container Registry, Object Storage, Secret Management, Log และ Audit Trail: `harbor`, `nexus-repository`, `minio`, `elasticsearch`, `logstash`, `kibana`, `vault`, `redis`, `filebeat`
- **DEPLOY-MON-01** — Deploy & Monitor: Orchestration, Helm, GitOps, Runtime Security, Observability, Backup: `k3s-control`, `helm`, `kustomize`, `argocd`, `prometheus`, `grafana`, `falco`, `ansible-chef`, `velero-restic`, `filebeat`

### ผัง 6 เครื่อง — ภาครัฐ / CII ครบตามมาตรฐานบังคับ

On-premise หรือ Air-gapped, แยก Edge ที่มี WAF และ SSO ออกมา และแยกเครื่อง Security/Performance Test ไม่ให้ทับเวลากับ Pipeline หลัก

- **EDGE-01** — Edge / Reverse Proxy: รับ traffic ขาเข้า, WAF, TLS Termination, SSO: `nginx-gateway`, `modsecurity`, `keycloak`, `filebeat`
- **CI-CONTROL-01** — CI Control: Git Repository, Pipeline Orchestration, SAST และ Quality Gate: `gitea`, `jenkins-master`, `sonarqube`, `postgresql-tools`, `opa-conftest`, `filebeat`
- **BUILD-AGENT-01** — Build Agent: Compile, Container Build, Unit/Integration Test และสแกนใน Pipeline: `jenkins-agent`, `maven-gradle`, `docker-buildkit`, `unit-test-runner`, `testcontainers`, `semgrep`, `gitleaks`, `trivy`, `checkov`, `cosign`, `syft`, `scancode`, `linters`, `filebeat`
- **SEC-TEST-01** — Security & Performance Test: DAST, API Security, Accessibility, TLS, Load Test: `owasp-zap`, `nuclei`, `dependency-check`, `playwright-a11y`, `testssl`, `locust`, `prowler`, `filebeat`
- **STORE-LOG-01** — Store & Log: Container Registry, Object Storage, Secret Management, Log และ Audit Trail: `harbor`, `nexus-repository`, `minio`, `elasticsearch`, `logstash`, `kibana`, `vault`, `redis`, `filebeat`
- **DEPLOY-MON-01** — Deploy & Monitor: Orchestration, Helm, GitOps, Runtime Security, Observability, Backup: `k3s-control`, `helm`, `kustomize`, `argocd`, `prometheus`, `grafana`, `falco`, `ansible-chef`, `velero-restic`, `filebeat`

### ผัง 5 เครื่อง — AI/ML Engineering

เพิ่ม Model Registry และ Evaluation แยกจาก Pipeline ปกติ และแยก Training Node ที่ต้องมี GPU ออกไป (สภาพแวดล้อมหลายแห่งไม่รองรับ GPU จึงต้องระบุผู้รับผิดชอบใน TOR)

- **CI-CONTROL-01** — CI Control: Git Repository, Pipeline Orchestration, SAST และ Quality Gate: `gitea`, `jenkins-master`, `sonarqube`, `postgresql-tools`, `opa-conftest`, `filebeat`, `nginx-gateway`, `keycloak`
- **BUILD-AGENT-01** — Build Agent: Compile, Container Build, Unit/Integration Test และสแกนใน Pipeline: `jenkins-agent`, `maven-gradle`, `docker-buildkit`, `unit-test-runner`, `testcontainers`, `semgrep`, `gitleaks`, `trivy`, `checkov`, `cosign`, `syft`, `scancode`, `linters`, `filebeat`, `owasp-zap`, `nuclei`, `dependency-check`, `locust`, `prowler`
- **ML-REGISTRY-01** — ML Registry & Evaluation: Experiment Tracking, Model Registry, Model/LLM Evaluation: `mlflow`, `llm-eval`, `minio`, `nexus-repository`, `filebeat`, `elasticsearch`, `kibana`, `vault`, `testssl`
- **ML-TRAIN-01** — ML Training: Fine-tune / Train โมเดล (ต้องมี GPU): `gpu-training`, `filebeat`
- **DEPLOY-MON-01** — Deploy & Monitor: Orchestration, Helm, GitOps, Runtime Security, Observability, Backup: `k3s-control`, `helm`, `kustomize`, `argocd`, `prometheus`, `grafana`, `falco`, `ansible-chef`, `velero-restic`, `filebeat`
