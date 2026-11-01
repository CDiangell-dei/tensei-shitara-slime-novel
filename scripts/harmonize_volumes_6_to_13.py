"""
HARMONIZAÇÃO E FUSÃO EDITORIAL - VOLUMES 6 A 13
Une o melhor da fluidez humana da TSSDK Scan à Edição Ilustrada Revisada de Tensei Shitara Slime,
eliminando calques de tradução do inglês, blindando a terminologia canônica em PT-BR
e preservando 100% dos parágrafos, diálogos, ilustrações oficiais e notas culturais.
"""

import os
import re
import json

HARMONIZATION_RULES = [
    # 1. Calques e gírias literais do inglês presentes na TSSDK Scan
    (r'\bHoo querido\b', 'Nossa, cara'),
    (r'\bOh querido\b', 'Puxa vida'),
    (r'\bquase morri para sempre\b', 'quase bati as botas de vez'),
    (r'\bquase morreu para sempre\b', 'quase bateu as botas de vez'),
    (r'\bjogar de ouvido\b', 'improvisar no momento'),
    (r'\bjogando de ouvido\b', 'improvisando no momento'),
    (r'\bIsso pode realmente ser ajudado\?', 'Tem mesmo jeito?'),
    (r'\bisso pode realmente ser ajudado\?', 'tem mesmo jeito?'),
    (r'\bNão pode ser ajudado\b', 'Não há o que fazer'),
    (r'\bnão pode ser ajudado\b', 'não há o que fazer'),
    (r'\bO gol de um santo\b', 'O Objetivo de um Santo'),
    (r'\bo gol de um santo\b', 'o objetivo de um santo'),

    # 2. Termos do sistema de poder deixados em inglês
    (r'\bUltimate Skills\b', 'Habilidades Supremas'),
    (r'\bUltimate Skill\b', 'Habilidade Suprema'),
    (r'\bUnique Skills\b', 'Habilidades Únicas'),
    (r'\bUnique Skill\b', 'Habilidade Única'),
    (r'\bExtra Skills\b', 'Habilidades Extras'),
    (r'\bExtra Skill\b', 'Habilidade Extra'),
    (r'\bDemon Lords\b', 'Lordes Demônios'),
    (r'\bDemon Lord\b', 'Lorde Demônio'),
    (r'\bTrue Dragons\b', 'Dragões Verdadeiros'),
    (r'\bTrue Dragon\b', 'Dragão Verdadeiro'),
    (r'\bMagicules\b', 'Magículas'),
    (r'\bMagicule\b', 'Magícula'),
    (r'\bVoice of the World\b', 'Voz do Mundo'),
    (r'\bOctagram\b', 'Octagrama'),
    (r'\bSoul Corridor\b', 'Corredor da Alma'),
    (r'\bThought Acceleration\b', 'Aceleração do Pensamento'),
    (r'\bParallel Operation\b', 'Operação Paralela'),
    (r'\bChant Annulment\b', 'Anulação de Canto'),
    (r'\bAll of Creation\b', 'Compreensão de Toda a Criação'),
    (r'\bGreat Sage\b', 'Grande Sábio'),
    (r'\bLord of Wisdom\b', 'Rei da Sabedoria'),
    (r'\bWisdom King\b', 'Rei da Sabedoria'),

    # 3. Nomes próprios e títulos
    (r'\bCara Carmesim\b', 'Guy Crimson'),
    (r'\bFusível\b', 'Fuse'),
    (r'\bCampo de golfe\b', 'Feldway'),
    (r'\bCampo de Golfe\b', 'Feldway'),
    (r'\bLacaio\b', 'Footman'),
    (r'\bTeare\b', 'Tear'),
    (r'\bZegião\b', 'Zegion'),

    # 4. Concordância das Primordiais
    (r'\bPrimordial Branco\b', 'Primordial Branca'),
    (r'\bPrimordial Amarelo\b', 'Primordial Amarela'),
    (r'\bPrimordial Roxo\b', 'Primordial Violeta'),
    (r'\bPrimordial Preto\b', 'Primordial Negro'),

    # 5. Habilidades Supremas nomeadas
    (r'\bGluttonous King Beelzebuth\b', 'Rei da Gula Beelzebuth'),
    (r'\bCovenant King Uriel\b', 'Rei do Pacto Uriel'),
    (r'\bStorm King Veldora\b', 'Rei da Tempestade Veldora'),
    (r'\bScorch King Velgrynd\b', 'Rei Escaldante Velgrynd'),
    (r'\bInvestigation King Faust\b', 'Rei da Investigação Faust'),
    (r'\bExecutioner Sandalphon\b', 'Executor Sandalphon'),
    (r'\bJustice King Michael\b', 'Rei da Justiça Michael'),
    (r'\bHope King Sariel\b', 'Rei da Esperança Sariel'),
    (r'\bPurity King Metatron\b', 'Rei da Pureza Metatron'),
    (r'\bPatience King Gabriel\b', 'Rei da Paciência Gabriel'),
    (r'\bWrath King Satanael\b', 'Rei da Ira Satanael'),
    (r'\bGreedy King Mammon\b', 'Rei da Ganância Mammon'),
    (r'\bLustful King Asmodeus\b', 'Rei da Luxúria Asmodeus'),
    (r'\bSloth King Belphegor\b', 'Rei da Preguiça Belphegor'),
    (r'\bEnvy King Leviathan\b', 'Rei da Inveja Leviatã'),
    (r'\bPride King Lucifer\b', 'Rei do Orgulho Lúcifer')
]

