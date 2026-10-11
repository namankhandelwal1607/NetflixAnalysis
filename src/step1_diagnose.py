import os
import json
import glob
import re

print("=" * 60)
print("STEP 1 DIAGNOSTIC AUDIT")
print("=" * 60)

report_dir = r"powerbi/netflix_report/processedData.Report/definition"
pages_dir = os.path.join(report_dir, "pages")

# 1a: Scan for hard-coded colors
dark_bg_patterns = [r"#141414", r"#1a1a1a", r"#1A1A1A", r"#000000", r"#0d0d0d", r"#222222"]
white_patterns = [r"#ffffff", r"#FFFFFF", r"\bwhite\b"]

conflicts_dark_bg = []
conflicts_white_text = []

for root, dirs, files in os.walk(report_dir):
    for f in files:
        if f.endswith(".json"):
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, report_dir)
            with open(path, "r", encoding="utf-8") as jf:
                content = jf.read()
                for pat in dark_bg_patterns:
                    if re.search(pat, content, re.IGNORECASE):
                        conflicts_dark_bg.append((rel_path, pat))
                for pat in white_patterns:
                    if re.search(pat, content, re.IGNORECASE):
                        conflicts_white_text.append((rel_path, pat))

print("\n--- 1a: Dark Backgrounds Found ---")
for p, pat in sorted(set(conflicts_dark_bg)):
    print(f"  {p}: matches {pat}")

print(f"\n--- 1a: Total Files with White/Light Text References: {len(set(p for p, _ in conflicts_white_text))} ---")
for p in sorted(set(p for p, _ in conflicts_white_text))[:25]:
    print(f"  {p}")

# 1b: Check transparency semantics in Page 1 (and others)
print("\n--- 1b: Transparency in Sidebar & KPI Cards ---")
for p in glob.glob(f"{pages_dir}/*/visuals/*/visual.json"):
    with open(p, "r", encoding="utf-8") as jf:
        try:
            d = json.load(jf)
            vname = d.get("name", "")
            if "sidebar" in vname or "kpi1" in vname or "p1_kpi" in vname:
                props = str(d.get("visual", {}).get("visualContainerObjects", {}))
                print(f"  {vname} in {os.path.basename(os.path.dirname(os.path.dirname(p)))}:")
                # Search for transparency in objects
                for obj_name, obj_list in d.get("visual", {}).get("visualContainerObjects", {}).items():
                    for item in obj_list:
                        props_dict = item.get("properties", {})
                        if "transparency" in props_dict:
                            print(f"    {obj_name}.transparency: {props_dict['transparency']}")
        except Exception as e:
            pass

# 1c: Check slicers across all pages
print("\n--- 1c: Slicers Audit (all 9 slicers) ---")
for page_folder in sorted(glob.glob(f"{pages_dir}/*")):
    page_id = os.path.basename(page_folder)
    page_json_path = os.path.join(page_folder, "page.json")
    with open(page_json_path, "r", encoding="utf-8") as pf:
        page_d = json.load(pf)
    print(f"\nPage: {page_id} ({page_d.get('displayName')})")
    
    # Check visualInteractions in page.json
    vis_interactions = page_d.get("visualInteractions", [])
    print(f"  visualInteractions count: {len(vis_interactions)}")
    for vi in vis_interactions:
        if vi.get("type") in ["NoFilter", "None", 2]:
            print(f"    WARNING: NoFilter interaction: {vi}")

    # Check visuals on page
    for vis_folder in sorted(glob.glob(f"{page_folder}/visuals/*")):
        vjson_path = os.path.join(vis_folder, "visual.json")
        if os.path.exists(vjson_path):
            with open(vjson_path, "r", encoding="utf-8") as vf:
                vd = json.load(vf)
            vtype = vd.get("visual", {}).get("visualType", "")
            vname = vd.get("name", "")
            if vtype == "slicer" or "slicer" in vname.lower():
                pos = vd.get("position", {})
                sync = vd.get("syncGroup", {})
                is_hidden = vd.get("isHidden", False)
                print(f"  Slicer: {vname} (folder {os.path.basename(vis_folder)})")
                print(f"    pos: x={pos.get('x')}, y={pos.get('y')}, w={pos.get('width')}, h={pos.get('height')}, z={pos.get('z')}, isHidden={is_hidden}")
                print(f"    syncGroup: {sync}")

# 1d: Compare global elements across pages
print("\n--- 1d: Global Elements Layout Comparison ---")
for page_folder in sorted(glob.glob(f"{pages_dir}/*")):
    page_id = os.path.basename(page_folder)
    print(f"\nPage {page_id}:")
    for vis_folder in sorted(glob.glob(f"{page_folder}/visuals/*")):
        vjson_path = os.path.join(vis_folder, "visual.json")
        if os.path.exists(vjson_path):
            with open(vjson_path, "r", encoding="utf-8") as vf:
                vd = json.load(vf)
            vname = vd.get("name", os.path.basename(vis_folder))
            vtype = vd.get("visual", {}).get("visualType", "")
            pos = vd.get("position", {})
            if any(k in vname.lower() for k in ["title", "filter", "summary", "sidebar", "nav", "tab", "slicer", "year", "genre", "language"]) or vtype in ["slicer", "textbox", "shape"]:
                print(f"  {vname} ({vtype}): x={pos.get('x')}, y={pos.get('y')}, w={pos.get('width')}, h={pos.get('height')}, z={pos.get('z')}")

# 1e: Mini month charts
print("\n--- 1e: Mini Month Charts Audit ---")
for p in glob.glob(f"{pages_dir}/*/visuals/*minibar*/visual.json"):
    with open(p, "r", encoding="utf-8") as jf:
        d = json.load(jf)
        vname = d.get("name", "")
        pos = d.get("position", {})
        query = d.get("visual", {}).get("query", {})
        vtype = d.get("visual", {}).get("visualType", "")
        objects = d.get("visual", {}).get("objects", {})
        vc_objects = d.get("visual", {}).get("visualContainerObjects", {})
        print(f"  {vname}: type={vtype}, pos={pos}")
        print(f"    has query: {bool(query)}, query keys: {list(query.keys()) if query else []}")
        print(f"    objects keys: {list(objects.keys())}")
        print(f"    padding in vc_objects: {vc_objects.get('padding', None)}")
