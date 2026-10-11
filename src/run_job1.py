import json
import os

visuals_dir = 'powerbi/netflix_report/processedData.Report/definition/pages/95c0693daf92b6d6c188/visuals'
theme_file = 'powerbi/netflix_report/processedData.Report/StaticResources/RegisteredResources/NetflixDark.json'

def run_job1():
    # 1. Update NetflixDark.json theme
    if os.path.exists(theme_file):
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme = json.load(f)
        
        theme.setdefault("visualStyles", {})["slicer"] = {
            "*": {
                "*": [
                    {
                        "fontColor": {"solid": {"color": "#FFFFFF"}},
                        "background": {"solid": {"color": "#1A1A1A"}}
                    }
                ],
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
                "input": [
                    {
                        "fontColor": {"solid": {"color": "#FFFFFF"}},
                        "background": {"solid": {"color": "#1A1A1A"}},
                        "textSize": 11,
                        "fontSize": 11
                    }
                ],
                "numeric": [
                    {
                        "fontColor": {"solid": {"color": "#FFFFFF"}},
                        "background": {"solid": {"color": "#1A1A1A"}},
                        "textSize": 11,
                        "fontSize": 11
                    }
                ],
                "slider": [
                    {
                        "show": False,
                        "color": {"solid": {"color": "#FFFFFF"}}
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

    # 2. Year slicer (35ed6b4c865d18e5e108)
    year_file = os.path.join(visuals_dir, '35ed6b4c865d18e5e108', 'visual.json')
    if os.path.exists(year_file):
        with open(year_file, 'r', encoding='utf-8') as f:
            ydata = json.load(f)
        
        ydata['visual']['syncGroup'] = {
            "groupName": "YearSyncGroup",
            "fieldChanges": True,
            "filterChanges": True
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
            "input": [
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
                        }
                    }
                }
            ],
            "numeric": [
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
                        }
                    }
                }
            ]
        }
        with open(year_file, 'w', encoding='utf-8') as f:
            json.dump(ydata, f, indent=2)

    # 3. Genre slicer syncGroup
    genre_file = os.path.join(visuals_dir, '0fbf12be9ac7644a1f2f', 'visual.json')
    if os.path.exists(genre_file):
        with open(genre_file, 'r', encoding='utf-8') as f:
            gdata = json.load(f)
        gdata['visual']['syncGroup'] = {
            "groupName": "GenreSyncGroup",
            "fieldChanges": True,
            "filterChanges": True
        }
        with open(genre_file, 'w', encoding='utf-8') as f:
            json.dump(gdata, f, indent=2)

    # 4. Language slicer syncGroup
    lang_file = os.path.join(visuals_dir, 'b0a9e95c30030c64f446', 'visual.json')
    if os.path.exists(lang_file):
        with open(lang_file, 'r', encoding='utf-8') as f:
            ldata = json.load(f)
        ldata['visual']['syncGroup'] = {
            "groupName": "LanguageSyncGroup",
            "fieldChanges": True,
            "filterChanges": True
        }
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(ldata, f, indent=2)

    # 5. Annual chart title update
    v1_file = os.path.join(visuals_dir, 'p1_v1_annual_trajectory', 'visual.json')
    if os.path.exists(v1_file):
        with open(v1_file, 'r', encoding='utf-8') as f:
            v1data = json.load(f)
        v1data['visual']['visualContainerObjects'] = {
            "title": [
                {
                    "properties": {
                        "text": {
                            "expr": {
                                "Literal": {
                                    "Value": "'Annual Release Volume (Grey = Partial/Sparse Years)'"
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
        with open(v1_file, 'w', encoding='utf-8') as f:
            json.dump(v1data, f, indent=2)

    print("Job 1 completed successfully.")

if __name__ == '__main__':
    run_job1()
