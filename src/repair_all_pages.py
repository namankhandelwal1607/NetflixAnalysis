import os
import json
import shutil
import glob

print("=== REBUILDING ALL 3 PAGES ===")

base_dir = r"powerbi/netflix_report/processedData.Report"
def_dir = os.path.join(base_dir, "definition")
pages_dir = os.path.join(def_dir, "pages")

SCHEMA_VC = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"

PAGE_1_ID = "95c0693daf92b6d6c188"
PAGE_2_ID = "c048b71f92e143fa9d30"
PAGE_3_ID = "e89c4d21f8a74e5088bd"

def write_visual(page_folder, vis_obj):
    v_folder = os.path.join(page_folder, "visuals", vis_obj["name"])
    os.makedirs(v_folder, exist_ok=True)
    with open(os.path.join(v_folder, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(vis_obj, f, indent=2)

import subprocess

def clean_visual_folder(page_folder, vis_name):
    v_folder = os.path.join(page_folder, "visuals", vis_name)
    if os.path.exists(v_folder):
        subprocess.run(["powershell", "-Command", f"Remove-Item -Path '{v_folder}' -Recurse -Force"], check=False)

# Setup page.json for a page
def setup_page_json(page_id, display_name):
    p_path = os.path.join(pages_dir, page_id, "page.json")
    page_data = {
        "$schema": SCHEMA_PAGE,
        "name": page_id,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920,
        "objects": {
            "background": [{
                "properties": {
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E6EDF5'"}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}},
                    "image": {
                        "image": {
                            "name": {"expr": {"Literal": {"Value": "'bg_gradient.png'"}}},
                            "url": {
                                "expr": {
                                    "ResourcePackageItem": {
                                        "PackageName": "RegisteredResources",
                                        "PackageType": 1,
                                        "ItemName": "bg_gradient.png"
                                    }
                                }
                            },
                            "scaling": {"expr": {"Literal": {"Value": "'Fit'"}}}
                        }
                    }
                }
            }]
        }
    }
    with open(p_path, "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2)

# Helper for shapes
def make_shape(name, x, y, w, h, z, shape_type="roundRectangle", fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True):
    return {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w},
        "visual": {
            "visualType": "shape",
            "objects": {
                "shape": [{"properties": {"tileShape": {"expr": {"Literal": {"Value": f"'{shape_type}'"}}}}}] if shape_type != "rectangle" else [],
                "fill": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{fill_color}'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": f"{transparency}D"}}}
                    }
                }],
                "outline": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "roundEdge": [{"properties": {"roundEdge": {"expr": {"Literal": {"Value": f"{round_edge}D"}}}}}] if round_edge else []
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "dropShadow": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": str(shadow).lower()}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#000000'"}}}}},
                        "position": {"expr": {"Literal": {"Value": "'Outer'"}}},
                        "preset": {"expr": {"Literal": {"Value": "'Custom'"}}},
                        "shadowBlur": {"expr": {"Literal": {"Value": "18D"}}},
                        "shadowDistance": {"expr": {"Literal": {"Value": "4D"}}},
                        "transparency": {"expr": {"Literal": {"Value": "88D"}}}
                    }
                }] if shadow else [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }

