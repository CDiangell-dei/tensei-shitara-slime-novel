import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

# Dictionary of skill replacements (English -> PT-BR)
# Note: we need case-insensitive or exact regex
skill_translations = [
    # Skill categories
    (r'\bUltimate Skills\b', 'Habilidades Supremas'),
    (r'\bUltimate Skill\b', 'Habilidade Suprema'),
    (r'\bUnique Skills\b', 'Habilidades Únicas'),
    (r'\bUnique Skill\b', 'Habilidade Única'),
    (r'\bExtra Skills\b', 'Habilidades Extras'),
    (r'\bExtra Skill\b', 'Habilidade Extra'),
    (r'\bIntrinsic Skills\b', 'Habilidades Intrínsecas'),
    (r'\bIntrinsic Skill\b', 'Habilidade Intrínseca'),
    (r'\bCommon Skills\b', 'Habilidades Comuns'),
    (r'\bCommon Skill\b', 'Habilidade Comum'),
    (r'\bUltimate Enchant\b', 'Encantamento Supremo'),
    (r'\bUltimate Ability\b', 'Habilidade Suprema'),
    (r'\bUltimate Abilities\b', 'Habilidades Supremas'),
    (r'\bSkill Steal\b', 'Roubo de Habilidade'),
    (r'\bSteal Life\b', 'Roubo de Vida'),
    (r'\bPower Steal\b', 'Roubo de Poder'),
    (r'\bAnti-Skill\b', 'Anti-Habilidade'),
    (r'\bAnti Skill\b', 'Anti-Habilidade'),
    (r'\bFloor Guardian\b', 'Guardião do Andar'),
    (r'\bFloor Guardians\b', 'Guardiões do Andar'),
    (r'\bFloor Boss\b', 'Chefe do Andar'),
    (r'\bFloor Light\b', 'Luz do Andar'),
    (r'\bMaster Chef\b', 'Mestre Cuca'),
    (r'\bDark Flame\b', 'Chamas Negras'),
    (r'\bDark Thunder\b', 'Raio Negro'),
    (r'\bShadow Motion\b', 'Movimento nas Sombras'),
    (r'\bShadow Step\b', 'Passo nas Sombras'),
    (r'\bBlack Lightning\b', 'Raio Negro'),
    (r'\bBlack Flame\b', 'Chamas Negras'),
    (r'\bSpacetime Manipulation\b', 'Manipulação Espaço-Temporal'),
    (r'\bSpace-Time Manipulation\b', 'Manipulação Espaço-Temporal'),
    (r'\bCast Cancel\b', 'Cancelamento de Encantamento'),
    (r'\bDeath Palm\b', 'Palma da Morte'),
    (r'\bThe Heartless Jester\b', 'O Bufão Desalmado'),
    (r'\bDead Heroe\b', 'Herói Morto'),
    (r'\bGod Destruction Bullet\b', 'Bala Destruidora de Deus'),
    (r'\bGod of SpaceTime\b', 'Deus do Espaço-Tempo'),
    (r'\bGreed King\b', 'Rei da Ganância'),
    (r'\bGreedy King\b', 'Rei da Ganância'),
    (r'\bKing of Greed\b', 'Rei da Ganância'),
    (r'\bKing of Pride\b', 'Rei do Orgulho'),
    (r'\bKing of Justice\b', 'Rei da Justiça'),
    (r'\bKing of Patience\b', 'Rei da Paciência'),
    (r'\bKing of Jealousy\b', 'Rei da Inveja'),
    (r'\bKing of Evil\b', 'Rei do Mal'),
    (r'\bKing of Flames\b', 'Rei das Chamas'),
    (r'\bKing of SpaceTime\b', 'Rei do Espaço-Tempo'),
    (r'\bKing of Tyranny\b', 'Rei da Tirania'),
    (r'\bKing of the Dead\b', 'Rei dos Mortos'),
    (r'\bKing of the Sky\b', 'Rei dos Céus'),
    (r'\bKing of the Star Realm\b', 'Rei do Reino Estelar'),
    (r'\bLust King\b', 'Rei da Luxúria'),
    (r'\bFlame King Agni\b', 'Rei das Chamas Agni'),
    (r'\bInfinity Prison\b', 'Prisão Infinita'),
    (r'\bTear Scythe\b', 'Foice de Tear'),
    (r'\bTemptation King\b', 'Rei da Tentação'),
    (r'\bWrathful King\b', 'Rei da Ira'),
    (r'\bWhite Pure World\b', 'Mundo Branco Puro'),
    (r'\bWhite Flare\b', 'Chama Branca'),
    (r'\bTime Warp\b', 'Dobra Temporal'),
    (r'\bCalamity Claw\b', 'Garra da Calamidade'),
    (r'\bCrimson Corps\b', 'Corpo Carmesim'),
    (r'\bFlying Dragon Corps\b', 'Corpo de Dragões Voadores'),
    (r'\bEternal Twilight\b', 'Crepúsculo Eterno'),
    (r'\bFatal Lost\b', 'Perda Fatal'),
    (r'\bHeart Core\b', 'Núcleo do Coração'),
    (r'\bMythic Grade\b', 'Grau Mítico'),
    (r'\bNapalm Burst\b', 'Explosão Napalm'),
    (r'\bNihilistic Vanish\b', 'Desaparecimento Niilista'),
    (r'\bNihilistic World\b', 'Mundo Niilista'),
    (r'\bPseudo-Dragon Body\b', 'Corpo de Pseudo-Dragão'),
    (r'\bReverse Fate\b', 'Destino Reverso'),
    (r'\bAbsolute End\b', 'Fim Absoluto'),
]

# Let's test matches across all files
total_matches = 0
matches_by_file = {}

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    file_matches = []
    for pat, rep in skill_translations:
        hits = re.findall(pat, content)
        if hits:
            file_matches.append((pat, rep, len(hits)))
            total_matches += len(hits)
    
    # Also check generic 'Skill' and 'Skills'
    skill_hits = len(re.findall(r'\bSkills?\b', content))
    
    if file_matches or skill_hits:
        matches_by_file[f] = {
            'translations': file_matches,
            'raw_skills': skill_hits
        }

print(f"Total pattern matches: {total_matches}")
for f, info in matches_by_file.items():
    print(f, info)
