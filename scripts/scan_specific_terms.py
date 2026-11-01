import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

terms = [
    'Skill', 'Skills', 'Floor', 'Chef', 'Deviant', 'Heartless', 
    'Spacetime Manipulation', 'Shadow Motion', 'Dark Flame', 
    'Cast Cancel', 'Boss'
]

findings = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    vol_num = f.split('vol-')[-1].replace('.json', '')
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    for c_idx, ch in enumerate(chapters):
        ch_title = ch.get('title', f'Capítulo {c_idx}')
        paras = ch.get('paragraphs', [])
        for p_idx, p in enumerate(paras):
            for t in terms:
                # word boundary match
                if re.search(r'\b' + re.escape(t) + r'\b', p):
                    findings.append({
                        'file': f,
                        'volume': vol_num,
                        'chapter': ch_title,
                        'p_idx': p_idx,
                        'term': t,
                        'text': p
                    })

print(f"Total findings for checked terms: {len(findings)}")
with open('findings_terms.json', 'w', encoding='utf-8') as out:
    json.dump(findings, out, ensure_ascii=False, indent=2)

# Print a summary count by term
from collections import Counter
counts = Counter(f['term'] for f in findings)
print("Counts by term:", counts)
