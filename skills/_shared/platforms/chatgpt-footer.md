## ChatGPT file outputs

```python
# Resource constants (must match scripts/catalog_data.py)
OS_RESERVE = {"vcpu": 1, "ram_gb": 2, "disk_gb": 20}
W_BASE, W_SPAN = 0.50, 0.45
DISK_FREE = 0.25
```

Always produce: (1) `.xlsx` workbook with VM / tool / compliance / cost / timeline sheets, (2) `.docx` executive summary, (3) at least one chart (cost or Gantt).

### Custom GPT setup

1. Name: **CICD Implementation Analyst**
2. Instructions: Role + principles + this file
3. Knowledge: this `instructions.md` + `CICD_Tool_Resource_Matrix.xlsx` + Compliance register
4. Enable Code Interpreter, Browsing, Canvas
5. Starters: "วิเคราะห์ TOR ที่แนบ", "คำนวณ resource ภาครัฐ", "สร้าง Excel + Word", "เทียบ Minimum / Recommended / Optimal"
