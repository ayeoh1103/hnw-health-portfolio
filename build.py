# -*- coding: utf-8 -*-
"""将统计结果与 ECharts 库注入模板，产出单文件、可离线打开的作品集页面 index.html"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "template.html"), encoding="utf-8") as f:
    html = f.read()
with open(os.path.join(BASE_DIR, "dashboard_data.json"), encoding="utf-8") as f:
    data = json.load(f)
with open(os.path.join(BASE_DIR, "echarts.min.js"), encoding="utf-8") as f:
    echarts = f.read()

html = html.replace("__ECHARTS_LIB__", echarts)
html = html.replace("__DASHBOARD_DATA__", json.dumps(data, ensure_ascii=False))

out = os.path.join(BASE_DIR, "index.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"生成完成: {out}  ({os.path.getsize(out)/1024/1024:.2f} MB)")
