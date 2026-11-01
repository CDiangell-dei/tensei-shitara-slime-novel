import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

all_skill_sentences = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    vol_num = f.split('vol-')[-1].replace('.json', '')
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    for c_idx, ch in enumerate(chapters):
        ch_title = ch.get('title', f'Capítulo {c_idx}')
        paras = ch.get('paragraphs', [])
        for p_idx, p in enumerate(paras):
            if re.search(r'\bSkills?\b', p):
                all_skill_sentences.append({
                    'file': f,
                    'volume': vol_num,
                    'chapter': ch_title,
                    'p_idx': p_idx,
                    'text': p
                })

print(f"Total paragraphs with Skill/Skills: {len(all_skill_sentences)}")
with open('all_skill_paragraphs.json', 'w', encoding='utf-8') as out:
    json.dump(all_skill_sentences, out, ensure_ascii=False, indent=2)
