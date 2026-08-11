/* รัน engine.js (ฝั่งเบราว์เซอร์) ผ่าน Node เพื่อเทียบผลกับ engine.py
 * ใช้:  node scripts/verify_engines.mjs cases.json > js_out.json
 */
import { readFileSync } from 'node:fs';
import { Planner } from '../assets/engine.js';

const catalog = JSON.parse(readFileSync(new URL('../data/catalog.json', import.meta.url), 'utf8'));
const cases = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const P = new Planner(catalog);

const out = cases.map(c => {
  const r = P.colocate(c.tools, {
    horizonMonths: c.horizon, mode: c.mode, scaleFactor: c.scale,
    retentionOverride: c.retention ?? null, executors: c.executors || {},
    useRec: !!c.use_rec,
  });
  const comp = P.complianceCheck(c.tools, c.profile, c.impact,
                                 c.frameworks ?? null, c.block ?? null, c.ext ?? null);
  return {
    id: c.id,
    a: [r.method_a.vcpu, r.method_a.ram_gb],
    b1: [r.method_b.vcpu, r.method_b.ram_gb],
    b2: [r.method_b2.vcpu, r.method_b2.ram_gb],
    c: [r.method_c.vcpu, r.method_c.ram_gb],
    governing: [r.governing.vcpu, r.governing.ram],
    required: [r.required.vcpu, r.required.ram_gb, r.required.disk_os_gb, r.required.disk_data_gb],
    allocated: [r.allocated.vcpu, r.allocated.ram_gb, r.allocated.disk_os_gb, r.allocated.disk_data_gb],
    storage: [r.storage.install_gb, r.storage.data_gb],
    long_term: r.storage.long_term.map(x => [x.months, x.data_gb, x.provisioned_gb]),
    weights: r.tools.map(t => [t.tool_id, t.weight, t.w_vcpu, t.w_ram]),
    compliance: [comp.score, comp.passed, comp.total_rules, comp.failed_count,
                 Object.keys(comp.gaps).sort(), comp.recommendations.map(x => x.tool_id),
                 comp.uncovered_caps, Object.keys(comp.by_framework).sort(),
                 Object.fromEntries(Object.entries(comp.by_framework)
                   .map(([k, v]) => [k, [v.passed, v.total]]))],
  };
});
process.stdout.write(JSON.stringify(out, null, 1));
