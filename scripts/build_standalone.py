# -*- coding: utf-8 -*-
"""รวม web/index.html + CSS + JS + catalog.json เป็น HTML ไฟล์เดียว

เขียนทับ index.html ที่ราก — เปิดได้ทันที (file://, Live Preview, http.server)
ไม่ใช้ ES module และไม่ fetch JSON

รัน:  python scripts/build_standalone.py [optional-extra-output.html]
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(f"[ok] {path}  ({os.path.getsize(path) / 1024:,.0f} KB)")


def catalog_js(catalog: dict) -> str:
    # Escape < so a </script> inside JSON cannot close the HTML script tag
    payload = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e")
    return payload


def strip_es(src: str) -> str:
    src = re.sub(r"^\s*import\s+[\s\S]*?from\s+'[^']+';\s*$", "", src, flags=re.M)
    src = re.sub(r"^\s*export\s+class\s+", "class ", src, flags=re.M)
    src = re.sub(r"^\s*export\s+function\s+", "function ", src, flags=re.M)
    src = re.sub(r"^\s*export\s+\{[^}]*\};?\s*$", "", src, flags=re.M)
    return src


def main():
    extra_out = sys.argv[1] if len(sys.argv) > 1 else None
    html = read("web", "index.html")
    css = read("assets", "style.css")
    engine = strip_es(read("assets", "engine.js"))
    pipeline = strip_es(read("assets", "pipeline.js"))
    app = strip_es(read("assets", "app.js"))
    catalog = json.loads(read("data", "catalog.json"))

    if not catalog.get("tools"):
        raise SystemExit("catalog.json ไม่มี tools — รัน python scripts/build_catalog.py ก่อน")
    if catalog.get("schema_version") != "1.3.0":
        print("[warn] schema_version =", catalog.get("schema_version"), "(คาด 1.3.0)")

    html = html.replace(
        '<link rel="stylesheet" href="assets/style.css">',
        "<style>\n" + css + "\n</style>",
    )

    bundle = (
        "/* ===== bundled: assets/engine.js ===== */\n"
        + engine
        + "\n/* ===== bundled: assets/pipeline.js ===== */\n"
        + pipeline
        + "\n/* ===== bundled: assets/app.js ===== */\n"
        + app
    )
    if re.search(r"^\s*import\s+", bundle, re.M) or re.search(r"^\s*export\s+", bundle, re.M):
        raise SystemExit("ยังมี import/export หลงเหลือใน bundle — ห้ามเขียน index.html แบบนี้")

    payload = (
        '<script id="cicd-catalog">window.__STANDALONE__=true;'
        "window.__CATALOG__=" + catalog_js(catalog) + ";</script>\n"
        '<script id="cicd-app">\n' + bundle + "\n</script>"
    )
    marker = '<script type="module" src="assets/app.js"></script>'
    if marker not in html:
        raise SystemExit("web/index.html ต้องมี <script type=\"module\" src=\"assets/app.js\">")
    html = html.replace(marker, payload)

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = html.replace(
        "</head>",
        f"<!-- standalone build {stamp} schema {catalog['schema_version']} "
        f"tools={len(catalog['tools'])} — no fetch, no modules -->\n</head>",
        1,
    )

    leftovers = re.findall(r'(?:src|href)="(?!data:|#)([^"]+)"', html)
    if leftovers:
        print("[warn] ยังมีการอ้างอิงภายนอก: " + ", ".join(leftovers))
        sys.exit(1)

    # User-facing page MUST be the standalone file
    write(os.path.join(ROOT, "index.html"), html)
    write(os.path.join(ROOT, "planner-standalone.html"), html)
    write(os.path.join(ROOT, "dist", "planner-standalone.html"), html)
    if extra_out:
        write(extra_out if os.path.isabs(extra_out) else os.path.join(ROOT, extra_out), html)
    print("[ok] ไม่มีการอ้างอิงไฟล์หรือ network ภายนอก — เปิด index.html ได้เลย")


if __name__ == "__main__":
    main()