def make_icon(name, x, y, w, h, z, icon_name, nav_page=None, bookmark=None):
    obj = {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w},
        "visual": {
            "visualType": "image",
            "objects": {
                "general": [{
                    "properties": {
                        "imageUrl": {
                            "expr": {
                                "ResourcePackageItem": {
                                    "PackageName": "RegisteredResources",
                                    "PackageType": 1,
                                    "ItemName": icon_name
                                }
                            }
                        },
                        "scaling": {"expr": {"Literal": {"Value": "'Fit'"}}}
                    }
                }]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    if nav_page:
        obj["visual"]["objects"]["action"] = [{
            "properties": {
                "actionType": {"expr": {"Literal": {"Value": "'PageNavigation'"}}},
                "page": {"expr": {"Literal": {"Value": f"'{nav_page}'"}}}
            }
        }]
    elif bookmark:
        obj["visual"]["objects"]["action"] = [{
            "properties": {
                "actionType": {"expr": {"Literal": {"Value": "'Bookmark'"}}},
                "bookmark": {"expr": {"Literal": {"Value": f"'{bookmark}'"}}}
            }
        }]
    return obj

def build_sidebar(page_folder, prefix, active_tab_num):
    # active_tab_num: 1 for Overview, 2 for Quality, 3 for Outliers
    # Sidebar Background
    sb_bg = make_shape(f"{prefix}_sidebar_bg", 24, 24, 96, 1032, 1, shape_type="roundRectangle", fill_color="#7FA5C0", transparency=15, round_edge=28, shadow=True)
    write_visual(page_folder, sb_bg)

    # Active Indicator marker and circle
    active_y_circle = 112 if active_tab_num == 1 else (192 if active_tab_num == 2 else 272)
    active_y_bar = 124 if active_tab_num == 1 else (204 if active_tab_num == 2 else 284)

    act_circle = make_shape(f"{prefix}_nav_active_circle", 44, active_y_circle, 56, 56, 2, shape_type="oval", fill_color="#FFFFFF", transparency=0, round_edge=0, shadow=False)
    act_bar = make_shape(f"{prefix}_nav_active_indicator", 24, active_y_bar, 4, 32, 6, shape_type="roundRectangle", fill_color="#E50914", transparency=0, round_edge=2, shadow=False)
    write_visual(page_folder, act_circle)
    write_visual(page_folder, act_bar)

    # 4 Nav Buttons
    # Overview (Page 1)
    btn_overview = make_icon(f"{prefix}_nav_btn_overview", 48, 116, 48, 48, 5, "nav_overview.png", nav_page=PAGE_1_ID)
    # Quality (Page 2)
    btn_quality = make_icon(f"{prefix}_nav_btn_quality", 48, 196, 48, 48, 5, "nav_quality.png", nav_page=PAGE_2_ID)
    # Outliers (Page 3)
    btn_outliers = make_icon(f"{prefix}_nav_btn_outliers", 48, 276, 48, 48, 5, "nav_outliers.png", nav_page=PAGE_3_ID)
    # Reset (Clear Filters)
    btn_reset = make_icon(f"{prefix}_nav_btn_reset", 48, 980, 48, 48, 5, "nav_reset.png", bookmark="ClearFilters")

    write_visual(page_folder, btn_overview)
    write_visual(page_folder, btn_quality)
    write_visual(page_folder, btn_outliers)
    write_visual(page_folder, btn_reset)

def build_header(page_folder, prefix, title_text):
    # Title
    t_obj = {
        "$schema": SCHEMA_VC,
        "name": f"{prefix}_title",
        "position": {"x": 150, "y": 20, "z": 10, "height": 44, "width": 700},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": title_text,
                                "textStyle": {
                                    "fontFamily": "Segoe UI Bold",
                                    "fontWeight": "bold",
                                    "fontSize": "26pt",
                                    "color": "#2F4A63"
                                }
                            }]
                        }]
                    }
                }]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    write_visual(page_folder, t_obj)

    # Red underline accent
    acc_obj = make_shape(f"{prefix}_title_accent", 150, 66, 120, 3, 10, shape_type="rectangle", fill_color="#E50914", transparency=0, round_edge=0, shadow=False)
    write_visual(page_folder, acc_obj)

    # Filter summary text
    fs_obj = {
        "$schema": SCHEMA_VC,
        "name": f"{prefix}_filter_summary",
        "position": {"x": 150, "y": 72, "z": 10, "height": 22, "width": 700},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {
                                "Measure": {
                                    "Expression": {"SourceRef": {"Entity": "fact_titles"}},
                                    "Property": "Filter Summary Text"
                                }
                            },
                            "queryRef": "fact_titles.Filter Summary Text",
                            "nativeQueryRef": "Filter Summary Text"
                        }]
                    }
                }
            },
            "objects": {
                "labels": [{
                    "properties": {
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#7A8CA0'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                    }
                }],
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    write_visual(page_folder, fs_obj)

def build_slicers(page_folder, prefix):
    # Year Slicer (Between style)
    s_year = {
        "$schema": SCHEMA_VC,
        "name": f"{prefix}_slicer_year",
        "position": {"x": 150, "y": 100, "z": 50, "height": 46, "width": 340},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": "dim_date"}},
                                    "Property": "year"
                                }
                            },
                            "queryRef": "dim_date.year",
                            "nativeQueryRef": "year",
                            "active": True
                        }]
                    }
                }
            },
            "objects": {
                "general": [{"properties": {"filter": {"filter": {"Version": 2}}}}]
            },
            "visualContainerObjects": {
                "title": [{
                    "properties": {
                        "text": {"expr": {"Literal": {"Value": "'Release Year'"}}},
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2F4A63'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "11D"}}}
                    }
                }],
                "background": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }],
                "border": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#D5DEE8'"}}}}},
                        "radius": {"expr": {"Literal": {"Value": "20D"}}}
                    }
                }],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    write_visual(page_folder, s_year)

    # Genre Slicer (Dropdown style)
    s_genre = {
        "$schema": SCHEMA_VC,
        "name": f"{prefix}_slicer_genre",
        "position": {"x": 506, "y": 100, "z": 50, "height": 46, "width": 340},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": "fact_titles"}},
                                    "Property": "genre_group"
                                }
                            },
                            "queryRef": "fact_titles.genre_group",
                            "nativeQueryRef": "genre_group",
                            "active": True
                        }]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [{
                    "properties": {
                        "text": {"expr": {"Literal": {"Value": "'Genre'"}}},
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2F4A63'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "11D"}}}
                    }
                }],
                "background": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }],
                "border": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#D5DEE8'"}}}}},
                        "radius": {"expr": {"Literal": {"Value": "20D"}}}
                    }
                }],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    write_visual(page_folder, s_genre)

    # Language Slicer (Dropdown style with search)
    s_lang = {
        "$schema": SCHEMA_VC,
        "name": f"{prefix}_slicer_language",
        "position": {"x": 862, "y": 100, "z": 50, "height": 46, "width": 340},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": "dim_language"}},
                                    "Property": "language_name"
                                }
                            },
                            "queryRef": "dim_language.language_name",
                            "nativeQueryRef": "language_name",
                            "active": True
                        }]
                    }
                }
            },
            "visualContainerObjects": {
                "title": [{
                    "properties": {
                        "text": {"expr": {"Literal": {"Value": "'Language'"}}},
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2F4A63'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "11D"}}}
                    }
                }],
                "background": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }],
                "border": [{
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#D5DEE8'"}}}}},
                        "radius": {"expr": {"Literal": {"Value": "20D"}}}
                    }
                }],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    write_visual(page_folder, s_lang)

