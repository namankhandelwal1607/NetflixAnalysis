import os
import json
import glob
import re

report_dir = r"powerbi/netflix_report/processedData.Report/definition"
pages_dir = os.path.join(report_dir, "pages")

print("=== DEEP DIVE: 1a COLOR CONFLICTS ===")

def search_colors(d, file_rel, parent_key=""):
    conflicts = []
    if isinstance(d, dict):
        for k, v in d.items():
            current_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, str):
                # Check dark background
                if any(c in v.upper() for c in ["#141414", "#1A1A1A", "#000000", "#0D0D0D", "#222222", "#3A3A3A"]):
                    # Ignore dropShadow color #000000 (standard for shadows)
                    if "dropShadow" not in current_key:
                        conflicts.append((current_key, v, "dark_bg_or_stroke"))
                # Check white text/font color
                if any(c in v.upper() for c in ["#FFFFFF", "WHITE"]):
                    if any(term in current_key.lower() for term in ["fontcolor", "color", "labels"]):
                        # Check if this is the highlighted KPI card (Total Titles) or sidebar icon where white is allowed
                        if "kpi1" not in file_rel and "p1_kpi_total_titles" not in file_rel and "sidebar" not in file_rel and "nav" not in file_rel:
                            conflicts.append((current_key, v, "white_text"))
            elif isinstance(v, (dict, list)):
                conflicts.extend(search_colors(v, file_rel, current_key))
    elif isinstance(d, list):
        for i, item in enumerate(d):
            conflicts.extend(search_colors(item, file_rel, f"{parent_key}[{i}]"))
    return conflicts

all_conflicts = {}
for root, dirs, files in os.walk(pages_dir):
    for f in files:
        if f.endswith(".json"):
            path = os.path.join(root, f)
            rel = os.path.relpath(path, pages_dir)
            with open(path, "r", encoding="utf-8") as jf:
                try:
                    data = json.load(jf)
                    confs = search_colors(data, rel)
                    if confs:
                        all_conflicts[rel] = confs
                except Exception as ex:
                    pass

print(f"Found conflicts in {len(all_conflicts)} files:\n")
for fpath, confs in sorted(all_conflicts.items()):
    print(f"File: {fpath}")
    for k, v, ctype in confs:
        print(f"   [{ctype}] {k} = {v}")
