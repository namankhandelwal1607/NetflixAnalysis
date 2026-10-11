import csv
from collections import Counter

with open('data/processed/powerbi/fact_titles.csv', mode='r', encoding='utf-8') as f:
    facts = list(csv.DictReader(f))

with open('data/processed/powerbi/dim_date.csv', mode='r', encoding='utf-8') as f:
    dates = list(csv.DictReader(f))

with open('data/processed/powerbi/dim_genre.csv', mode='r', encoding='utf-8') as f:
    genres = list(csv.DictReader(f))

with open('data/processed/powerbi/dim_language.csv', mode='r', encoding='utf-8') as f:
    langs = list(csv.DictReader(f))

with open('data/processed/powerbi/bridge_title_genre.csv', mode='r', encoding='utf-8') as f:
    bridges = list(csv.DictReader(f))

print("=== TABLE ROW COUNTS ===")
print("fact_titles:", len(facts))
print("dim_date:", len(dates))
print("dim_genre:", len(genres))
print("dim_language:", len(langs))
print("bridge_title_genre:", len(bridges))

print("\n=== SECTION 2 CHECKS ===")
# 51 titles with '/' in raw genre? 23 titles with '/' in raw language?
# 159 titles in raw Documentary with mean 78.96 min?
with open('original/NetflixOriginals.csv', mode='r', encoding='latin-1') as f:
    raw_rows = list(csv.DictReader(f))

slash_genre = [r for r in raw_rows if '/' in r['Genre']]
slash_lang = [r for r in raw_rows if '/' in r['Language']]
print("Raw rows:", len(raw_rows))
print("Raw titles with '/' in Genre:", len(slash_genre))
print("Raw titles with '/' in Language:", len(slash_lang))
raw_docs = [r for r in raw_rows if r['Genre'] == 'Documentary']
raw_doc_rt = [float(r['Runtime']) for r in raw_docs]
print("Raw 'Documentary' count:", len(raw_docs), "mean runtime:", sum(raw_doc_rt)/len(raw_doc_rt))

print("\n=== SECTION 7 CHECKS ===")
# 1. Scaling
by_year = Counter(r['date_key'][:4] for r in facts)
print("By year:", sorted(by_year.items()))
mature = [r for r in facts if '2016' <= r['date_key'][:4] <= '2020']
print(f"Mature titles (2016-2020): {len(mature)} ({len(mature)/len(facts)*100:.2f}%)")
growth_2016_to_2020 = (by_year['2020'] - by_year['2016']) / by_year['2016'] * 100
growth_2017 = (by_year['2017'] - by_year['2016']) / by_year['2016'] * 100
diff_2017 = by_year['2017'] - by_year['2016']
growth_2020 = (by_year['2020'] - by_year['2019']) / by_year['2019'] * 100
diff_2020 = by_year['2020'] - by_year['2019']
print(f"Scaling 2016 ({by_year['2016']}) to 2020 ({by_year['2020']}): +{growth_2016_to_2020:.1f}%")
print(f"2017 growth: +{diff_2017} titles, +{growth_2017:.1f}%")
print(f"2020 growth: +{diff_2020} titles, +{growth_2020:.1f}%")

# Friday count
date_map = {d['date_key']: d['weekday_name'] for d in dates}
fridays = [r for r in facts if date_map.get(r['date_key']) == 'Friday']
print(f"Friday titles: {len(fridays)} ({len(fridays)/len(facts)*100:.2f}%)")

# 2. Genres
by_genre = {}
for r in facts:
    by_genre.setdefault(r['genre_group'], []).append(r)

for g, g_rows in sorted(by_genre.items()):
    scs = [float(r['imdb_score']) for r in g_rows]
    mean_s = sum(scs) / len(scs)
    high = sum(1 for s in scs if s >= 7.0)
    low = sum(1 for s in scs if s < 5.5)
    print(f"Genre: {g:<25} Count: {len(g_rows):<4} Mean: {mean_s:.4f}  High%: {high/len(scs)*100:.2f}% ({high})  Low%: {low/len(scs)*100:.2f}% ({low})")

# 3. Runtime & correlation
rts = [float(r['runtime']) for r in facts]
scs = [float(r['imdb_score']) for r in facts]
rts_sorted = sorted(rts)
median_rt = (rts_sorted[len(rts)//2 - 1] + rts_sorted[len(rts)//2]) / 2 if len(rts)%2==0 else rts_sorted[len(rts)//2]
print(f"Runtime min: {min(rts)}, max: {max(rts)}, median: {median_rt}")

# 4. Languages
by_lang = Counter(r['primary_language'] for r in facts)
print("Language counts:", by_lang.most_common(5))
for l in ['English', 'Hindi', 'Spanish']:
    c = by_lang[l]
    print(f"  {l}: {c} ({c/len(facts)*100:.2f}%)")
comb3 = by_lang['English'] + by_lang['Hindi'] + by_lang['Spanish']
print(f"Top 3 combined: {comb3} ({comb3/len(facts)*100:.2f}%)")
langs_lt_10 = sum(1 for c in by_lang.values() if c < 10)
print(f"Languages with n < 10: {langs_lt_10} of {len(by_lang)}")

# 5. Outliers
short_53 = [r for r in facts if float(r['runtime']) < 53]
short_40 = [r for r in facts if float(r['runtime']) < 40]
epic_141 = [r for r in facts if float(r['runtime']) > 141]
print(f"Short < 53m: {len(short_53)}")
print(f"Short < 40m: {len(short_40)}")
print(f"Epic > 141m: {len(epic_141)}")
for r in epic_141:
    print(f"  Epic: {r['title']} ({r['runtime']}m)")

low_score = [r for r in facts if float(r['imdb_score']) < 3.75]
high_score = [r for r in facts if float(r['imdb_score']) > 8.95]
print(f"Low score < 3.75: {len(low_score)}")
print(f"High score > 8.95: {len(high_score)}")
