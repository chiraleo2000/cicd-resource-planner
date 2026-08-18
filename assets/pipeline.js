/* =============================================================================
 * pipeline.js — PipelineIR + mermaid + YAML emitters
 * ต้องให้ผลลัพธ์ตรงกับ scripts/pipeline_gen.py (เทสต์ใน verify.py)
 * ห้ามใส่ URL แบบ http(s):// ในไฟล์นี้ (air-gap lint)
 * ========================================================================== */
'use strict';

const PIPE_SCHEMA = '1.3.0';

const PIPE_STAGES = [
  { id: 'source', n: 1, label: 'Source Code' },
  { id: 'check', n: 2, label: 'Check & Scan' },
  { id: 'build', n: 3, label: 'Build & Sign' },
  { id: 'test', n: 4, label: 'Test' },
  { id: 'store', n: 5, label: 'Store & Version' },
  { id: 'deploy', n: 6, label: 'Deploy & Operate' },
];

const JOB_SPECS = [
  ['policy', 'source', ['opa-conftest'], [], 'pr', null, ['G-12'],
    'Policy-as-Code (OPA/Conftest)', ['conftest test policy/']],
  ['secret-scan', 'check', ['gitleaks'], [], 'commit', null, ['G-07'],
    'Secret scan (GitLeaks)', ['gitleaks detect --redact --exit-code 1']],
  ['sast-semgrep', 'check', ['semgrep'], [], 'commit', null, ['G-01'],
    'SAST (Semgrep)', ['semgrep scan --error --metrics=off']],
  ['sast-sonar', 'check', ['sonarqube'], [], 'commit', null, ['G-09'],
    'SAST + Quality Gate (SonarQube)', ['sonar-scanner -Dsonar.qualitygate.wait=true']],
  ['lint', 'check', ['linters'], [], 'commit', null, [],
    'Linters', ['echo run project linters']],
  ['sca-trivy', 'check', ['trivy'], [], 'build', null, ['G-01', 'G-05'],
    'SCA + image scan (Trivy)', ['trivy fs --exit-code 1 --severity CRITICAL,HIGH .']],
  ['sca-owasp', 'check', ['dependency-check'], [], 'build', null, ['G-01'],
    'SCA (OWASP Dependency-Check)', ['dependency-check.sh --scan . --failOnCVSS 9']],
  ['license', 'check', ['scancode', 'fossology'], [], 'build', null, ['G-08'],
    'License compliance', ['scancode --license --json-pp license-report.json .']],
  ['compile', 'build', ['maven-gradle'], ['lint'], 'commit', null, [],
    'Compile / package', ['echo compile with project build tool']],
  ['image', 'build', ['docker-buildkit', 'podman-buildah'], ['compile'], 'build', null, [],
    'Container image (rootless BuildKit / Buildah)', ['buildctl build --frontend dockerfile.v0 --local context=.']],
  ['helm-lint', 'check', ['helm'], [], 'commit', null, ['G-02'],
    'Helm lint / template', ['helm lint ./chart', 'helm template "${APP_NAME:-app}" ./chart >/tmp/helm-rendered.yaml']],
  ['kustomize-build', 'build', ['kustomize'], ['image'], 'build', null, [],
    'Kustomize build', ['kustomize build overlays/dev']],
  ['kyverno-test', 'check', ['kyverno'], [], 'pr', null, ['G-12'],
    'Kyverno policy test', ['kyverno test ./policies']],
  ['dtrack-upload', 'store', ['dependency-track'], ['sbom'], 'build', null, ['G-01', 'G-10'],
    'Upload SBOM to Dependency-Track', ['dtrack-cli upload --bom sbom.json --project "${DTRACK_PROJECT:-app}"']],
  ['iac', 'build', ['checkov'], [], 'build', null, ['G-02'],
    'IaC scan (Checkov)', ['checkov -d . --quiet --compact']],
  ['sbom', 'build', ['syft'], ['image', 'compile'], 'build', null, ['G-10'],
    'SBOM (Syft / CycloneDX)', ['syft dir:. -o cyclonedx-json > sbom.json']],
  ['sign', 'build', ['cosign'], ['sbom', 'image'], 'build', null, ['G-11'],
    'Sign artifact (Cosign)', ['cosign sign --yes ${IMAGE_REF}']],
  ['unit', 'test', ['unit-test-runner'], ['compile'], 'commit', null, ['G-09'],
    'Unit test + coverage', ['echo unit tests --coverage']],
  ['integration', 'test', ['testcontainers'], ['unit'], 'build', null, [],
    'Integration / contract test', ['echo integration tests']],
  ['dast', 'test', ['owasp-zap'], ['deploy-dev'], 'release', 'uat', ['G-01', 'G-02'],
    'DAST (OWASP ZAP) on UAT', ['zap-baseline.py -t ${UAT_URL} -I']],
  ['api-dast', 'test', ['nuclei'], ['deploy-dev'], 'release', 'uat', ['G-01'],
    'API / template scan (Nuclei)', ['nuclei -u ${UAT_URL} -severity critical,high']],
  ['a11y', 'test', ['playwright-a11y'], ['deploy-dev'], 'nightly', 'uat', [],
    'Accessibility (Playwright + axe)', ['echo playwright a11y']],
  ['tls', 'test', ['testssl', 'cbomkit'], ['deploy-dev'], 'weekly', 'uat', [],
    'TLS / crypto check', ['echo tls scan on UAT']],
  ['load', 'test', ['locust'], ['deploy-uat'], 'weekly', 'uat', [],
    'Load test (Locust)', ['echo locust -f locustfile.py']],
  ['push-registry', 'store',
    ['harbor', 'azure-container-registry', 'aws-ecr', 'gcp-artifact-registry'],
    ['image', 'sign', 'sbom'], 'build', null, ['G-10', 'G-11'],
    'Push image + SBOM to registry', ['echo crane push ${IMAGE_REF}']],
  ['verify-sign', 'store', ['cosign'], ['push-registry'], 'release', null, ['G-11'],
    'Verify signature before deploy', ['cosign verify ${IMAGE_REF}']],
];

