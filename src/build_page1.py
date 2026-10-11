import json
import os

page1_dir = 'powerbi/netflix_report/processedData.Report/definition/pages/95c0693daf92b6d6c188'
visuals_dir = os.path.join(page1_dir, 'visuals')
theme_file = 'powerbi/netflix_report/processedData.Report/StaticResources/RegisteredResources/NetflixDark.json'

SCHEMA_CONTAINER = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"

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

def update_theme():
    if os.path.exists(theme_file):
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme = json.load(f)
        theme.setdefault("visualStyles", {}).setdefault("card", {})["*"] = {
            "labels": [
                {
                    "color": {"solid": {"color": "#FFFFFF"}},
                    "fontSize": 28
                }
            ],
            "categoryLabels": [
                {
                    "show": False
                }
            ]
        }
        with open(theme_file, 'w', encoding='utf-8') as f:
            json.dump(theme, f, indent=2)

def make_card(name, x, y, width, height, z, measure_prop, title_text, format_str=None):
    proj = {
        "field": {
            "Measure": {
                "Expression": {
                    "SourceRef": {
                        "Entity": "fact_titles"
                    }
                },
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
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "height": height,
            "width": width,
            "tabOrder": z
        },
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [proj]
                    }
                }
            },
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "color": {
                                "solid": {
                                    "color": {
                                        "expr": {
                                            "Literal": {
                                                "Value": "'#FFFFFF'"
                                            }
                                        }
                                    }
                                }
                            },
                            "fontSize": {
                                "expr": {
                                    "Literal": {
                                        "Value": "28D"
                                    }
                                }
                            }
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "false"
                                    }
                                }
                            }
                        }
                    }
                ]
            },
            "visualContainerObjects": make_title_object(title_text),
            "drillFilterOtherVisuals": True
        }
    }