def harmonize_text(text: str) -> str:
    if not text:
        return text
    result = text
    for pattern, replacement in HARMONIZATION_RULES:
        result = re.sub(pattern, replacement, result)
    return result

def harmonize_volume_file(filepath: str, is_scan: bool = False) -> int:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changed_count = 0

    if 'edition' in data:
        if is_scan:
            data['edition'] = 'Tradução de Fã TSSDK Scan (Revisada & Polida)'
        else:
            data['edition'] = 'Edição Ilustrada Revisada & Harmonizada (PT-BR)'

    if 'title' in data and isinstance(data['title'], str):
        new_title = harmonize_text(data['title'])
        if new_title != data['title']:
            data['title'] = new_title
            changed_count += 1

    if 'chapters' in data:
        for ch in data['chapters']:
            if 'title' in ch and isinstance(ch['title'], str):
                new_ch_title = harmonize_text(ch['title'])
                if new_ch_title != ch['title']:
                    ch['title'] = new_ch_title
                    changed_count += 1

            if 'paragraphs' in ch and isinstance(ch['paragraphs'], list):
                new_paras = []
                for p in ch['paragraphs']:
                    new_p = harmonize_text(p)
                    if new_p != p:
                        changed_count += 1
                    new_paras.append(new_p)
                ch['paragraphs'] = new_paras

            if 'blocks' in ch and isinstance(ch['blocks'], list):
                for b in ch['blocks']:
                    if b.get('type') == 'p' and 'text' in b:
                        new_bt = harmonize_text(b['text'])
                        if new_bt != b['text']:
                            b['text'] = new_bt
                            changed_count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return changed_count

def main():
    print("=== INICIANDO HARMONIZAÇÃO DOS VOLUMES 6 A 13 ===")
    total_rev_changes = 0
    total_scan_changes = 0

    for v in range(6, 14):
        f_rev = f"data/light_novel/vol-{v}.json"
        f_scan = f"data/light_novel/vol-{v}-scan.json"

        if os.path.exists(f_rev):
            c_rev = harmonize_volume_file(f_rev, is_scan=False)
            total_rev_changes += c_rev
            print(f"Volume {v} (Edição Ilustrada Revisada): {c_rev} parágrafos/títulos harmonizados.")

        if os.path.exists(f_scan):
            c_scan = harmonize_volume_file(f_scan, is_scan=True)
            total_scan_changes += c_scan
            print(f"Volume {v} (TSSDK Scan): {c_scan} parágrafos/títulos harmonizados.")

    print(f"\nTotal harmonizado na Edição Revisada: {total_rev_changes}")
    print(f"Total harmonizado na TSSDK Scan: {total_scan_changes}")
    print("=== HARMONIZAÇÃO CONCLUÍDA COM SUCESSO! ===")

if __name__ == '__main__':
    main()