const ORCH_TOOLS = [
  ['gitlab-ce', 'gitlab'],
  ['github-actions', 'github'],
  ['github-actions-runner', 'github'],
  ['jenkins-master', 'jenkins'],
  ['jenkins-agent', 'jenkins'],
  ['azure-devops', 'azure'],
  ['woodpecker', 'generic'],
  ['tekton', 'generic'],
];

const DEPLOY_TOOLS = [
  'argocd', 'flux-cd', 'helm', 'kustomize',
  'k3s-control', 'kubernetes-kubeadm', 'microk8s', 'kind-k3d',
  'azure-kubernetes-service', 'aws-eks', 'gcp-gke',
];

const DEPLOY_NAMES = {
  'argocd': 'GitOps deploy (Argo CD)',
  'flux-cd': 'GitOps deploy (Flux)',
  'helm': 'Helm upgrade',
  'kustomize': 'Kustomize apply',
  'k3s-control': 'Deploy to K3s',
  'kubernetes-kubeadm': 'Deploy to kubeadm',
  'microk8s': 'Deploy to MicroK8s',
  'kind-k3d': 'Deploy to kind/k3d',
  'azure-kubernetes-service': 'Deploy to AKS',
  'aws-eks': 'Deploy to EKS',
  'gcp-gke': 'Deploy to GKE',
};