def apply_page1_fixes():
    update_theme()

    # 1. Update Title Textbox (dd367181ade5d758077c) -> white text, bold, 18pt
    title_file = os.path.join(visuals_dir, 'dd367181ade5d758077c', 'visual.json')
    if os.path.exists(title_file):
        with open(title_file, 'r', encoding='utf-8') as f:
            vdata = json.load(f)
        vdata['position'] = {
            "x": 30,
            "y": 15,
            "z": 1,
            "height": 45,
            "width": 910,
            "tabOrder": 1
        }
        vdata['visual']['objects'] = {
            "general": [
                {
                    "properties": {
                        "paragraphs": [
                            {
                                "textRuns": [
                                    {
                                        "value": "NETFLIX ORIGINALS: PORTFOLIO OVERVIEW & RELEASE DYNAMICS",
                                        "textStyle": {
                                            "fontWeight": "bold",
                                            "fontSize": "18pt",
                                            "color": "#FFFFFF"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        with open(title_file, 'w', encoding='utf-8') as f:
            json.dump(vdata, f, indent=2)

    # 2. Update KPI cards: callout font white, 28pt, hide category label, format Top Genre Share % as 0.0%
    kpis = [
        ("p1_kpi_total_titles", 30, "Total Titles", "Total Titles (584)", None),
        ("p1_kpi_mature_titles", 406, "Mature Period Titles", "Mature Period Releases (503)", None),
        ("p1_kpi_avg_runtime", 782, "Avg Runtime", "Avg Runtime (93.6 min)", None),
        ("p1_kpi_avg_imdb", 1158, "Avg IMDb Score", "Avg IMDb Score (6.27)", None),
        ("p1_kpi_top_genre_share", 1534, "Top Genre Share %", "Top Genre Share % (27.9%)", "0.0%"),
    ]
    for idx, (name, x, meas, title, fmt) in enumerate(kpis):
        card_dir = os.path.join(visuals_dir, name)
        os.makedirs(card_dir, exist_ok=True)
        card_json = make_card(name, x, 80, 356, 110, 10 + idx, meas, title, fmt)
        with open(os.path.join(card_dir, 'visual.json'), 'w', encoding='utf-8') as f:
            json.dump(card_json, f, indent=2)

    # 3. Genre chart (p1_v2): sort descending by Total Titles
    v2_file = os.path.join(visuals_dir, 'p1_v2_genre_composition', 'visual.json')
    if os.path.exists(v2_file):
        with open(v2_file, 'r', encoding='utf-8') as f:
            v2 = json.load(f)
        v2['visual']['query']['sortDefinition'] = {
            "sort": [
                {
                    "field": {
                        "Measure": {
                            "Expression": {
                                "SourceRef": {
                                    "Entity": "fact_titles"
                                }
                            },
                            "Property": "Total Titles"
                        }
                    },
                    "direction": "Descending"
                }
            ],
            "isDefaultSort": False
        }
        with open(v2_file, 'w', encoding='utf-8') as f:
            json.dump(v2, f, indent=2)

    # 4. Language chart (p1_v3): Top N filter (Top 6 by Total Titles) and sorted descending
    v3_file = os.path.join(visuals_dir, 'p1_v3_language_concentration', 'visual.json')
    if os.path.exists(v3_file):
        with open(v3_file, 'r', encoding='utf-8') as f:
            v3 = json.load(f)
        v3['visual']['query']['sortDefinition'] = {
            "sort": [
                {
                    "field": {
                        "Measure": {
                            "Expression": {
                                "SourceRef": {
                                    "Entity": "fact_titles"
                                }
                            },
                            "Property": "Total Titles"
                        }
                    },
                    "direction": "Descending"
                }
            ],
            "isDefaultSort": False
        }
        v3.pop('visualContainerObjects', None)
        v3['visual']['visualContainerObjects'] = make_title_object("Primary Language Concentration (Top 6 Languages)")
        v3['filterConfig'] = {
            "filters": [
                {
                    "name": "Top6LanguagesFilter",
                    "type": "TopN",
                    "field": {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "Entity": "fact_titles"
                                }
                            },
                            "Property": "primary_language"
                        }
                    },
                    "filter": {
                        "Version": 2,
                        "From": [
                            {
                                "Name": "subquery",
                                "Expression": {
                                    "Subquery": {
                                        "Query": {
                                            "Version": 2,
                                            "From": [
                                                {
                                                    "Name": "f",
                                                    "Entity": "fact_titles",
                                                    "Type": 0
                                                }
                                            ],
                                            "Select": [
                                                {
                                                    "Column": {
                                                        "Expression": {
                                                            "SourceRef": {
                                                                "Source": "f"
                                                            }
                                                        },
                                                        "Property": "primary_language"
                                                    },
                                                    "Name": "field"
                                                }
                                            ],
                                            "OrderBy": [
                                                {
                                                    "Direction": 2,
                                                    "Expression": {
                                                        "Measure": {
                                                            "Expression": {
                                                                "SourceRef": {
                                                                    "Source": "f"
                                                                }
                                                            },
                                                            "Property": "Total Titles"
                                                        }
                                                    }
                                                }
                                            ],
                                            "Top": 6
                                        }
                                    }
                                },
                                "Type": 2
                            },
                            {
                                "Name": "f",
                                "Entity": "fact_titles",
                                "Type": 0
                            }
                        ],
                        "Where": [
                            {
                                "Condition": {
                                    "In": {
                                        "Expressions": [
                                            {
                                                "Column": {
                                                    "Expression": {
                                                        "SourceRef": {
                                                            "Source": "f"
                                                        }
                                                    },
                                                    "Property": "primary_language"
                                                }
                                            }
                                        ],
                                        "Table": {
                                            "SourceRef": {
                                                "Source": "subquery"
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
        with open(v3_file, 'w', encoding='utf-8') as f:
            json.dump(v3, f, indent=2)

    # 5. Annual chart (p1_v1): Combo chart (lineClusteredColumnComboChart) with Y2 line and conditional color formatting
    v1_file = os.path.join(visuals_dir, 'p1_v1_annual_trajectory', 'visual.json')
    if os.path.exists(v1_file):
        with open(v1_file, 'r', encoding='utf-8') as f:
            v1 = json.load(f)
        v1['visual']['visualType'] = "lineClusteredColumnComboChart"
        v1['visual']['query'] = {
            "queryState": {
                "Category": {
                    "projections": [
                        {
                            "field": {
                                "Column": {
                                    "Expression": {
                                        "SourceRef": {
                                            "Entity": "dim_date"
                                        }
                                    },
                                    "Property": "year"
                                }
                            },
                            "queryRef": "dim_date.year",
                            "nativeQueryRef": "year",
                            "active": True
                        }
                    ]
                },
                "Y": {
                    "projections": [
                        {
                            "field": {
                                "Measure": {
                                    "Expression": {
                                        "SourceRef": {
                                            "Entity": "fact_titles"
                                        }
                                    },
                                    "Property": "Total Titles"
                                }
                            },
                            "queryRef": "fact_titles.Total Titles",
                            "nativeQueryRef": "Total Titles"
                        }
                    ]
                },
                "Y2": {
                    "projections": [
                        {
                            "field": {
                                "Measure": {
                                    "Expression": {
                                        "SourceRef": {
                                            "Entity": "fact_titles"
                                        }
                                    },
                                    "Property": "Titles YoY Growth %"
                                }
                            },
                            "queryRef": "fact_titles.Titles YoY Growth %",
                            "nativeQueryRef": "Titles YoY Growth %"
                        }
                    ]
                }
            }
        }
        v1['visual']['objects'] = {
            "dataPoint": [
                {
                    "properties": {
                        "fill": {
                            "solid": {
                                "color": {
                                    "expr": {
                                        "Conditional": {
                                            "Cases": [
                                                {
                                                    "Condition": {
                                                        "Comparison": {
                                                            "ComparisonKind": 0,
                                                            "Left": {
                                                                "Column": {
                                                                    "Expression": {
                                                                        "SourceRef": {
                                                                            "Entity": "dim_date"
                                                                        }
                                                                    },
                                                                    "Property": "is_full_year"
                                                                }
                                                            },
                                                            "Right": {
                                                                "Literal": {
                                                                    "Value": "1L"
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "Value": {
                                                        "Literal": {
                                                            "Value": "'#E50914'"
                                                        }
                                                    }
                                                }
                                            ],
                                            "DefaultValue": {
                                                "Literal": {
                                                    "Value": "'#6E6E6E'"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            ]
        }
        v1.pop('visualContainerObjects', None)
        v1['visual']['visualContainerObjects'] = make_title_object("Annual Releases & YoY Growth (2014-2021 | Grey = Partial/Sparse Years)")
        with open(v1_file, 'w', encoding='utf-8') as f:
            json.dump(v1, f, indent=2)

    print("All Page 1 fixes applied successfully.")

if __name__ == '__main__':
    apply_page1_fixes()
