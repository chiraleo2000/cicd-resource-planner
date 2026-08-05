# Assets — Claude CICD Analysis

วาง output / template ที่สร้างจาก Claude ไว้ในนี้:

## ประเภทไฟล์ที่จะอยู่ใน folder นี้
- Report templates (.md) — exported จาก Artifacts
- Pipeline diagrams (.mermaid / .svg)
- Executive report drafts (.md → convert to .docx via pandoc)
- Resource tables (.md → copy to Excel)

## Export Artifacts
- Artifact type `text/markdown` → save เป็น .md
- Artifact type `application/vnd.ant.mermaid` → save เป็น .mermaid
- ใช้ pandoc แปลง MD → DOCX: `pandoc report.md -o report.docx`
