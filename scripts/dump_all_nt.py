import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

all_nt = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    matches = re.finditer(r'(\([^\)]*?N/?T:?[^\)]*?\))', c, re.IGNORECASE)
    for m in matches:
        all_nt.append({
            'file': f,
            'text': m.group(1),
            'start': m.start(),
            'end': m.end()
        })

# Deduplicate
seen = set()
unique_nt = []
for n in all_nt:
    key = (n['file'], n['text'])
    if key not in seen:
        seen.add(key)
        unique_nt.append(n)

print(f"Total unique NT notes: {len(unique_nt)}")

with open('all_unique_nt.json', 'w', encoding='utf-8') as out:
    json.dump(unique_nt, out, ensure_ascii=False, indent=2)

for n in unique_nt:
    print(f"[{n['file']}] {n['text']}")
