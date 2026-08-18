/* เทียบ PipelineIR / YAML ฝั่ง JS กับ Python */
import { readFileSync } from 'node:fs';
import { buildPipelineIR, emitGitlab, emitGithub, mermaidFlow, buildInstallPack } from '../assets/pipeline.js';

const catalog = JSON.parse(readFileSync(new URL('../data/catalog.json', import.meta.url), 'utf8'));
const cases = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const out = cases.map(c => {
  const ir = buildPipelineIR(c.tools, {
    profile: c.profile, disabled: c.disabled || [], vms: c.vms || [],
  });
  return {
    id: c.id,
    job_ids: ir.jobs.map(j => j.id),
    enabled: ir.jobs.map(j => j.enabled),
    gitlab: emitGitlab(ir),
    github: emitGithub(ir),
    mermaid_flow: mermaidFlow(ir),
    install: buildInstallPack(ir, catalog.tools),
  };
});
process.stdout.write(JSON.stringify(out, null, 1));
