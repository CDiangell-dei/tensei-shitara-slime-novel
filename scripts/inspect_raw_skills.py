import glob
import json
import re

files = [
    'data/light_novel/vol-9.json',
    'data/light_novel/vol-10.json',
    'data/light_novel/vol-11.json',
    'data/light_novel/vol-12.json',
    'data/light_novel/vol-13.json',
    'data/light_novel/vol-14.json',
    'data/light_novel/vol-15.json',
    'data/light_novel/vol-16.json',
    'data/light_novel/vol-18.json',
]

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    # find all occurrences of Skill or Skills
    matches = re.finditer(r'([^\.\n\?!]*?\bSkills?\b[^\.\n\?!]*)', c)
    print(f"=== {f} ===")
    seen = set()
    for m in matches:
        snippet = m.group(1).strip()
        if snippet not in seen:
            seen.add(snippet)
            print("  *", snippet[:140])
