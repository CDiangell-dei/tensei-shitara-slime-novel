import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

nt_notes = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    # Let's search for inline notes in paragraphs
    matches = re.finditer(r'(\([^\)]*?(?:NT|N/T|Nota|Tradutor|Revisor)[^\)]*?\))', c, re.IGNORECASE)
    for m in matches:
        note_text = m.group(1)
        # get surrounding context
        start = max(0, m.start() - 60)
        end = min(len(c), m.end() + 60)
        context = c[start:end].replace('\n', ' ')
        nt_notes.append({
            'file': f,
            'note': note_text,
            'context': context
        })

print(f"Total inline notes found: {len(nt_notes)}")

# Let's write them to a json file to inspect
with open('inline_nt_notes.json', 'w', encoding='utf-8') as out:
    json.dump(nt_notes, out, ensure_ascii=False, indent=2)

# Print a breakdown by volume
from collections import Counter
by_file = Counter(n['file'] for n in nt_notes)
for f, cnt in sorted(by_file.items()):
    print(f"{f}: {cnt} notes")
