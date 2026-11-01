import json
import re

with open('all_skill_paragraphs.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

for i, it in enumerate(items):
    t = it['text']
    # highlight where Skill occurs
    matches = re.findall(r'(\S*\s*\S*\s*\bSkills?\b\s*\S*\s*\S*)', t)
    print(f"[{it['volume']} | {it['chapter'][:25]}] {matches}")
