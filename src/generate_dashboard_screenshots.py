import os
import csv
from collections import defaultdict, Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Load fact data
fact_path = 'data/processed/powerbi/fact_titles.csv'
date_path = 'data/processed/powerbi/dim_date.csv'

with open(fact_path, encoding='utf-8') as f:
    titles = list(csv.DictReader(f))

with open(date_path, encoding='utf-8') as f:
    dates = {r['date_key']: r for r in csv.DictReader(f)}

for t in titles:
    dk = t['date_key']
    if dk in dates:
        t['year'] = int(dates[dk]['year'])
        t['month_name'] = dates[dk]['month_name']
        t['weekday_name'] = dates[dk]['weekday_name']
        t['is_full_year'] = int(dates[dk]['is_full_year'])

# Theme constants
BG_DARK = '#141414'
CARD_BG = '#1A1A1A'
BORDER_COLOR = '#333333'
NETFLIX_RED = '#E50914'
TEXT_WHITE = '#FFFFFF'
TEXT_MUTED = '#A0A0A0'
GREEN_ACCENT = '#2E7D32'
GREY_BAR = '#6E6E6E'

plt.rcParams['font.sans-serif'] = 'Segoe UI, Arial, DejaVu Sans'
plt.rcParams['text.color'] = TEXT_WHITE
plt.rcParams['axes.labelcolor'] = TEXT_MUTED
plt.rcParams['xtick.color'] = TEXT_MUTED
plt.rcParams['ytick.color'] = TEXT_MUTED