function deployScript(tid, env) {
  const overlay = 'overlays/' + env;
  if (tid === 'argocd') {
    return ['argocd app sync "${APP_NAME:-app}-' + env + '" --prune --timeout 300'];
  }
  if (tid === 'flux-cd') {
    return ['flux reconcile kustomization "${APP_NAME:-app}-' + env + '" --with-source'];
  }
  if (tid === 'helm') {
    return ['helm upgrade --install "${APP_NAME:-app}" ./chart --namespace apps-' + env +
      ' --create-namespace --atomic --wait --timeout 10m -f ' + overlay + '/values.yaml'];
  }
  if (tid === 'kustomize') {
    return ['kubectl apply -k ' + overlay];
  }
  if (tid === 'k3s-control') {
    return ['export KUBECONFIG="${KUBECONFIG:-/etc/rancher/k3s/k3s.yaml}"',
      'kubectl apply -k ' + overlay];
  }
  if (tid === 'kubernetes-kubeadm') {
    return ['export KUBECONFIG="${KUBECONFIG:-/etc/kubernetes/admin.conf}"',
      'kubectl apply -k ' + overlay];
  }
  if (tid === 'microk8s') {
    return ['microk8s kubectl apply -k ' + overlay];
  }
  if (tid === 'kind-k3d') {
    return ['export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"',
      'kubectl apply -k ' + overlay];
  }
  if (tid === 'azure-kubernetes-service') {
    return ['az aks get-credentials --resource-group "${AZ_RG}" --name "${AKS_NAME}" --overwrite-existing',
      'kubectl apply -k ' + overlay];
  }
  if (tid === 'aws-eks') {
    return ['aws eks update-kubeconfig --name "${EKS_NAME}" --region "${AWS_REGION}"',
      'kubectl apply -k ' + overlay];
  }
  if (tid === 'gcp-gke') {
    return ['gcloud container clusters get-credentials "${GKE_NAME}" --region "${GCP_REGION}"',
      'kubectl apply -k ' + overlay];
  }
  return ['kubectl apply -k ' + overlay];
}

function pickTool(toolSet, prefs) {
  for (const tid of prefs) if (toolSet.has(tid)) return tid;
  return null;
}

export function detectOrchestrator(toolIds) {
  const s = new Set(toolIds || []);
  for (const [tid, flavor] of ORCH_TOOLS) if (s.has(tid)) return flavor;
  return 'generic';
}

function flavorsFor(orch) {
  return orch === 'generic' ? ['github', 'gitlab'] : [orch];
}

export function buildPipelineIR(toolIds, opts = {}) {
  const tools = [...(toolIds || [])];
  const tset = new Set(tools);
  const disabled = [...(opts.disabled || [])];
  const off = new Set(disabled);
  const vms = [...(opts.vms || [])];
  const project = opts.project || {};
  const profile = opts.profile || 'gov';
  const orch = detectOrchestrator(tools);
  const envs = ['dev', 'uat', 'prod'];
  if (profile === 'gov') envs.push('dr');

  const jobs = [];
  for (const spec of JOB_SPECS) {
    const [jid, stage, prefs, needs, when, env, gates, title, script] = spec;
    const tid = pickTool(tset, prefs);
    if (!tid) continue;
    jobs.push({
      id: jid, stage, tool_id: tid, name: title,
      needs: [...needs], when, env, gates: [...gates],
      script: [...script], enabled: !off.has(jid),
    });
  }

  const deployTool = pickTool(tset, DEPLOY_TOOLS);
  const deployJobs = [
    ['deploy-dev', 'dev', 'auto', ['verify-sign', 'push-registry', 'image', 'compile'],
      [], 'Deploy DEV (auto)'],
    ['deploy-uat', 'uat', 'release', ['deploy-dev', 'dast', 'verify-sign'],
      ['G-01', 'G-02'], 'Deploy UAT + quality gate'],
    ['deploy-prod', 'prod', 'manual', ['deploy-uat'],
      ['G-01', 'G-11'], 'Deploy PROD (manual approval)'],
  ];
  if (envs.includes('dr')) {
    deployJobs.push(['deploy-dr', 'dr', 'manual', ['deploy-prod'], ['G-11'], 'Deploy DR']);
  }
  if (vms.length) {
    jobs.push({
      id: 'bootstrap', stage: 'source', tool_id: null,
      name: 'Install tools on hosts (once)',
      needs: [], when: 'manual', env: null, gates: [],
      script: ['sh install/all.sh'], enabled: !off.has('bootstrap'),
    });
  }
  for (const [jid, env, when, needs, gates, title] of deployJobs) {
    jobs.push({
      id: jid, stage: 'deploy', tool_id: deployTool, name: title,
      needs: [...needs], when, env, gates: [...gates],
      script: deployScript(deployTool, env), enabled: !off.has(jid),
    });
  }
  if (tset.has('modsecurity')) {
    jobs.push({
      id: 'waf-review', stage: 'deploy', tool_id: 'modsecurity',
      name: 'WAF rule review', needs: ['deploy-uat'], when: 'monthly', env: 'prod',
      gates: [], script: ['nginx -t && echo review WAF rules in /etc/nginx/modsec'], enabled: !off.has('waf-review'),
    });
  }
  if (tset.has('falco')) {
    jobs.push({
      id: 'runtime', stage: 'deploy', tool_id: 'falco',
      name: 'Runtime security (Falco)', needs: ['deploy-prod'], when: 'resident', env: 'prod',
      gates: [], script: ['falco-driver-loader && falco --pidfile /run/falco.pid'], enabled: !off.has('runtime'),
    });
  }
  if (tset.has('velero-restic')) {
    jobs.push({
      id: 'backup', stage: 'deploy', tool_id: 'velero-restic',
      name: 'Backup / restore drill', needs: ['deploy-prod'], when: 'nightly', env: 'prod',
      gates: [], script: ['velero backup create nightly --wait'], enabled: !off.has('backup'),
    });
  }
  if (tset.has('kyverno')) {
    jobs.push({
      id: 'kyverno-apply', stage: 'deploy', tool_id: 'kyverno',
      name: 'Apply cluster policies (Kyverno)', needs: ['deploy-uat'], when: 'release', env: 'uat',
      gates: ['G-12'], script: ['kubectl apply -f policies/'], enabled: !off.has('kyverno-apply'),
    });
  }

  const present = new Set(jobs.map(j => j.id));
  for (const j of jobs) j.needs = j.needs.filter(x => present.has(x));
  const stageN = Object.fromEntries(PIPE_STAGES.map(s => [s.id, s.n]));
  jobs.sort((a, b) => (stageN[a.stage] - stageN[b.stage]) || a.id.localeCompare(b.id));

  return {
    schema: PIPE_SCHEMA,
    orchestrator: orch,
    flavors: flavorsFor(orch),
    profile,
    envs,
    stages: PIPE_STAGES.map(s => ({ ...s })),
    jobs,
    tools: [...tset].sort(),
    vms: vms.map(v => ({
      name: v.name || 'VM', role: v.role || '', tools: [...(v.tools || [])],
    })),
    disabled: [...off].sort(),
    project: { name: project.name || '', org: project.org || '', env: project.env || '' },
  };
}

