import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

standalone_pattern = re.compile(
    r'^\s*[\(\[]\s*(?:N/?T|Nota\s+do\s+Tradutor|Nota\s+do\s+Revisor|Item ganho: ingresso)',
    re.IGNORECASE
)

count_by_file = {}
total_removed = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    vol_removed = 0
    
    for ch in chapters:
        paras = ch.get('paragraphs', [])
        new_paras = []
        for p in paras:
            if standalone_pattern.match(p) or p.strip().startswith('*(NT'):
                vol_removed += 1
            else:
                new_paras.append(p)
    
    if vol_removed > 0:
        count_by_file[f] = vol_removed
        total_removed += vol_removed

print(f"Total standalone note paragraphs to remove: {total_removed}")
for f, cnt in count_by_file.items():
    print(f"  {f}: {cnt}")
