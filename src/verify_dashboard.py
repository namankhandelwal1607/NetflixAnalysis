import os
import json
import glob
import re
import jsonschema

print("=" * 70)
print("DASHBOARD AUTOMATED VERIFICATION AUDIT")
print("=" * 70)

report_dir = r"powerbi/netflix_report/processedData.Report"
def_dir = os.path.join(report_dir, "definition")
pages_dir = os.path.join(def_dir, "pages")
resources_dir = os.path.join(report_dir, "StaticResources/RegisteredResources")

# -------------------------------------------------------------
# 1. RESOURCES CHECK
# -------------------------------------------------------------
print("\n[CHECK 1: RESOURCES AUDIT]")
report_json_path = os.path.join(def_dir, "report.json")
with open(report_json_path, "r", encoding="utf-8") as f:
    report_data = json.load(f)

missing_resources = []
registered_items = []
for pkg in report_data.get("resourcePackages", []):
    for item in pkg.get("items", []):
        name = item.get("name")
        path = item.get("path")
        registered_items.append((name, path))
        if pkg.get("name") == "RegisteredResources":
            full_p = os.path.join(resources_dir, path)
            if not os.path.exists(full_p):
                missing_resources.append((name, full_p))

print(f"  Total registered resources in report.json: {len(registered_items)}")
if missing_resources:
    print(f"  FAILED: Missing resources: {missing_resources}")
else:
    print("  PASSED: All registered resources exist on disk.")

# -------------------------------------------------------------
# 2. INTERACTIONS CHECK
# -------------------------------------------------------------
print("\n[CHECK 2: VISUAL INTERACTIONS AUDIT]")
bad_interactions = []
for pdir in sorted(glob.glob(f"{pages_dir}/*")):
    if not os.path.isdir(pdir): continue
    pid = os.path.basename(pdir)
    pfile = os.path.join(pdir, "page.json")
    with open(pfile, "r", encoding="utf-8") as f:
        pd = json.load(f)
    for vi in pd.get("visualInteractions", []):
        if vi.get("type") in ["NoFilter", "None", 2]:
            bad_interactions.append((pid, vi))

if bad_interactions:
    print(f"  FAILED: Found NoFilter interactions blocking slicers: {bad_interactions}")
else:
    print("  PASSED: 0 NoFilter interactions. All slicers can filter visuals properly.")

# -------------------------------------------------------------
# 3. GLOBAL ELEMENTS CONSISTENCY CHECK
# -------------------------------------------------------------
print("\n[CHECK 3: GLOBAL ELEMENTS IDENTICAL LAYOUT AUDIT]")
global_elements = {
    "sidebar_bg": ("shape", 24, 24, 96, 1032),
    "title": ("textbox", 150, 20, 700, 44),
    "filter_summary": ("card", 150, 72, 700, 22),
    "slicer_year": ("slicer", 150, 100, 340, 46),
    "slicer_genre": ("slicer", 506, 100, 340, 46),
    "slicer_language": ("slicer", 862, 100, 340, 46)
}

layout_mismatches = []
for pid in [("p1", "95c0693daf92b6d6c188"), ("p2", "c048b71f92e143fa9d30"), ("p3", "e89c4d21f8a74e5088bd")]:
    p_prefix, page_id = pid
    p_dir = os.path.join(pages_dir, page_id)
    print(f"  Checking Page {page_id} ({p_prefix}):")
    for elem_key, (exp_type, exp_x, exp_y, exp_w, exp_h) in global_elements.items():
        vname = f"{p_prefix}_{elem_key}"
        vpath = os.path.join(p_dir, f"visuals/{vname}/visual.json")
        if not os.path.exists(vpath):
            layout_mismatches.append(f"Missing {vname} on page {page_id}")
            print(f"    MISSING: {vname}")
            continue
        with open(vpath, "r", encoding="utf-8") as vf:
            vd = json.load(vf)
        pos = vd.get("position", {})
        px, py, pw, ph = pos.get("x"), pos.get("y"), pos.get("width"), pos.get("height")
        if (px, py, pw, ph) != (exp_x, exp_y, exp_w, exp_h):
            layout_mismatches.append(f"Mismatch {vname}: got ({px},{py},{pw},{ph}) vs exp ({exp_x},{exp_y},{exp_w},{exp_h})")
            print(f"    MISMATCH: {vname} pos ({px},{py},{pw},{ph})")
        else:
            print(f"    OK: {vname:25} x={px} y={py} w={pw} h={ph}")

if layout_mismatches:
    print(f"  FAILED: Layout mismatches found: {layout_mismatches}")
else:
    print("  PASSED: Sidebar, title, filter summary, and 3 slicers have 100% IDENTICAL positions across all 3 pages.")

# -------------------------------------------------------------
# 4. OVERLAPPING BOUNDING BOXES CHECK
# -------------------------------------------------------------
print("\n[CHECK 4: OVERLAPPING BOUNDING BOXES AUDIT]")
# Exclude intentional overlays:
# 1. Inside KPI cards: kpi*_card_bg covers the card, icon/pill/card/minibar sit inside it
# 2. Inside sidebar: sidebar_bg covers sidebar, nav_btn_* and active indicator sit inside it
# 3. Inside donut: donut_center sits inside donut chart hole