function nid(jid) { return 'N_' + String(jid).replace(/-/g, '_'); }

export function mermaidFlow(ir) {
  const lines = ['flowchart LR'];
  for (const st of ir.stages) {
    lines.push('  subgraph ' + st.id + ' [' + st.n + ' ' + st.label + ']');
    let shown = false;
    for (const j of ir.jobs) {
      if (j.stage !== st.id || !j.enabled) continue;
      lines.push('    ' + nid(j.id) + '[' + j.name.replace(/]/g, '') + ']');
      shown = true;
    }
    if (!shown) lines.push('    ' + st.id + '_empty[ไม่มีงานที่เลือก]');
    lines.push('  end');
  }
  for (const j of ir.jobs) {
    if (!j.enabled) continue;
    for (const dep of j.needs) lines.push('  ' + nid(dep) + ' --> ' + nid(j.id));
  }
  return lines.join('\n') + '\n';
}

export function mermaidVms(ir) {
  const lines = ['flowchart TB'];
  if (!ir.vms.length) {
    lines.push('  empty[ยังไม่ได้จัดเครื่องมือลง VM]');
    return lines.join('\n') + '\n';
  }
  ir.vms.forEach((vm, i) => {
    const vid = 'VM' + i;
    lines.push('  subgraph ' + vid + ' [' + (vm.name || vid) + ']');
    const tools = vm.tools.length ? vm.tools : ['empty'];
    for (const tid of tools) {
      lines.push('    ' + vid + '_' + tid.replace(/-/g, '_') + '[' + tid + ']');
    }
    lines.push('  end');
  });
  return lines.join('\n') + '\n';
}

