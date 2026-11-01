"""
CORREÇÃO GERAL DE CALQUES E PADRONIZAÇÃO DE NOMES CANÔNICOS
Aplica correções nos 24 volumes da Light Novel:
- Padronização de "Dinastia Feiticeira de Sarion"
- "Santa Igreja Ocidental"
- "Reino Armado de Dwargon"
- "Reino das Feras Eurazânia"
- "Lorde Demônio" e "Dez Grandes Lordes Demônios"
- "Majin" (em substituição a "Nascido na magia")
- Expressões idiomáticas naturais ("uma gota no oceano", "no fim das contas", "agir de improviso", "Puxa vida", "Ora, vejam só")
"""

import os
import glob
import json
import re

REPLACEMENTS = [
    # 1. Sarion e Reinos
    (r'(?i)\b(?:do\s+)?Sarion\s+da\s+Dinastia\s+do\s+Feiticeiro\b', 'da Dinastia Feiticeira de Sarion'),
    (r'(?i)\bo\s+Sarion\s+da\s+Dinastia\s+do\s+Feiticeiro\b', 'a Dinastia Feiticeira de Sarion'),
    (r'(?i)\bSarion\s+da\s+Dinastia\s+do\s+Feiticeiro\b', 'Dinastia Feiticeira de Sarion'),
    (r'(?i)\ba\s+Dinastia\s+do\s+Feiticeiro\s+Sarion\b', 'a Dinastia Feiticeira de Sarion'),
    (r'(?i)\bda\s+Dinastia\s+do\s+Feiticeiro\s+Sarion\b', 'da Dinastia Feiticeira de Sarion'),
    (r'(?i)\bna\s+Dinastia\s+do\s+Feiticeiro\s+Sarion\b', 'na Dinastia Feiticeira de Sarion'),
    (r'(?i)\bà\s+Dinastia\s+do\s+Feiticeiro\s+Sarion\b', 'à Dinastia Feiticeira de Sarion'),
    (r'(?i)\bpela\s+Dinastia\s+do\s+Feiticeiro\s+Sarion\b', 'pela Dinastia Feiticeira de Sarion'),
    (r'(?i)\bDinastia\s+do\s+Feiticeiro\s+Sarion\b', 'Dinastia Feiticeira de Sarion'),
    (r'(?i)\bDinastia\s+do\s+Feiticeiro\b', 'Dinastia Feiticeira'),

    (r'\bReino\s+Blindado\s+Dwargon\b', 'Reino Armado de Dwargon'),
    (r'\bReino\s+das\s+Bestas\s+Eurazânia\b', 'Reino das Feras Eurazânia'),
    (r'\bIgreja\s+Sagrada\s+Ocidental\b', 'Santa Igreja Ocidental'),

    # 2. Títulos e Raças
    (r'\bDez\s+Grandes\s+Senhores\s+Demônios\b', 'Dez Grandes Lordes Demônios'),
    (r'\bSenhores\s+Demônios\b', 'Lordes Demônios'),
    (r'\bSenhor\s+Demônio\b', 'Lorde Demônio'),
    (r'\bHumano\?\s+Nascido\s+na\s+magia\?', 'Humano? Majin?'),
    (r'\bNascidos\s+na\s+magia\b', 'Majins'),
    (r'\bNascido\s+na\s+magia\b', 'Majin'),
    (r'\bNascido\s+na\s+Magia\b', 'Majin'),

    # 3. Expressões e Calques do Inglês
    (r'\buma\s+gota\s+no\s+balde\b', 'uma gota no oceano'),
    (r'\btocar\s+de\s+ouvido\b', 'agir de improviso'),
    (r'\bHoo\s+querido\b', 'Nossa, cara'),
    (r'\bquase\s+morre(?:u|i)\s+para\s+sempre\b', 'quase morri de vez'),

    # "Oh querido" adaptado ao falante
    (r'Kufufufu\.\.\.\s*Oh\s+querido,?\s*', 'Kufufufu... Ora, ora, '),
    (r'“Oh\s+querido,?\s*Rimuru-Sama\b', '“Nossa, Rimuru-Sama'),
    (r'“Oh\s+querido,?\s*o\s+tempo\s+acabou\b', '“Puxa vida, o tempo acabou'),
    (r'“Oh\s+querido…\s*ainda\s+tenho\b', '“Puxa vida… ainda tenho'),
    (r'\"Oh\s+querido\.?\s*Todos\s+vocês\b', '\"Ora, vejam só. Todos vocês'),
    (r'\bOh\s+querido\b', 'Puxa vida'),

    # "no final do dia" -> contexto
    (r'a\s+assumir\s+alguma\s+responsabilidade,\s*no\s+final\s+do\s+dia\.', 'a assumir alguma responsabilidade, no fim das contas.'),
    (r'arrumar\s+os\s+lençóis\s+no\s+final\s+do\s+dia\.', 'arrumar os lençóis ao final da tarde.'),
    (r'fardo\s+muito\s+pesado\s+para\s+ela\s+no\s+final\s+do\s+dia\.', 'fardo muito pesado para ela, no fim das contas.'),
    (r'\bno\s+final\s+do\s+dia\b', 'no fim das contas'),
]

def clean_text(text: str) -> str:
    if not text:
        return text
    result = text
    for pat, rep in REPLACEMENTS:
        result = re.sub(pat, rep, result)
    return result

def main():
    files = sorted(glob.glob('data/light_novel/*.json'))
    total_files_changed = 0
    total_items_changed = 0

    print("=== EXECUTANDO CORREÇÃO GERAL DE TERMOS E CALQUES ===")

    for fn in files:
        with open(fn, 'r', encoding='utf-8') as f:
            data = json.load(f)

        file_changed = False
        file_items = 0

        # Title
        if 'title' in data and isinstance(data['title'], str):
            nt = clean_text(data['title'])
            if nt != data['title']:
                data['title'] = nt
                file_items += 1
                file_changed = True

        # Chapters
        if 'chapters' in data:
            for ch in data['chapters']:
                if 'title' in ch and isinstance(ch['title'], str):
                    nt = clean_text(ch['title'])
                    if nt != ch['title']:
                        ch['title'] = nt
                        file_items += 1
                        file_changed = True

                if 'paragraphs' in ch and isinstance(ch['paragraphs'], list):
                    new_p = []
                    for p in ch['paragraphs']:
                        np = clean_text(p)
                        if np != p:
                            file_items += 1
                            file_changed = True
                        new_p.append(np)
                    ch['paragraphs'] = new_p

                if 'blocks' in ch and isinstance(ch['blocks'], list):
                    for b in ch['blocks']:
                        if b.get('type') == 'p' and 'text' in b:
                            nbt = clean_text(b['text'])
                            if nbt != b['text']:
                                b['text'] = nbt
                                file_items += 1
                                file_changed = True

        if file_changed:
            with open(fn, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            total_files_changed += 1
            total_items_changed += file_items
            print(f"✓ {os.path.basename(fn)}: {file_items} alterações aplicadas.")

    print(f"\n==========================================")
    print(f"Total de arquivos corrigidos: {total_files_changed}")
    print(f"Total de parágrafos/títulos ajustados: {total_items_changed}")
    print(f"==========================================")

if __name__ == '__main__':
    main()
