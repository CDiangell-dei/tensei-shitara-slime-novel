import glob
import os
import re

PATTERNS = [
    # 1. Sarion e Reinos
    (r'(?:do\s+|da\s+|o\s+|a\s+)?Sarion\s+da\s+Dinastia\s+do\s+Feiticeiro', 'Sarion da Dinastia do Feiticeiro'),
    (r'(?:(?:da|a)\s+)?Dinastia\s+do\s+Feiticeiro(?:\s+Sarion)?', 'Dinastia do Feiticeiro (sem Feiticeira de Sarion)'),
    (r'\bReino\s+Blindado\s+(?:de\s+)?Dwargon\b', 'Reino Blindado Dwargon'),
    (r'\bReino\s+Armado\s+Dwargon\b', 'Reino Armado Dwargon (sem "de")'),
    (r'\bNação\s+Armada\s+Dwargon\b', 'Nação Armada Dwargon (sem "de")'),
    (r'\bFederação\s+da\s+Tempestade\s+(?:de\s+)?Jura\b', 'Federação da Tempestade de Jura'),
    (r'\bImpério\s+Sagrado\s+(?:de\s+)?(?:Lubelius|Ruberios)\b', 'Império Sagrado Lubelius/Ruberios'),
    (r'\bIgreja\s+Sagrada\s+Ocidental\b', 'Igreja Sagrada Ocidental (vs Santa Igreja Ocidental)'),
    (r'\bIgreja\s+Ocidental\s+Sagrada\b', 'Igreja Ocidental Sagrada'),
    (r'\bReino\s+das\s+Bestas\s+Eurazânia\b', 'Reino das Bestas Eurazânia (vs Reino das Feras)'),

    # 2. Calques idiomáticos do inglês
    (r'\bHoo\s+querido\b', 'Hoo querido (Hoo boy)'),
    (r'\bOh\s+querido\b', 'Oh querido (Oh dear)'),
    (r'\b[Qq]uase\s+morre(?:u|i)\s+para\s+sempre\b', 'quase morreu para sempre (died for good)'),
    (r'\bjoga(?:ndo|r)\s+de\s+ouvido\b', 'jogar de ouvido (play by ear)'),
    (r'\btoca(?:ndo|r)\s+de\s+ouvido\b', 'tocar de ouvido (play by ear em contexto não musical)'),
    (r'\b[Ii]sso\s+pode\s+realmente\s+ser\s+ajudado\b', 'isso pode realmente ser ajudado (can it be helped)'),
    (r'\b[Nn]ão\s+pode\s+ser\s+ajudado\b', 'não pode ser ajudado (can\'t be helped)'),
    (r'\b[Oo]\s+gol\s+de\s+um\s+santo\b', 'o gol de um santo (goal of a saint)'),
    (r'\bfotografar\s+com\s+armas\b', 'fotografar com armas (shooting with guns)'),
    (r'\bsalvar\s+o\s+rosto\b', 'salvar o rosto (save face)'),
    (r'\bperder\s+a\s+cara\b', 'perder a cara (lose face)'),
    (r'\bfora\s+da\s+pergunta\b', 'fora da pergunta (out of the question)'),
    (r'\bfora\s+da\s+questão\b', 'fora da questão (out of the question)'),
    (r'\buma\s+gota\s+no\s+balde\b', 'uma gota no balde (drop in the bucket)'),
    (r'\bfazer\s+senso\b', 'fazer senso (make sense)'),
    (r'\btomar\s+(?:isso\s+)?por\s+garantido\b', 'tomar por garantido (take for granted)'),
    (r'\bno\s+final\s+do\s+dia\b', 'no final do dia (at the end of the day)'),

    # 3. Termos e Classes
    (r'\bNascidos?\s+na\s+[Mm]agia\b', 'Nascido na Magia (Majin)'),
    (r'\bPar\s+Demônio\b', 'Par Demônio (Par Demoníaco)'),
    (r'\bClassificação\s+de\s+Contagem\b', 'Classificação de Contagem (Classe Conde)'),
    (r'\bNove\s+Caldas\b', 'Nove Caldas (Nove Caudas)'),
    (r'\bSenhor\s+Demônio\b', 'Senhor Demônio (vs Lorde Demônio)'),
    (r'\bDez\s+Grandes\s+Senhores\s+Demônios\b', 'Dez Grandes Senhores Demônios'),
    (r'\bDragões\s+Reais\b', 'Dragões Reais (vs Dragões Verdadeiros)'),
    (r'\bDragão\s+Real\b', 'Dragão Real (vs Dragão Verdadeiro)'),
    (r'\bSete\s+Sábios\s+Celestiais\b', 'Sete Sábios Celestiais (Sete Luminares)'),

    # 4. Habilidades e termos residuais em inglês
    (r'\bUltimate\s+Skills?\b', 'Ultimate Skill(s)'),
    (r'\bUnique\s+Skills?\b', 'Unique Skill(s)'),
    (r'\bExtra\s+Skills?\b', 'Extra Skill(s)'),
    (r'\bSoul\s+Corridor\b', 'Soul Corridor'),
    (r'\bVoice\s+of\s+the\s+World\b', 'Voice of the World'),
    (r'\bMagic\s+Beast\s+Corps\b', 'Magic Beast Corps'),
]

files = sorted(glob.glob('data/light_novel/*.json'))
grand_total = 0

for fn in files:
    with open(fn, 'r', encoding='utf-8') as f:
        txt = f.read()

    v_matches = []
    for pat, label in PATTERNS:
        matches = list(re.finditer(pat, txt))
        if matches:
            v_matches.append((label, len(matches), [m.group(0) for m in matches[:3]]))
            grand_total += len(matches)

    if v_matches:
        print(f"\n=== {os.path.basename(fn)} ===")
        for label, count, samples in v_matches:
            print(f"  [{count}x] {label} -> Ex: {samples}")

print(f"\n==========================================")
print(f"TOTAL GERAL DE OCORRÊNCIAS ENCONTRADAS: {grand_total}")
print(f"==========================================")
