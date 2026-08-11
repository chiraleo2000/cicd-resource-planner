# วิธี push ขึ้น GitHub และเปิด Pages

repo นี้ commit ไว้เรียบร้อยแล้ว (มี git history 3 commit) เหลือแค่ต่อ remote แล้ว push

## 1. สร้าง repo บน GitHub

**แบบใช้ `gh` CLI** (ถ้าติดตั้งและ login แล้ว)

```bash
cd cicd-resource-planner
gh repo create cicd-resource-planner --public --source=. --remote=origin --push
gh api -X POST repos/:owner/cicd-resource-planner/pages -f build_type=workflow
```

**แบบทำผ่านหน้าเว็บ**

1. ไปที่ https://github.com/new สร้าง repo ชื่อ `cicd-resource-planner`
   — **ไม่ต้อง** ติ๊ก Add README / .gitignore / license เพราะมีอยู่แล้วในนี้
2. กลับมาที่เครื่อง แล้วรัน

```bash
cd cicd-resource-planner
git remote add origin https://github.com/<ORG_หรือ_USER>/cicd-resource-planner.git
git branch -M main
git push -u origin main
```

## 2. เปิด GitHub Pages (ทำครั้งเดียว)

ไปที่ repo → **Settings → Pages → Build and deployment → Source** เลือก **GitHub Actions**
แล้วสั่ง push อีกครั้ง (หรือกด Re-run ที่ workflow `Deploy to GitHub Pages`)

## 3. URL ที่จะได้

```
https://<ORG_หรือ_USER>.github.io/cicd-resource-planner/
```

หน้าอื่นที่ deploy ไปด้วย

| ไฟล์ | URL |
|---|---|
| โปรแกรมวางแผน | `https://<owner>.github.io/cicd-resource-planner/` |
| Excel | `.../dist/CICD_Tool_Resource_Matrix.xlsx` |
| HTML ไฟล์เดียว (Air-gapped) | `.../dist/planner-standalone.html` |
| ข้อมูลกลาง | `.../data/catalog.json` |
| รายงาน Compliance ของผังอ้างอิง | `.../reports/compliance.md` |

URL จริงจะแสดงในผลลัพธ์ของ job `deploy` ใน workflow run ด้วย

## 4. Workflow ที่จะทำงานให้อัตโนมัติ

| Workflow | เมื่อไหร่ | ทำอะไร |
|---|---|---|
| `CI — Validate & Compliance Gate` | ทุก push / PR | ตรวจว่า `catalog.json` ตรงกับ source, รัน verification suite (Python ↔ JavaScript ต้องให้ผลตรงกัน), ตรวจว่าไม่มี dependency ภายนอก, รัน Compliance Gate กับ `plans/arch-*.json` (ต้องผ่าน 100% ไม่งั้น build fail), สร้าง Excel + standalone HTML เป็น artifact |
| `Deploy to GitHub Pages` | push เข้า `main` | build ใหม่ทั้งหมดแล้ว deploy |

## 5. ถ้าเป็น repo ภายในองค์กร (GitHub Enterprise / GitLab)

- **GitHub Enterprise Server** — ใช้ได้เหมือนกัน เปลี่ยน remote เป็นโดเมนขององค์กร
  Pages ต้องเปิดที่ระดับ instance ก่อน (ให้ผู้ดูแลเปิด GitHub Pages ใน Management Console)
- **GitLab** — เพิ่มไฟล์ `.gitlab-ci.yml` ตามนี้ แล้วใช้ GitLab Pages

```yaml
image: python:3.12
stages: [test, deploy]

verify:
  stage: test
  before_script:
    - apt-get update -qq && apt-get install -y -qq nodejs
    - pip install -r requirements.txt
  script:
    - python3 scripts/build_catalog.py
    - git diff --exit-code -- data/catalog.json
    - python3 scripts/verify.py
    - node scripts/lint_frontend.mjs
    - python3 scripts/check_compliance.py "plans/arch-*.json"

pages:
  stage: deploy
  before_script:
    - pip install -r requirements.txt
  script:
    - python3 scripts/build_catalog.py
    - python3 scripts/build_xlsx.py dist/CICD_Tool_Resource_Matrix.xlsx
    - python3 scripts/build_standalone.py dist/planner-standalone.html
    - mkdir -p public && cp index.html public/ && cp -r assets data dist public/
  artifacts:
    paths: [public]
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## 6. เครือข่ายปิด (ไม่มี GitHub เลย)

ใช้ `dist/planner-standalone.html` ได้ทันที — เป็นไฟล์เดียว ไม่เรียก network
ไม่ต้องมี web server ดับเบิลคลิกเปิดได้เลย (มีเทสต์ `test_standalone_bundle` บังคับไว้ว่า
ต้องไม่มีการอ้างอิงภายนอกหลงเหลือ)