def make_minibar(name, x, y, w=304, h=74, z=15, is_highlight=False):
    default_color = "'#B7CCDC'" if is_highlight else "'#C9CED6'"
    return {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": "dim_date"}},
                                    "Property": "month_name"
                                }
                            },
                            "queryRef": "dim_date.month_name",
                            "nativeQueryRef": "month_name",
                            "active": True
                        }]
                    },
                    "Y": {
                        "projections": [{
                            "field": {
                                "Measure": {
                                    "Expression": {"SourceRef": {"Entity": "fact_titles"}},
                                    "Property": "Total Titles"
                                }
                            },
                            "queryRef": "fact_titles.Total Titles",
                            "nativeQueryRef": "Total Titles"
                        }]
                    }
                }
            },
            "objects": {
                "categoryAxis": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "valueAxis": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "dataPoint": [
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": default_color}}}}}}},
                    {
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#5BB98C'"}}}}}},
                        "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_date"}}, "Property": "month_name"}}, "Right": {"Literal": {"Value": "'October'"}}}}}]}
                    },
                    {
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E8604C'"}}}}}},
                        "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_date"}}, "Property": "month_name"}}, "Right": {"Literal": {"Value": "'July'"}}}}}]}
                    }
                ]
            },
            "visualContainerObjects": {
                "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "padding": [{"properties": {"top": {"expr": {"Literal": {"Value": "0D"}}}, "bottom": {"expr": {"Literal": {"Value": "0D"}}}, "left": {"expr": {"Literal": {"Value": "4D"}}}, "right": {"expr": {"Literal": {"Value": "4D"}}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }

def make_kpi_card_element(name, x, y, w, h, z, measure_name, title_text, is_highlight=False, format_string=None):
    callout_color = "'#FFFFFF'" if is_highlight else "'#1F2D3D'"
    title_color = "'#FFFFFF'" if is_highlight else "'#2F4A63'"
    
    proj_entry = {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": "fact_titles"}},
                "Property": measure_name
            }
        },
        "queryRef": f"fact_titles.{measure_name}",
        "nativeQueryRef": measure_name
    }
    if format_string:
        proj_entry["format"] = format_string

    return {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [proj_entry]
                    }
                }
            },
            "objects": {
                "labels": [{
                    "properties": {
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": callout_color}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "34D"}}}
                    }
                }],
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "wordWrap": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": {
                "title": [{
                    "properties": {
                        "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},
                        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": title_color}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "11D"}}},
                        "show": {"expr": {"Literal": {"Value": "true"}}}
                    }
                }],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }

def make_pill_textbox(name, x, y, w, h, z, pill_text, pill_color="#7A8CA0"):
    return {
        "$schema": SCHEMA_VC,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": pill_text,
                                "textStyle": {
                                    "fontFamily": "Segoe UI Semibold",
                                    "fontWeight": "bold",
                                    "fontSize": "10pt",
                                    "color": pill_color
                                }
                            }]
                        }]
                    }
                }]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }

# ==============================================================
# REPAIR PAGE 1
# ==============================================================
print("\n--- Repairing Page 1 (Portfolio Overview & Release Dynamics) ---")
p1_folder = os.path.join(pages_dir, PAGE_1_ID)
setup_page_json(PAGE_1_ID, "Portfolio Overview & Release Dynamics")