export function mermaidEnvs(ir) {
  const lines = ['flowchart LR'];
  let prev = null;
  for (const env of ir.envs) {
    const id = 'E_' + env;
    lines.push('  ' + id + '[' + env.toUpperCase() + ']');
    if (prev) lines.push('  ' + prev + ' --> ' + id);
    prev = id;
  }
  for (const j of ir.jobs) {
    if (j.env && j.enabled) {
      lines.push('  E_' + j.env + ' --- ' + nid(j.id) + '[' + j.id + ']');
    }
  }
  return lines.join('\n') + '\n';
}

function header(ir, flavor) {
  const pj = ir.project || {};
  return '# Generated by CI/CD Resource Planner ' + PIPE_SCHEMA + '\n'
    + '# flavor=' + flavor + ' profile=' + ir.profile
    + ' orchestrator=' + ir.orchestrator + '\n'
    + '# project=' + (pj.name || '-') + ' org=' + (pj.org || '-') + '\n'
    + '# tools=' + ir.tools.join(',') + '\n';
}

export function emitGitlab(ir) {
  const L = [header(ir, 'gitlab'), 'stages:'];
  for (const st of ir.stages) L.push('  - ' + st.id);
  L.push('');
  for (const j of ir.jobs) {
    if (!j.enabled) continue;
    L.push(j.id + ':');
    L.push('  stage: ' + j.stage);
    if (j.needs.length) {
      L.push('  needs:');
      for (const n of j.needs) L.push('    - ' + n);
    }
    L.push('  script:');
    for (const s of j.script) L.push('    - ' + s);
    if (j.when === 'manual') {
      L.push('  when: manual');
      L.push('  allow_failure: false');
    }
    if (j.env) {
      L.push('  environment:');
      L.push('    name: ' + j.env);
    }
    if (j.gates.length) {
      L.push('  variables:');
      L.push('    CICD_GATES: "' + j.gates.join(',') + '"');
    }
    L.push('');
  }
  return L.join('\n');
}

export function emitGithub(ir) {
  let out = header(ir, 'github')
    + 'name: CI-CD\n'
    + 'on:\n  push:\n    branches: [main]\n  pull_request:\n\n'
    + 'jobs:\n';
  for (const j of ir.jobs) {
    if (!j.enabled) continue;
    out += '  ' + j.id + ':\n';
    out += '    name: ' + j.name + '\n';
    out += '    runs-on: ubuntu-latest\n';
    if (j.needs.length) out += '    needs: [' + j.needs.join(', ') + ']\n';
    if (j.when === 'manual') {
      out += "    if: github.ref == 'refs/heads/main'\n";
      out += '    environment: ' + (j.env || 'prod') + '\n';
    } else if (j.env) {
      out += '    environment: ' + j.env + '\n';
    }
    out += '    steps:\n';
    out += '      - uses: actions/checkout@v4\n';
    for (const s of j.script) {
      out += '      - name: ' + j.id + '\n';
      out += '        run: ' + s + '\n';
    }
    out += '\n';
  }
  return out;
}

export function emitAzure(ir) {
  let out = header(ir, 'azure') + 'trigger:\n  - main\n\n' + 'stages:\n';
  for (const st of ir.stages) {
    const jobs = ir.jobs.filter(j => j.enabled && j.stage === st.id);
    if (!jobs.length) continue;
    out += '- stage: ' + st.id + '\n';
    out += '  displayName: ' + st.label + '\n';
    out += '  jobs:\n';
    for (const j of jobs) {
      out += '  - job: ' + j.id.replace(/-/g, '_') + '\n';
      out += '    displayName: ' + j.name + '\n';
      out += '    steps:\n';
      for (const s of j.script) {
        out += '    - script: ' + s + '\n';
        out += '      displayName: ' + j.id + '\n';
      }
    }
    out += '\n';
  }
  return out;
}

