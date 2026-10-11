import os
import json
import glob
import hashlib

print("=" * 70)
print("ROLLBACK VERIFICATION AUDIT")
print("=" * 70)

active_dir = r"powerbi/netflix_report"
backup_dir = r"powerbi/netflix_report_backup_design"

# 1. FILE HASH COMPARISON
print("\n[CHECK 1: FILE HASH COMPARISON (Active vs Backup)]")
def get_file_hash(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def get_all_files(root_dir):
    file_map = {}
    for r, dirs, files in os.walk(root_dir):
        for f in files:
            full_p = os.path.join(r, f)
            rel_p = os.path.relpath(full_p, root_dir)
            file_map[rel_p] = full_p
    return file_map

active_files = get_all_files(active_dir)
backup_files = get_all_files(backup_dir)

hash_mismatches = []
missing_in_active = []
extra_in_active = []

for rel_p, b_full in backup_files.items():
    if rel_p not in active_files:
        missing_in_active.append(rel_p)
    else:
        a_hash = get_file_hash(active_files[rel_p])
        b_hash = get_file_hash(b_full)
        if a_hash != b_hash:
            hash_mismatches.append(rel_p)

for rel_p in active_files:
    if rel_p not in backup_files:
        extra_in_active.append(rel_p)

print(f"  Total files in backup: {len(backup_files)}")
print(f"  Total files in active: {len(active_files)}")
print(f"  Missing in active:     {len(missing_in_active)}")
print(f"  Extra in active:       {len(extra_in_active)}")
print(f"  Hash mismatches:       {len(hash_mismatches)}")

if not missing_in_active and not extra_in_active and not hash_mismatches:
    print("  RESULT: ZERO differences found! 100% byte-for-byte exact hash match.")
else:
    print(f"  FAILED: Differences found! Extra={extra_in_active}, Missing={missing_in_active}, Mismatch={hash_mismatches}")

# 2. THEME REGISTRATION IN report.json
print("\n[CHECK 2: THEME REGISTRATION IN report.json]")
report_json_path = os.path.join(active_dir, "processedData.Report/definition/report.json")
with open(report_json_path, "r", encoding="utf-8") as f:
    report_json = json.load(f)

custom_theme = report_json.get("themeCollection", {}).get("customTheme", {})
print(f"  customTheme: {custom_theme}")

registered_themes = []
for pkg in report_json.get("resourcePackages", []):
    for item in pkg.get("items", []):
        if item.get("type") == "CustomTheme" or "json" in item.get("path", ""):
            registered_themes.append((item.get("name"), item.get("path")))
print(f"  Registered theme items: {registered_themes}")

if custom_theme.get("name") == "NetflixDark" and len(registered_themes) == 1 and registered_themes[0][0] == "NetflixDark":
    print("  RESULT: PASSED - Only NetflixDark is registered in report.json.")
else:
    print("  RESULT: WARNING - Unexpected theme registration.")

# 3. JSON PARSE & FIELD REFERENCES IN SEMANTIC MODEL
print("\n[CHECK 3: JSON PARSE & FIELD REFERENCE VALIDATION]")
json_errors = 0
for r, dirs, files in os.walk(os.path.join(active_dir, "processedData.Report")):
    for f in files:
        if f.endswith(".json"):
            fp = os.path.join(r, f)
            try:
                with open(fp, "r", encoding="utf-8") as jf:
                    json.load(jf)
            except Exception as e:
                print(f"  Error parsing {fp}: {e}")
                json_errors += 1
print(f"  JSON parse check: {json_errors} errors across all JSON files.")

# Validate PBIR field references
import subprocess
val_res = subprocess.run(["python", "src/validate_pbir.py"], capture_output=True, text=True)
print(f"  PBIR Field References validation:")
print(f"  {val_res.stdout.strip()}")

# 4. PAGES & VISUAL COUNTS
print("\n[CHECK 4: PAGES & VISUAL COUNTS]")
pages_dir = os.path.join(active_dir, "processedData.Report/definition/pages")
page_folders = sorted(glob.glob(f"{pages_dir}/*"))
for pdir in page_folders:
    if not os.path.isdir(pdir): continue
    pid = os.path.basename(pdir)
    pfile = os.path.join(pdir, "page.json")
    with open(pfile, "r", encoding="utf-8") as pf:
        pd = json.load(pf)
    disp = pd.get("displayName")
    vis_count = len(glob.glob(f"{pdir}/visuals/*"))
    kpi_count = len(glob.glob(f"{pdir}/visuals/*kpi*"))
    slicer_count = len(glob.glob(f"{pdir}/visuals/*slicer*"))
    print(f"  Page '{disp}' (ID: {pid}):")
    print(f"    Total visuals: {vis_count} | KPI cards: {kpi_count} | Slicers: {slicer_count}")

# 5. MODEL MEASURES & COLUMNS VERIFICATION
print("\n[CHECK 5: SEMANTIC MODEL MEASURES & COLUMNS AUDIT]")
fact_tmdl_path = os.path.join(active_dir, "processedData.SemanticModel/definition/tables/fact_titles.tmdl")
with open(fact_tmdl_path, "r", encoding="utf-8") as f:
    fact_text = f.read()

dim_date_path = os.path.join(active_dir, "processedData.SemanticModel/definition/tables/dim_date.tmdl")
with open(dim_date_path, "r", encoding="utf-8") as f:
    date_text = f.read()

required_measures = [
    "Total Titles",
    "Mature Period Titles",
    "Avg Runtime",
    "Avg IMDb Score",
    "Top Genre Share %",
    "Titles YoY Growth %",
    "Catalog Avg IMDb"
]

required_columns = [
    "runtime_outlier",
    "score_outlier"
]

for m in required_measures:
    present = f"measure '{m}'" in fact_text or f"measure {m}" in fact_text
    print(f"  Measure '{m}': {'PRESENT' if present else 'MISSING'}")

for c in required_columns:
    present = f"column {c}" in fact_text
    print(f"  Column '{c}': {'PRESENT' if present else 'MISSING'}")

month_sort = "sortByColumn: month_num" in date_text
weekday_sort = "sortByColumn: day_of_week" in date_text
print(f"  sortByColumn on month_name (month_num): {'PRESENT' if month_sort else 'MISSING'}")
print(f"  sortByColumn on weekday_name (day_of_week): {'PRESENT' if weekday_sort else 'MISSING'}")

# 6. LEFTOVER LIGHT-DESIGN MEASURES
print("\n[CHECK 6: LEFTOVER LIGHT-DESIGN MEASURES AUDIT]")
light_measures = [
    "Filter Summary Text",
    "Latest Full Year",
    "Total Titles Prior Year",
    "Total Titles Latest Year",
    "Total Titles YoY Delta %",
    "Total Titles Pill Text",
    "Total Titles Pill Color",
    "Avg IMDb Prior Year",
    "Avg IMDb Latest Year",
    "Avg IMDb YoY Delta %",
    "Avg IMDb Pill Text",
    "Avg IMDb Pill Color",
    "Avg Runtime Prior Year",
    "Avg Runtime Latest Year",
    "Avg Runtime YoY Delta %",
    "Avg Runtime Pill Text",
    "Avg Runtime Pill Color",
    "Month Release Color",
    "Annual Release Color",
    "Avg Annual Releases",
    "Avg IMDb Score (display)",
    "Heatmap Cell Font Color"
]

leftovers_found = []
for lm in light_measures:
    if f"measure '{lm}'" in fact_text or f"measure {lm}" in fact_text:
        leftovers_found.append(lm)

if not leftovers_found:
    print("  RESULT: PASSED - 0 leftover light-design measures found in model.")
else:
    print(f"  Leftover light-design measures: {leftovers_found}")

# 7. KNOWN IMPERFECTIONS AUDIT
print("\n[CHECK 7: KNOWN IMPERFECTIONS IN BACKUP AUDIT]")
if "score_bucket_order" in fact_text:
    print("  NOTE: fact_titles.tmdl contains 'column score_bucket_order' and 'sortByColumn: score_bucket_order' (pre-existing in this backup).")

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