# Remove obsolete visuals on Page 1
for old_v in ["0fbf12be9ac7644a1f2f", "35ed6b4c865d18e5e108", "b0a9e95c30030c64f446", "dd367181ade5d758077c", "4da9ea601d7efec9a9bb", "p1_tab_switcher"]:
    clean_visual_folder(p1_folder, old_v)

# Build Sidebar, Header, Slicers
build_sidebar(p1_folder, "p1", active_tab_num=1)
build_header(p1_folder, "p1", "Portfolio Overview & Release Dynamics")
build_slicers(p1_folder, "p1")

# KPI 1 (Total Titles - Highlighted Card)
kpi1_bg = make_shape("p1_kpi1_card_bg", 150, 160, 336, 194, 10, fill_color="#7FA5C0", transparency=0, round_edge=16, shadow=True)
write_visual(p1_folder, kpi1_bg)
kpi1_card = make_kpi_card_element("p1_kpi_total_titles", 166, 172, 220, 68, 12, "Total Titles", "Total Titles", is_highlight=True)
write_visual(p1_folder, kpi1_card)
kpi1_icon = make_icon("p1_kpi1_icon", 430, 172, 36, 36, 12, "icon_titles.png")
write_visual(p1_folder, kpi1_icon)
kpi1_pill = make_pill_textbox("p1_kpi1_pill", 166, 244, 250, 24, 12, "▲ +24.4% vs prev yr", "#FFFFFF")
write_visual(p1_folder, kpi1_pill)
kpi1_minibar = make_minibar("p1_kpi1_minibar", 166, 272, 304, 74, 15, is_highlight=True)
write_visual(p1_folder, kpi1_minibar)

# KPI 2 (Mature Period Titles)
kpi2_bg = make_shape("p1_kpi2_card_bg", 502, 160, 336, 194, 10, fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True)
write_visual(p1_folder, kpi2_bg)
kpi2_card = make_kpi_card_element("p1_kpi_mature_titles", 518, 172, 220, 68, 12, "Mature Period Titles", "Mature Period Titles", is_highlight=False)
write_visual(p1_folder, kpi2_card)
kpi2_icon = make_icon("p1_kpi2_icon", 782, 172, 36, 36, 12, "icon_mature.png")
write_visual(p1_folder, kpi2_icon)
kpi2_pill = make_pill_textbox("p1_kpi2_pill", 518, 244, 250, 24, 12, "86.1% of all titles (2016-2020)", "#7A8CA0")
write_visual(p1_folder, kpi2_pill)
kpi2_minibar = make_minibar("p1_kpi2_minibar", 518, 272, 304, 74, 15, is_highlight=False)
write_visual(p1_folder, kpi2_minibar)

# KPI 3 (Avg Runtime)
kpi3_bg = make_shape("p1_kpi3_card_bg", 854, 160, 336, 194, 10, fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True)
write_visual(p1_folder, kpi3_bg)
kpi3_card = make_kpi_card_element("p1_kpi_avg_runtime", 870, 172, 220, 68, 12, "Avg Runtime", "Avg Runtime (min)", is_highlight=False, format_string="0.0")
write_visual(p1_folder, kpi3_card)
kpi3_icon = make_icon("p1_kpi3_icon", 1134, 172, 36, 36, 12, "icon_runtime.png")
write_visual(p1_folder, kpi3_icon)
kpi3_pill = make_pill_textbox("p1_kpi3_pill", 870, 244, 250, 24, 12, "▼ -2.1% runtime trend", "#5B6B7C")
write_visual(p1_folder, kpi3_pill)
kpi3_minibar = make_minibar("p1_kpi3_minibar", 870, 272, 304, 74, 15, is_highlight=False)
write_visual(p1_folder, kpi3_minibar)

# KPI 4 (Avg IMDb Score)
kpi4_bg = make_shape("p1_kpi4_card_bg", 1206, 160, 336, 194, 10, fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True)
write_visual(p1_folder, kpi4_bg)
kpi4_card = make_kpi_card_element("p1_kpi_avg_imdb", 1222, 172, 220, 68, 12, "Avg IMDb Score", "Avg IMDb Score", is_highlight=False, format_string="0.00")
write_visual(p1_folder, kpi4_card)
kpi4_icon = make_icon("p1_kpi4_icon", 1486, 172, 36, 36, 12, "icon_imdb.png")
write_visual(p1_folder, kpi4_icon)
kpi4_pill = make_pill_textbox("p1_kpi4_pill", 1222, 244, 250, 24, 12, "Catalog benchmark: 6.27", "#5B6B7C")
write_visual(p1_folder, kpi4_pill)
kpi4_minibar = make_minibar("p1_kpi4_minibar", 1222, 272, 304, 74, 15, is_highlight=False)
write_visual(p1_folder, kpi4_minibar)

