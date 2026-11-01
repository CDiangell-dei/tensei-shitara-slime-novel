import glob
import json
import re

TARGETED_FIXES = [
    # vol-13
    (r'\bsuperioridade de Skills\b', 'superioridade de Habilidades'),
    # vol-15
    (r'Um mero Skill dando desculpas', 'Uma mera Habilidade dando desculpas'),
    (r'fixado na Skill do Esprit', 'fixado na Habilidade de Esprit'),
    (r'“Azure Dragon” Baraga', '“Dragão Azul” Baraga'),
    (r'“Vermillion Bird” Nazim', '“Pássaro Carmesim” Nazim'),
    (r'“Black Tortoise” Gozari', '“Tartaruga Negra” Gozari'),
    (r'Azure Dragon \(Baraga\)', 'Dragão Azul (Baraga)'),
    (r'Vermillion Bird \(Nazim\)', 'Pássaro Carmesim (Nazim)'),
    (r'Black Tortoise \(Gozarim\)', 'Tartaruga Negra (Gozarim)'),
    (r'“Gale-Thunder Supreme”', '“Supremo Vendaval-Trovão”'),

    # vol-19
    (r'\'Thunder Rain\'', '‘Chuva de Trovões’'),
    (r'“Thousand-Hand Shadow Kill”', '“Assassinato das Mil Sombras”'),

    # vol-22
    (r'mulher \[Dark Elf\]', 'mulher [Elfa Negra]'),
    (r'“\[Moon Goddess Sword\.?\]”', '“[Espada da Deusa da Lua]”'),
    (r'\[Moon Goddess Sword\.?\]', '[Espada da Deusa da Lua]'),
    (r'"Shining King \[Surya\]"', '“Rei Brilhante [Surya]”'),
    (r'"Thunder King \[Indra\]"', '“Rei do Trovão [Indra]”'),
    (r'"Wind Sky King \[Vayu\]"', '“Rei dos Céus [Vayu]”'),
    (r'\[King of Envy Leviatã\\?\]', '[Rei da Inveja Leviatã]'),
    (r'lâmina de \[World\] que Guy', 'lâmina de [Mundo] que Guy'),
    (r'aproveitar ao máximo “\[World\]”', 'aproveitar ao máximo “[Mundo]”'),
    (r'unidade com “\[World\]”', 'unidade com “[Mundo]”'),
    (r'nível do \\?"World\\?" do Guy', 'nível da "Mundo" de Guy'),
    (r'nível do "World" do Guy', 'nível da "Mundo" de Guy'),
    (r'\[Explosão da Estrela do Dragão\] \[Dragon Nova\]', '[Explosão da Estrela do Dragão: Drago Nova]'),
    (r'\[Dragon Nova\]', '[Drago Nova]'),
    (r'\bDragon Nova\b', 'Drago Nova'),

    # vol-23
    (r'\bSoul Gluttony\b', 'Gula da Alma'),
    (r'“Dragon Demon Blade”', '“Lâmina Demoníaca do Dragão”'),

    # vol-6
    (r'título de “Curse King”', 'título de “Rei da Maldição”'),
    (r'inseri \'Domination Heart\'', 'inseri o ‘Coração da Dominação’'),

    # vol-8
    (r'“Master Access”', '“Acesso Mestre”'),
]

files = sorted(glob.glob('data/light_novel/vol-*.json'))
count = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    
    file_modified = False
    chapters = data if isinstance(data, list) else data.get('chapters', [])
    for ch in chapters:
        if 'paragraphs' in ch and isinstance(ch['paragraphs'], list):
            new_p = []
            for p in ch['paragraphs']:
                curr = p
                for pat, rep in TARGETED_FIXES:
                    if re.search(pat, curr):
                        curr = re.sub(pat, rep, curr)
                        count += 1
                        file_modified = True
                new_p.append(curr)
            ch['paragraphs'] = new_p
        
        if 'blocks' in ch and isinstance(ch['blocks'], list):
            for b in ch['blocks']:
                if isinstance(b, dict) and 'text' in b and isinstance(b['text'], str):
                    curr = b['text']
                    for pat, rep in TARGETED_FIXES:
                        if re.search(pat, curr):
                            curr = re.sub(pat, rep, curr)
                            count += 1
                            file_modified = True
                    b['text'] = curr
    
    if file_modified:
        print(f"Updated {f}")
        with open(f, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

print(f"Finished applying {count} targeted fixes.")
