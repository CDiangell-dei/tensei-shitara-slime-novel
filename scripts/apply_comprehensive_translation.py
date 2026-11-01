import glob
import json
import re
import os

# Comprehensive list of regex replacements: (pattern, replacement, description)
# Note: More specific patterns should come before more general patterns!

REPLACEMENTS = [
    # 1. Dialogue replacements
    (r'\bHey,\s*Rigurdo\b', 'Ei, Rigurdo', 'Hey Rigurdo -> Ei, Rigurdo'),
    (r'\bHey,\s*chefe\b', 'Ei, chefe', 'Hey chefe -> Ei, chefe'),
    (r'\bHey,\s*uh\b', 'Ei, uh', 'Hey uh -> Ei, uh'),
    (r'([“"«])Hey([”"»\?!\.,])', r'\1Ei\2', 'Hey punctuation -> Ei'),
    (r'([“"«])Hey\b', r'\1Ei', 'Hey dialogue start -> Ei'),
    (r'\bmas hey\b', 'mas ei', 'mas hey -> mas ei'),
    (r'\bOooooh yeah!\b', 'Oooooh sim!', 'Oooooh yeah! -> Oooooh sim!'),
    (r'([“"«])Yeah, yeah([!,\.])', r'\1Sim, sim\2', 'Yeah, yeah -> Sim, sim'),
    (r'\bYeah, yeah([!,\.])', r'Sim, sim\1', 'Yeah, yeah -> Sim, sim'),
    (r'([“"«])Yeah([”"»!,\.])', r'\1Sim\2', 'Yeah -> Sim'),
    (r'\bY-yeah\.\.\.', 'S-sim...', 'Y-yeah... -> S-sim...'),
    (r'\bverdade, yeah\b', 'verdade, sim', 'verdade, yeah -> verdade, sim'),

    # 2. Skill Types and Generic Skills
    (r'\bUltimate Skills\b', 'Habilidades Supremas', 'Ultimate Skills -> Habilidades Supremas'),
    (r'\bUltimate Skill\b', 'Habilidade Suprema', 'Ultimate Skill -> Habilidade Suprema'),
    (r'\bUnique Skills\b', 'Habilidades Únicas', 'Unique Skills -> Habilidades Únicas'),
    (r'\bUnique Skill\b', 'Habilidade Única', 'Unique Skill -> Habilidade Única'),
    (r'\bExtra Skills\b', 'Habilidades Extras', 'Extra Skills -> Habilidades Extras'),
    (r'\bExtra Skill\b', 'Habilidade Extra', 'Extra Skill -> Habilidade Extra'),
    (r'\bIntrinsic Skills\b', 'Habilidades Intrínsecas', 'Intrinsic Skills -> Habilidades Intrínsecas'),
    (r'\bIntrinsic Skill\b', 'Habilidade Intrínseca', 'Intrinsic Skill -> Habilidade Intrínseca'),
    (r'\bCommon Skills\b', 'Habilidades Comuns', 'Common Skills -> Habilidades Comuns'),
    (r'\bCommon Skill\b', 'Habilidade Comum', 'Common Skill -> Habilidade Comum'),
    (r'\bUltimate Enchant\b', 'Encantamento Supremo', 'Ultimate Enchant -> Encantamento Supremo'),
    (r'\bUltimate Ability\b', 'Habilidade Suprema', 'Ultimate Ability -> Habilidade Suprema'),
    (r'\bUltimate Abilities\b', 'Habilidades Supremas', 'Ultimate Abilities -> Habilidades Supremas'),
    (r'\bSkill Steal\b', 'Roubo de Habilidade', 'Skill Steal -> Roubo de Habilidade'),
    (r'\bSteal Life Palm\b', 'Palma de Roubo de Vida', 'Steal Life Palm -> Palma de Roubo de Vida'),
    (r'\bSteal Life\b', 'Roubo de Vida', 'Steal Life -> Roubo de Vida'),
    (r'\bPower Steal\b', 'Roubo de Poder', 'Power Steal -> Roubo de Poder'),
    (r'\bAnti-Skill\b', 'Anti-Habilidade', 'Anti-Skill -> Anti-Habilidade'),
    (r'\bAnti Skill\b', 'Anti-Habilidade', 'Anti Skill -> Anti-Habilidade'),
    (r'\bQuartet Skill\b', 'Habilidade do Quarteto', 'Quartet Skill -> Habilidade do Quarteto'),
    (r'\bSkill Gifting\b', 'Concessão de Habilidades', 'Skill Gifting -> Concessão de Habilidades'),

    # 3. Floor terms
    (r'\bFloor Guardian\b', 'Guardião do Andar', 'Floor Guardian -> Guardião do Andar'),
    (r'\bFloor Guardians\b', 'Guardiões do Andar', 'Floor Guardians -> Guardiões do Andar'),
    (r'\bFloor Boss\b', 'Chefe do Andar', 'Floor Boss -> Chefe do Andar'),
    (r'\bFloor Light\b', 'Luz do Andar', 'Floor Light -> Luz do Andar'),

    # 4. Specific Skills and Abilities
    (r'\bMaster Chef\b', 'Mestre Cuca', 'Master Chef -> Mestre Cuca'),
    (r'Habilidade Única \'Chef\'', 'Habilidade Única ‘Cozinheiro’', 'Habilidade Única Chef -> Cozinheiro'),
    (r'‘Chef’ de Zonda', '‘Cozinheiro’ de Zonda', 'Chef de Zonda -> Cozinheiro de Zonda'),
    (r'Chef da Princesa Venenosa', 'Cozinheiro da Princesa Venenosa', 'Chef da Princesa Venenosa -> Cozinheiro da Princesa Venenosa'),
    (r'habilidade única Deviant\b', 'habilidade única ‘Degenerado’', 'habilidade única Deviant -> Degenerado'),
    (r'habilidade exclusiva Deviant\b', 'habilidade única ‘Degenerado’', 'habilidade exclusiva Deviant -> Degenerado'),
    (r'\'Deviant\' de Shizu-san', '‘Degenerado’ de Shizu-san', 'Deviant de Shizu-san -> Degenerado de Shizu-san'),
    (r'habilidade única Deviant,', 'habilidade única ‘Degenerado’,', 'Deviant Shizu -> Degenerado'),
    (r'\bDark Flame\b', 'Chamas Negras', 'Dark Flame -> Chamas Negras'),
    (r'\bDark Thunder\b', 'Raio Negro', 'Dark Thunder -> Raio Negro'),
    (r'\bBlack Lightning\b', 'Raio Negro', 'Black Lightning -> Raio Negro'),
    (r'\bBlack Flame\b', 'Chamas Negras', 'Black Flame -> Chamas Negras'),
    (r'\bDark Flame Fog\b', 'Névoa de Chamas Negras', 'Dark Flame Fog -> Névoa de Chamas Negras'),
    (r'\bBlack Flame Fog\b', 'Névoa de Chamas Negras', 'Black Flame Fog -> Névoa de Chamas Negras'),
    (r'\bBlack Thunder Flame\b', 'Chama do Trovão Negro', 'Black Thunder Flame -> Chama do Trovão Negro'),
    (r'\bShadow Motion\b', 'Movimento nas Sombras', 'Shadow Motion -> Movimento nas Sombras'),
    (r'\bShadow Step\b', 'Passo nas Sombras', 'Shadow Step -> Passo nas Sombras'),
    (r'\bShadow Clone\b', 'Clone de Sombra', 'Shadow Clone -> Clone de Sombra'),
    (r'\bBlood Shadow\b', 'Sombra de Sangue', 'Blood Shadow -> Sombra de Sangue'),
    (r'\bDark Shadow\b', 'Sombra Escura', 'Dark Shadow -> Sombra Escura'),
    (r'\bThousand-Hand Shadow Kill\b', 'Assassinato das Mil Sombras', 'Thousand-Hand Shadow Kill -> Assassinato das Mil Sombras'),
    (r'\bSpacetime Manipulation\b', 'Manipulação Espaço-Temporal', 'Spacetime Manipulation -> Manipulação Espaço-Temporal'),
    (r'\bSpace-Time Manipulation\b', 'Manipulação Espaço-Temporal', 'Space-Time Manipulation -> Manipulação Espaço-Temporal'),
    (r'\bCast Cancel\b', 'Cancelamento de Encantamento', 'Cast Cancel -> Cancelamento de Encantamento'),
    (r'\bDeath Palm\b', 'Palma da Morte', 'Death Palm -> Palma da Morte'),
    (r'\bThe Heartless Jester\b', 'O Bufão Desalmado', 'The Heartless Jester -> O Bufão Desalmado'),
    (r'\bDead Heroe\b', 'Herói Morto', 'Dead Heroe -> Herói Morto'),
    (r'\bGod Destruction Bullet\b', 'Bala Destruidora de Deus', 'God Destruction Bullet -> Bala Destruidora de Deus'),
    (r'\bGod of SpaceTime\b', 'Deus do Espaço-Tempo', 'God of SpaceTime -> Deus do Espaço-Tempo'),
    (r'\bSpacetime King Yog-Sothoth\b', 'Rei do Espaço-Tempo Yog-Sothoth', 'Spacetime King Yog-Sothoth -> Rei do Espaço-Tempo Yog-Sothoth'),
    (r'\bDeath King Belial\b', 'Rei da Morte Belial', 'Death King Belial -> Rei da Morte Belial'),
    (r'\bFate King Fortuna\b', 'Rei do Destino Fortuna', 'Fate King Fortuna -> Rei do Destino Fortuna'),
    (r'\bDomination King Melchizedek\b', 'Rei da Dominação Melchizedek', 'Domination King Melchizedek -> Rei da Dominação Melchizedek'),
    (r'\bEvil Dragon King \(Azi Dahaka\)', 'Rei Dragão Maligno (Azi Dahaka)', 'Evil Dragon King -> Rei Dragão Maligno'),
    (r'\bFertility King Shub-Niggurath\b', 'Rei da Fertilidade Shub-Niggurath', 'Fertility King Shub-Niggurath -> Rei da Fertilidade Shub-Niggurath'),
    (r'\bJudgement King Israfil\b', 'Rei do Julgamento Israfil', 'Judgement King Israfil -> Rei do Julgamento Israfil'),
    (r'\bAusterity King Jibril\b', 'Rei da Austeridade Jibril', 'Austerity King Jibril -> Rei da Austeridade Jibril'),
    (r'\bBeast King Bahamut\b', 'Rei das Feras Bahamut', 'Beast King Bahamut -> Rei das Feras Bahamut'),
    (r'\bLight King \(Hamiel\)', 'Rei da Luz (Hamiel)', 'Light King (Hamiel) -> Rei da Luz (Hamiel)'),
    (r'\bGourmet King Beelzebub\b', 'Rei Gourmet Beelzebub', 'Gourmet King Beelzebub -> Rei Gourmet Beelzebub'),
    (r'\bMoon King Tsukuyomi\b', 'Rei da Lua Tsukuyomi', 'Moon King Tsukuyomi -> Rei da Lua Tsukuyomi'),
    (r'\bPsychology King Mood Maker\b', 'Rei da Psicologia Criador de Humor', 'Psychology King Mood Maker -> Rei da Psicologia Criador de Humor'),
    (r'\bPsicologia King Mood Maker\b', 'Rei da Psicologia Criador de Humor', 'Psicologia King Mood Maker -> Rei da Psicologia Criador de Humor'),
    (r'\bRetribution King Metis\b', 'Rei da Retribuição Metis', 'Retribution King Metis -> Rei da Retribuição Metis'),
    (r'\bEnvious King Leviatã\b', 'Rei da Inveja Leviatã', 'Envious King Leviatã -> Rei da Inveja Leviatã'),
    (r'\bFlame King Agni\b', 'Rei das Chamas Agni', 'Flame King Agni -> Rei das Chamas Agni'),
    (r'\bGluttonous King Beelzeebuth\b', 'Rei Glutão Beelzebuth', 'Gluttonous King Beelzeebuth -> Rei Glutão Beelzebuth'),
    (r'\bMagic Wolf King\b', 'Rei Lobo Mágico', 'Magic Wolf King -> Rei Lobo Mágico'),
    (r'\bBarrier Lord\b', 'Senhor das Barreiras', 'Barrier Lord -> Senhor das Barreiras'),
    (r'\bCurse Lord\b', 'Senhor da Maldição', 'Curse Lord -> Senhor da Maldição'),
    (r'\bFlare Lord\b', 'Senhor das Chamas', 'Flare Lord -> Senhor das Chamas'),
    (r'\bBeast Master\b', 'Mestre das Feras', 'Beast Master -> Mestre das Feras'),
    (r'\bMarionette Master\b', 'Mestre Marionetista', 'Marionette Master -> Mestre Marionetista'),
    (r'\bGreed King\b', 'Rei da Ganância', 'Greed King -> Rei da Ganância'),
    (r'\bGreedy King\b', 'Rei da Ganância', 'Greedy King -> Rei da Ganância'),
    (r'\bKing of Greed\b', 'Rei da Ganância', 'King of Greed -> Rei da Ganância'),
    (r'\bKing of Pride\b', 'Rei do Orgulho', 'King of Pride -> Rei do Orgulho'),
    (r'\bKing of Justice\b', 'Rei da Justiça', 'King of Justice -> Rei da Justiça'),
    (r'\bKing of Patience\b', 'Rei da Paciência', 'King of Patience -> Rei da Paciência'),
    (r'\bKing of Jealousy\b', 'Rei da Inveja', 'King of Jealousy -> Rei da Inveja'),
    (r'\bKing of Evil\b', 'Rei do Mal', 'King of Evil -> Rei do Mal'),
    (r'\bKing of Flames\b', 'Rei das Chamas', 'King of Flames -> Rei das Chamas'),
    (r'\bKing of SpaceTime\b', 'Rei do Espaço-Tempo', 'King of SpaceTime -> Rei do Espaço-Tempo'),
    (r'\bKing of Tyranny\b', 'Rei da Tirania', 'King of Tyranny -> Rei da Tirania'),
    (r'\bKing of the Dead\b', 'Rei dos Mortos', 'King of the Dead -> Rei dos Mortos'),
    (r'\bKing of the Sky\b', 'Rei dos Céus', 'King of the Sky -> Rei dos Céus'),
    (r'\bKing of the Star Realm\b', 'Rei do Reino Estelar', 'King of the Star Realm -> Rei do Reino Estelar'),
    (r'\bLust King\b', 'Rei da Luxúria', 'Lust King -> Rei da Luxúria'),
    (r'\bTemptation King\b', 'Rei da Tentação', 'Temptation King -> Rei da Tentação'),
    (r'\bWrathful King\b', 'Rei da Ira', 'Wrathful King -> Rei da Ira'),
    (r'\bInfinity Prison\b', 'Prisão Infinita', 'Infinity Prison -> Prisão Infinita'),
    (r'\bTear Scythe\b', 'Foice de Tear', 'Tear Scythe -> Foice de Tear'),
    (r'\bWhite Pure World\b', 'Mundo Branco Puro', 'White Pure World -> Mundo Branco Puro'),
    (r'\bWhite Flare\b', 'Chama Branca', 'White Flare -> Chama Branca'),
    (r'\bTime Warp\b', 'Dobra Temporal', 'Time Warp -> Dobra Temporal'),
    (r'\bCalamity Claw\b', 'Garra da Calamidade', 'Calamity Claw -> Garra da Calamidade'),
    (r'\bCrimson Corps\b', 'Corpo Carmesim', 'Crimson Corps -> Corpo Carmesim'),
    (r'\bFlying Dragon Corps\b', 'Corpo de Dragões Voadores', 'Flying Dragon Corps -> Corpo de Dragões Voadores'),
    (r'\bEternal Twilight\b', 'Crepúsculo Eterno', 'Eternal Twilight -> Crepúsculo Eterno'),
    (r'\bFatal Lost\b', 'Perda Fatal', 'Fatal Lost -> Perda Fatal'),
    (r'\bHeart Core\b', 'Núcleo do Coração', 'Heart Core -> Núcleo do Coração'),
    (r'\bMythic Grade\b', 'Grau Mítico', 'Mythic Grade -> Grau Mítico'),
    (r'\bNapalm Burst\b', 'Explosão Napalm', 'Napalm Burst -> Explosão Napalm'),
    (r'\bNihilistic Vanish\b', 'Desaparecimento Niilista', 'Nihilistic Vanish -> Desaparecimento Niilista'),
    (r'\bNihilistic World\b', 'Mundo Niilista', 'Nihilistic World -> Mundo Niilista'),
    (r'\bPseudo-Dragon Body\b', 'Corpo de Pseudo-Dragão', 'Pseudo-Dragon Body -> Corpo de Pseudo-Dragão'),
    (r'\bReverse Fate\b', 'Destino Reverso', 'Reverse Fate -> Destino Reverso'),
    (r'\bAbsolute End\b', 'Fim Absoluto', 'Absolute End -> Fim Absoluto'),
    (r'\bDragon Eye\b', 'Olho do Dragão', 'Dragon Eye -> Olho do Dragão'),
    (r'\bDragon Body\b', 'Corpo de Dragão', 'Dragon Body -> Corpo de Dragão'),
    (r'\bDragon Factor\b', 'Fator Dragão', 'Dragon Factor -> Fator Dragão'),
    (r'\bDragon Kind\b', 'Espécie Dragão', 'Dragon Kind -> Espécie Dragão'),
    (r'\bDragon Kinds\b', 'Espécies de Dragões', 'Dragon Kinds -> Espécies de Dragões'),
    (r'\bDragon Skin\b', 'Pele de Dragão', 'Dragon Skin -> Pele de Dragão'),
    (r'\bDragon Scaling\b', 'Escamas de Dragão', 'Dragon Scaling -> Escamas de Dragão'),
    (r'\bDragon Warrior Conversion\b', 'Conversão de Guerreiro Dragão', 'Dragon Warrior Conversion -> Conversão de Guerreiro Dragão'),
    (r'\bFrost Dragon\b', 'Dragão de Gelo', 'Frost Dragon -> Dragão de Gelo'),
    (r'\bScorch Dragon\b', 'Dragão Chamuscante', 'Scorch Dragon -> Dragão Chamuscante'),
    (r'\bElemental Dragon\b', 'Dragão Elemental', 'Elemental Dragon -> Dragão Elemental'),
    (r'\bSpirit Dragon\b', 'Dragão Espiritual', 'Spirit Dragon -> Dragão Espiritual'),
    (r'\bSword Devil\b', 'Demônio da Espada', 'Sword Devil -> Demônio da Espada'),
    (r'\bDeath Heralding Wind\b', 'Vento Prenúncio da Morte', 'Death Heralding Wind -> Vento Prenúncio da Morte'),
    (r'\bFlame Pillar\b', 'Pilar de Chamas', 'Flame Pillar -> Pilar de Chamas'),
    (r'\bMelt Strike\b', 'Golpe Derretedor', 'Melt Strike -> Golpe Derretedor'),
    (r'\bFallen Strike\b', 'Golpe Caído', 'Fallen Strike -> Golpe Caído'),
    (r'\bNova Break\b', 'Ruptura Nova', 'Nova Break -> Ruptura Nova'),
    (r'\bSuspended World\b', 'Mundo Suspenso', 'Suspended World -> Mundo Suspenso'),
    (r'\bTime Stop\b', 'Parada do Tempo', 'Time Stop -> Parada do Tempo'),
    (r'\bVoice Of the World\b', 'Voz do Mundo', 'Voice Of the World -> Voz do Mundo'),
    (r'\bWorld Simulator\b', 'Simulador de Mundo', 'World Simulator -> Simulador de Mundo'),
    (r'\bWorld of Annihilation\b', 'Mundo de Aniquilação', 'World of Annihilation -> Mundo de Aniquilação'),
    (r'\bImaginary Space\b', 'Espaço Imaginário', 'Imaginary Space -> Espaço Imaginário'),
    (r'\bImaginary Blade\b', 'Lâmina Imaginária', 'Imaginary Blade -> Lâmina Imaginária'),
    (r'\bBlade Transformation\b', 'Transformação em Lâmina', 'Blade Transformation -> Transformação em Lâmina'),
    (r'\bBlade of Death\b', 'Lâmina da Morte', 'Blade of Death -> Lâmina da Morte'),
    (r'\bPortal Warp\b', 'Portal de Dobra', 'Portal Warp -> Portal de Dobra'),
    (r'\bWarp Portal\b', 'Portal de Dobra', 'Warp Portal -> Portal de Dobra'),
    (r'\bPredation\b', 'Predação', 'Predation -> Predação'),
    (r'\bHeavy Thunder\b', 'Trovão Pesado', 'Heavy Thunder -> Trovão Pesado'),
    (r'\bMind Read\b', 'Leitura Mental', 'Mind Read -> Leitura Mental'),
    (r'\bDeath Streak\b', 'Raio da Morte', 'Death Streak -> Raio da Morte'),
    (r'\bDragon Roost\b', 'Poleiro do Dragão', 'Dragon Roost -> Poleiro do Dragão'),
    (r'\bEye of the Moon\b', 'Olho da Lua', 'Eye of the Moon -> Olho da Lua'),
    (r'\bGale-Thunder Supreme\b', 'Supremo Trovão-Vendaval', 'Gale-Thunder Supreme -> Supremo Trovão-Vendaval'),
    (r'\bWhite Tiger-Blue Dragon Strike\b', 'Golpe do Tigre Branco e Dragão Azul', 'White Tiger-Blue Dragon Strike -> Golpe do Tigre Branco e Dragão Azul'),
    (r'\bDead End Rainbow\b', 'Arco-Íris da Morte Final', 'Dead End Rainbow -> Arco-Íris da Morte Final'),
    (r'\bDevour Soul\b', 'Devorar Alma', 'Devour Soul -> Devorar Alma'),
    (r'\bSoul Eater\b', 'Devorador de Almas', 'Soul Eater -> Devorador de Almas'),
    (r'\bChaos Eater\b', 'Devorador do Caos', 'Chaos Eater -> Devorador do Caos'),
    (r'\bInfinite Eater\b', 'Devorador Infinito', 'Infinite Eater -> Devorador Infinito'),
    (r'\bDragon Star Explosion Flame Pain\b', 'Dor da Explosão da Chama da Estrela do Dragão', 'Dragon Star Explosion Flame Pain -> Dor da Explosão da Chama da Estrela do Dragão'),
    (r'\bDragon Star Explosion Flame Pavilion\b', 'Pavilhão da Explosão da Chama da Estrela do Dragão', 'Dragon Star Explosion Flame Pavilion -> Pavilhão da Explosão da Chama da Estrela do Dragão'),
    (r'\bDragon Star Explosion Overlord\b', 'Soberano da Explosão da Estrela do Dragão', 'Dragon Star Explosion Overlord -> Soberano da Explosão da Estrela do Dragão'),
    (r'\bDragon Star Explosion Flame\b', 'Chama da Explosão da Estrela do Dragão', 'Dragon Star Explosion Flame -> Chama da Explosão da Estrela do Dragão'),
    (r'\bDragon Star Explosion Pa\b', 'Explosão da Estrela do Dragão', 'Dragon Star Explosion Pa -> Explosão da Estrela do Dragão'),
    (r'\bDragon Star Explosion\b', 'Explosão da Estrela do Dragão', 'Dragon Star Explosion -> Explosão da Estrela do Dragão'),
    (r'\bDragon Star Flame Blast\b', 'Rajada de Chamas da Estrela do Dragão', 'Dragon Star Flame Blast -> Rajada de Chamas da Estrela do Dragão'),
    (r'\bHundred Break Light Spirit Smash\b', 'Quebra das Cem Luzes Destruição Espiritual', 'Hundred Break Light Spirit Smash -> Quebra das Cem Luzes Destruição Espiritual'),
    (r'\bHundred Breaker\b', 'Cem Destruidores', 'Hundred Breaker -> Cem Destruidores'),
    (r'\bHeat Dragon Flame Blast\b', 'Rajada de Chamas do Dragão de Calor', 'Heat Dragon Flame Blast -> Rajada de Chamas do Dragão de Calor'),
    (r'\bFlash Break Spirit Smash\b', 'Destruição Espiritual Relâmpago', 'Flash Break Spirit Smash -> Destruição Espiritual Relâmpago'),
    (r'\bWhite Flash Annihilation Flame Tyrant\b', 'Tirano de Chamas de Aniquilação Relâmpago Branco', 'White Flash Annihilation Flame Tyrant -> Tirano de Chamas de Aniquilação Relâmpago Branco'),
    (r'\[Deathman\]', '[Homem-Morto]', 'Deathman -> Homem-Morto'),

    # 5. Generic Skill / Skills replacements in context
    (r'\bum mero Skill\b', 'uma mera Habilidade', 'um mero Skill -> uma mera Habilidade'),
    (r'\bum Skill\b', 'uma Habilidade', 'um Skill -> uma Habilidade'),
    (r'\buma Skill\b', 'uma Habilidade', 'uma Skill -> uma Habilidade'),
    (r'\bseu próprio Skill\b', 'sua própria Habilidade', 'seu próprio Skill -> sua própria Habilidade'),
    (r'\bdo poder da Skill\b', 'do poder da Habilidade', 'do poder da Skill -> da Habilidade'),
    (r'\befeito da Skill\b', 'efeito da Habilidade', 'efeito da Skill -> da Habilidade'),
    (r'\befeitos da Skill\b', 'efeitos da Habilidade', 'efeitos da Skill -> das Habilidades'),
    (r'\blançou a Skill\b', 'lançou a Habilidade', 'lançou a Skill -> a Habilidade'),
    (r'\ba Skill\b', 'a Habilidade', 'a Skill -> a Habilidade'),
    (r'\bda Skill\b', 'da Habilidade', 'da Skill -> da Habilidade'),
    (r'\bdesta Skill\b', 'desta Habilidade', 'desta Skill -> desta Habilidade'),
    (r'\bpela Skill\b', 'pela Habilidade', 'pela Skill -> pela Habilidade'),
    (r'\bcom a Skill\b', 'com a Habilidade', 'com a Skill -> com a Habilidade'),
    (r'\bde sua Skill\b', 'de sua Habilidade', 'de sua Skill -> de sua Habilidade'),
    (r'\bde sua própria Skill\b', 'de sua própria Habilidade', 'de sua própria Skill -> Habilidade'),
    (r'\bse sua Skill\b', 'se sua Habilidade', 'se sua Skill -> se sua Habilidade'),
    (r'\bminha Skill\b', 'minha Habilidade', 'minha Skill -> minha Habilidade'),
    (r'\bSua Skill\b', 'Sua Habilidade', 'Sua Skill -> Sua Habilidade'),
    (r'\bsua Skill\b', 'sua Habilidade', 'sua Skill -> sua Habilidade'),
    (r'\broubar a Skill\b', 'roubar a Habilidade', 'roubar a Skill -> a Habilidade'),
    (r'\broubar Skill\b', 'roubar Habilidade', 'roubar Skill -> Habilidade'),
    (r'\badquirir Skill\b', 'adquirir Habilidade', 'adquirir Skill -> Habilidade'),
    (r'\bconceder Skills\b', 'conceder Habilidades', 'conceder Skills -> Habilidades'),
    (r'\busuários de Skill\b', 'usuários de Habilidades', 'usuários de Skill -> Habilidades'),
    (r'\busuário da Skill\b', 'usuário da Habilidade', 'usuário da Skill -> Habilidade'),
    (r'\busuários angelicais de Skill\b', 'usuários de Habilidades angelicais', 'usuários angelicais de Skill -> Habilidades'),
    (r'\bangélicos proprietários de Skill\b', 'possuidores de Habilidades angelicais', 'proprietários de Skill -> Habilidades'),
    (r'\bangélicos usuários de Skill\b', 'usuários de Habilidades angelicais', 'usuários de Skill -> Habilidades'),
    (r'\bSkills angelicais\b', 'Habilidades angelicais', 'Skills angelicais -> Habilidades angelicais'),
    (r'\bSkills angélicas\b', 'Habilidades angélicas', 'Skills angélicas -> Habilidades angélicas'),
    (r'\banular Skills\b', 'anular Habilidades', 'anular Skills -> anular Habilidades'),
    (r'\bas Skills\b', 'as Habilidades', 'as Skills -> as Habilidades'),
    (r'\bAs Skills\b', 'As Habilidades', 'As Skills -> As Habilidades'),
    (r'\bsuas Skills\b', 'suas Habilidades', 'suas Skills -> suas Habilidades'),
    (r'\bminhas Skills\b', 'minhas Habilidades', 'minhas Skills -> minhas Habilidades'),
    (r'\btodas as Skills\b', 'todas as Habilidades', 'todas as Skills -> todas as Habilidades'),
    (r'\bduas Skills\b', 'duas Habilidades', 'duas Skills -> duas Habilidades'),
    (r'\bNúmero de Skills\b', 'Número de Habilidades', 'número de Skills -> Habilidades'),
    (r'\bnúmero de Skills\b', 'número de Habilidades', 'número de Skills -> Habilidades'),
    (r'\bdaria Skills\b', 'daria Habilidades', 'daria Skills -> Habilidades'),
    (r'\bmaior de Skills\b', 'maior de Habilidades', 'maior de Skills -> Habilidades'),
    (r'\bpensar em Skills\b', 'pensar em Habilidades', 'pensar em Skills -> Habilidades'),
    (r'\busar Skills\b', 'usar Habilidades', 'usar Skills -> Habilidades'),
    (r'\bàs suas Skills\b', 'às suas Habilidades', 'às suas Skills -> Habilidades'),
    (r'\bdependia de Skills\b', 'dependia de Habilidades', 'dependia de Skills -> Habilidades'),
    (r'\bsobre Skills\b', 'sobre Habilidades', 'sobre Skills -> Habilidades'),
    (r'\bentre Skills\b', 'entre Habilidades', 'entre Skills -> Habilidades'),
    (r'\bcontra Skills\b', 'contra Habilidades', 'contra Skills -> Habilidades'),
    (r'\busando Skills\b', 'usando Habilidades', 'usando Skills -> Habilidades'),
    (r'\bconfiar nas Skills\b', 'confiar nas Habilidades', 'confiar nas Skills -> Habilidades'),
    (r'\bunificador de Skills\b', 'unificador de Habilidades', 'unificador de Skills -> Habilidades'),
    (r'\bmodificar Skills\b', 'modificar Habilidades', 'modificar Skills -> Habilidades'),
    (r'\bcombinar minhas Skills\b', 'combinar minhas Habilidades', 'combinar minhas Skills -> Habilidades'),
    (r'\bhabilidades de Skill\b', 'habilidades de combate', 'habilidades de Skill -> habilidades de combate'),
    (r'\bderivados de Skill\b', 'derivados de Habilidades', 'derivados de Skill -> Habilidades'),
    (r'\bdepender de Skills\b', 'depender de Habilidades', 'depender de Skills -> Habilidades'),
]

files = sorted(glob.glob('data/light_novel/vol-*.json'))

total_edits = 0
file_counts = {}

def apply_transforms(text):
    global total_edits
    new_text = text
    for pat, rep, desc in REPLACEMENTS:
        matches = len(re.findall(pat, new_text))
        if matches > 0:
            new_text = re.sub(pat, rep, new_text)
            total_edits += matches
    return new_text

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    
    vol_edits_before = total_edits
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    
    for ch in chapters:
        # paragraphs
        if 'paragraphs' in ch and isinstance(ch['paragraphs'], list):
            new_paras = []
            for p in ch['paragraphs']:
                new_paras.append(apply_transforms(p))
            ch['paragraphs'] = new_paras
        
        # blocks
        if 'blocks' in ch and isinstance(ch['blocks'], list):
            for b in ch['blocks']:
                if isinstance(b, dict) and 'text' in b and isinstance(b['text'], str):
                    b['text'] = apply_transforms(b['text'])
    
    vol_edits = total_edits - vol_edits_before
    if vol_edits > 0:
        file_counts[f] = vol_edits
        # Save back to file
        with open(f, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

print(f"Total replacements applied: {total_edits}")
print("Edits by file:")
for f, c in file_counts.items():
    print(f"  {f}: {c} edits")