# KPI 5 (Top Genre Share %)
kpi5_bg = make_shape("p1_kpi5_card_bg", 1558, 160, 336, 194, 10, fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True)
write_visual(p1_folder, kpi5_bg)
kpi5_card = make_kpi_card_element("p1_kpi_top_genre_share", 1574, 172, 220, 68, 12, "Top Genre Share %", "Top Genre Share", is_highlight=False, format_string="0.0%")
write_visual(p1_folder, kpi5_card)
kpi5_icon = make_icon("p1_kpi5_icon", 1838, 172, 36, 36, 12, "icon_share.png")
write_visual(p1_folder, kpi5_icon)
kpi5_pill = make_pill_textbox("p1_kpi5_pill", 1574, 244, 250, 24, 12, "Documentary leads (163 titles)", "#5B6B7C")
write_visual(p1_folder, kpi5_pill)
kpi5_minibar = make_minibar("p1_kpi5_minibar", 1574, 272, 304, 74, 15, is_highlight=False)
write_visual(p1_folder, kpi5_minibar)

# Middle Row Visuals: Annual & Donut
# Update Donut Center Textbox to 24pt, w=140, h=78, padding 0 to prevent scrollbar
donut_center_path = os.path.join(p1_folder, "visuals/p1_v2_donut_center/visual.json")
if os.path.exists(donut_center_path):
    with open(donut_center_path, "r", encoding="utf-8") as f:
        dc_data = json.load(f)
    dc_data["position"] = {"x": 1490, "y": 490, "z": 25, "height": 78, "width": 140}
    dc_data["visual"]["objects"]["general"] = [{
        "properties": {
            "paragraphs": [
                {
                    "horizontalTextAlignment": "center",
                    "textRuns": [{
                        "value": "584",
                        "textStyle": {
                            "fontFamily": "Segoe UI Bold",
                            "fontWeight": "bold",
                            "fontSize": "24pt",
                            "color": "#1F2D3D"
                        }
                    }]
                },
                {
                    "horizontalTextAlignment": "center",
                    "textRuns": [{
                        "value": "Titles",
                        "textStyle": {
                            "fontFamily": "Segoe UI",
                            "fontSize": "10pt",
                            "color": "#7A8CA0"
                        }
                    }]
                }
            ]
        }
    }]
    with open(donut_center_path, "w", encoding="utf-8") as f:
        json.dump(dc_data, f, indent=2)

print("  Page 1 repaired successfully.")

# ==============================================================
# REPAIR PAGE 2
# ==============================================================
print("\n--- Repairing Page 2 (Perceived Quality & Format Analysis) ---")
p2_folder = os.path.join(pages_dir, PAGE_2_ID)
setup_page_json(PAGE_2_ID, "Perceived Quality & Format Analysis")

# Remove obsolete visuals on Page 2
for old_v in ["p2_divider", "p2_slicer_year", "p2_slicer_genre", "p2_slicer_language", "p2_title"]:
    clean_visual_folder(p2_folder, old_v)

# Build Sidebar, Header, Slicers
build_sidebar(p2_folder, "p2", active_tab_num=2)
build_header(p2_folder, "p2", "Perceived Quality & Format Analysis")
build_slicers(p2_folder, "p2")

# Page 2 Top KPI Row (5 Cards at y=160, h=194)
# Card 1: Avg IMDb Score (Highlighted card)
p2_kpi1_bg = make_shape("p2_kpi1_card_bg", 150, 160, 336, 194, 10, fill_color="#7FA5C0", transparency=0, round_edge=16, shadow=True)
write_visual(p2_folder, p2_kpi1_bg)
p2_kpi1_card = make_kpi_card_element("p2_kpi_avg_score", 166, 172, 220, 68, 12, "Avg IMDb Score", "Avg IMDb Score", is_highlight=True, format_string="0.00")
write_visual(p2_folder, p2_kpi1_card)
p2_kpi1_icon = make_icon("p2_kpi1_icon", 430, 172, 36, 36, 12, "icon_imdb.png")
write_visual(p2_folder, p2_kpi1_icon)
p2_kpi1_pill = make_pill_textbox("p2_kpi1_pill", 166, 244, 250, 24, 12, "Benchmark: 6.27 (584 titles)", "#FFFFFF")
write_visual(p2_folder, p2_kpi1_pill)
p2_kpi1_minibar = make_minibar("p2_kpi1_minibar", 166, 272, 304, 74, 15, is_highlight=True)
write_visual(p2_folder, p2_kpi1_minibar)

