import os
import json
import glob

report_dir = r"powerbi/netflix_report/processedData.Report/definition"
pages_dir = os.path.join(report_dir, "pages")

print("=== SLICER AUDIT ACROSS ALL PAGES ===")

for pdir in sorted(glob.glob(f"{pages_dir}/*")):
    if not os.path.isdir(pdir):
        continue
    page_id = os.path.basename(pdir)
    page_json = os.path.join(pdir, "page.json")
    with open(page_json, "r", encoding="utf-8") as f:
        pd = json.load(f)
    print(f"\n--- Page: {page_id} ({pd.get('displayName')}) ---")
    print(f"visualInteractions: {pd.get('visualInteractions', [])}")

    # List all visuals on this page
    visuals = []
    for vdir in sorted(glob.glob(f"{pdir}/visuals/*")):
        vfile = os.path.join(vdir, "visual.json")
        if os.path.exists(vfile):
            with open(vfile, "r", encoding="utf-8") as vf:
                vd = json.load(vf)
                visuals.append((os.path.basename(vdir), vd))

    slicers = [v for v in visuals if v[1].get("visual", {}).get("visualType") == "slicer" or "slicer" in v[0].lower()]
    non_slicers = [v for v in visuals if v not in slicers]

    for s_name, s_data in slicers:
        s_pos = s_data.get("position", {})
        sx = s_pos.get("x", 0)
        sy = s_pos.get("y", 0)
        sw = s_pos.get("width", 0)
        sh = s_pos.get("height", 0)
        sz = s_pos.get("z", 0)
        s_sync = s_data.get("syncGroup", {})
        s_hidden = s_data.get("isHidden", False)
        print(f"\n  Slicer '{s_name}': pos=({sx}, {sy}, w={sw}, h={sh}, z={sz}), hidden={s_hidden}, sync={s_sync}")
        
        # Check field binding
        projections = s_data.get("visual", {}).get("query", {}).get("queryState", {}).get("Values", {}).get("projections", [])
        field_names = []
        for p in projections:
            fld = p.get("field", {})
            if "Column" in fld:
                col = fld["Column"]
                field_names.append(f"{col.get('Expression', {}).get('SourceRef', {}).get('Entity')}[{col.get('Property')}]")
        print(f"    Field bound: {field_names}")

        # Check visualContainerObjects and visual objects for dark styling
        vstr = json.dumps(s_data)
        dark_matches = [c for c in ["#141414", "#1A1A1A", "#1a1a1a", "#000000", "#3A3A3A", "#3a3a3a"] if c in vstr]
        print(f"    Dark styling colors present: {dark_matches}")

        # Check for overlaps with higher z visuals
        overlapping_covers = []
        for o_name, o_data in non_slicers:
            opos = o_data.get("position", {})
            ox = opos.get("x", 0)
            oy = opos.get("y", 0)
            ow = opos.get("width", 0)
            oh = opos.get("height", 0)
            oz = opos.get("z", 0)
            # check rectangle intersection
            if not (sx + sw <= ox or ox + ow <= sx or sy + sh <= oy or oy + oh <= sy):
                # overlaps!
                if oz >= sz:
                    overlapping_covers.append((o_name, oz, (ox, oy, ow, oh)))
        if overlapping_covers:
            print(f"    WARNING: Covered by higher/equal z visuals: {overlapping_covers}")
        else:
            print(f"    No higher-z covering visual.")
