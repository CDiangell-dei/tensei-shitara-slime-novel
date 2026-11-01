import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

standalone_pattern = re.compile(
    r'^\s*[\(\[]\s*(?:N/?T|Nota\s+do\s+Tradutor|Nota\s+do\s+Revisor|Item ganho: ingresso)',
    re.IGNORECASE
)

suspect_regex = re.compile(
    r'(\([^\)]*?\b(?:NT|N/T|kkk+|ksks+|kakak+|jkk+|fodase|pqp|poha|fdp|si fudeu|sifude)\b[^\)]*?\))',
    re.IGNORECASE
)

hits = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    for c_idx, ch in enumerate(chapters):
        paras = ch.get('paragraphs', [])
        for p_idx, p in enumerate(paras):
            if standalone_pattern.match(p) or p.strip().startswith('*(NT'):
                continue
            for m in suspect_regex.finditer(p):
                hits.append({
                    'file': f,
                    'chapter': ch.get('title'),
                    'p_idx': p_idx,
                    'snippet': m.group(0),
                    'paragraph': p
                })

print(f"Truly suspect inline notes: {len(hits)}")
for h in hits:
    print(f"[{h['file']} - {h['chapter']}] {h['snippet']}")
    print(f"   FULL: {h['paragraph']}")