# Card 2: Median IMDb Score
p2_kpi2_bg = make_shape("p2_kpi2_card_bg", 502, 160, 336, 194, 10, fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True)
write_visual(p2_folder, p2_kpi2_bg)
p2_kpi2_card = make_kpi_card_element("p2_kpi_median_score", 518, 172, 220, 68, 12, "Median IMDb Score", "Median IMDb Score", is_highlight=False, format_string="0.0")
write_visual(p2_folder, p2_kpi2_card)
p2_kpi2_icon = make_icon("p2_kpi2_icon", 782, 172, 36, 36, 12, "icon_imdb.png")
write_visual(p2_folder, p2_kpi2_icon)
p2_kpi2_pill = make_pill_textbox("p2_kpi2_pill", 518, 244, 250, 24, 12, "Robust central score: 6.4", "#5B6B7C")
write_visual(p2_folder, p2_kpi2_pill)
p2_kpi2_minibar = make_minibar("p2_kpi2_minibar", 518, 272, 304, 74, 15, is_highlight=False)
write_visual(p2_folder, p2_kpi2_minibar)

# Card 3: % High-Rated Titles
p2_kpi3_bg = make_shape("p2_kpi3_card_bg", 854, 160, 336, 194, 10, fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True)
write_visual(p2_folder, p2_kpi3_bg)
p2_kpi3_card = make_kpi_card_element("p2_kpi_high_rated", 870, 172, 220, 68, 12, "% High-Rated Titles", "% High-Rated (>=7.0)", is_highlight=False, format_string="0.0%")
write_visual(p2_folder, p2_kpi3_card)
p2_kpi3_icon = make_icon("p2_kpi3_icon", 1134, 172, 36, 36, 12, "icon_mature.png")
write_visual(p2_folder, p2_kpi3_icon)
p2_kpi3_pill = make_pill_textbox("p2_kpi3_pill", 870, 244, 250, 24, 12, "144 titles with score >= 7.0", "#5BB98C")
write_visual(p2_folder, p2_kpi3_pill)
p2_kpi3_minibar = make_minibar("p2_kpi3_minibar", 870, 272, 304, 74, 15, is_highlight=False)
write_visual(p2_folder, p2_kpi3_minibar)

# Card 4: % Low-Rated Titles
p2_kpi4_bg = make_shape("p2_kpi4_card_bg", 1206, 160, 336, 194, 10, fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True)
write_visual(p2_folder, p2_kpi4_bg)
p2_kpi4_card = make_kpi_card_element("p2_kpi_low_rated", 1222, 172, 220, 68, 12, "% Low-Rated Titles", "% Low-Rated (<5.5)", is_highlight=False, format_string="0.0%")
write_visual(p2_folder, p2_kpi4_card)
p2_kpi4_icon = make_icon("p2_kpi4_icon", 1486, 172, 36, 36, 12, "icon_runtime.png")
write_visual(p2_folder, p2_kpi4_icon)
p2_kpi4_pill = make_pill_textbox("p2_kpi4_pill", 1222, 244, 250, 24, 12, "143 titles with score < 5.5", "#E8604C")
write_visual(p2_folder, p2_kpi4_pill)
p2_kpi4_minibar = make_minibar("p2_kpi4_minibar", 1222, 272, 304, 74, 15, is_highlight=False)
write_visual(p2_folder, p2_kpi4_minibar)

# Card 5: Avg Runtime
p2_kpi5_bg = make_shape("p2_kpi5_card_bg", 1558, 160, 336, 194, 10, fill_color="#FFFFFF", transparency=0, round_edge=16, shadow=True)
write_visual(p2_folder, p2_kpi5_bg)
p2_kpi5_card = make_kpi_card_element("p2_kpi_avg_runtime", 1574, 172, 220, 68, 12, "Avg Runtime", "Avg Runtime (min)", is_highlight=False, format_string="0.0")
write_visual(p2_folder, p2_kpi5_card)
p2_kpi5_icon = make_icon("p2_kpi5_icon", 1838, 172, 36, 36, 12, "icon_runtime.png")
write_visual(p2_folder, p2_kpi5_icon)
p2_kpi5_pill = make_pill_textbox("p2_kpi5_pill", 1574, 244, 250, 24, 12, "Overall average: 93.6 min", "#5B6B7C")
write_visual(p2_folder, p2_kpi5_pill)
p2_kpi5_minibar = make_minibar("p2_kpi5_minibar", 1574, 272, 304, 74, 15, is_highlight=False)
write_visual(p2_folder, p2_kpi5_minibar)

# Page 2 Middle Row: Genre Score Bar Chart & Acclaim 100% Stacked
# p2_v5_genre_score (x=150, y=366, w=860, h=330)
p2_v5_path = os.path.join(p2_folder, "visuals/p2_v5_genre_score/visual.json")
with open(p2_v5_path, "r", encoding="utf-8") as f:
    v5 = json.load(f)
