import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

all_nt_notes = []

# Pattern to catch all variations of (NT: ...), [NT: ...], (N/T: ...), (Nota: ...), etc.
note_regex = re.compile(r'([\({\[](?:NT|N/T|Nota do Tradutor|Nota da Tradução|Nota do Revisor|Nota Cen|nota Cen|TN|TL)[:\s][^\)}\]]*?[\)}\]])', re.IGNORECASE)

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    
    vol_num = f.split('vol-')[-1].replace('.json', '')
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    
    for c_idx, ch in enumerate(chapters):
        ch_title = ch.get('title', f'Capítulo {c_idx}')
        paras = ch.get('paragraphs', [])
        for p_idx, p in enumerate(paras):
            for m in note_regex.finditer(p):
                note_str = m.group(1)
                all_nt_notes.append({
                    'file': f,
                    'volume': vol_num,
                    'chapter': ch_title,
                    'p_idx': p_idx,
                    'note': note_str,
                    'full_paragraph': p
                })

print(f"Total matching translator notes found in paragraphs: {len(all_nt_notes)}")

# Save to json for analysis
with open('all_translator_notes.json', 'w', encoding='utf-8') as out:
    json.dump(all_nt_notes, out, ensure_ascii=False, indent=2)

# Print summary by volume
from collections import Counter
counts = Counter(n['file'] for n in all_nt_notes)
for f, cnt in sorted(counts.items()):
    print(f"  {f}: {cnt} notes")
