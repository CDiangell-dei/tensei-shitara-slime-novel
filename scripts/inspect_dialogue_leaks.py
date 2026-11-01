import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

dialogue_english_patterns = [
    (r'\bMy\s+[A-Za-zÀ-ÿ]+', 'My ...'),
    (r'\bYour\s+[A-Za-zÀ-ÿ]+', 'Your ...'),
    (r'\bHis\s+[A-Za-zÀ-ÿ]+', 'His ...'),
    (r'\bHer\s+[A-Za-zÀ-ÿ]+', 'Her ...'),
    (r'\bOur\s+[A-Za-zÀ-ÿ]+', 'Our ...'),
    (r'\bTheir\s+[A-Za-zÀ-ÿ]+', 'Their ...'),
    (r'["“«]\s*(?:Hey|Yeah|Wait|No way|Shut up|Please|Look|Listen|Come on|Let\'s go|Good luck|Thank you|Thanks|Sorry|Nevermind)[\s,\.!\?]', 'English dialogue start'),
    (r'\b(?:Oh my God|Oh my gosh|What the heck|What the hell|Holy shit|God damn)\b', 'English exclamation'),
]

leaks = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    for pat, desc in dialogue_english_patterns:
        for m in re.finditer(pat, c, re.IGNORECASE):
            match_str = m.group(0)
            # Filter out false positives
            # e.g., 'Hero' might match something, or 'Herói' matching 'Her'
            if desc.startswith('Her ') and re.match(r'Her[óo]', match_str, re.IGNORECASE):
                continue
            # Get surrounding context
            start = max(0, m.start() - 30)
            end = min(len(c), m.end() + 30)
            context = c[start:end].replace('\n', ' ')
            leaks.append((f, desc, match_str, context))

print(f"Total potential leaks found: {len(leaks)}")
# Print distinct samples
seen = set()
for f, desc, match_str, context in leaks:
    key = (desc, match_str.strip())
    if key not in seen:
        seen.add(key)
        print(f"{f} [{desc}] '{match_str.strip()}' --> {context.strip()}")