v5["position"] = {"x": 150, "y": 366, "z": 20, "height": 330, "width": 860}
# Data labels color #2F4A63
v5["visual"]["objects"]["labels"] = [{
    "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "labelPrecision": {"expr": {"Literal": {"Value": "2L"}}},
        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2F4A63'"}}}}}
    }
}]
# Data points: Above 6.27 steel blue (#7FA5C0), below 6.27 grey (#C9CED6)
genre_colors = {
    "Documentary": "#7FA5C0",
    "Music/Concert/Special": "#7FA5C0",
    "Drama": "#7FA5C0",
    "Sci-Fi/Fantasy/Animation": "#C9CED6",
    "Action/Adventure/Other": "#C9CED6",
    "Romance": "#C9CED6",
    "Comedy": "#C9CED6",
    "Thriller/Crime/Horror": "#C9CED6"
}
v5_dps = [{"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#C9CED6'"}}}}}}}]
for g_name, col in genre_colors.items():
    v5_dps.append({
        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{col}'"}}}}}},
        "selector": {
            "data": [{
                "scopeId": {
                    "Comparison": {
                        "ComparisonKind": 0,
                        "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "genre_group"}},
                        "Right": {"Literal": {"Value": f"'{g_name}'"}}
                    }
                }
            }]
        }
    })
v5["visual"]["objects"]["dataPoint"] = v5_dps
# Ensure constant line at 6.27
v5["visual"]["objects"]["valueAxisReferenceLine"] = [{
    "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "value": {"expr": {"Literal": {"Value": "6.27D"}}},
        "displayName": {"expr": {"Literal": {"Value": "'Catalog Avg (6.27)'"}}},
        "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E50914'"}}}}},
        "style": {"expr": {"Literal": {"Value": "'dashed'"}}}
    }
}]
with open(p2_v5_path, "w", encoding="utf-8") as f:
    json.dump(v5, f, indent=2)

# p2_v6_acclaim_tier (x=1034, y=366, w=860, h=330)
p2_v6_path = os.path.join(p2_folder, "visuals/p2_v6_acclaim_tier/visual.json")
with open(p2_v6_path, "r", encoding="utf-8") as f:
    v6 = json.load(f)
v6["position"] = {"x": 1034, "y": 366, "z": 20, "height": 330, "width": 860}
# High = green (#5BB98C), Mid = grey (#C9CED6), Low = coral (#E8604C)
v6["visual"]["objects"]["dataPoint"] = [
    {
        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#5BB98C'"}}}}}},
        "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "score_bucket"}}, "Right": {"Literal": {"Value": "'High (>=7.0)'"}}}}}]}
    },
    {
        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#C9CED6'"}}}}}},
        "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "score_bucket"}}, "Right": {"Literal": {"Value": "'Mid (5.5-6.9)'"}}}}}]}
    },
    {
        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E8604C'"}}}}}},
        "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "score_bucket"}}, "Right": {"Literal": {"Value": "'Low (<5.5)'"}}}}}]}
    }
]
with open(p2_v6_path, "w", encoding="utf-8") as f:
    json.dump(v6, f, indent=2)

# Page 2 Bottom Row: Scatter & Reliability Table
# p2_v7_scatter (x=150, y=712, w=860, h=344)
p2_v7_path = os.path.join(p2_folder, "visuals/p2_v7_scatter/visual.json")
with open(p2_v7_path, "r", encoding="utf-8") as f:
    v7 = json.load(f)
v7["position"] = {"x": 150, "y": 712, "z": 20, "height": 344, "width": 860}
with open(p2_v7_path, "w", encoding="utf-8") as f:
    json.dump(v7, f, indent=2)

# p2_v8_table (x=1034, y=712, w=860, h=344)
p2_v8_path = os.path.join(p2_folder, "visuals/p2_v8_table/visual.json")
with open(p2_v8_path, "r", encoding="utf-8") as f:
    v8 = json.load(f)
v8["position"] = {"x": 1034, "y": 712, "z": 20, "height": 344, "width": 860}
with open(p2_v8_path, "w", encoding="utf-8") as f:
    json.dump(v8, f, indent=2)

print("  Page 2 repaired successfully.")

# ==============================================================
# REPAIR PAGE 3
# ==============================================================
print("\n--- Repairing Page 3 (Outliers & Strategic Opportunity Matrix) ---")
p3_folder = os.path.join(pages_dir, PAGE_3_ID)
setup_page_json(PAGE_3_ID, "Outliers & Strategic Opportunity Matrix")

# Remove obsolete visuals on Page 3
for old_v in ["p3_divider", "p3_slicer_year", "p3_slicer_genre", "p3_slicer_language", "p3_title"]:
    clean_visual_folder(p3_folder, old_v)

# Build Sidebar, Header, Slicers
build_sidebar(p3_folder, "p3", active_tab_num=3)
build_header(p3_folder, "p3", "Outliers & Strategic Positioning")
build_slicers(p3_folder, "p3")

