/* เทียบ PipelineIR / YAML ฝั่ง JS กับ Python */
import { readFileSync } from 'node:fs';
import { buildPipelineIR, emitGitlab, emitGithub, mermaidFlow } from '../assets/pipeline.js';

const cases = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const out = cases.map(c => {
  const ir = buildPipelineIR(c.tools, { profile: c.profile, disabled: c.disabled || [] });
  return {
    id: c.id,
    job_ids: ir.jobs.map(j => j.id),
    enabled: ir.jobs.map(j => j.enabled),
    gitlab: emitGitlab(ir),
    github: emitGithub(ir),
    mermaid_flow: mermaidFlow(ir),
  };
});
process.stdout.write(JSON.stringify(out, null, 1));
