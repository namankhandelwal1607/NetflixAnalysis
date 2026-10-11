import json
import os

SCHEMA_CONTAINER = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCHEMA_PAGES_META = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"

pages_dir = 'powerbi/netflix_report/processedData.Report/definition/pages'
pages_meta_file = os.path.join(pages_dir, 'pages.json')

PAGE1_ID = "95c0693daf92b6d6c188"
PAGE2_ID = "c048b71f92e143fa9d30"
PAGE3_ID = "e89c4d21f8a74e5088bd"

def make_title_object(text):
    return {
        "title": [
            {
                "properties": {
                    "text": {
                        "expr": {
                            "Literal": {
                                "Value": f"'{text}'"
                            }
                        }
                    },
                    "show": {
                        "expr": {
                            "Literal": {
                                "Value": "true"
                            }
                        }
                    }
                }
            }
        ]
    }

def make_header_elements(page_id, page_title, page_idx):
    p_visuals_dir = os.path.join(pages_dir, page_id, 'visuals')
    os.makedirs(p_visuals_dir, exist_ok=True)
    
    # 1. Title Textbox
    title_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": f"p{page_idx}_title",
        "position": {"x": 30, "y": 12, "z": 1, "height": 48, "width": 740, "tabOrder": 1},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": page_title,
                                            "textStyle": {"fontWeight": "bold", "fontSize": "16pt", "color": "#FFFFFF"}
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True
        }
    }
    os.makedirs(os.path.join(p_visuals_dir, f"p{page_idx}_title"), exist_ok=True)
    with open(os.path.join(p_visuals_dir, f"p{page_idx}_title", "visual.json"), "w", encoding="utf-8") as f:
        json.dump(title_data, f, indent=2)

    # 2. Divider Line
    line_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": f"p{page_idx}_divider",
        "position": {"x": 30, "y": 66, "z": 2, "height": 3, "width": 1860, "tabOrder": 2},
        "visual": {
            "visualType": "shape",
            "objects": {
                "shape": [{"properties": {"tileShape": {"expr": {"Literal": {"Value": "'line'"}}}}}],
                "rotation": [{"properties": {"shapeAngle": {"expr": {"Literal": {"Value": "0L"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    os.makedirs(os.path.join(p_visuals_dir, f"p{page_idx}_divider"), exist_ok=True)
    with open(os.path.join(p_visuals_dir, f"p{page_idx}_divider", "visual.json"), "w", encoding="utf-8") as f:
        json.dump(line_data, f, indent=2)

    # 3. Year Slicer (Between, inputs only, synced)
    s1_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": f"p{page_idx}_slicer_year",
        "position": {"x": 786, "y": 12, "z": 3, "height": 50, "width": 360, "tabOrder": 3},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_date"}}, "Property": "year"}},
                                "queryRef": "dim_date.year",
                                "nativeQueryRef": "year",
                                "active": True
                            }
                        ]
                    }
                }
            },
            "syncGroup": {
                "groupName": "YearSyncGroup",
                "fieldChanges": True,
                "filterChanges": True
            },
            "objects": {
                "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Between'"}}}}}],
                "slider": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "titleText": {"expr": {"Literal": {"Value": "'Year'"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "11D"}}}, "fontSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                "input": [{"properties": {"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                "numeric": [{"properties": {"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                "items": [{"properties": {"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                "general": [{"properties": {"responsive": {"expr": {"Literal": {"Value": "true"}}}}}]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#3A3A3A'"}}}}}, "radius": {"expr": {"Literal": {"Value": "4D"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    os.makedirs(os.path.join(p_visuals_dir, f"p{page_idx}_slicer_year"), exist_ok=True)
    with open(os.path.join(p_visuals_dir, f"p{page_idx}_slicer_year", "visual.json"), "w", encoding="utf-8") as f:
        json.dump(s1_data, f, indent=2)

    # 4. Genre Slicer (Dropdown, synced)
    s2_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": f"p{page_idx}_slicer_genre",
        "position": {"x": 1158, "y": 12, "z": 4, "height": 50, "width": 360, "tabOrder": 4},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "genre_group"}},
                                "queryRef": "fact_titles.genre_group",
                                "nativeQueryRef": "genre_group",
                                "active": True
                            }
                        ]
                    }
                }
            },
            "syncGroup": {
                "groupName": "GenreSyncGroup",
                "fieldChanges": True,
                "filterChanges": True
            },
            "objects": {
                "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
                "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "titleText": {"expr": {"Literal": {"Value": "'Genre Group'"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "11D"}}}, "fontSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                "selection": [{"properties": {"selectAllCheckboxEnabled": {"expr": {"Literal": {"Value": "true"}}}, "singleSelect": {"expr": {"Literal": {"Value": "false"}}}}}],
                "items": [{"properties": {"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                "general": [{"properties": {"responsive": {"expr": {"Literal": {"Value": "true"}}}}}]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#3A3A3A'"}}}}}, "radius": {"expr": {"Literal": {"Value": "4D"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    os.makedirs(os.path.join(p_visuals_dir, f"p{page_idx}_slicer_genre"), exist_ok=True)
    with open(os.path.join(p_visuals_dir, f"p{page_idx}_slicer_genre", "visual.json"), "w", encoding="utf-8") as f:
        json.dump(s2_data, f, indent=2)

    # 5. Language Slicer (Dropdown, synced, search ON)
    s3_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": f"p{page_idx}_slicer_language",
        "position": {"x": 1530, "y": 12, "z": 5, "height": 50, "width": 360, "tabOrder": 5},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_language"}}, "Property": "language_name"}},
                                "queryRef": "dim_language.language_name",
                                "nativeQueryRef": "language_name",
                                "active": True
                            }
                        ]
                    }
                }
            },
            "syncGroup": {
                "groupName": "LanguageSyncGroup",
                "fieldChanges": True,
                "filterChanges": True
            },
            "objects": {
                "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
                "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "titleText": {"expr": {"Literal": {"Value": "'Language'"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "11D"}}}, "fontSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                "selection": [{"properties": {"selectAllCheckboxEnabled": {"expr": {"Literal": {"Value": "true"}}}, "singleSelect": {"expr": {"Literal": {"Value": "false"}}}}}],
                "general": [{"properties": {"selfFilterEnabled": {"expr": {"Literal": {"Value": "true"}}}}}],
                "items": [{"properties": {"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "11D"}}}}}],
                "general": [{"properties": {"responsive": {"expr": {"Literal": {"Value": "true"}}}}}]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#3A3A3A'"}}}}}, "radius": {"expr": {"Literal": {"Value": "4D"}}}}}],
                "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        }
    }
    os.makedirs(os.path.join(p_visuals_dir, f"p{page_idx}_slicer_language"), exist_ok=True)
    with open(os.path.join(p_visuals_dir, f"p{page_idx}_slicer_language", "visual.json"), "w", encoding="utf-8") as f:
        json.dump(s3_data, f, indent=2)

def make_card(name, x, y, width, height, z, measure_prop, title_text, format_str=None):
    proj = {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": "fact_titles"}},
                "Property": measure_prop
            }
        },
        "queryRef": f"fact_titles.{measure_prop}",
        "nativeQueryRef": measure_prop
    }
    if format_str:
        proj["format"] = format_str

    return {
        "$schema": SCHEMA_CONTAINER,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": height, "width": width, "tabOrder": z},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {"projections": [proj]}
                }
            },
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "28D"}}}
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": make_title_object(title_text),
            "drillFilterOtherVisuals": True
        }
    }

