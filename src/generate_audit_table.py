import csv
from collections import Counter, defaultdict

with open('data/processed/powerbi/fact_titles.csv', encoding='utf-8') as f:
    titles = list(csv.DictReader(f))

total_titles = len(titles)
print('Total titles:', total_titles)

# 1. genre_group stats: title count, mean IMDb, % >= 7.0
genre_groups = defaultdict(list)
for t in titles:
    g = t['genre_group']
    score = float(t['imdb_score'])
    runtime = float(t['runtime'])
    genre_groups[g].append((score, runtime, t))

print('\n--- GENRE GROUP VERIFICATION TABLE ---')
print(f'| {"genre_group":<26} | {"Title Count":<11} | {"Mean IMDb":<9} | {"% >= 7.0":<10} |')
print('|----------------------------|-------------|-----------|------------|')

sorted_genres = sorted(genre_groups.keys(), key=lambda g: len(genre_groups[g]), reverse=True)
for g in sorted_genres:
    scores = [s for s, r, _ in genre_groups[g]]
    cnt = len(scores)
    mean_s = sum(scores) / cnt
    high_cnt = sum(1 for s in scores if s >= 7.0)
    pct_high = (high_cnt / cnt) * 100
    print(f'| {g:<26} | {cnt:<11} | {mean_s:<9.2f} | {pct_high:<9.2f}% |')

# Top 3 genres combined share
top3_count = sum(len(genre_groups[g]) for g in sorted_genres[:3])
top3_share = (top3_count / total_titles) * 100
print(f'\nTop 3 genres ({sorted_genres[0]}, {sorted_genres[1]}, {sorted_genres[2]}):')
print(f'Count = {top3_count}, Share = {top3_share:.2f}% ({top3_count}/{total_titles})')

# English + Hindi + Spanish combined share
eng_count = sum(1 for t in titles if t['primary_language'] == 'English')
spa_count = sum(1 for t in titles if t['primary_language'] == 'Spanish')
hin_count = sum(1 for t in titles if t['primary_language'] == 'Hindi')
top3_lang_count = eng_count + spa_count + hin_count
top3_lang_share = (top3_lang_count / total_titles) * 100
print(f'\nEnglish ({eng_count}) + Hindi ({hin_count}) + Spanish ({spa_count}):')
print(f'Count = {top3_lang_count}, Share = {top3_lang_share:.2f}% ({top3_lang_count}/{total_titles})')

# Runtime outliers (short < 53, epic > 141)
short_runtime = [t for t in titles if float(t['runtime']) < 53]
epic_runtime = [t for t in titles if float(t['runtime']) > 141]
print(f'\nRuntime outliers: Short (<53) = {len(short_runtime)}, Epic (>141) = {len(epic_runtime)}')
print('Epic runtime titles:')
for t in sorted(epic_runtime, key=lambda x: float(x['runtime']), reverse=True):
    print(f'  - "{t["title"]}": runtime = {t["runtime"]} min, score = {t["imdb_score"]}, genre = {t["genre_group"]}')

# Score outliers (low < 3.75, high > 8.95)
low_score = [t for t in titles if float(t['imdb_score']) < 3.75]
high_score = [t for t in titles if float(t['imdb_score']) > 8.95]
print(f'\nScore outliers: Low (<3.75) = {len(low_score)}, High (>8.95) = {len(high_score)}')
print('Low score titles:')
for t in sorted(low_score, key=lambda x: float(x['imdb_score'])):
    print(f'  - "{t["title"]}": score = {t["imdb_score"]}, runtime = {t["runtime"]} min, genre = {t["genre_group"]}')
print('High score titles:')
for t in sorted(high_score, key=lambda x: float(x['imdb_score']), reverse=True):
    print(f'  - "{t["title"]}": score = {t["imdb_score"]}, runtime = {t["runtime"]} min, genre = {t["genre_group"]}')

# Overlapping outliers
overlap = [t for t in titles if (float(t['runtime']) < 53 or float(t['runtime']) > 141) and (float(t['imdb_score']) < 3.75 or float(t['imdb_score']) > 8.95)]
print(f'\nOverlapping outliers count: {len(overlap)}')
for t in overlap:
    print(f'  - "{t["title"]}": runtime = {t["runtime"]} min, score = {t["imdb_score"]}')
