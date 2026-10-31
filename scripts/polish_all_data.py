"""
POLIMENTO E PADRONIZAÇÃO EM LOTE DE TODA A BIBLIOTECA (LN + WN)
Aplica o motor idempotente fix_translation.py sobre todos os JSONs em data/light_novel/ e data/web_novel/.
"""

import glob
import json
from fix_translation import correct_text_block


def polish_json_quiet(path: str) -> int:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changed = 0
    if 'title' in data and isinstance(data['title'], str):
        nt = correct_text_block(data['title'])
        if nt != data['title']:
            data['title'] = nt
            changed += 1

    if 'paragraphs' in data:
        new_p = []
        for p in data['paragraphs']:
            np = correct_text_block(p)
            if np != p:
                changed += 1
            new_p.append(np)
        data['paragraphs'] = new_p

    if 'chapters' in data:
        for ch in data['chapters']:
            if 'title' in ch and isinstance(ch['title'], str):
                nt = correct_text_block(ch['title'])
                if nt != ch['title']:
                    ch['title'] = nt
                    changed += 1
            if 'paragraphs' in ch:
                new_cp = []
                for p in ch['paragraphs']:
                    np = correct_text_block(p)
                    if np != p:
                        changed += 1
                    new_cp.append(np)
                ch['paragraphs'] = new_cp
            if 'blocks' in ch:
                for b in ch['blocks']:
                    if b.get('type') == 'p' and 'text' in b:
                        nb = correct_text_block(b['text'])
                        if nb != b['text']:
                            b['text'] = nb
                            changed += 1

    if 'footnotes' in data and isinstance(data['footnotes'], dict):
        new_fn = {}
        for k, v in data['footnotes'].items():
            nv = correct_text_block(v)
            if nv != v:
                changed += 1
            new_fn[k] = nv
        data['footnotes'] = new_fn

    if changed > 0:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return changed


def polish_all():
    ln_files = sorted(glob.glob('data/light_novel/*.json'))
    wn_files = sorted(glob.glob('data/web_novel/*.json'))

    ln_changes = sum(polish_json_quiet(p) for p in ln_files)
    wn_changes = sum(polish_json_quiet(p) for p in wn_files)

    print(f"Polimento concluído! LN ({len(ln_files)} arquivos): {ln_changes} ajustes adicionais | "
          f"WN ({len(wn_files)} arquivos): {wn_changes} ajustes aplicados.")


if __name__ == '__main__':
    polish_all()
