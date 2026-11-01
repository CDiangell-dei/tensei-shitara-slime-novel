import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

patterns = [
    r'\([^\)]*?(?:kkk+|rsrs+|ksks+|kakak+|jkk+)[^\)]*?\)',
    r'\([^\)]*?(?:fodase|pqp|poha|carai|seloco|stonks|press f|fetiche|lolicon|porra nem uma)[^\)]*?\)',
    r'\([^\)]*?mo fdp[^\)]*?\)',
    r'\([^\)]*?sifude[^\)]*?\)',
    r'\([^\)]*?si fudeu[^\)]*?\)',
    r'\([^\)]*?best waifu[^\)]*?\)',
    r'\(inocente kkkk\)',
    r'\(NT:.*?\)',
    r'\(N/T:.*?\)',
    r'\(NT Tradutor.*?\)',
    r'\(NT \(tradutor\).*?\)',
    r'\*\(NT.*?\)',
]

all_hits = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    for pat in patterns:
        for m in re.finditer(pat, c, re.IGNORECASE):
            all_hits.append({
                'file': f,
                'pattern': pat,
                'text': m.group(0)
            })

# Deduplicate
seen = set()
unique_hits = []
for h in all_hits:
    key = (h['file'], h['text'])
    if key not in seen:
        seen.add(key)
        unique_hits.append(h)

print(f"Total unique hits across patterns: {len(unique_hits)}")
for h in unique_hits[:40]:
    print(f"[{h['file']}] {h['text'][:90]}")
