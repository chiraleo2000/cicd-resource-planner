/* ตรวจข้อห้ามของโค้ดฝั่งหน้าเว็บ
 *  1. ห้ามใช้ browser storage API (localStorage / sessionStorage) — ข้อกำหนดของ artifact
 *  2. ห้ามเรียก URL ภายนอก — ต้องทำงานได้ในเครือข่าย Air-gapped ของภาครัฐ
 * ตรวจเฉพาะโค้ดจริง โดยตัด comment และ string literal ออกก่อน เพื่อไม่ให้คำในคำอธิบายทำให้ fail
 */
import { readFileSync, readdirSync } from 'node:fs';

const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:])\/\/.*$/gm, '$1');
const files = readdirSync('assets').filter(f => f.endsWith('.js')).map(f => 'assets/' + f);
let bad = 0;

for (const f of files) {
  const code = stripComments(readFileSync(f, 'utf8'));
  const storage = code.match(/\b(?:window\.)?(localStorage|sessionStorage)\s*[.[]/g);
  if (storage) { console.error(`[FAIL] ${f}: ใช้ browser storage API -> ${[...new Set(storage)]}`); bad++; }
  const urls = code.match(/["'`]https?:\/\/(?!localhost|127\.0\.0\.1)[^"'`]*/g);
  if (urls) { console.error(`[FAIL] ${f}: เรียก URL ภายนอก -> ${[...new Set(urls)]}`); bad++; }
  if (!storage && !urls) console.log(`[ok] ${f}`);
}
if (bad) { console.error(`พบปัญหา ${bad} รายการ`); process.exit(1); }
console.log('ผ่านการตรวจทั้งหมด');