export function emitJenkins(ir) {
  let out = '// Generated by CI/CD Resource Planner ' + PIPE_SCHEMA + '\n'
    + 'pipeline {\n  agent any\n  stages {\n';
  for (const st of ir.stages) {
    const jobs = ir.jobs.filter(j => j.enabled && j.stage === st.id);
    if (!jobs.length) continue;
    out += "    stage('" + st.label + "') {\n      steps {\n";
    for (const j of jobs) {
      for (const s of j.script) out += "        sh '" + s.replace(/'/g, '"') + "'\n";
    }
    out += '      }\n    }\n';
  }
  out += '  }\n}\n';
  return out;
}

export function emitAll(ir) {
  return {
    gitlab: emitGitlab(ir),
    github: emitGithub(ir),
    azure: emitAzure(ir),
    jenkins: emitJenkins(ir),
    mermaid_flow: mermaidFlow(ir),
    mermaid_vms: mermaidVms(ir),
    mermaid_envs: mermaidEnvs(ir),
  };
}

export function svgPipeline(ir, view) {
  if (view === 'vms') return svgColumns(ir.vms.map((vm, i) => ({
    title: vm.name || ('VM' + i),
    items: (vm.tools && vm.tools.length) ? vm.tools : ['(ว่าง)'],
  })), 'เครื่องที่จัดแล้ว');
  if (view === 'env') {
    return svgColumns(ir.envs.map(env => ({
      title: env.toUpperCase(),
      items: ir.jobs.filter(j => j.enabled && j.env === env).map(j => j.id),
    })), 'เส้นทางสภาพแวดล้อม');
  }
  return svgColumns(ir.stages.map(st => ({
    title: st.n + '. ' + st.label,
    items: ir.jobs.filter(j => j.enabled && j.stage === st.id).map(j => j.id),
  })), 'โครง Pipeline 6 ขั้น');
}

function svgColumns(cols, caption) {
  const colW = 168, gap = 18, pad = 16, headH = 28, rowH = 22;
  const maxItems = Math.max(1, ...cols.map(c => c.items.length || 1));
  const W = pad * 2 + cols.length * colW + Math.max(0, cols.length - 1) * gap;
  const H = pad * 2 + 28 + headH + maxItems * rowH + 12;
  let x = pad;
  const boxes = cols.map(c => {
    const h = headH + Math.max(1, c.items.length) * rowH + 8;
    const items = (c.items.length ? c.items : ['—']).map((it, i) =>
      '<text x="' + (x + 8) + '" y="' + (pad + 28 + headH + 16 + i * rowH) +
      '" fill="currentColor" font-size="11">' + escXml(String(it).slice(0, 22)) + '</text>').join('');
    const box = '<rect x="' + x + '" y="' + (pad + 28) + '" width="' + colW + '" height="' + h +
      '" rx="8" fill="var(--surface-2)" stroke="var(--border-strong)"/>' +
      '<text x="' + (x + 8) + '" y="' + (pad + 48) + '" font-size="11" font-weight="700" fill="var(--brand)">' +
      escXml(String(c.title).slice(0, 22)) + '</text>' + items;
    const arrow = (x + colW + gap / 2);
    const arr = (cols.indexOf(c) < cols.length - 1)
      ? '<path d="M' + (x + colW + 4) + ' ' + (pad + 28 + h / 2) + ' L' + (arrow + gap / 2 - 8) +
        ' ' + (pad + 28 + h / 2) + '" stroke="var(--brand-accent)" stroke-width="2" fill="none"/>'
      : '';
    x += colW + gap;
    return box + arr;
  }).join('');
  return '<figure style="margin:0"><figcaption class="hint" style="font-weight:700;margin-bottom:6px">' +
    escXml(caption) + '</figcaption><svg class="chart pipe-svg" viewBox="0 0 ' + W + ' ' + H +
    '" role="img" aria-label="' + escXml(caption) + '" style="width:100%;max-width:' + W +
    'px;height:auto">' + boxes + '</svg></figure>';
}

function escXml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function sanitizeVm(name) {
  const s = String(name || 'VM').replace(/[^A-Za-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '');
  return s || 'VM';
}

function commonInstallSh() {
  return [
    '#!/usr/bin/env sh',
    'set -eu',
    '# Generated by CI/CD Resource Planner ' + PIPE_SCHEMA,
    '# Offline: place binaries in $MIRROR (default ./vendor)',
    '# Then run: MIRROR=/path/to/vendor sh install/all.sh',
    'MIRROR="${MIRROR:-./vendor}"',
    'log() { printf \'%s\\n\' "$*"; }',
    'need_cmd() { command -v "$1" >/dev/null 2>&1; }',
    'pkg_install() {',
    '  if [ "$#" -eq 0 ]; then return 0; fi',
    '  if need_cmd apt-get; then',
    '    apt-get update -y',
    '    apt-get install -y "$@"',
    '  elif need_cmd dnf; then',
    '    dnf install -y "$@"',
    '  elif need_cmd yum; then',
    '    yum install -y "$@"',
    '  else',
    '    log "ไม่พบ apt/dnf/yum — ติดตั้งด้วยมือ: $*"',
    '    return 1',
    '  fi',
    '}',
    'install_from_mirror() {',
    '  name="$1"',
    '  file="${2:-$1}"',
    '  bin="$MIRROR/$file"',
    '  dest="/usr/local/bin/$name"',
    '  if need_cmd "$name"; then',
    '    log "มี $name อยู่แล้ว"',
    '    return 0',
    '  fi',
    '  if [ -f "$bin" ]; then',
    '    install -m 0755 "$bin" "$dest"',
    '    log "ติดตั้ง $name จาก $bin"',
    '    return 0',
    '  fi',
    '  log "ไม่พบ $bin — วางไฟล์ใน \\$MIRROR หรือตั้ง MIRROR เป็นเส้นทาง vendor"',
    '  return 1',
    '}',
    '',
  ].join('\n');
}

function toolByIdMap(tools) {
  const m = new Map();
  (tools || []).forEach(t => m.set(t.id, t));
  return m;
}

export function buildInstallPack(ir, tools) {
  const byId = toolByIdMap(tools);
  const files = {};
  files['install/00-common.sh'] = commonInstallSh();
  const vmFiles = [];
  const vms = ir.vms || [];
  vms.forEach((vm, i) => {
    const name = sanitizeVm(vm.name || ('VM-' + (i + 1)));
    const fname = 'install/' + name + '.sh';
    vmFiles.push(fname);
    const ids = [...(vm.tools || [])];
    const pkgs = [];
    const body = [];
    ids.forEach(tid => {
      const t = byId.get(tid);
      if (!t) {
        body.push('log "ข้าม ' + tid + ' — ไม่พบใน catalog"');
        return;
      }
      const inst = t.install || { family: 'binary', packages: [], lines: [] };
      body.push('');
      body.push('log "--- ' + (t.name || tid) + ' ---"');
      if (inst.family === 'managed' || t.managed) {
        body.push('log "managed service — ไม่ติดตั้งบน VM นี้ (' + tid + ')"');
        return;
      }
      (inst.packages || []).forEach(p => { if (!pkgs.includes(p)) pkgs.push(p); });
      (inst.lines || []).forEach(line => body.push(line));
    });
    const lines = [
      '#!/usr/bin/env sh',
      'set -eu',
      '# VM: ' + (vm.name || name),
      '# Role: ' + (vm.role || ''),
      'HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
      '# shellcheck disable=SC1091',
      '. "$HERE/00-common.sh"',
      'log "ติดตั้งเครื่องมือบน ' + (vm.name || name) + '"',
    ];
    if (pkgs.length) lines.push('pkg_install ' + pkgs.join(' '));
    files[fname] = lines.concat(body).concat(['log "เสร็จบน ' + (vm.name || name) + '"', '']).join('\n');
  });
  const all = [
    '#!/usr/bin/env sh',
    'set -eu',
    'HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
    '# shellcheck disable=SC1091',
    '. "$HERE/00-common.sh"',
    'log "ติดตั้งทุกเครื่องตามผัง VM"',
  ];
  vmFiles.forEach(f => {
    all.push('sh "$HERE/' + f.slice('install/'.length) + '"');
  });
  if (!vmFiles.length) all.push('log "ยังไม่มี VM ในแผน — จัดเครื่องมือลงเครื่องก่อน"');
  all.push('log "ติดตั้งครบทุกเครื่องแล้ว"');
  all.push('');
  files['install/all.sh'] = all.join('\n');
  return files;
}

export { PIPE_SCHEMA, PIPE_STAGES, DEPLOY_NAMES, deployScript, sanitizeVm };