# Page 3 Top Row: Outlier Explorer Table & Strategic Quadrant
# p3_v8_outlier_table (x=150, y=160, w=860, h=370)
p3_v8_path = os.path.join(p3_folder, "visuals/p3_v8_outlier_table/visual.json")
with open(p3_v8_path, "r", encoding="utf-8") as f:
    p3_v8 = json.load(f)
p3_v8["position"] = {"x": 150, "y": 160, "z": 20, "height": 370, "width": 860}
with open(p3_v8_path, "w", encoding="utf-8") as f:
    json.dump(p3_v8, f, indent=2)

# p3_v9_strategic_quadrant (x=1034, y=160, w=860, h=370)
p3_v9_path = os.path.join(p3_folder, "visuals/p3_v9_strategic_quadrant/visual.json")
with open(p3_v9_path, "r", encoding="utf-8") as f:
    p3_v9 = json.load(f)
p3_v9["position"] = {"x": 1034, "y": 160, "z": 20, "height": 370, "width": 860}
# Data labels ON next to dots
p3_v9["visual"]["objects"]["labels"] = [{
    "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2F4A63'"}}}}}
    }
}]
# Data point color: Steel blue #7FA5C0
p3_v9["visual"]["objects"]["dataPoint"] = [{
    "properties": {
        "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#7FA5C0'"}}}}}
    }
}]
# Axis titles ON
p3_v9["visual"]["objects"]["categoryAxis"] = [{
    "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "showAxisTitle": {"expr": {"Literal": {"Value": "true"}}}
    }
}]
p3_v9["visual"]["objects"]["valueAxis"] = [{
    "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "showAxisTitle": {"expr": {"Literal": {"Value": "true"}}}
    }
}]
# Reference lines at X = 73 (dashed #7A8CA0) and Y = 6.27 (dashed #E50914)
p3_v9["visual"]["objects"]["categoryAxisReferenceLine"] = [{
    "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "value": {"expr": {"Literal": {"Value": "73D"}}},
        "displayName": {"expr": {"Literal": {"Value": "'Avg Volume (73 Titles)'"}}},
        "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#7A8CA0'"}}}}},
        "style": {"expr": {"Literal": {"Value": "'dashed'"}}}
    }
}]
p3_v9["visual"]["objects"]["valueAxisReferenceLine"] = [{
    "properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "value": {"expr": {"Literal": {"Value": "6.27D"}}},
        "displayName": {"expr": {"Literal": {"Value": "'Catalog Avg (6.27)'"}}},
        "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E50914'"}}}}},
        "style": {"expr": {"Literal": {"Value": "'dashed'"}}}
    }
}]
with open(p3_v9_path, "w", encoding="utf-8") as f:
    json.dump(p3_v9, f, indent=2)

# Page 3 Bottom Row: Opportunity Heatmap Matrix (x=150, y=550, w=1744, h=500)
p3_v10_path = os.path.join(p3_folder, "visuals/p3_v10_opportunity_heatmap/visual.json")
with open(p3_v10_path, "r", encoding="utf-8") as f:
    p3_v10 = json.load(f)
p3_v10["position"] = {"x": 150, "y": 550, "z": 20, "height": 500, "width": 1744}
# Bind Values to 'Avg IMDb Score (display)'
p3_v10["visual"]["query"]["queryState"]["Values"]["projections"] = [{
    "field": {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": "fact_titles"}},
            "Property": "Avg IMDb Score (display)"
        }
    },
    "queryRef": "fact_titles.Avg IMDb Score (display)",
    "nativeQueryRef": "Avg IMDb Score (display)",
    "format": "0.00"
}]
# Ensure subtitle has caption: 'Grey = fewer than 10 titles (low confidence) | Values shown for sample n >= 5'
p3_v10["visual"]["visualContainerObjects"]["title"] = [{
    "properties": {
        "text": {"expr": {"Literal": {"Value": "'Strategic Opportunity Heatmap Matrix: Genre Group x Primary Language (Top 6 Languages)'"}}},
        "show": {"expr": {"Literal": {"Value": "true"}}}
    }
}]
p3_v10["visual"]["visualContainerObjects"]["subTitle"] = [{
    "properties": {
        "text": {"expr": {"Literal": {"Value": "'Grey text = fewer than 10 titles (low confidence) | Values shown for sample n >= 5'"}}},
        "show": {"expr": {"Literal": {"Value": "true"}}}
    }
}]
with open(p3_v10_path, "w", encoding="utf-8") as f:
    json.dump(p3_v10, f, indent=2)

print("  Page 3 repaired successfully.")
print("\n=== ALL 3 PAGES REPAIRED SUCCESSFULLY ===")
