import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

standalone_pattern = re.compile(
    r'^\s*[\(\[]\s*(?:N/?T|Nota\s+do\s+Tradutor|Nota\s+do\s+Revisor|Item ganho: ingresso)',
    re.IGNORECASE
)

inline_fixes = [
    ('data/light_novel/vol-2.json', r'\s*\(\s*kkkkkkkkk\s*\)', ''),
    ('data/light_novel/vol-2.json', r'\s*\(\s*wtf kkkkk\s*\)', ''),
    ('data/light_novel/vol-3.json', r'\s*\(\s*inocente kkkk\s*\)', ''),
    ('data/light_novel/vol-3.json', r'\s*\(\s*NT:\s*Só que não\s*\),?', ','),
    ('data/light_novel/vol-8.json', r'\s*\(nota Cen:[^\)]*\)', ''),
    ('data/light_novel/vol-8.json', r'\s*Mas, honestamente, parece muito fora de lugar, ou talvez apenas minha habilidade com o moonrune seja uma merda\. Provavelmente o último\.', ''),
    ('data/light_novel/vol-20.json', r'\s*Haha, petição para adicionar esta palavra ao dicionário de inglês, por favor\.', ''),
]

total_standalone = 0
total_inline = 0
modified_files = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    
    file_modified = False
    vol_standalone = 0
    vol_inline = 0
    
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    for ch in chapters:
        # 1. Paragraphs
        paras = ch.get('paragraphs', [])
        new_paras = []
        for p in paras:
            is_st = standalone_pattern.match(p) or p.strip().startswith('*(NT')
            if is_st:
                vol_standalone += 1
                file_modified = True
            else:
                curr = p
                for tgt_file, pat, rep in inline_fixes:
                    if f.replace('\\', '/') == tgt_file:
                        if re.search(pat, curr):
                            curr = re.sub(pat, rep, curr)
                            vol_inline += 1
                            file_modified = True
                new_paras.append(curr)
        ch['paragraphs'] = new_paras
        
        # 2. Blocks
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
                                file_modified = True
                    b['text'] = curr_b
                    new_blocks.append(b)
                else:
                    file_modified = True
            else:
                new_blocks.append(b)
        ch['blocks'] = new_blocks

    # 3. Footnotes
    if isinstance(data, dict) and 'footnotes' in data:
        for k, v in data['footnotes'].items():
            curr_v = v
            for tgt_file, pat, rep in inline_fixes:
                if f.replace('\\', '/') == tgt_file:
                    if re.search(pat, curr_v):
                        curr_v = re.sub(pat, rep, curr_v)
                        vol_inline += 1
                        file_modified = True
            data['footnotes'][k] = curr_v

    if file_modified:
        modified_files.append(f)
        total_standalone += vol_standalone
        total_inline += vol_inline
        print(f"Saving {f}: removed {vol_standalone} standalone notes, fixed {vol_inline} inline/footnotes")
        with open(f, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

print("\n--- SUMMARY ---")
print(f"Total modified files: {len(modified_files)}")
print(f"Total standalone note paragraphs removed: {total_standalone}")
print(f"Total inline / footnote comments cleaned: {total_inline}")
