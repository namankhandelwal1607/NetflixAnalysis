import os
import json
import glob
import datetime

print("=== STEP 2: IDENTIFY THE CORRECT BACKUP ===")

backup_dirs = sorted(glob.glob("powerbi/netflix_report_backup*"))

for bdir in backup_dirs:
    # Get last modified time
    mtime = os.path.getmtime(bdir)
    dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    print(f"\nFolder: {bdir} (Modified: {dt})")

    # a) Check registered theme in report.json
    rep_json = os.path.join(bdir, "processedData.Report/definition/report.json")
    if not os.path.exists(rep_json):
        # Check subfolder nesting if any
        sub_rep = glob.glob(f"{bdir}/**/report.json", recursive=True)
        if sub_rep:
            rep_json = sub_rep[0]
    
    has_netflix_dark = False
    has_netflix_light = False
    if os.path.exists(rep_json):
        with open(rep_json, "r", encoding="utf-8") as f:
            try:
                rd = json.load(f)
                custom_theme = rd.get("themeCollection", {}).get("customTheme", {})
                custom_theme_name = custom_theme.get("name")
                for pkg in rd.get("resourcePackages", []):
                    for item in pkg.get("items", []):
                        if "NetflixDark" in item.get("name", ""):
                            has_netflix_dark = True
                        if "NetflixLight" in item.get("name", ""):
                            has_netflix_light = True
                print(f"  a) Theme: customTheme={custom_theme_name}, hasDark={has_netflix_dark}, hasLight={has_netflix_light}")
            except Exception as e:
                print(f"  a) Error reading report.json: {e}")
    else:
        print("  a) report.json NOT FOUND")

    # b) Check page backgrounds and sidebar / wallpaper
    pages = glob.glob(f"{bdir}/**/pages/*/page.json", recursive=True)
    print(f"  b) Page count: {len(pages)}")
    for p in pages:
        pname = os.path.basename(os.path.dirname(p))
        with open(p, "r", encoding="utf-8") as f:
            pd = json.load(f)
        disp = pd.get("displayName")
        bg_objs = pd.get("objects", {}).get("background", [])
        bg_str = str(bg_objs)
        has_wallpaper = "bg_gradient" in bg_str
        print(f"     Page {disp} ({pname}): bg_objs count={len(bg_objs)}, has_wallpaper={has_wallpaper}")

    # Check for sidebar visual
    sidebar_vis = glob.glob(f"{bdir}/**/visuals/*sidebar*", recursive=True)
    print(f"     Sidebar visuals found: {len(sidebar_vis)}")

    # c) Check fact_titles.tmdl for runtime_outlier and score_outlier
    tmdl_files = glob.glob(f"{bdir}/**/tables/fact_titles.tmdl", recursive=True)
    if tmdl_files:
        with open(tmdl_files[0], "r", encoding="utf-8") as f:
            tmdl_text = f.read()
        has_runtime_outlier = "column runtime_outlier" in tmdl_text
        has_score_outlier = "column score_outlier" in tmdl_text
        has_outlier_type = "column outlier_type" in tmdl_text
        has_circ = "score_bucket_order" in tmdl_text
        print(f"  c) fact_titles.tmdl: runtime_outlier={has_runtime_outlier}, score_outlier={has_score_outlier}, outlier_type={has_outlier_type}, score_bucket_order={has_circ}")
    else:
        print("  c) fact_titles.tmdl NOT FOUND")

    # d) Check KPI cards count on Page 1 and 2
    # Page 1 ID = 95c0693daf92b6d6c188, Page 2 ID = c048b71f92e143fa9d30, Page 3 ID = e89c4d21f8a74e5088bd
    p1_kpis = glob.glob(f"{bdir}/**/95c0693daf92b6d6c188/visuals/*kpi*", recursive=True)
    p2_kpis = glob.glob(f"{bdir}/**/c048b71f92e143fa9d30/visuals/*kpi*", recursive=True)
    p3_visuals = glob.glob(f"{bdir}/**/e89c4d21f8a74e5088bd/visuals/*", recursive=True)
    print(f"  d) Visual counts: P1 KPI count={len(p1_kpis)}, P2 KPI count={len(p2_kpis)}, P3 visual count={len(p3_visuals)}")
