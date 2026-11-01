import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

standalone_pattern = re.compile(
    r'^\s*[\(\[]\s*(?:N/?T|Nota\s+do\s+Tradutor|Nota\s+do\s+Revisor|Item ganho: ingresso)',
    re.IGNORECASE
)

inline_gems = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    for c_idx, ch in enumerate(chapters):
        paras = ch.get('paragraphs', [])
        for p_idx, p in enumerate(paras):
            if standalone_pattern.match(p) or p.strip().startswith('*(NT'):
                continue
            # Search for inline suspect patterns
            matches = re.finditer(r'(\([^\)]*?(?:NT|N/T|kkk+|ksks+|kakak+|jkk+|fodase|pqp|poha|fdp|si fudeu|sifude|safado|burro)[^\)]*?\))', p, re.IGNORECASE)
            for m in matches:
                inline_gems.append({
                    'file': f,
                    'chapter': ch.get('title'),
                    'p_idx': p_idx,
                    'snippet': m.group(0),
                    'paragraph': p
                })

print(f"Total other inline gems found: {len(inline_gems)}")
for g in inline_gems:
    print(f"[{g['file']} - {g['chapter']}] {g['snippet']}")
    print(f"   FULL: {g['paragraph']}")
