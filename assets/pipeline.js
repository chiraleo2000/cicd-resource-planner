/* =============================================================================
 * pipeline.js — PipelineIR + mermaid + YAML emitters
 * ต้องให้ผลลัพธ์ตรงกับ scripts/pipeline_gen.py (เทสต์ใน verify.py)
 * ห้ามใส่ URL แบบ http(s):// ในไฟล์นี้ (air-gap lint)
 * ========================================================================== */
'use strict';

const PIPE_SCHEMA = '1.2.0';

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
  ['image', 'build', ['docker-buildkit'], ['compile'], 'build', null, [],
    'Container image (rootless BuildKit)', ['buildctl build --frontend dockerfile.v0 --local context=.']],
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
];

const DEPLOY_TOOLS = [
  'argocd', 'k3s-control',
  'azure-kubernetes-service', 'aws-eks', 'gcp-gke',
];

const DEPLOY_NAMES = {
  'argocd': 'GitOps deploy (Argo CD)',
  'k3s-control': 'Deploy to K3s',
  'azure-kubernetes-service': 'Deploy to AKS',
  'aws-eks': 'Deploy to EKS',
  'gcp-gke': 'Deploy to GKE',
};

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
  for (const [jid, env, when, needs, gates, title] of deployJobs) {
    jobs.push({
      id: jid, stage: 'deploy', tool_id: deployTool, name: title,
      needs: [...needs], when, env, gates: [...gates],
      script: ['echo ' + title], enabled: !off.has(jid),
    });
  }
  if (tset.has('modsecurity')) {
    jobs.push({
      id: 'waf-review', stage: 'deploy', tool_id: 'modsecurity',
      name: 'WAF rule review', needs: ['deploy-uat'], when: 'monthly', env: 'prod',
      gates: [], script: ['echo review WAF rules'], enabled: !off.has('waf-review'),
    });
  }
  if (tset.has('falco')) {
    jobs.push({
      id: 'runtime', stage: 'deploy', tool_id: 'falco',
      name: 'Runtime security (Falco)', needs: ['deploy-prod'], when: 'resident', env: 'prod',
      gates: [], script: ['echo falco is resident on nodes'], enabled: !off.has('runtime'),
    });
  }
  if (tset.has('velero-restic')) {
    jobs.push({
      id: 'backup', stage: 'deploy', tool_id: 'velero-restic',
      name: 'Backup / restore drill', needs: ['deploy-prod'], when: 'nightly', env: 'prod',
      gates: [], script: ['echo velero backup create nightly'], enabled: !off.has('backup'),
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

export { PIPE_SCHEMA, PIPE_STAGES, DEPLOY_NAMES };
