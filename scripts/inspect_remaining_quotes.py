import json
import re

targets = [
    ('data/light_novel/vol-15.json', ['Azure Dragon', 'Gale-Thunder Supreme']),
    ('data/light_novel/vol-19.json', ['Dead End Rainbow', 'Thousand-Hand Shadow Kill', 'Thunder Rain']),
    ('data/light_novel/vol-2.json', ['skill']),
    ('data/light_novel/vol-22.json', ['Dark Elf', 'Dragon Nova', 'Moon Goddess Sword', 'Surya', 'Indra', 'Vayu', 'World']),
    ('data/light_novel/vol-23.json', ['Dragon Demon Blade']),
    ('data/light_novel/vol-6.json', ['Curse King', 'Domination Heart']),
    ('data/light_novel/vol-7.json', ['Trinity Break']),
    ('data/light_novel/vol-8.json', ['Dark Alley', 'Elemental Dragon', 'Gourmet', 'Master Access', 'Spirit Dragon', 'Sword Devil']),
    ('data/light_novel/vol-9.json', ['Gourmet']),
]

for f, words in targets:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    print(f"=== {f} ===")
    for w in words:
        for m in re.finditer(r'.{0,40}' + re.escape(w) + r'.{0,40}', c):
            print(f"  [{w}] -> {m.group(0).strip()}")