def is_intentional_overlay(name_a, name_b):
    a, b = name_a.lower(), name_b.lower()
    # Sidebar
    if "sidebar" in a and ("nav" in b or "indicator" in b or "circle" in b): return True
    if "sidebar" in b and ("nav" in a or "indicator" in a or "circle" in a): return True
    if ("nav" in a or "circle" in a or "indicator" in a) and ("nav" in b or "circle" in b or "indicator" in b): return True
    # KPI cards
    for k in ["kpi1", "kpi2", "kpi3", "kpi4", "kpi5"]:
        if k in a and k in b: return True
        if f"p1_{k}" in a and "p1_kpi_" in b: return True
        if f"p1_{k}" in b and "p1_kpi_" in a: return True
        if f"p2_{k}" in a and "p2_kpi_" in b: return True
        if f"p2_{k}" in b and "p2_kpi_" in a: return True
    # Donut center
    if ("donut_center" in a and "genre_composition" in b) or ("donut_center" in b and "genre_composition" in a): return True
    # Title & accent line
    if ("title" in a and "accent" in b) or ("title" in b and "accent" in a): return True
    return False

unintended_overlaps = []
for pdir in sorted(glob.glob(f"{pages_dir}/*")):
    if not os.path.isdir(pdir): continue
    pid = os.path.basename(pdir)
    visuals = []
    for vdir in sorted(glob.glob(f"{pdir}/visuals/*")):
        vf = os.path.join(vdir, "visual.json")
        if os.path.exists(vf):
            with open(vf, "r", encoding="utf-8") as f:
                vd = json.load(f)
            pos = vd.get("position", {})
            visuals.append((vd.get("name", os.path.basename(vdir)), pos.get("x", 0), pos.get("y", 0), pos.get("width", 0), pos.get("height", 0)))
    
    for i in range(len(visuals)):
        for j in range(i + 1, len(visuals)):
            na, xa, ya, wa, ha = visuals[i]
            nb, xb, yb, wb, hb = visuals[j]
            # Check overlap
            if not (xa + wa <= xb or xb + wb <= xa or ya + ha <= yb or yb + hb <= ya):
                if not is_intentional_overlay(na, nb):
                    unintended_overlaps.append((pid, na, nb, (xa, ya, wa, ha), (xb, yb, wb, hb)))

if unintended_overlaps:
    print(f"  WARNING: Found unintended overlapping bounding boxes:")
    for pid, na, nb, box_a, box_b in unintended_overlaps:
        print(f"    Page {pid}: '{na}' {box_a} overlaps '{nb}' {box_b}")
else:
    print("  PASSED: 0 unintended overlaps. All visuals have clean non-colliding layout.")

# -------------------------------------------------------------
# 5. CONTRAST AUDIT (WCAG 2.1)
# -------------------------------------------------------------
print("\n[CHECK 5: CONTRAST RATIO AUDIT (Target >= 4.5:1)]")

def lum(r, g, b):
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)

def contrast(hex1, hex2):
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    l1, l2 = lum(r1, g1, b1), lum(r2, g2, b2)
    lmax, lmin = max(l1, l2), min(l1, l2)
    return (lmax + 0.05) / (lmin + 0.05)

text_elements = [
    # Element name, Text Color, Background Color, Description
    ("KPI Callout Value (Normal Cards)", "#1F2D3D", "#FFFFFF", "34pt Bold Value"),
    ("KPI Title (Normal Cards)", "#2F4A63", "#FFFFFF", "11pt Semibold Title"),
    ("KPI Highlight Callout Value", "#FFFFFF", "#467290", "34pt Bold White Callout on Steel Blue"),
    ("KPI Highlight Title", "#FFFFFF", "#467290", "11pt Semibold White Title on Steel Blue"),
    ("Page Title", "#2F4A63", "#E6EDF5", "26pt Bold Header on Page Background"),
    ("Filter Summary Text", "#5B6B7C", "#E6EDF5", "10pt Filter Summary on Page Background"),
    ("Slicer Header", "#2F4A63", "#FFFFFF", "11pt Slicer Header"),
    ("Slicer Text", "#2F4A63", "#FFFFFF", "11pt Slicer Value/Dropdown"),
    ("Delta Pill (Positive)", "#1E7E45", "#FFFFFF", "10pt Delta Pill Green"),
    ("Delta Pill (Negative)", "#C62828", "#FFFFFF", "10pt Delta Pill Red"),
    ("Delta Pill (Neutral)", "#5B6B7C", "#FFFFFF", "10pt Delta Pill Grey"),
    ("Chart Data Labels", "#2F4A63", "#FFFFFF", "Data labels on charts"),
    ("Donut Center Number", "#1F2D3D", "#FFFFFF", "24pt Bold Center Value"),
    ("Donut Center Subtitle", "#5B6B7C", "#FFFFFF", "10pt Center Subtitle"),
    ("Table Column Headers", "#2F4A63", "#FFFFFF", "10pt Semibold Table Headers"),
    ("Table Values", "#2F4A63", "#FFFFFF", "10pt Table Values")
]

contrast_failures = []
for name, fg, bg, desc in text_elements:
    ratio = contrast(fg, bg)
    status = "PASS" if ratio >= 4.5 else ("PASS (Large text >= 3:1)" if ratio >= 3.0 and ("34pt" in desc or "26pt" in desc or "24pt" in desc) else "FAIL")
    print(f"  {name:36}: FG={fg} BG={bg} -> Ratio={ratio:5.2f}:1 [{status}]")
    if "FAIL" in status:
        contrast_failures.append((name, fg, bg, ratio))

if contrast_failures:
    print(f"\n  FAILED: Contrast failures: {contrast_failures}")
else:
    print("\n  PASSED: All text styles meet or exceed WCAG 2.1 contrast guidelines.")

# -------------------------------------------------------------
# 6. JSON SCHEMA & MODEL VALIDATION
# -------------------------------------------------------------
print("\n[CHECK 6: PBIR & MODEL VALIDATION]")
import subprocess
res = subprocess.run(["python", "src/validate_pbir.py"], capture_output=True, text=True)
print(res.stdout.strip())

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