def build_job2():
    print("Building Job 2: Page 2 (Perceived Quality & Format Analysis)...")
    p2_dir = os.path.join(pages_dir, PAGE2_ID)
    os.makedirs(p2_dir, exist_ok=True)
    p2_visuals_dir = os.path.join(p2_dir, 'visuals')
    os.makedirs(p2_visuals_dir, exist_ok=True)

    # Page definition
    page_json = {
        "$schema": SCHEMA_PAGE,
        "name": PAGE2_ID,
        "displayName": "Perceived Quality & Format Analysis",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    }
    with open(os.path.join(p2_dir, "page.json"), "w", encoding="utf-8") as f:
        json.dump(page_json, f, indent=2)

    # Header elements
    make_header_elements(PAGE2_ID, "NETFLIX ORIGINALS: PERCEIVED QUALITY & FORMAT ANALYSIS", 2)

    # 1. KPI Cards (y: 80, height: 110, width: 356)
    kpis = [
        ("p2_kpi_avg_score", 30, "Avg IMDb Score", "Avg IMDb Score (Catalog: 6.27)", None),
        ("p2_kpi_median_score", 406, "Median IMDb Score", "Median IMDb Score (6.35)", None),
        ("p2_kpi_high_rated", 782, "% High-Rated Titles", "% High-Rated Titles (>= 7.0 Acclaim)", "0.0%"),
        ("p2_kpi_low_rated", 1158, "% Low-Rated Titles", "% Low-Rated Titles (< 5.5 Quality Floor)", "0.0%"),
        ("p2_kpi_avg_runtime", 1534, "Avg Runtime", "Avg Runtime (Minutes: 93.6m)", None),
    ]
    for idx, (name, x, meas, title, fmt) in enumerate(kpis):
        card_data = make_card(name, x, 80, 356, 110, 10 + idx, meas, title, fmt)
        cdir = os.path.join(p2_visuals_dir, name)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(cdir, "visual.json"), "w", encoding="utf-8") as f:
            json.dump(card_data, f, indent=2)

    # 2. Visual 5: Avg IMDb Score by genre_group (Bar Chart, sorted desc, constant line 6.27)
    v5_name = "p2_v5_genre_score"
    v5_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": v5_name,
        "position": {"x": 30, "y": 210, "z": 20, "height": 410, "width": 910, "tabOrder": 20},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "genre_group"}},
                                "queryRef": "fact_titles.genre_group",
                                "nativeQueryRef": "genre_group",
                                "active": True
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Avg IMDb Score"}},
                                "queryRef": "fact_titles.Avg IMDb Score",
                                "nativeQueryRef": "Avg IMDb Score"
                            }
                        ]
                    },
                    "Tooltips": {
                        "projections": [
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Catalog Avg IMDb"}},
                                "queryRef": "fact_titles.Catalog Avg IMDb",
                                "nativeQueryRef": "Catalog Avg IMDb"
                            }
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Avg IMDb Score"}},
                            "direction": "Descending"
                        }
                    ],
                    "isDefaultSort": False
                }
            },
            "objects": {
                "valueAxisReferenceLine": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "value": {"expr": {"Literal": {"Value": "6.27D"}}},
                            "displayName": {"expr": {"Literal": {"Value": "'Catalog Avg (6.27)'"}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E50914'"}}}}},
                            "style": {"expr": {"Literal": {"Value": "'dashed'"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": make_title_object("Average IMDb Score by Genre Group (Catalog Benchmark: 6.27)"),
            "drillFilterOtherVisuals": True
        }
    }
    v5_dir = os.path.join(p2_visuals_dir, v5_name)
    os.makedirs(v5_dir, exist_ok=True)
    with open(os.path.join(v5_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(v5_data, f, indent=2)

    # 3. Visual 6: 100% Stacked Bar (score_bucket per genre_group)
    v6_name = "p2_v6_acclaim_tier"
    v6_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": v6_name,
        "position": {"x": 980, "y": 210, "z": 21, "height": 410, "width": 910, "tabOrder": 21},
        "visual": {
            "visualType": "hundredPercentStackedBarChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "genre_group"}},
                                "queryRef": "fact_titles.genre_group",
                                "nativeQueryRef": "genre_group",
                                "active": True
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Total Titles"}},
                                "queryRef": "fact_titles.Total Titles",
                                "nativeQueryRef": "Total Titles"
                            }
                        ]
                    },
                    "Series": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "score_bucket"}},
                                "queryRef": "fact_titles.score_bucket",
                                "nativeQueryRef": "score_bucket"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "dataPoint": [
                    {
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2E7D32'"}}}}}},
                        "selector": {
                            "data": [
                                {
                                    "scopeId": {
                                        "Comparison": {
                                            "ComparisonKind": 0,
                                            "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "score_bucket"}},
                                            "Right": {"Literal": {"Value": "'High (>=7.0)'"}}
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#757575'"}}}}}},
                        "selector": {
                            "data": [
                                {
                                    "scopeId": {
                                        "Comparison": {
                                            "ComparisonKind": 0,
                                            "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "score_bucket"}},
                                            "Right": {"Literal": {"Value": "'Mid (5.5-6.9)'"}}
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E50914'"}}}}}},
                        "selector": {
                            "data": [
                                {
                                    "scopeId": {
                                        "Comparison": {
                                            "ComparisonKind": 0,
                                            "Left": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "score_bucket"}},
                                            "Right": {"Literal": {"Value": "'Low (<5.5)'"}}
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            },
            "visualContainerObjects": make_title_object("Acclaim Tier Breakdown by Genre Group (100% Stacked)"),
            "drillFilterOtherVisuals": True
        }
    }
    v6_dir = os.path.join(p2_visuals_dir, v6_name)
    os.makedirs(v6_dir, exist_ok=True)
    with open(os.path.join(v6_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(v6_data, f, indent=2)

    # 4. Visual 7: Scatter (runtime vs imdb_score with trendline, title as details)
    v7_name = "p2_v7_scatter"
    v7_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": v7_name,
        "position": {"x": 30, "y": 640, "z": 22, "height": 410, "width": 910, "tabOrder": 22},
        "visual": {
            "visualType": "scatterChart",
            "query": {
                "queryState": {
                    "Details": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "title"}},
                                "queryRef": "fact_titles.title",
                                "nativeQueryRef": "title",
                                "active": True
                            }
                        ]
                    },
                    "X": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "runtime"}},
                                "queryRef": "fact_titles.runtime",
                                "nativeQueryRef": "runtime"
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "imdb_score"}},
                                "queryRef": "fact_titles.imdb_score",
                                "nativeQueryRef": "imdb_score"
                            }
                        ]
                    },
                    "Tooltips": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "genre_group"}},
                                "queryRef": "fact_titles.genre_group",
                                "nativeQueryRef": "genre_group"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "trendLine": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": make_title_object("Runtime vs IMDb Score (rho = -0.022)"),
            "drillFilterOtherVisuals": True
        }
    }
    v7_dir = os.path.join(p2_visuals_dir, v7_name)
    os.makedirs(v7_dir, exist_ok=True)
    with open(os.path.join(v7_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(v7_data, f, indent=2)

    # 5. Visual 8: Table (primary_language, Total Titles, Avg IMDb Score, Sample Reliability Badge)
    v8_name = "p2_v8_table"
    v8_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": v8_name,
        "position": {"x": 980, "y": 640, "z": 23, "height": 410, "width": 910, "tabOrder": 23},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "primary_language"}},
                                "queryRef": "fact_titles.primary_language",
                                "nativeQueryRef": "primary_language"
                            },
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Total Titles"}},
                                "queryRef": "fact_titles.Total Titles",
                                "nativeQueryRef": "Total Titles"
                            },
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Avg IMDb Score"}},
                                "queryRef": "fact_titles.Avg IMDb Score",
                                "nativeQueryRef": "Avg IMDb Score"
                            },
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Sample Reliability Badge"}},
                                "queryRef": "fact_titles.Sample Reliability Badge",
                                "nativeQueryRef": "Sample Reliability Badge"
                            }
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Total Titles"}},
                            "direction": "Descending"
                        }
                    ],
                    "isDefaultSort": False
                }
            },
            "visualContainerObjects": make_title_object("Language Perceived Quality Benchmarks & Reliability (n >= 10 vs n < 10)"),
            "drillFilterOtherVisuals": True
        }
    }
    v8_dir = os.path.join(p2_visuals_dir, v8_name)
    os.makedirs(v8_dir, exist_ok=True)
    with open(os.path.join(v8_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(v8_data, f, indent=2)

    print("Job 2 completed successfully.")

def build_job3():
    print("Building Job 3: Page 3 (Outliers & Strategic Opportunity Matrix)...")
    p3_dir = os.path.join(pages_dir, PAGE3_ID)
    os.makedirs(p3_dir, exist_ok=True)
    p3_visuals_dir = os.path.join(p3_dir, 'visuals')
    os.makedirs(p3_visuals_dir, exist_ok=True)

    # Page definition
    page_json = {
        "$schema": SCHEMA_PAGE,
        "name": PAGE3_ID,
        "displayName": "Outliers & Strategic Opportunity Matrix",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    }
    with open(os.path.join(p3_dir, "page.json"), "w", encoding="utf-8") as f:
        json.dump(page_json, f, indent=2)

    # Header elements
    make_header_elements(PAGE3_ID, "NETFLIX ORIGINALS: OUTLIERS & STRATEGIC OPPORTUNITY MATRIX", 3)

    # 1. Visual 8: Outlier Explorer Table (title, runtime, imdb_score, outlier_type filtered to <> "None")
    p3_v8_name = "p3_v8_outlier_table"
    p3_v8_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": p3_v8_name,
        "position": {"x": 30, "y": 80, "z": 20, "height": 440, "width": 910, "tabOrder": 20},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "title"}},
                                "queryRef": "fact_titles.title",
                                "nativeQueryRef": "title"
                            },
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "runtime"}},
                                "queryRef": "fact_titles.runtime",
                                "nativeQueryRef": "runtime"
                            },
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "imdb_score"}},
                                "queryRef": "fact_titles.imdb_score",
                                "nativeQueryRef": "imdb_score"
                            },
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "outlier_type"}},
                                "queryRef": "fact_titles.outlier_type",
                                "nativeQueryRef": "outlier_type"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": make_title_object("Statistical Outlier Explorer (IQR Fences: Runtime < 53m or > 141m | Score < 3.75 or > 8.95)"),
            "drillFilterOtherVisuals": True
        },
        "filterConfig": {
            "filters": [
                {
                    "name": "ExcludeNoneOutliers",
                    "type": "Categorical",
                    "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "outlier_type"}},
                    "filter": {
                        "Version": 2,
                        "From": [{"Name": "f", "Entity": "fact_titles", "Type": 0}],
                        "Where": [
                            {
                                "Condition": {
                                    "In": {
                                        "Expressions": [
                                            {"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": "outlier_type"}}
                                        ],
                                        "Values": [
                                            [{"Literal": {"Value": "'Short Runtime'"}}],
                                            [{"Literal": {"Value": "'Epic Runtime'"}}],
                                            [{"Literal": {"Value": "'Low Score'"}}],
                                            [{"Literal": {"Value": "'High Score'"}}]
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    p3_v8_dir = os.path.join(p3_visuals_dir, p3_v8_name)
    os.makedirs(p3_v8_dir, exist_ok=True)
    with open(os.path.join(p3_v8_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(p3_v8_data, f, indent=2)

    # 2. Visual 9: Strategic Quadrant Scatter (genre_group as Details, X = Total Titles, Y = Avg IMDb Score)
    p3_v9_name = "p3_v9_strategic_quadrant"
    p3_v9_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": p3_v9_name,
        "position": {"x": 980, "y": 80, "z": 21, "height": 440, "width": 910, "tabOrder": 21},
        "visual": {
            "visualType": "scatterChart",
            "query": {
                "queryState": {
                    "Details": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "genre_group"}},
                                "queryRef": "fact_titles.genre_group",
                                "nativeQueryRef": "genre_group",
                                "active": True
                            }
                        ]
                    },
                    "X": {
                        "projections": [
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Total Titles"}},
                                "queryRef": "fact_titles.Total Titles",
                                "nativeQueryRef": "Total Titles"
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Avg IMDb Score"}},
                                "queryRef": "fact_titles.Avg IMDb Score",
                                "nativeQueryRef": "Avg IMDb Score"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "valueAxisReferenceLine": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "value": {"expr": {"Literal": {"Value": "6.27D"}}},
                            "displayName": {"expr": {"Literal": {"Value": "'Catalog Avg Score (6.27)'"}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#E50914'"}}}}},
                            "style": {"expr": {"Literal": {"Value": "'dashed'"}}}
                        }
                    }
                ],
                "categoryAxisReferenceLine": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "value": {"expr": {"Literal": {"Value": "73D"}}},
                            "displayName": {"expr": {"Literal": {"Value": "'Avg Genre Volume (73 Titles)'"}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                            "style": {"expr": {"Literal": {"Value": "'dashed'"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": make_title_object("Strategic Portfolio Quadrants (Volume vs Quality | Ref Lines: 73 Titles, 6.27 Score)"),
            "drillFilterOtherVisuals": True
        }
    }
    p3_v9_dir = os.path.join(p3_visuals_dir, p3_v9_name)
    os.makedirs(p3_v9_dir, exist_ok=True)
    with open(os.path.join(p3_v9_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(p3_v9_data, f, indent=2)

    # 3. Visual 10: Opportunity Heatmap Matrix (Rows: genre_group, Cols: primary_language, Values: Avg IMDb Score)
    p3_v10_name = "p3_v10_opportunity_heatmap"
    p3_v10_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": p3_v10_name,
        "position": {"x": 30, "y": 540, "z": 22, "height": 500, "width": 1860, "tabOrder": 22},
        "visual": {
            "visualType": "pivotTable",
            "query": {
                "queryState": {
                    "Rows": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "genre_group"}},
                                "queryRef": "fact_titles.genre_group",
                                "nativeQueryRef": "genre_group"
                            }
                        ]
                    },
                    "Columns": {
                        "projections": [
                            {
                                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "primary_language"}},
                                "queryRef": "fact_titles.primary_language",
                                "nativeQueryRef": "primary_language"
                            }
                        ]
                    },
                    "Values": {
                        "projections": [
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "Avg IMDb Score"}},
                                "queryRef": "fact_titles.Avg IMDb Score",
                                "nativeQueryRef": "Avg IMDb Score"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": make_title_object("Strategic Opportunity Heatmap Matrix: Genre Group x Primary Language (Avg IMDb Score | Top 6 Languages)"),
            "drillFilterOtherVisuals": True
        },
        "filterConfig": {
            "filters": [
                {
                    "name": "Top6LanguagesMatrixFilter",
                    "type": "TopN",
                    "field": {"Column": {"Expression": {"SourceRef": {"Entity": "fact_titles"}}, "Property": "primary_language"}},
                    "filter": {
                        "Version": 2,
                        "From": [
                            {
                                "Name": "subquery",
                                "Expression": {
                                    "Subquery": {
                                        "Query": {
                                            "Version": 2,
                                            "From": [{"Name": "f", "Entity": "fact_titles", "Type": 0}],
                                            "Select": [
                                                {
                                                    "Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": "primary_language"},
                                                    "Name": "field"
                                                }
                                            ],
                                            "OrderBy": [
                                                {
                                                    "Direction": 2,
                                                    "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": "Total Titles"}}
                                                }
                                            ],
                                            "Top": 6
                                        }
                                    }
                                },
                                "Type": 2
                            },
                            {"Name": "f", "Entity": "fact_titles", "Type": 0}
                        ],
                        "Where": [
                            {
                                "Condition": {
                                    "In": {
                                        "Expressions": [
                                            {"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": "primary_language"}}
                                        ],
                                        "Table": {"SourceRef": {"Source": "subquery"}}
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    p3_v10_dir = os.path.join(p3_visuals_dir, p3_v10_name)
    os.makedirs(p3_v10_dir, exist_ok=True)
    with open(os.path.join(p3_v10_dir, "visual.json"), "w", encoding="utf-8") as f:
        json.dump(p3_v10_data, f, indent=2)

    print("Job 3 completed successfully.")

def update_pages_meta(order=None):
    if order is None:
        order = [PAGE1_ID, PAGE2_ID, PAGE3_ID]
    meta = {
        "$schema": SCHEMA_PAGES_META,
        "pageOrder": order,
        "activePageName": PAGE1_ID
    }
    with open(pages_meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"pages.json updated with {len(order)} pages: {order}")

if __name__ == '__main__':
    import shutil
    import subprocess

    # Step 1: Build Job 2
    build_job2()
    update_pages_meta([PAGE1_ID, PAGE2_ID])

    # Step 2: Backup to powerbi/netflix_report_backup_job3 before Job 3
    print("Backing up powerbi/netflix_report to powerbi/netflix_report_backup_job3...")
    backup_cmd = 'powershell -Command "Copy-Item -Path powerbi\\netflix_report -Destination powerbi\\netflix_report_backup_job3 -Recurse -Force"'
    subprocess.run(backup_cmd, shell=True, check=True)
    print("Backup job3 completed.")

    # Step 3: Build Job 3
    build_job3()
    update_pages_meta([PAGE1_ID, PAGE2_ID, PAGE3_ID])
    print("All pages successfully built.")
