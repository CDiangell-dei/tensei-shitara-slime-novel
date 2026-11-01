import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

patterns = [
    (r'\b(?:Hey|hey)\b(?!\s+(?:Crimson|da\s+noite))', 'Ei'),
    (r'\b(?:Yeah|yeah)\b', 'Sim'),
    (r'["“«]\s*Wait[!\?,\.]', 'Espere'),
    (r'["“«]\s*What\?+["”»]', 'O quê?'),
    (r'["“«]\s*Why\?+["”»]', 'Por quê?'),
    (r'\bNevermind\b', 'Deixa para lá'),
    (r'\bCome on\b', 'Vamos lá'),
    (r'\bOh my [Gg]od\b', 'Ai meu Deus'),
]

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    hits = []
    for pat, rep in patterns:
        matches = list(re.finditer(pat, c))
        if matches:
            hits.append((pat, rep, len(matches)))
    if hits:
        print(f, hits)