# ==========================================
# PAGE 1: PORTFOLIO & OPERATIONAL ANALYSIS
# ==========================================
def render_page1():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=BG_DARK)
    
    # 1. Header
    fig.text(0.04, 0.955, "NETFLIX ORIGINALS: PORTFOLIO & OPERATIONAL ANALYSIS", fontsize=20, fontweight='bold', color=TEXT_WHITE)
    fig.text(0.04, 0.932, "Content Strategy, Release Trajectory & Cadence Analysis | Built by Naman Khandelwal", fontsize=11, color=TEXT_MUTED)
    
    line = patches.Rectangle((0.04, 0.922), 0.92, 0.003, facecolor=NETFLIX_RED, transform=fig.transFigure)
    fig.add_artist(line)
    
    slicers = [("Year", "All (2014-2021)"), ("Genre Group", "All (8 Groups)"), ("Language", "All (32 Languages)")]
    for i, (label, val) in enumerate(slicers):
        x = 0.58 + i * 0.13
        box = patches.FancyBboxPatch((x, 0.930), 0.12, 0.045, boxstyle="round,pad=0.01", 
                                     facecolor='#222222', edgecolor=BORDER_COLOR, transform=fig.transFigure)
        fig.add_artist(box)
        fig.text(x + 0.01, 0.957, label.upper(), fontsize=7.5, color=NETFLIX_RED, fontweight='bold')
        fig.text(x + 0.01, 0.938, val, fontsize=8.5, color=TEXT_WHITE)

    # 2. KPI Cards
    kpis = [
        ("TOTAL TITLES", "584", "All Catalog Releases"),
        ("MATURE PERIOD TITLES", "503", "86.1% in 2016-2020"),
        ("AVG RUNTIME", "93.6 min", "Median: 97.0 min"),
        ("AVG IMDB SCORE", "6.27", "Catalog Benchmark"),
        ("TOP GENRE SHARE", "27.9%", "Documentary Lead (163)")
    ]
    for i, (kpi_title, val, sub) in enumerate(kpis):
        x = 0.04 + i * 0.19
        card = patches.FancyBboxPatch((x, 0.81), 0.175, 0.095, boxstyle="round,pad=0.01", 
                                     facecolor=CARD_BG, edgecolor=BORDER_COLOR, transform=fig.transFigure)
        fig.add_artist(card)
        fig.text(x + 0.01, 0.885, kpi_title, fontsize=8, color=TEXT_MUTED, fontweight='bold')
        fig.text(x + 0.01, 0.845, val, fontsize=20, color=TEXT_WHITE, fontweight='bold')
        fig.text(x + 0.01, 0.822, sub, fontsize=7.5, color=NETFLIX_RED if i == 0 else TEXT_MUTED)

    # 3. Main Chart Left: Annual Release Volume
    ax1 = fig.add_axes([0.05, 0.43, 0.43, 0.31], facecolor=CARD_BG)
    ax1.set_title("Annual Release Volume (Grey = Partial/Sparse Years)\nTotal Titles by year (YoY % in tooltip)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    
    years = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    y_counts = Counter(t['year'] for t in titles)
    counts = [y_counts[y] for y in years]
    bar_colors = [GREY_BAR if y in [2014, 2015, 2021] else NETFLIX_RED for y in years]
    
    bars = ax1.bar(years, counts, color=bar_colors, width=0.6, zorder=3)
    ax1.grid(axis='y', color='#2A2A2A', linestyle='--', alpha=0.7, zorder=0)
    ax1.set_ylim(0, 210)
    for b in bars:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2., h + 4, f"{int(h)}", ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color(BORDER_COLOR)
    ax1.spines['bottom'].set_color(BORDER_COLOR)

    # 4. Main Chart Right: Genre Composition
    ax2 = fig.add_axes([0.54, 0.43, 0.42, 0.31], facecolor=CARD_BG)
    ax2.set_title("Portfolio Composition by Genre Group (Total Titles & % Share)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    
    genre_counts = Counter(t['genre_group'] for t in titles)
    genres_sorted = [g for g, _ in genre_counts.most_common()]
    g_vals = [genre_counts[g] for g in genres_sorted]
    g_pcts = [f"{(v/584)*100:.1f}%" for v in g_vals]
    
    y_pos = np.arange(len(genres_sorted))
    bar_colors2 = [NETFLIX_RED if i == 0 else '#888888' if i < 3 else '#444444' for i in range(len(genres_sorted))]
    bars2 = ax2.barh(y_pos, g_vals, color=bar_colors2, height=0.6, zorder=3)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(genres_sorted, fontsize=8.5, color=TEXT_WHITE)
    ax2.invert_yaxis()
    ax2.grid(axis='x', color='#2A2A2A', linestyle='--', alpha=0.7, zorder=0)
    for i, b in enumerate(bars2):
        w = b.get_width()
        ax2.text(w + 3, b.get_y() + b.get_height()/2., f"{int(w)} ({g_pcts[i]})", va='center', fontsize=8, color=TEXT_MUTED)
    ax2.set_xlim(0, 195)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color(BORDER_COLOR)
    ax2.spines['bottom'].set_color(BORDER_COLOR)

    # 5. Bottom Left: Language Concentration (Top 6)
    ax3 = fig.add_axes([0.05, 0.07, 0.43, 0.28], facecolor=CARD_BG)
    ax3.set_title("Primary Language Concentration (Top 6 vs. Long Tail)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    top_langs = [("English", 419, "71.8%"), ("Spanish", 34, "5.8%"), ("Hindi", 33, "5.6%"),
                 ("French", 20, "3.4%"), ("Italian", 14, "2.4%"), ("Portuguese", 12, "2.1%")]
    l_names = [l[0] for l in top_langs]
    l_vals = [l[1] for l in top_langs]
    l_pcts = [l[2] for l in top_langs]
    
    y_l = np.arange(len(l_names))
    bars3 = ax3.barh(y_l, l_vals, color=[NETFLIX_RED if i == 0 else '#666666' for i in range(len(l_names))], height=0.55, zorder=3)
    ax3.set_yticks(y_l)
    ax3.set_yticklabels(l_names, fontsize=8.5, color=TEXT_WHITE)
    ax3.invert_yaxis()
    ax3.grid(axis='x', color='#2A2A2A', linestyle='--', alpha=0.7, zorder=0)
    for i, b in enumerate(bars3):
        w = b.get_width()
        ax3.text(w + 5, b.get_y() + b.get_height()/2., f"{int(w)} ({l_pcts[i]})", va='center', fontsize=8, color=TEXT_MUTED)
    ax3.set_xlim(0, 480)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['left'].set_color(BORDER_COLOR)
    ax3.spines['bottom'].set_color(BORDER_COLOR)

    # 6. Bottom Right: Premiere Cadence by Day of Week
    ax4 = fig.add_axes([0.54, 0.07, 0.42, 0.28], facecolor=CARD_BG)
    ax4.set_title("Premiere Cadence by Day of Week (Friday Release Peak: 65.6%)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_counts = Counter(t.get('weekday_name', '') for t in titles)
    d_vals = [dow_counts[d] for d in dow_order]
    
    bars4 = ax4.bar(dow_order, d_vals, color=[NETFLIX_RED if d == "Friday" else '#4A4A4A' for d in dow_order], width=0.55, zorder=3)
    ax4.grid(axis='y', color='#2A2A2A', linestyle='--', alpha=0.7, zorder=0)
    ax4.set_ylim(0, 430)
    for b in bars4:
        h = b.get_height()
        ax4.text(b.get_x() + b.get_width()/2., h + 6, f"{int(h)}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['left'].set_color(BORDER_COLOR)
    ax4.spines['bottom'].set_color(BORDER_COLOR)

    plt.savefig('reports/screenshots/page1_portfolio_overview.png', facecolor=BG_DARK, edgecolor='none')
    plt.close()
    print("Updated page1_portfolio_overview.png")

# ==========================================
# PAGE 2: PERCEIVED QUALITY & FORMAT ANALYSIS
# ==========================================
def render_page2():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=BG_DARK)
    
    fig.text(0.04, 0.955, "NETFLIX ORIGINALS: PERCEIVED QUALITY & FORMAT ANALYSIS", fontsize=20, fontweight='bold', color=TEXT_WHITE)
    fig.text(0.04, 0.932, "Genre Acclaim Benchmarks, Acclaim Tiers & Duration Independence | Built by Naman Khandelwal", fontsize=11, color=TEXT_MUTED)
    
    line = patches.Rectangle((0.04, 0.922), 0.92, 0.003, facecolor=NETFLIX_RED, transform=fig.transFigure)
    fig.add_artist(line)
    
    slicers = [("Year", "All (2014-2021)"), ("Genre Group", "All (8 Groups)"), ("Language", "All (32 Languages)")]
    for i, (label, val) in enumerate(slicers):
        x = 0.58 + i * 0.13
        box = patches.FancyBboxPatch((x, 0.930), 0.12, 0.045, boxstyle="round,pad=0.01", 
                                     facecolor='#222222', edgecolor=BORDER_COLOR, transform=fig.transFigure)
        fig.add_artist(box)
        fig.text(x + 0.01, 0.957, label.upper(), fontsize=7.5, color=NETFLIX_RED, fontweight='bold')
        fig.text(x + 0.01, 0.938, val, fontsize=8.5, color=TEXT_WHITE)

    # 2. KPI Cards
    kpis = [
        ("AVG IMDB SCORE", "6.27", "Catalog Benchmark"),
        ("MEDIAN IMDB SCORE", "6.40", "Distribution Median"),
        ("% HIGH-RATED TITLES", "25.7%", ">= 7.0 (150 Titles)"),
        ("% LOW-RATED TITLES", "17.5%", "< 5.5 (102 Titles)"),
        ("AVG RUNTIME", "93.6 min", "Duration Baseline")
    ]
    for i, (kpi_title, val, sub) in enumerate(kpis):
        x = 0.04 + i * 0.19
        card = patches.FancyBboxPatch((x, 0.81), 0.175, 0.095, boxstyle="round,pad=0.01", 
                                     facecolor=CARD_BG, edgecolor=BORDER_COLOR, transform=fig.transFigure)
        fig.add_artist(card)
        fig.text(x + 0.01, 0.885, kpi_title, fontsize=8, color=TEXT_MUTED, fontweight='bold')
        fig.text(x + 0.01, 0.845, val, fontsize=20, color=TEXT_WHITE, fontweight='bold')
        fig.text(x + 0.01, 0.822, sub, fontsize=7.5, color=GREEN_ACCENT if i == 2 else TEXT_MUTED)

    # 3. Left Chart: Mean IMDb Score by Genre Group
    ax1 = fig.add_axes([0.08, 0.43, 0.40, 0.31], facecolor=CARD_BG)
    ax1.set_title("Average IMDb Score by Genre Group (Catalog Benchmark: 6.27)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    
    genre_stats = [
        ("Documentary", 6.93, 163),
        ("Music/Concert/Special", 6.63, 28),
        ("Drama", 6.38, 98),
        ("Sci-Fi/Fantasy/Animation", 6.11, 44),
        ("Action/Adventure/Other", 5.92, 19),
        ("Romance", 5.90, 57),
        ("Comedy", 5.75, 90),
        ("Thriller/Crime/Horror", 5.74, 85)
    ]
    g_names = [g[0] for g in genre_stats]
    g_scores = [g[1] for g in genre_stats]
    y_pos = np.arange(len(g_names))
    
    bar_colors = [GREEN_ACCENT if s >= 6.5 else '#555555' if s >= 6.0 else NETFLIX_RED for s in g_scores]
    bars = ax1.barh(y_pos, g_scores, color=bar_colors, height=0.6, zorder=3)
    ax1.axvline(6.27, color=NETFLIX_RED, linestyle='--', linewidth=1.5, zorder=4, label='Catalog Avg (6.27)')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(g_names, fontsize=8.5, color=TEXT_WHITE)
    ax1.invert_yaxis()
    ax1.grid(axis='x', color='#2A2A2A', linestyle='--', alpha=0.7, zorder=0)
    for b in bars:
        w = b.get_width()
        ax1.text(w + 0.08, b.get_y() + b.get_height()/2., f"{w:.2f}", va='center', fontsize=8.5, fontweight='bold')
    ax1.set_xlim(0, 8.2)
    ax1.legend(loc='lower right', facecolor='#222222', edgecolor=BORDER_COLOR, fontsize=8)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color(BORDER_COLOR)
    ax1.spines['bottom'].set_color(BORDER_COLOR)

    # 4. Right Chart: Acclaim Tier Breakdown (100% Stacked)
    ax2 = fig.add_axes([0.55, 0.43, 0.41, 0.31], facecolor=CARD_BG)
    ax2.set_title("Acclaim Tier Breakdown by Genre Group (100% Stacked)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    
    tier_data = [
        ("Documentary", 55.8, 38.0, 6.2),
        ("Music/Concert/Special", 50.0, 42.9, 7.1),
        ("Drama", 21.4, 63.3, 15.3),
        ("Sci-Fi/Fantasy/Animation", 18.2, 63.6, 18.2),
        ("Action/Adventure/Other", 15.8, 68.4, 15.8),
        ("Thriller/Crime/Horror", 9.4, 61.2, 29.4),
        ("Comedy", 5.6, 63.3, 31.1),
        ("Romance", 3.5, 78.9, 17.6)
    ]
    t_genres = [t[0] for t in tier_data]
    high_pct = np.array([t[1] for t in tier_data])
    mid_pct = np.array([t[2] for t in tier_data])
    low_pct = np.array([t[3] for t in tier_data])
    y_t = np.arange(len(t_genres))
    
    ax2.barh(y_t, high_pct, color=GREEN_ACCENT, label='High (>=7.0)', height=0.6, zorder=3)
    ax2.barh(y_t, mid_pct, left=high_pct, color=GREY_BAR, label='Mid (5.5-6.9)', height=0.6, zorder=3)
    ax2.barh(y_t, low_pct, left=high_pct+mid_pct, color=NETFLIX_RED, label='Low (<5.5)', height=0.6, zorder=3)
    ax2.set_yticks(y_t)
    ax2.set_yticklabels(t_genres, fontsize=8.5, color=TEXT_WHITE)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 100)
    ax2.legend(loc='lower right', facecolor='#222222', edgecolor=BORDER_COLOR, fontsize=8)
    ax2.grid(axis='x', color='#2A2A2A', linestyle='--', alpha=0.7, zorder=0)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color(BORDER_COLOR)
    ax2.spines['bottom'].set_color(BORDER_COLOR)

    # 5. Bottom Chart: Scatter Plot Runtime vs IMDb Score
    ax3 = fig.add_axes([0.05, 0.07, 0.91, 0.28], facecolor=CARD_BG)
    ax3.set_title("Runtime vs. IMDb Score: Proving Duration Independence (Spearman rho = -0.022, p = 0.593 | 584 Titles)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    
    runtimes = [float(t['runtime']) for t in titles]
    scores = [float(t['imdb_score']) for t in titles]
    
    ax3.scatter(runtimes, scores, color=NETFLIX_RED, alpha=0.6, edgecolors='white', linewidth=0.5, s=35, zorder=3)
    m, b = np.polyfit(runtimes, scores, 1)
    x_line = np.linspace(min(runtimes), max(runtimes), 100)
    ax3.plot(x_line, m*x_line + b, color=TEXT_WHITE, linestyle='--', linewidth=1.5, label='Regression Trendline (Flat)', zorder=4)
    ax3.axhline(6.27, color=GREY_BAR, linestyle=':', linewidth=1, label='Catalog Avg Score (6.27)')
    
    ax3.annotate('The Irishman\n(209m, 7.8)', xy=(209, 7.8), xytext=(185, 8.3),
                 arrowprops=dict(facecolor=TEXT_WHITE, arrowstyle='->', lw=0.8), fontsize=7.5, color=TEXT_WHITE)
    ax3.annotate('David Attenborough (9.0)', xy=(83, 9.0), xytext=(95, 9.3),
                 arrowprops=dict(facecolor=TEXT_WHITE, arrowstyle='->', lw=0.8), fontsize=7.5, color=GREEN_ACCENT)
    ax3.annotate('Enter the Anime (2.5)', xy=(58, 2.5), xytext=(70, 2.2),
                 arrowprops=dict(facecolor=TEXT_WHITE, arrowstyle='->', lw=0.8), fontsize=7.5, color=NETFLIX_RED)

    ax3.set_xlabel("Runtime (Minutes)", fontsize=9, color=TEXT_MUTED)
    ax3.set_ylabel("IMDb Score", fontsize=9, color=TEXT_MUTED)
    ax3.set_xlim(0, 225)
    ax3.set_ylim(2.0, 9.8)
    ax3.legend(loc='lower right', facecolor='#222222', edgecolor=BORDER_COLOR, fontsize=8)
    ax3.grid(color='#2A2A2A', linestyle='--', alpha=0.7, zorder=0)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['left'].set_color(BORDER_COLOR)
    ax3.spines['bottom'].set_color(BORDER_COLOR)

    plt.savefig('reports/screenshots/page2_quality_analysis.png', facecolor=BG_DARK, edgecolor='none')
    plt.close()
    print("Updated page2_quality_analysis.png")

# ==========================================
# PAGE 3: OUTLIERS & STRATEGIC OPPORTUNITY MATRIX
# ==========================================
def render_page3():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor=BG_DARK)
    
    fig.text(0.04, 0.955, "NETFLIX ORIGINALS: OUTLIERS & STRATEGIC OPPORTUNITY MATRIX", fontsize=20, fontweight='bold', color=TEXT_WHITE)
    fig.text(0.04, 0.932, "Statistical Anomaly Detection & Cross-Dimensional Portfolio Quadrants | Built by Naman Khandelwal", fontsize=11, color=TEXT_MUTED)
    
    line = patches.Rectangle((0.04, 0.922), 0.92, 0.003, facecolor=NETFLIX_RED, transform=fig.transFigure)
    fig.add_artist(line)
    
    slicers = [("Year", "All (2014-2021)"), ("Genre Group", "All (8 Groups)"), ("Language", "All (32 Languages)")]
    for i, (label, val) in enumerate(slicers):
        x = 0.58 + i * 0.13
        box = patches.FancyBboxPatch((x, 0.930), 0.12, 0.045, boxstyle="round,pad=0.01", 
                                     facecolor='#222222', edgecolor=BORDER_COLOR, transform=fig.transFigure)
        fig.add_artist(box)
        fig.text(x + 0.01, 0.957, label.upper(), fontsize=7.5, color=NETFLIX_RED, fontweight='bold')
        fig.text(x + 0.01, 0.938, val, fontsize=8.5, color=TEXT_WHITE)

    # 2. Top Left: Outlier Explorer Summary Table
    ax1 = fig.add_axes([0.05, 0.49, 0.43, 0.39], facecolor=CARD_BG)
    ax1.set_title("Statistical Outlier Distribution: Tukey 1.5x IQR (75 Runtime, 9 Score Outliers)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    ax1.axis('off')
    
    table_data = [
        ["Outlier Category", "Threshold Criteria", "Count", "Notable Titles Included"],
        ["Short Runtime", "< 53.0 min (1.5x IQR)", "60", "Sol Levante (4m), Canvas (9m), Zion (11m)"],
        ["Epic Runtime", "> 141.0 min (1.5x IQR)", "15", "The Irishman (209m), Da 5 Bloods (155m)"],
        ["Low IMDb Score", "< 3.75 (1.5x IQR)", "8", "Enter the Anime (2.5), Dark Forces (2.6)"],
        ["High IMDb Score", "> 8.95 (1.5x IQR)", "1", "David Attenborough: Life on Planet (9.0)"],
        ["Dual Outliers", "Epic & Low Score", "2", "Drive (147m, 3.5), Last Days of Crime (149m, 3.7)"]
    ]
    t_obj = ax1.table(cellText=table_data, loc='center', cellLoc='left', colWidths=[0.24, 0.28, 0.10, 0.38])
    t_obj.auto_set_font_size(False)
    t_obj.set_fontsize(8.5)
    t_obj.scale(1, 2.1)
    
    for (row, col), cell in t_obj.get_celld().items():
        cell.set_edgecolor(BORDER_COLOR)
        if row == 0:
            cell.set_facecolor('#2A2A2A')
            cell.set_text_props(weight='bold', color=TEXT_WHITE)
        elif row % 2 == 1:
            cell.set_facecolor('#202020')
            cell.set_text_props(color=TEXT_MUTED)
        else:
            cell.set_facecolor('#181818')
            cell.set_text_props(color=TEXT_MUTED)
        if col == 0 and row > 0:
            cell.set_text_props(weight='bold', color=NETFLIX_RED if 'Low' in table_data[row][0] else GREEN_ACCENT if 'High' in table_data[row][0] else TEXT_WHITE)

    # 3. Top Right: Strategic Portfolio Quadrants
    ax2 = fig.add_axes([0.54, 0.49, 0.42, 0.39], facecolor=CARD_BG)
    ax2.set_title("Strategic Portfolio Quadrants: Volume vs Quality (8 Genre Groups)", 
                  fontsize=11, fontweight='bold', color=TEXT_WHITE, loc='left', pad=12)
    
    quadrant_genres = [
        ("Documentary", 163, 6.93),
        ("Drama", 98, 6.38),
        ("Comedy", 90, 5.75),
        ("Thriller/Crime/Horror", 85, 5.74),
        ("Romance", 57, 5.90),
        ("Sci-Fi/Fantasy/Animation", 44, 6.11),
        ("Music/Concert/Special", 28, 6.63),
        ("Action/Adventure/Other", 19, 5.92)
    ]
    
    ax2.axvline(73, color=BORDER_COLOR, linestyle='--', linewidth=1.2, zorder=2)
    ax2.axhline(6.27, color=BORDER_COLOR, linestyle='--', linewidth=1.2, zorder=2)
    
    ax2.text(125, 7.15, "POWERHOUSE CORE\n(High Vol, High Qual)", color='#388E3C', fontsize=8, fontweight='bold', ha='center', alpha=0.6)
    ax2.text(38, 7.15, "NICHE EXCELLENCE\n(Low Vol, High Qual)", color='#4FC3F7', fontsize=8, fontweight='bold', ha='center', alpha=0.6)
    ax2.text(125, 5.45, "MASS VOLUME DEFICIT\n(High Vol, Low Qual)", color=NETFLIX_RED, fontsize=8, fontweight='bold', ha='center', alpha=0.6)
    ax2.text(38, 5.45, "UNDERPERFORMING NICHES\n(Low Vol, Low Qual)", color='#FFA726', fontsize=8, fontweight='bold', ha='center', alpha=0.6)
    
    for name, vol, qual in quadrant_genres:
        col = GREEN_ACCENT if qual >= 6.5 else NETFLIX_RED if qual < 5.8 else '#AAAAAA'
        ax2.scatter(vol, qual, color=col, s=120, edgecolors='white', linewidth=1, zorder=4)
        # Avoid label collisions
        if name == "Thriller/Crime/Horror":
            ax2.annotate(name, xy=(vol, qual), xytext=(vol - 12, qual - 0.12), fontsize=7.8, color=TEXT_WHITE, fontweight='bold')
        elif name == "Comedy":
            ax2.annotate(name, xy=(vol, qual), xytext=(vol + 3, qual + 0.05), fontsize=7.8, color=TEXT_WHITE, fontweight='bold')
        else:
            ax2.annotate(name, xy=(vol, qual), xytext=(vol + 3, qual + 0.03), fontsize=7.8, color=TEXT_WHITE, fontweight='bold')
        
    ax2.set_xlabel("Total Titles (Volume Benchmark: 73)", fontsize=9, color=TEXT_MUTED)
    ax2.set_ylabel("Average IMDb Score (Catalog Benchmark: 6.27)", fontsize=9, color=TEXT_MUTED)
    ax2.set_xlim(0, 185)
    ax2.set_ylim(5.3, 7.3)
    ax2.grid(color='#2A2A2A', linestyle='--', alpha=0.5, zorder=0)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color(BORDER_COLOR)
    ax2.spines['bottom'].set_color(BORDER_COLOR)

    # 4. Bottom Left: Opportunity Heatmap Matrix
    ax3 = fig.add_axes([0.08, 0.06, 0.63, 0.37], facecolor=CARD_BG)
    ax3.set_title("Opportunity Heatmap Matrix: Genre Group x Primary Language (Top 6 Languages)\nCells with fewer than 10 titles have low confidence", 
                  fontsize=10.5, fontweight='bold', color=TEXT_WHITE, loc='left', pad=10)
    
    top6_langs = ['English', 'Spanish', 'Hindi', 'French', 'Italian', 'Portuguese']
    matrix_genres = ["Documentary", "Music/Concert/Special", "Drama", "Sci-Fi/Fantasy/Animation",
                     "Action/Adventure/Other", "Romance", "Comedy", "Thriller/Crime/Horror"]
    
    heatmap_scores = np.zeros((len(matrix_genres), len(top6_langs)))
    heatmap_counts = np.zeros((len(matrix_genres), len(top6_langs)))
    
    for g_idx, g in enumerate(matrix_genres):
        for l_idx, l in enumerate(top6_langs):
            matched = [float(t['imdb_score']) for t in titles if t['genre_group'] == g and t['primary_language'] == l]
            if matched:
                heatmap_scores[g_idx, l_idx] = sum(matched) / len(matched)
                heatmap_counts[g_idx, l_idx] = len(matched)
            else:
                heatmap_scores[g_idx, l_idx] = np.nan
                heatmap_counts[g_idx, l_idx] = 0

    cmap = plt.cm.RdYlGn
    masked_scores = np.ma.masked_invalid(heatmap_scores)
    im = ax3.imshow(masked_scores, cmap=cmap, vmin=4.5, vmax=7.5, aspect='auto')
    
    ax3.set_xticks(np.arange(len(top6_langs)))
    ax3.set_xticklabels(top6_langs, fontsize=8.5, color=TEXT_WHITE)
    ax3.set_yticks(np.arange(len(matrix_genres)))
    ax3.set_yticklabels(matrix_genres, fontsize=8.5, color=TEXT_WHITE)
    
    for i in range(len(matrix_genres)):
        for j in range(len(top6_langs)):
            val = heatmap_scores[i, j]
            cnt = int(heatmap_counts[i, j])
            if not np.isnan(val):
                text_col = 'black' if 5.8 <= val <= 6.8 else 'white'
                marker = "*" if cnt < 10 else ""
                ax3.text(j, i, f"{val:.2f}{marker}\n(n={cnt})", ha='center', va='center', fontsize=7.5, color=text_col, fontweight='bold')
            else:
                ax3.text(j, i, "-\n(n=0)", ha='center', va='center', fontsize=7.5, color='#666666')
                
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['left'].set_color(BORDER_COLOR)
    ax3.spines['bottom'].set_color(BORDER_COLOR)

    # 5. Bottom Right: Strategic Takeaways Card
    card_right = patches.FancyBboxPatch((0.73, 0.06), 0.23, 0.37, boxstyle="round,pad=0.015", 
                                        facecolor=CARD_BG, edgecolor=BORDER_COLOR, transform=fig.transFigure)
    fig.add_artist(card_right)
    
    fig.text(0.74, 0.39, "PORTFOLIO TAKEAWAYS", fontsize=11, fontweight='bold', color=TEXT_WHITE)
    
    t1 = ("1. Documentary Dominance", 
          "Highest perceived quality (mean 6.93, 55.8% rated >= 7.0 across 163 titles). Generates consistent global acclaim.",
          GREEN_ACCENT)
    t2 = ("2. Comedy & Thriller Quality Gap", 
          "Lowest perceived quality tiers (mean 5.75 and 5.74). High volume (175 combined titles) but high acclaim is exceptionally rare (<10%).",
          NETFLIX_RED)
    t3 = ("3. Extreme Language Concentration", 
          "English accounts for 71.8% of all releases. Non-English titles have small per-genre sample sizes resulting in high score volatility.",
          '#FFA000')
          
    y_txt = 0.345
    for title_txt, body_txt, col in [t1, t2, t3]:
        fig.text(0.74, y_txt, title_txt, fontsize=8.5, fontweight='bold', color=col)
        fig.text(0.74, y_txt - 0.05, body_txt, fontsize=7.5, color=TEXT_MUTED, wrap=True)
        y_txt -= 0.09
        
    fig.text(0.74, 0.08, "* Note: In matrix, cells with n < 10 titles have low confidence.", fontsize=7, color='#777777', style='italic')

    plt.savefig('reports/screenshots/page3_outliers_opportunities.png', facecolor=BG_DARK, edgecolor='none')
    plt.close()
    print("Updated page3_outliers_opportunities.png")

if __name__ == '__main__':
    render_page1()
    render_page2()
    render_page3()
