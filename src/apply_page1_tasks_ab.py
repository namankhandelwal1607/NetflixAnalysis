import json
import os

page1_dir = 'powerbi/netflix_report/processedData.Report/definition/pages/95c0693daf92b6d6c188'
visuals_dir = os.path.join(page1_dir, 'visuals')
theme_file = 'powerbi/netflix_report/processedData.Report/StaticResources/RegisteredResources/NetflixDark.json'
SCHEMA_CONTAINER = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"

def apply_tasks():
    # -------------------------------------------------------------
    # 1. Update NetflixDark.json with Slicer Defaults
    # -------------------------------------------------------------
    if os.path.exists(theme_file):
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme = json.load(f)
        
        theme.setdefault("visualStyles", {})["slicer"] = {
            "*": {
                "general": [
                    {
                        "outlineColor": {"solid": {"color": "#3A3A3A"}}
                    }
                ],
                "header": [
                    {
                        "show": True,
                        "fontColor": {"solid": {"color": "#FFFFFF"}},
                        "textSize": 11,
                        "fontSize": 11
                    }
                ],
                "items": [
                    {
                        "fontColor": {"solid": {"color": "#FFFFFF"}},
                        "background": {"solid": {"color": "#1A1A1A"}},
                        "textSize": 11,
                        "fontSize": 11
                    }
                ],
                "selection": [
                    {
                        "selectAllCheckboxEnabled": True,
                        "singleSelect": False
                    }
                ],
                "dropdown": [
                    {
                        "borderColor": {"solid": {"color": "#3A3A3A"}},
                        "borderRadius": 4,
                        "accentBarShow": True
                    }
                ],
                "background": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#1A1A1A"}},
                        "transparency": 0
                    }
                ],
                "border": [
                    {
                        "show": True,
                        "color": {"solid": {"color": "#3A3A3A"}},
                        "radius": 4
                    }
                ]
            }
        }
        
        with open(theme_file, 'w', encoding='utf-8') as f:
            json.dump(theme, f, indent=2)

    # -------------------------------------------------------------
    # 2. TASK A: Fix Annual Chart (p1_v1_annual_trajectory)
    # -------------------------------------------------------------
    v1_file = os.path.join(visuals_dir, 'p1_v1_annual_trajectory', 'visual.json')
    years = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    datapoints = []
    for y in years:
        color = "#6E6E6E" if y in (2014, 2015, 2021) else "#E50914"
        datapoints.append({
            "properties": {
                "fill": {
                    "solid": {
                        "color": {
                            "expr": {
                                "Literal": {
                                    "Value": f"'{color}'"
                                }
                            }
                        }
                    }
                }
            },
            "selector": {
                "data": [
                    {
                        "scopeId": {
                            "Comparison": {
                                "ComparisonKind": 0,
                                "Left": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": "dim_date"
                                            }
                                        },
                                        "Property": "year"
                                    }
                                },
                                "Right": {
                                    "Literal": {
                                        "Value": f"{y}L"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        })

    v1_data = {
        "$schema": SCHEMA_CONTAINER,
        "name": "p1_v1_annual_trajectory",
        "position": {
            "x": 30,
            "y": 210,
            "z": 20,
            "height": 410,
            "width": 910,
            "tabOrder": 20
        },
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
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
                    "Tooltips": {
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
            },
            "objects": {
                "dataPoint": datapoints
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Annual Release Volume & YoY Trajectory (2014-2021 | Grey = Partial/Sparse)'"
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
            },
            "drillFilterOtherVisuals": True
        }
    }
    with open(v1_file, 'w', encoding='utf-8') as f:
        json.dump(v1_data, f, indent=2)

    # -------------------------------------------------------------
    # 3. TASK B: Header Layout & Slicers Redesign
    # -------------------------------------------------------------
    # (a) Title Textbox (dd367181ade5d758077c)
    title_file = os.path.join(visuals_dir, 'dd367181ade5d758077c', 'visual.json')
    if os.path.exists(title_file):
        with open(title_file, 'r', encoding='utf-8') as f:
            tdata = json.load(f)
        tdata['position'] = {
            "x": 30,
            "y": 12,
            "z": 1,
            "height": 48,
            "width": 740,
            "tabOrder": 1
        }
        tdata['visual']['objects'] = {
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
                                            "fontSize": "16pt",
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
            json.dump(tdata, f, indent=2)

    # (b) Red Divider Line (4da9ea601d7efec9a9bb)
    line_file = os.path.join(visuals_dir, '4da9ea601d7efec9a9bb', 'visual.json')
    if os.path.exists(line_file):
        with open(line_file, 'r', encoding='utf-8') as f:
            ldata = json.load(f)
        ldata['position'] = {
            "x": 30,
            "y": 66,
            "z": 2,
            "height": 3,
            "width": 1860,
            "tabOrder": 2
        }
        with open(line_file, 'w', encoding='utf-8') as f:
            json.dump(ldata, f, indent=2)

    # (c) Slicer 1: Year (35ed6b4c865d18e5e108)
    # Between style with input boxes visible (no slider)
    year_file = os.path.join(visuals_dir, '35ed6b4c865d18e5e108', 'visual.json')
    if os.path.exists(year_file):
        with open(year_file, 'r', encoding='utf-8') as f:
            ydata = json.load(f)
        ydata['position'] = {
            "x": 786,
            "y": 12,
            "z": 3,
            "height": 50,
            "width": 360,
            "tabOrder": 3
        }
        ydata['visual']['objects'] = {
            "data": [
                {
                    "properties": {
                        "mode": {
                            "expr": {
                                "Literal": {
                                    "Value": "'Between'"
                                }
                            }
                        }
                    }
                }
            ],
            "slider": [
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
            ],
            "header": [
                {
                    "properties": {
                        "show": {
                            "expr": {
                                "Literal": {
                                    "Value": "true"
                                }
                            }
                        },
                        "titleText": {
                            "expr": {
                                "Literal": {
                                    "Value": "'Year'"
                                }
                            }
                        },
                        "fontColor": {
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
                        "textSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        },
                        "fontSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        }
                    }
                }
            ],
            "items": [
                {
                    "properties": {
                        "fontColor": {
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
                        "textSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        },
                        "fontSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        }
                    }
                }
            ],
            "general": [
                {
                    "properties": {
                        "responsive": {
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
        ydata['visual']['visualContainerObjects'] = {
            "background": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }
            ],
            "border": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#3A3A3A'"}}}}},
                        "radius": {"expr": {"Literal": {"Value": "4D"}}}
                    }
                }
            ]
        }
        with open(year_file, 'w', encoding='utf-8') as f:
            json.dump(ydata, f, indent=2)

    # (d) Slicer 2: Genre Group (0fbf12be9ac7644a1f2f)
    # Dropdown style, Select All ON, multi-select ON
    genre_file = os.path.join(visuals_dir, '0fbf12be9ac7644a1f2f', 'visual.json')
    if os.path.exists(genre_file):
        with open(genre_file, 'r', encoding='utf-8') as f:
            gdata = json.load(f)
        gdata['position'] = {
            "x": 1158,
            "y": 12,
            "z": 4,
            "height": 50,
            "width": 360,
            "tabOrder": 4
        }
        gdata['visual']['objects'] = {
            "data": [
                {
                    "properties": {
                        "mode": {
                            "expr": {
                                "Literal": {
                                    "Value": "'Dropdown'"
                                }
                            }
                        }
                    }
                }
            ],
            "header": [
                {
                    "properties": {
                        "show": {
                            "expr": {
                                "Literal": {
                                    "Value": "true"
                                }
                            }
                        },
                        "titleText": {
                            "expr": {
                                "Literal": {
                                    "Value": "'Genre Group'"
                                }
                            }
                        },
                        "fontColor": {
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
                        "textSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        },
                        "fontSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        }
                    }
                }
            ],
            "selection": [
                {
                    "properties": {
                        "selectAllCheckboxEnabled": {
                            "expr": {
                                "Literal": {
                                    "Value": "true"
                                }
                            }
                        },
                        "singleSelect": {
                            "expr": {
                                "Literal": {
                                    "Value": "false"
                                }
                            }
                        }
                    }
                }
            ],
            "items": [
                {
                    "properties": {
                        "fontColor": {
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
                        "background": {
                            "solid": {
                                "color": {
                                    "expr": {
                                        "Literal": {
                                            "Value": "'#1A1A1A'"
                                        }
                                    }
                                }
                            }
                        },
                        "textSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        },
                        "fontSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        }
                    }
                }
            ]
        }
        gdata['visual']['visualContainerObjects'] = {
            "background": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }
            ],
            "border": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#3A3A3A'"}}}}},
                        "radius": {"expr": {"Literal": {"Value": "4D"}}}
                    }
                }
            ]
        }
        with open(genre_file, 'w', encoding='utf-8') as f:
            json.dump(gdata, f, indent=2)

    # (e) Slicer 3: Language (b0a9e95c30030c64f446)
    # Dropdown style, Select All ON, multi-select ON, search ON
    lang_file = os.path.join(visuals_dir, 'b0a9e95c30030c64f446', 'visual.json')
    if os.path.exists(lang_file):
        with open(lang_file, 'r', encoding='utf-8') as f:
            ldata = json.load(f)
        ldata['position'] = {
            "x": 1530,
            "y": 12,
            "z": 5,
            "height": 50,
            "width": 360,
            "tabOrder": 5
        }
        ldata['visual']['objects'] = {
            "data": [
                {
                    "properties": {
                        "mode": {
                            "expr": {
                                "Literal": {
                                    "Value": "'Dropdown'"
                                }
                            }
                        }
                    }
                }
            ],
            "header": [
                {
                    "properties": {
                        "show": {
                            "expr": {
                                "Literal": {
                                    "Value": "true"
                                }
                            }
                        },
                        "titleText": {
                            "expr": {
                                "Literal": {
                                    "Value": "'Language'"
                                }
                            }
                        },
                        "fontColor": {
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
                        "textSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        },
                        "fontSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        }
                    }
                }
            ],
            "selection": [
                {
                    "properties": {
                        "selectAllCheckboxEnabled": {
                            "expr": {
                                "Literal": {
                                    "Value": "true"
                                }
                            }
                        },
                        "singleSelect": {
                            "expr": {
                                "Literal": {
                                    "Value": "false"
                                }
                            }
                        }
                    }
                }
            ],
            "general": [
                {
                    "properties": {
                        "selfFilterEnabled": {
                            "expr": {
                                "Literal": {
                                    "Value": "true"
                                }
                            }
                        }
                    }
                }
            ],
            "items": [
                {
                    "properties": {
                        "fontColor": {
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
                        "background": {
                            "solid": {
                                "color": {
                                    "expr": {
                                        "Literal": {
                                            "Value": "'#1A1A1A'"
                                        }
                                    }
                                }
                            }
                        },
                        "textSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        },
                        "fontSize": {
                            "expr": {
                                "Literal": {
                                    "Value": "11D"
                                }
                            }
                        }
                    }
                }
            ]
        }
        ldata['visual']['visualContainerObjects'] = {
            "background": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A1A1A'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }
            ],
            "border": [
                {
                    "properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#3A3A3A'"}}}}},
                        "radius": {"expr": {"Literal": {"Value": "4D"}}}
                    }
                }
            ]
        }
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(ldata, f, indent=2)

    print("Task A and Task B successfully executed.")

if __name__ == '__main__':
    apply_tasks()
