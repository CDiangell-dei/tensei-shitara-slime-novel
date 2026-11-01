import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

standalone_pattern = re.compile(
    r'^\s*[\(\[]\s*(?:N/?T|Nota\s+do\s+Tradutor|Nota\s+do\s+Revisor|Item ganho: ingresso)',
    re.IGNORECASE
)

# Inline fixes: (file, regex, replacement)
inline_fixes = [
    ('data/light_novel/vol-2.json', r'\s*\(\s*kkkkkkkkk\s*\)', ''),
    ('data/light_novel/vol-2.json', r'\s*\(\s*wtf kkkkk\s*\)', ''),
    ('data/light_novel/vol-3.json', r'\s*\(\s*inocente kkkk\s*\)', ''),
    ('data/light_novel/vol-3.json', r'\s*\(\s*NT:\s*Só que não\s*\),?', ','),
    ('data/light_novel/vol-8.json', r'\s*\(nota Cen:[^\)]*\)', ''),
    ('data/light_novel/vol-8.json', r'\s*Mas, honestamente, parece muito fora de lugar, ou talvez apenas minha habilidade com o moonrune seja uma merda\. Provavelmente o último\.', ''),
    ('data/light_novel/vol-20.json', r'\s*Haha, petição para adicionar esta palavra ao dicionário de inglês, por favor\.', ''),
]

total_standalone_removed = 0
total_inline_fixed = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    
    vol_standalone = 0
    vol_inline = 0
    
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    for ch in chapters:
        paras = ch.get('paragraphs', [])
        new_paras = []
        for p in paras:
            is_st = standalone_pattern.match(p) or p.strip().startswith('*(NT')
            if is_st:
                vol_standalone += 1
            else:
                curr = p
                for tgt_file, pat, rep in inline_fixes:
                    if f.replace('\\', '/') == tgt_file:
                        if re.search(pat, curr):
                            curr = re.sub(pat, rep, curr)
                            vol_inline += 1
                new_paras.append(curr)
        
        # Also check blocks
        blocks = ch.get('blocks', [])
        new_blocks = []
        for b in blocks:
            if isinstance(b, dict) and 'text' in b and isinstance(b['text'], str):
                b_text = b['text']
                is_st = standalone_pattern.match(b_text) or b_text.strip().startswith('*(NT')
                if not is_st:
                    curr_b = b_text
                    for tgt_file, pat, rep in inline_fixes:
                        if f.replace('\\', '/') == tgt_file:
                            if re.search(pat, curr_b):
                                curr_b = re.sub(pat, rep, curr_b)
                    b['text'] = curr_b
                    new_blocks.append(b)
            else:
                new_blocks.append(b)

    # Footnotes check for vol-8 and vol-20
    if isinstance(data, dict) and 'footnotes' in data:
        for k, v in data['footnotes'].items():
            curr_v = v
            for tgt_file, pat, rep in inline_fixes:
                if f.replace('\\', '/') == tgt_file:
                    if re.search(pat, curr_v):
                        curr_v = re.sub(pat, rep, curr_v)
                        vol_inline += 1
            data['footnotes'][k] = curr_v

    if vol_standalone > 0 or vol_inline > 0:
        print(f"{f}: removed {vol_standalone} standalone notes, fixed {vol_inline} inline/footnotes")
        total_standalone_removed += vol_standalone
        total_inline_fixed += vol_inline

print(f"Total standalone removed: {total_standalone_removed}")
print(f"Total inline/footnotes fixed: {total_inline_fixed}")
