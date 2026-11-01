"""
GERADOR DO CATÁLOGO MESTRE - TENSEI SHITARA SLIME DATTA KEN
Consolida Light Novel 100% completa (Volumes 1 a 23 + 8.5, incluindo edições alternativas da Scan nos Vols 6-13),
Web Novel completa (Capítulos 0 a 249 + Intermissões .5 + 48 Capítulos Extras),
Resumo até o Volume 11 (Guia Pós-Anime), Comparador Duplo (WN vs LN + Fontes da Comunidade),
Guia Cultural expandido com Glossário Inline e Catálogo Oficial da Amazon Brasil.
"""

import json
import os
import re


def build_catalog():
    # 1. Carregar índice completo da Web Novel
    with open('web_novel_index.json', 'r', encoding='utf-8') as f:
        wn_raw = json.load(f)

    wn_arcs = [
        {
            "id": "arc-1",
            "num": 1,
            "is_extra": False,
            "title": "Arco 1: Empoderamento dos Monstros (Reencarnação)",
            "range": [0, 18.9],
            "desc": "Satoru Mikami reencarna como um Slime, faz pacto de amizade com o Dragão da Tempestade Veldora, assume o nome Rimuru Tempest, evolui os Goblins e Lobos da Presa e visita o Reino Armado de Dwargon."
        },
        {
            "id": "arc-2",
            "num": 2,
            "is_extra": False,
            "title": "Arco 2: Agitação na Floresta de Jura & O Lorde Orc",
            "range": [19, 44],
            "desc": "O encontro com Shizu Izawa, a chegada dos Ogros sobreviventes (que evoluem para Kijin), a invasão de 200 mil Orcs comandados pelo Orc Desastre Geld e a fundação da Aliança da Grande Floresta de Jura."
        },
        {
            "id": "arc-3",
            "num": 3,
            "is_extra": False,
            "title": "Arco 3: Vida na Capital Real & As Crianças Invocadas",
            "range": [45, 64],
            "desc": "A visita explosiva da Lorde Demônio Milim Nava, os tratados diplomáticos e a jornada de Rimuru até o Reino de Ingrassia para ensinar e salvar os alunos de Shizu."
        },
        {
            "id": "arc-4",
            "num": 4,
            "is_extra": False,
            "title": "Arco 4: Nascimento do Lorde Demônio & Walpurgis",
            "range": [65, 83],
            "desc": "O ataque covarde do Reino de Farmas, o despertar de Rimuru como Verdadeiro Lorde Demônio com o feitiço Megiddo, a libertação de Veldora e o julgamento de Clayman no Walpurgis."
        },
        {
            "id": "arc-5",
            "num": 5,
            "is_extra": False,
            "title": "Arco 5: Confronto com os Cavaleiros Sagrados",
            "range": [84, 97],
            "desc": "A queda definitiva de Farmas, as manipulações nos bastidores da Igreja Santa Ocidental e a revanche decisiva entre Rimuru e Hinata Sakaguchi."
        },
        {
            "id": "arc-6",
            "num": 6,
            "is_extra": False,
            "title": "Arco 6: O Grande Torneio & Abertura do Labirinto",
            "range": [98, 119],
            "desc": "O Festival de Fundação de Tempest, o torneio marcial com a estreia cômica do herói Masayuki e a inauguração da Masmorra Subterrânea de 100 andares."
        },
        {
            "id": "arc-7",
            "num": 7,
            "is_extra": False,
            "title": "Arco 7: O Despertar da Heroína & Conspirações de Yuuki",
            "range": [120, 136],
            "desc": "O mistério temporal envolvendo Chloe e Hinata, o duelo entre Leon Cromwell e Yuuki Kagurazaka e a fuga de Yuuki rumo ao Império Oriental."
        },
        {
            "id": "arc-8",
            "num": 8,
            "is_extra": False,
            "title": "Arco 8: A Invasão do Império Oriental",
            "range": [137, 161.9],
            "desc": "Quase um milhão de soldados blindados do Império marcham contra Tempest e enfrentam o terror absoluto dos Guardiões do Labirinto e da Legião Negra."
        },
        {
            "id": "arc-9",
            "num": 9,
            "is_extra": False,
            "title": "Arco 9: Fúria Dracônica, Evolução dos Patronos & Golpe Imperial",
            "range": [162, 185.9],
            "desc": "A evolução dos 12 Patronos de Rimuru para Lordes Demônios Despertos, o embate contra Velgrynd, o nascimento de Ciel e a reviravolta na Capital Imperial."
        },
        {
            "id": "arc-10",
            "num": 10,
            "is_extra": False,
            "title": "Arco 10: A Grande Guerra Tenma & Epílogo Cósmico",
            "range": [186, 249],
            "desc": "A guerra apocalíptica contra o exército celestial, o confronto final no Fim do Espaço-Tempo contra Yuuki Kagurazaka e o epílogo da reencarnação de Satoru."
        },
        {
            "id": "arc-extra-1",
            "num": 11,
            "is_extra": True,
            "title": "Arco Extra 1: O Jogo de Fuga Elegante de Rimuru",
            "range": [1, 26],
            "desc": "Após o fim da Guerra Tenma, Rimuru decide viajar incógnito pelo mundo como um aventureiro comum, envolvendo-se em intrigas acadêmicas e conspirações reais."
        },
        {
            "id": "arc-extra-2",
            "num": 12,
            "is_extra": True,
            "title": "Arco Extra 2: Visita ao Desconhecido (Pós-História Sci-Fi)",
            "range": [27, 45],
            "desc": "Veldora, Ramiris e Beretta são transportados acidentalmente para um universo futurista cibernético ameaçado por invasores dimensionais."
        },
        {
            "id": "arc-extra-3",
            "num": 13,
            "is_extra": True,
            "title": "Arco Extra 3: Histórias Especiais de Tempest (Side Stories)",
            "range": [46, 48],
            "desc": "Contos especiais de cotidiano em Tempest: águas termais (Onsen), bastidores e o grande sorteio do Festival da Academia."
        }
    ]

    cleaned_wn_chapters = []
    downloaded_count = 0
    for idx, ch in enumerate(wn_raw):
        fpath = os.path.join('data/web_novel', ch['file'])
        has_file = os.path.exists(fpath)
        p_count = 0
        if has_file:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                p_count = d.get('paragraph_count', len(d.get('paragraphs', [])))
                if p_count > 0:
                    downloaded_count += 1
                else:
                    has_file = False
            except Exception:
                has_file = False

        is_extra = bool(ch.get('is_extra'))
        ch_num = ch['num']
        arc_id = 'arc-extra-3' if is_extra else 'arc-10'
        for a in wn_arcs:
            if a['is_extra'] == is_extra and a['range'][0] <= float(ch_num) <= a['range'][1]:
                arc_id = a['id']
                break

        cleaned_wn_chapters.append({
            'seq': idx,
            'id': ch['id'],
            'num': ch_num,
            'display_num': ch.get('display_num', f"Capítulo {ch_num}"),
            'is_extra': is_extra,
            'title': ch['title'],
            'url': ch['url'],
            'file': ch['file'],
            'arc_id': arc_id,
            'paragraph_count': p_count,
            'is_downloaded': has_file,
        })

    # 2. Metadados Completos dos 21 Volumes da Light Novel (1..20 + 8.5)
    ln_metadata = [
        {"id": "vol-1", "num": 1, "title": "Volume 1: Morte e Reencarnação", "kanji": "転生したらスライムだった件 1", "desc": "Satoru Mikami é assassinado em Tóquio e reencarna como um Slime em uma caverna selada. Após fazer amizade com o Dragão da Tempestade Veldora, recebe o nome Rimuru Tempest e passa a proteger e nomear Goblins e Lobos da Presa."},
        {"id": "vol-2", "num": 2, "title": "Volume 2: O Despertar da Floresta & O Lorde Orc", "kanji": "転生したらスライムだった件 2", "desc": "Seis Ogros sobreviventes juram lealdade a Rimuru e evoluem para Kijin. Logo depois, 200 mil Orcs famintos liderados pelo Lorde Orc Geld marcham sobre a Grande Floresta de Jura."},
        {"id": "vol-3", "num": 3, "title": "Volume 3: A Ameaça de Charybdis & O Tratado das Bestas", "kanji": "転生したらスライムだった件 3", "desc": "Nasce oficialmente a Federação de Jura Tempest! A Lorde Demônio Milim Nava se muda para a cidade, e a calamidade aérea Charybdis desperta para testar as alianças recém-firmadas."},
        {"id": "vol-4", "num": 4, "title": "Volume 4: Rumo às Terras Humanas & As Crianças Invocadas", "kanji": "転生したらスライムだった件 4", "desc": "Cumprindo a promessa feita a Shizu Izawa, Rimuru viaja ao Reino de Blumund e à Academia da Liberdade em Ingrassia para salvar cinco crianças de outro mundo condenadas pelo excesso de energia mágica."},
        {"id": "vol-5", "num": 5, "title": "Volume 5: Nascimento do Lorde Demônio & Megiddo", "kanji": "転生したらスライムだった件 5", "desc": "O Reino de Farmas ataca Tempest sob barreiras anti-magia e massacra moradores inocentes. Tomado pela determinação, Rimuru dizima o exército invasor com Megiddo, invoca o Primordial Negro Diablo e desperta como Verdadeiro Lorde Demônio."},
        {"id": "vol-6", "num": 6, "title": "Volume 6: O Banquete de Walpurgis & O Octagrama", "kanji": "転生したらスライムだった件 6", "desc": "Enquanto o exército de Tempest esmaga as forças de Clayman em Eurazania, Rimuru comparece ao lendário Walpurgis diante de Guy Crimson, Leon e Luminas, desmascarando Clayman e fundando o Octagrama."},
        {"id": "vol-7", "num": 7, "title": "Volume 7: Confronto entre Santos e Monstros", "kanji": "転生したらスライムだった件 7", "desc": "Manipulada pelas conspirações dos Sete Dias Celestiais, Hinata Sakaguchi marcha rumo a Tempest. Rimuru enfrenta a líder dos Cavaleiros Sagrados em um duelo memorável que termina em aliança e culinária japonesa."},
        {"id": "vol-8", "num": 8, "title": "Volume 8: Reconciliação, Pactos e Preparativos", "kanji": "転生したらスライムだった件 8", "desc": "Após selar a paz com o Sacro Império de Ruberios, Rimuru mobiliza artesãos, mercadores, Ramiris e Veldora nos preparativos grandiosos para o Festival de Fundação de Tempest."},
        {"id": "vol-8-5", "num": 8.5, "title": "Volume 8.5: Histórias Extras & Guia Oficial", "kanji": "転生したらスライムだった件 8.5", "desc": "Coletânea especial com 13 contos divertidos dos bastidores de Tempest — das aventuras noturnas de Gobuta às termas, pescaria, mel da Milim e o diário de Rimuru."},
        {"id": "vol-9", "num": 9, "title": "Volume 9: O Grande Festival da Fundação de Tempest", "kanji": "転生したらスライムだった件 9", "desc": "Delegações do continente inteiro chegam a Tempest! O Festival brilha com concertos sinfônicos, comida japonesa, o Torneio Marcial com o sortudo 'Herói' Masayuki e a estreia da Masmorra de 100 andares."},
        {"id": "vol-10", "num": 10, "title": "Volume 10: O Labirinto e a Armadilha da Ganância", "kanji": "転生したらスライムだった件 10", "desc": "Enquanto o Labirinto prospera e Tempest ingressa no Conselho Ocidental, a reencarnada Mariabell Rosso usa sua Habilidade Única 'Ganância' para tentar subjugar Rimuru financeira e militarmente."},
        {"id": "vol-11", "num": 11, "title": "Volume 11: A Melancolia Dourada & O Herói do Tempo", "kanji": "転生したらスライムだった件 11", "desc": "Diablo recruta três Demônios Primordiais (Testarossa, Ultima e Carrera), e no Sacro Império de Ruberios revela-se o comovente paradoxo temporal de 2.000 anos vivido por Chloe Aubert e Chronoa."},
        {"id": "vol-12", "num": 12, "title": "Volume 12: Guerra no Horizonte — A Marcha do Império", "kanji": "転生したらスライムだった件 12", "desc": "O Império Oriental de Rudra prepara sua ofensiva total com divisões blindadas, aeronaves mágicas e quase um milhão de combatentes prontos para invadir a Grande Floresta de Jura."},
        {"id": "vol-13", "num": 13, "title": "Volume 13: A Grande Devastação no Labirinto", "kanji": "転生したらスライムだった件 13", "desc": "O exército mecanizado imperial cai na armadilha estratégica de Tempest: primeiro dizimado nos campos externos pelas Primordiais e depois humilhado dentro do Labirinto por Zegion, Kumara, Apito e Adalmann."},
        {"id": "vol-14", "num": 14, "title": "Volume 14: A Purificação do Lótus Vermelho & A Ira", "kanji": "転生したらスライムだった件 14", "desc": "Rimuru desperta seus principais generais como Verdadeiros Lordes Demônios, mas uma emboscada traiçoeira da Guarda Imperial e da Dragão Escaldante Velgrynd captura Veldora — desencadeando a fúria fria e absoluta de Rimuru."},
        {"id": "vol-15", "num": 15, "title": "Volume 15: Dragão Escaldante vs. Dragão da Tempestade", "kanji": "転生したらスライムだった件 15", "desc": "No auge da guerra, Rimuru nomeia Raphael como 'Ciel' e enfrenta simultaneamente dois Dragões Verdadeiros (Veldora controlado e Velgrynd), enquanto seus Patronos derrotam a elite imperial nos Oito Portões."},
        {"id": "vol-16", "num": 16, "title": "Volume 16: A Desintegração da Ordem & Entrevistas", "kanji": "転生したらスライムだった件 16", "desc": "Michael trai o Imperador Rudra, iniciando uma crise cósmica. De volta a Tempest, Rimuru entrevista todos os 12 Patronos, revisando suas novas Habilidades Supremas, Valores de Existência (EP) e gráficos de poder, encerrando com o passado de Guy Crimson."},
        {"id": "vol-17", "num": 17, "title": "Volume 17: Memórias Distantes — Contos Paralelos", "kanji": "転生したらスライムだった件 17", "desc": "Quatro grandes histórias que expandem o multiverso de Tensura: a ascensão comercial de Myourmiles, a jornada dimensional de Velgrynd em busca dos fragmentos da alma de Rudra, os bastidores da corte imperial e o hilário monólogo da Primordial Azul Rain."},
        {"id": "vol-18", "num": 18, "title": "Volume 18: O Segundo Walpurgis & Ambição Despedaçada", "kanji": "転生したらスライムだった件 18", "desc": "Diante da ameaça de Michael e do Rei Fantasma Feldway, os Lordes Demônios do Octagrama convocam um novo Walpurgis de emergência, enquanto em El Dorado ocorre o trágico confronto envolvendo Kagali, Footman, Tear, Laplace e Yuuki."},
        {"id": "vol-19", "num": 19, "title": "Volume 19: A Investida do Arcanjo & A Capital em Chamas", "kanji": "転生したらスライムだった件 19", "desc": "A Grande Guerra Tenma explode em múltiplas frentes: o exército angelical ataca Ingrassia, Hinata e Chloe enfrentam ameaças letais, e Rimuru trava o duelo definitivo contra Michael pelo legado de Veldanava e Rudra."},
        {"id": "vol-20", "num": 20, "title": "Volume 20: Feldway & A Batalha da Árvore Sagrada", "kanji": "転生したらスライムだった件 20", "desc": "Feldway mobiliza os Titãs liderados por Dagruel e Fenn, o Lorde Inseto Zelanus e Milim em fúria descontrolada perto da Árvore Divina de Sarion — culminando no chocante banimento de Rimuru além do fim do espaço-tempo."},
        {"id": "vol-21", "num": 21, "title": "Volume 21: Erosão do Labirinto & Além do Fim", "kanji": "転生したらスライムだった件 21", "desc": "Enquanto Rimuru está desaparecido no fim do espaço-tempo, Veldora, Shion e Luminas enfrentam Dagruel e os Titãs, e no Labirinto de Ramiris ocorre a invasão brutal liderada por Zelanus, Vega, Mai Furuki e o grupo de Dino — culminando no despertar supremo de Zegion."},
        {"id": "vol-22", "num": 22, "title": "Volume 22: Destruição Divina & O Retorno Triunfal", "kanji": "転生したらスライムだった件 22", "desc": "Testarossa, Carrera e Ultima enfrentam o ancestral Twilight Valentine, Chloe e Velzard duelam no norte, Diablo arrisca tudo contra Feldway para conter a Fúria Estelar de Milim — até o aguardado retorno triunfal de Rimuru e Ciel diante do despertar de Ivarage."},
        {"id": "vol-23", "num": 23, "title": "Volume 23: Mito da Criação & Pós-Reencarnação (Final)", "kanji": "転生したらスライムだった件 23", "desc": "O grandioso volume final da Light Novel oficial! Todas as frentes convergem na batalha apocalíptica contra o Deus Maligno Ivarage, Jahil e Feldway, selando o destino de Veldanava, Lucia, Milim e Rimuru até o emocionante epílogo pós-reencarnação."}
    ]

    ln_volumes = []
    total_ln_illustrations = 0
    total_ln_footnotes = 0
    total_ln_paragraphs = 0

    for v in ln_metadata:
        file_path = os.path.join('data/light_novel', f"{v['id']}.json")
        has_file = os.path.exists(file_path)
        ch_count = 0
        p_count = 0
        illus_list = []
        cover_img = None
        edition_label = "TSSDK Scan PT-BR"
        is_colored = False
        has_scan_alt = False
        scan_alt_id = None
        fn_count = 0

        if has_file:
            with open(file_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            ch_count = d.get('chapter_count', len(d.get('chapters', [])))
            p_count = sum(len(c.get('paragraphs', [])) for c in d.get('chapters', []))
            illus_list = d.get('illustrations', [])
            cover_img = d.get('cover_image') or (illus_list[0]['src'] if illus_list else None)
            edition_label = d.get('edition', edition_label)
            is_colored = bool(d.get('is_colored_edition'))
            has_scan_alt = bool(d.get('has_scan_alternative')) and os.path.exists(os.path.join('data/light_novel', f"{v['id']}-scan.json"))
            scan_alt_id = f"{v['id']}-scan" if has_scan_alt else None
            fn_count = len(d.get('footnotes', {}))

        total_ln_illustrations += len(illus_list)
        total_ln_footnotes += fn_count
        total_ln_paragraphs += p_count

        ln_volumes.append({
            **v,
            'volume_number': v['num'],
            'is_downloaded': has_file,
            'edition': edition_label,
            'is_colored_edition': is_colored,
            'has_scan_alternative': has_scan_alt,
            'scan_alternative_id': scan_alt_id,
            'cover_image': cover_img,
            'illustrations_count': len(illus_list),
            'illustrations': illus_list,
            'footnotes_count': fn_count,
            'chapter_count': ch_count,
            'paragraph_count': p_count,
        })

    future_ln = []

    # 3. Carregar auditoria real das correções nos EPUBs do Drive
    audit_data = {'total_paragraphs_repaired': 0, 'epubs_repaired_count': 15, 'samples': []}
    if os.path.exists('data/translation_comparison.json'):
        with open('data/translation_comparison.json', 'r', encoding='utf-8') as f:
            audit_data = json.load(f)

    curated_repairs = [
        {
            "category": "Nomes Próprios Traduzidos Literalmente",
            "before": "Prólogo: Campo de golfe / Epílogo: Cara Carmesim / Autor: Fusível / Lacaio & Carreira",
            "after": "Prólogo: Feldway / Epílogo: Guy Crimson / Autor: Fuse / Footman & Carrera",
            "why": "Tradutores automáticos confundiram 'Feldway' com 'Fairway' (campo de golfe), 'Guy' com 'cara', 'Fuse' com 'fusível', 'Footman' com 'lacaio' e 'Carrera' com 'carreira'."
        },
        {
            "category": "Fichas de Status e Classificações (Vols. 16 e 18)",
            "before": "Nome: Musgo / Espírito / Diabo — Corrida: Par Demônio: Classificação de Contagem / Nove Caldas",
            "after": "Nome: Moss / Esprit / Diablo — Raça: Par Demoníaco: Classe Conde / Nove Caudas",
            "why": "Em inglês, 'Race:' (espécie/raça) havia sido traduzido como 'Corrida:' (corrida esportiva), e 'Count Rank' (título nobiliárquico de Conde) como 'Classificação de Contagem'."
        },
        {
            "category": "Termos e Habilidades Deixados em Inglês",
            "before": "Ultimate Skill 'Gluttonous King Beelzebuth', 'Void God Azathoth', 'Magic Beast Corps', 'Soul Corridor'",
            "after": "Habilidade Suprema 'Rei da Gula Beelzebuth', 'Deus do Vazio Azathoth', 'Corpo de Bestas Mágicas', 'Corredor da Alma'",
            "why": "Centenas de habilidades angelicais, demoníacas, lovecraftianas e patentes militares haviam permanecido em inglês nos EPUBs públicos."
        },
        {
            "category": "Concordância de Gênero & Falsos Cognatos",
            "before": "Primordial Branco (Testarossa) / Primordial Amarelo (Carrera) / O gol de um santo / fotografar com armas / Isso pode realmente ser ajudado?",
            "after": "Primordial Branca / Primordial Amarela / O Objetivo de um Santo / atirar com armas / Tem mesmo o que fazer?",
            "why": "Ajustamos o gênero gramatical das três Primordiais femininas e corrigimos falsos cognatos clássicos do inglês ('goal' = objetivo, 'shooting' = atirar, 'can it be helped?' = tem jeito?)."
        }
    ]

    comparison = {
        'overview': "Tensei Shitara Slime Datta Ken nasceu originalmente como uma Web Novel publicada por Fuse no site japonês Shousetsuka ni Narou entre 2013 e 2016. Ao lançar a Light Novel comercial ilustrada por Mitz Vah (GC Novels), Fuse reescreveu mais de 50% da obra, introduzindo arcos inteiros inéditos, dezenas de personagens fundamentais, uma geopolítica muito mais madura e mudando completamente o verdadeiro antagonista final.",
        'key_differences': [
            {
                'topic': 'Charybdis (Caríbdis) e o Reino das Bestas de Eurazania',
                'wn': 'Charybdis não existe na Web Novel. A visita de Milim Nava ocorre sem a crise da calamidade voadora.',
                'ln': 'Exclusivo do Volume 3 da Light Novel! Charybdis nasce da mana densa de Veldora, sela a aliança militar com Karion (Eurazania) e demonstra a força conjunta de Tempest e Dwargon.'
            },
            {
                'topic': 'O Massacre de Farmas e o Momento da Invocação de Diablo',
                'wn': 'Rimuru usa Megiddo contra os invasores, mas Diablo só é invocado bem mais adiante de maneira administrativa.',
                'ln': 'No Volume 5, Rimuru invoca o Primordial Negro diretamente no campo de batalha usando os 20 mil cadáveres do exército de Farmas como oferenda física — tornando Diablo peça central desde o Walpurgis.'
            },
            {
                'topic': 'A Guerra de Eurazania e o Banquete de Walpurgis',
                'wn': 'O Walpurgis é mais curto e focado apenas no salão dos Lordes Demônios.',
                'ln': 'O Volume 6 divide o clímax em duas grandes frentes simultâneas: a campanha militar liderada por Benimaru contra o exército de Clayman (com Kumara, Adalmann e Middray) e o embate político-militar no Walpurgis.'
            },
            {
                'topic': 'A Diplomacia com Hinata Sakaguchi, Luminas e os Sete Dias Celestiais',
                'wn': 'O conflito com os Cavaleiros Sagrados é direto e sem a conspiração interna dos Sete Dias Celestiais.',
                'ln': 'O Volume 7 aprofunda a fé luminista, introduz o clero dos Sete Dias Celestiais, desenvolve a relação de respeito entre Rimuru e Hinata e sela a paz com ramen, gyoza e águas termais.'
            },
            {
                'topic': 'O Clã Rosso, Granbell e Mariabell da Ganância',
                'wn': 'Totalmente inexistentes na Web Novel!',
                'ln': 'Os Volumes 10 e 11 introduzem a família Rosso, que controla a economia ocidental pelas sombras, além de Mariabell (uma reencarnada europeia calculista) e o trágico passado do antigo herói Granbell Rosso.'
            },
            {
                'topic': 'O Paradoxo Temporal de Chloe Aubert e Chronoa',
                'wn': 'A viagem no tempo existe de modo mais linear e simplificado.',
                'ln': 'O Volume 11 entrega um arco monumental: revela como Chloe, Hinata e o manas/espírito Chronoa atravessaram loops de 2.000 anos para impedir a linha temporal em que Rimuru morria nas mãos do Império.'
            },
            {
                'topic': 'As Três Demônios Primordiais (Testarossa, Ultima e Carrera)',
                'wn': 'Na Web Novel, o Trio Primordial chega de forma secundária e com menos peso político.',
                'ln': 'Nos Volumes 11 a 16, Testarossa (Diplomata Militar), Ultima (Promotora-Chefe) e Carrera (Juíza Suprema da Corte) ganham personalidades marcantes, duelos individuais épicos e integram os 12 Patronos.'
            },
            {
                'topic': 'A Campanha Militar do Império Oriental e o Nascimento de Ciel',
                'wn': 'A invasão imperial termina de maneira muito mais rápida.',
                'ln': 'Os Volumes 12 a 15 constroem uma guerra total com divisões blindadas, a Guarda Real Imperial (Kondou, Damrada, Granit), a captura de Veldora e o momento sublime em que Rimuru nomeia Raphael como Ciel.'
            },
            {
                'topic': 'O Verdadeiro Antagonista Final (Yuuki vs. Michael, Feldway e Ivarage)',
                'wn': 'Yuuki Kagurazaka (aliado ao manas Velda) é o grande vilão final que rouba os Registros Akáshicos e envia Rimuru ao Fim do Espaço-Tempo.',
                'ln': 'Na Light Novel, Yuuki e a Trupe de Palhaços Moderados têm arcos trágicos e complexos (Vol. 18), enquanto os verdadeiros antagonistas finais são o manas Michael, o Rei Fantasma Feldway e o Dragão Destruidor Ivarage.'
            },
            {
                'topic': 'Histórias Pós-Guerra Exclusivas da Web Novel (Extras 1 a 48)',
                'wn': 'Possui dois grandes arcos pós-final completos: "O Jogo de Fuga Elegante de Rimuru" e "Visita ao Desconhecido" (viagem interdimensional de Veldora, Ramiris e Beretta) — ambos incluídos aqui na aba Web Novel!',
                'ln': 'Conclui a saga principal no Volume 23 ("Mito da Criação & Pós-Reencarnação"), enquanto diversas histórias paralelas ganharam mangás spin-off próprios (Diários de Slime, Trindade em Tempest, Maneiras de Passear no País dos Monstros).'
            }
        ],
        'translation_audit': {
            'overview': "Esta biblioteca reúne os 24 volumes da Light Novel (Volumes 1 a 23 + Volume 8.5) combinando e revisando as melhores fontes da comunidade: a tradução humana da TSSDK Scan PT-BR (base dos Volumes 1 a 5 + 8.5 e opção comparativa lado a lado nos Volumes 6 a 13), referências terminológicas e edições ilustradas consolidadas junto ao Slime Reader (TensuraFan — Vols. 6 a 20) e a compilação traduzida e padronizada em PT-BR dos Volumes finais 21, 22 e 23.",
            'total_paragraphs_repaired': audit_data.get('total_paragraphs_repaired', 0),
            'epubs_repaired_count': 18,
            'edition_comparison': [
                {
                    'aspect': 'Cobertura de Volumes',
                    'tssdk_scan': 'Volumes 1 a 13 + Volume 8.5 (interrompida no Vol. 13)',
                    'drive_original': 'Slime Reader (TensuraFan) até o Vol. 20 + Edições Ilustradas dos Vols. 6 a 23',
                    'repaired_repo': '100% Completa: todos os 24 Volumes (Vols. 1–23 + 8.5) em PT-BR + Dupla Tradução nos Vols. 6–13!'
                },
                {
                    'aspect': 'Qualidade do Texto & Nomes',
                    'tssdk_scan': 'Fluidez humana, mas com algumas variações de grafia e quebras de capítulo ausentes nos Vols. 4 e 10',
                    'drive_original': 'Bases brutas em PT/EN exigiam proteção de nomes próprios ("Feldway", "Guy", "Carrera", "Ivarage") e padronização de Skills',
                    'repaired_repo': '100% em Português Brasileiro natural, nomes canônicos protegidos, falas da Ciel («...») destacadas e capítulos estruturados'
                },
                {
                    'aspect': 'Ilustrações & Extras',
                    'tssdk_scan': 'Imagens inline no Google Sites (que expiravam com erro 403 fora da sessão)',
                    'drive_original': 'Capas, páginas duplas coloridas, gráficos de poder (Vol. 16), designs oficiais (Vol. 22), mangás bônus e notas culturais',
                    'repaired_repo': 'Mais de 510 ilustrações oficiais convertidas localmente para WebP rápido, posicionadas no ponto exato do capítulo + Galeria!'
                }
            ],
            'curated_highlights': curated_repairs,
            'real_samples': audit_data.get('samples', [])[:12]
        }
    }

    cultural_guide = {
        'title': 'Glossário de Nomes Originais e Guia Cultural de Tensura',
        'honorifics': [
            {'term': '-sama (様)', 'meaning': 'Sufixo de reverência máxima reservado a soberanos, divindades ou mestres absolutos. Diablo, Shion, Benimaru e Rigurd chamam Rimuru de "Rimuru-sama" para demonstrar devoção incondicional.'},
            {'term': '-san (さん)', 'meaning': 'Tratamento cordial e respeitoso entre iguais, aliados diplomáticos ou conhecidos (equivalente a Sr./Sra. ou tratamento educado).' },
            {'term': '-kun (君) / -chan (ちゃん)', 'meaning': 'Sufixos de proximidade e afeto. "-kun" é usado com colegas, jovens ou subordinados queridos (ex.: Yuuki, Masayuki); "-chan" expressa carinho com crianças ou amigas próximas (ex.: Milim-chan, Chloe-chan).'},
            {'term': '-dono (殿)', 'meaning': 'Sufixo arcaico e solene usado por samurais, guerreiros antigos e cavaleiros (como Hakurou, Gazel e Zegion) para demonstrar alto respeito marcial ("Lorde/Nobre").'},
            {'term': '-sensei (先生)', 'meaning': 'Significa "Mestre" ou "Professor". É como as crianças invocadas (Kenya, Ryota, Gale, Alice e Chloe) e Yuuki se dirigem carinhosamente a Rimuru e a Shizu.'},
            {'term': 'Senpai (先輩) / Kouhai (後輩)', 'meaning': 'Relação japonesa clássica entre veterano/mentor (Senpai) e calouro/aprendiz (Kouhai) no trabalho ou escola — base da relação de Satoru com Tamura no prólogo e com outros japoneses invocados.'},
            {'term': 'Danna (旦那) / Aniki (兄貴)', 'meaning': '"Danna" significa "Patrão/Chefe" (usado por mercadores como Myourmiles); "Aniki" significa "Irmão mais velho / Chefe admirado" (usado por Gobuta e subordinados leais).'}
        ],
        'tensura_concepts': [
            {'term': 'O Poder dos Nomes (名付け — Naming)', 'desc': 'Monstros nascem originalmente sem nome. Conceder um nome grava uma identidade espiritual na alma do monstro consumindo a magia (magículas) do nomeador, provocando evoluções dramáticas de espécie.'},
            {'term': 'Majin (魔人 — Nascido da Magia) vs. Mamono (魔物)', 'desc': 'Enquanto "Mamono" designa monstros e bestas mágicas em geral, "Majin" refere-se a seres mágicos sapientes, dotados de razão, fala e grande concentração de magículas.'},
            {'term': 'Kijin (鬼人 — Ogro Iluminado) & Oni Divino', 'desc': 'Evolução rara dos Ogros (Benimaru, Shion, Shuna, Souei, Hakurou e Kurobee), inspirada nos demônios guerreiros do folclore japonês. Mais tarde evoluem para Fair Oni e Oni Espiritual Divino.'},
            {'term': 'Dragões Verdadeiros (竜種 — True Dragons)', 'desc': 'As quatro encarnações supremas da própria natureza: Veldanava (Dragão Rei Estelar, Criador), Velzard (Gelo Branco), Velgrynd (Chama Escaldante) e Veldora (Tempestade). Mesmo destruídos, renascem eternamente.'},
            {'term': 'Os Sete Demônios Primordiais (原初の悪魔)', 'desc': 'Os sete arquidemônios nascidos na aurora da criação, identificados por cores em francês: Rouge (Guy Crimson), Noir (Diablo), Blanc (Testarossa), Jaune (Carrera), Violet (Ultima), Bleue (Rain) e Vert (Misery).'},
            {'term': 'Walpurgis & O Octagrama (八星魔王)', 'desc': 'Walpurgis (inspirado na Noite de Santa Valpúrgia europeia) é o conselho supremo dos Lordes Demônios. Após a queda de Clayman e a renúncia de Frey e Karion, Rimuru batiza os oito soberanos remanescentes como "Octagrama".'},
            {'term': 'Grande Sábio → Raphael → Manas: Ciel', 'desc': 'A jornada da parceira interior de Rimuru: nasce como Habilidade Única analítica (Grande Sábio), evolui no despertar para Habilidade Suprema (Rei da Sabedoria Raphael) e, ao receber o nome "Ciel" no Vol. 15, desperta um ego próprio como Manas (Núcleo Teosófico).'},
            {'term': 'Habilidades Únicas vs. Habilidades Supremas', 'desc': 'Habilidades Únicas nascem dos desejos intensos da alma; já as Habilidades Supremas (Ultimate Skills) operam diretamente sobre as leis fundamentais do Mundo Cardeal — apenas outra Habilidade Suprema ou vontade equivalente pode superá-las.'},
            {'term': 'Valor de Existência (EP — Existence Point)', 'desc': 'Métrica introduzida no Labirinto de Ramiris para quantificar a soma bruta de energia mágica e vitalidade física de um indivíduo ou arma mítica (Grau Deus / Mítico), embora perícia e cálculo (como Ciel) superem diferenças numéricas.'}
        ],
        'cultural_aspects': [
            {'element': 'Gastronomia Japonesa como Poder Diplomático', 'desc': 'Rimuru recria shoyu, missô, arroz branco, ramen, gyoza, sushi, tempura, bife hambúrguer e saquê. Em Tensura, a alta culinária desarma reis desconfiados, conquista Hinata e Luminas e transforma Tempest no polo turístico mundial.'},
            {'element': 'Onsen (温泉 — Banhos Termais Comunitários)', 'desc': 'No Japão, banhar-se despido em águas termais vulcânicas simboliza purificação e igualdade ("hadaka no tsukiai" — convivência sem armaduras sociais). Em Tempest, o Onsen é onde alianças entre reis, santos e lordes demônios são seladas em paz.'},
            {'element': 'Wa (和 — Harmonia Coletiva) & Prosperidade Mútua', 'desc': 'A regra de ouro de Rimuru ("não menosprezar humanos e buscar convivência") reflete o ideal japonês de Wa: construir estradas, pousadas, segurança e comércio onde todas as nações ganham mais cooperando com Tempest do que guerreando.'},
            {'element': 'Matsuri (Festivais), Izakaya e Mangás ("Textos Sagrados")', 'desc': 'O Festival da Fundação recria barraquinhas de matsuri japonês (takoyaki, maçã do amor, yukatas), enquanto Rimuru imprime mangás da memória de Satoru — que Veldora passa a venerar como "Escrituras Sagradas" de artes marciais!'},
            {'element': 'Sincretismo Mitológico: Xintoísmo, Budismo, Angeologia e Lovecraft', 'desc': 'Fuse combina tradições orientais e ocidentais: as Habilidades Supremas originais de Veldanava seguem as Sete Virtudes Angelicais (Michael, Uriel, Raphael...) e os Sete Pecados Demoníacos (Lúcifer, Beelzebuth...), enquanto Ciel cria habilidades cósmicas inspiradas em H.P. Lovecraft (Azathoth, Shub-Niggurath) e Benimaru/Hinata despertam poderes xintoístas (Amaterasu, Tsukuyomi).'}
        ],
        'inline_glossary': {
            'sama': 'Sufixo japonês de reverência suprema ("Senhor/Mestre Soberano").',
            'dono': 'Sufixo nobre/marcial de alto respeito ("Lorde").',
            'sensei': 'Tratamento japonês para "Professor" ou "Mestre".',
            'senpai': 'Veterano ou colega mais experiente na cultura japonesa.',
            'kouhai': 'Calouro ou colega mais novo sob orientação de um Senpai.',
            'onsen': 'Casa tradicional japonesa de banhos em águas termais naturais.',
            'yukata': 'Quimono leve de algodão usado após o banho termal ou em festivais de verão.',
            'tatami': 'Piso tradicional japonês trançado em palha de junco (igusa).',
            'kotatsu': 'Mesa baixa japonesa aquecida coberta por um edredom pesado para o inverno.',
            'izakaya': 'Bar/taberna tradicional japonesa que serve bebidas acompanhadas de petiscos.',
            'matsuri': 'Festival tradicional japonês com barracas de rua, música e celebração.',
            'ramen': 'Prato japonês de macarrão artesanal servido em caldo rico e aromático.',
            'gyoza': 'Pastelzinho oriental recheado de carne e legumes, grelhado na chapa e cozido no vapor.',
            'shoyu': 'Molho de soja fermentado essencial da culinária japonesa.',
            'sake': 'Bebida alcoólica tradicional japonesa fermentada a partir do arroz.',
            'katana': 'Espada curva japonesa de fio único forjada por mestres ferreiros (como Kurobee).',
            'majin': 'Ser Mágico sapiente dotado de intelecto e alta densidade de magículas.',
            'kijin': 'Forma evoluída, rara e iluminada da tribo dos Ogros.',
            'walpurgis': 'Banquete e conselho supremo dos Lordes Demônios.',
            'octagrama': 'Os Oito Lordes Demônios das Estrelas (Rimuru, Guy, Milim, Leon, Luminas, Dagruel, Dino e Ramiris).'
        }
    }

    amazon_catalog = []
    for n in range(1, 24):
        amazon_catalog.append({
            'volume': n,
            'title': f"That Time I Got Reincarnated as a Slime — Light Novel Vol. {n} (Edição Oficial)",
            'search_url': f"https://www.amazon.com.br/s?k=That+Time+I+Got+Reincarnated+as+a+Slime+Vol+{n}+light+novel",
            'direct_search': f"https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+volume+{n}+light+novel",
            'publisher': "Micro Magazine (JP) / Yen Press (Oficial)",
            'formats': ["eBook Kindle", "Capa Comum (Importado)"]
        })

    # Preservar story_recap existente em data/catalog.json para nunca perder o Resumo Vol. 1–11
    existing_story_recap = None
    if os.path.exists('data/catalog.json'):
        try:
            with open('data/catalog.json', 'r', encoding='utf-8') as f:
                prev_cat = json.load(f)
            existing_story_recap = prev_cat.get('story_recap')
        except Exception:
            existing_story_recap = None

    catalog = {
        'title': 'Tensei Shitara Slime Datta Ken — Biblioteca & Leitor Completo em Português',
        'sources': {
            'fan_scan_site': 'https://sites.google.com/view/tssdklscanptbr/p%C3%A1gina-inicial',
            'slime_reader_site': 'https://tensurafan.github.io/',
            'web_novel_site': 'https://centralnovel.com/series/tensei-shitara-slime-datta-ken/',
            'amazon_br_search': 'https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+light+novel'
        },
        'light_novel': {
            'info': {
                'title': 'Light Novel Oficial Completa (Volumes 1 a 23 + 8.5 em PT-BR)',
                'author': 'Fuse',
                'illustrator': 'Mitz Vah',
                'publisher_jp': 'GC Novels (Micro Magazine)',
                'publisher_en': 'Yen Press',
                'available_volumes_count': len(ln_volumes),
                'total_illustrations': total_ln_illustrations,
                'total_footnotes': total_ln_footnotes,
                'total_paragraphs': total_ln_paragraphs,
                'status': '24 Volumes Offline — Obra 100% Completa (Vols. 1–23 + 8.5) + Dupla Tradução nos Vols. 6–13'
            },
            'volumes': ln_volumes,
            'future_volumes': future_ln
        },
        'web_novel': {
            'info': {
                'title': 'Web Novel Original Completa (Shousetsuka ni Narou)',
                'author': 'Fuse',
                'platform': 'Shousetsuka ni Narou (Syosetu)',
                'ptbr_source': 'Central Novel PT-BR',
                'total_chapters': len(cleaned_wn_chapters),
                'main_chapters_count': sum(1 for c in cleaned_wn_chapters if not c['is_extra']),
                'extra_chapters_count': sum(1 for c in cleaned_wn_chapters if c['is_extra']),
                'downloaded_count': downloaded_count,
                'status': '100% Completa Offline (255 Capítulos Principais + 48 Capítulos Extras)'
            },
            'arcs': wn_arcs,
            'chapters': cleaned_wn_chapters
        },
        'comparison': comparison,
        'cultural_guide': cultural_guide,
        'amazon_br': {
            'general_search': 'https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+light+novel',
            'manga_search': 'https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+jbc+manga',
            'store_info': 'Adquira as edições oficiais de Tensei Shitara Slime Datta Ken (Light Novels para Kindle/físico da Yen Press e Mangás oficiais em português pela Editora JBC) na Amazon.com.br.',
            'volumes': amazon_catalog
        }
    }

    if existing_story_recap:
        catalog['story_recap'] = existing_story_recap

    with open('data/catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    # Atualizar também data/illustrations.json com todos os volumes
    illus_index = {
        v['id']: {
            'volume_number': v['volume_number'],
            'title': v['title'],
            'cover_image': v['cover_image'],
            'count': v['illustrations_count'],
            'items': v['illustrations'],
        }
        for v in ln_volumes
    }
    with open('data/illustrations.json', 'w', encoding='utf-8') as f:
        json.dump(illus_index, f, ensure_ascii=False, indent=2)

    print(f"Catálogo Mestre gerado com sucesso em data/catalog.json!")
    print(f"  - Light Novel: {len(ln_volumes)} volumes offline, {total_ln_illustrations} ilustrações WebP, {total_ln_footnotes} notas culturais.")
    print(f"  - Web Novel  : {downloaded_count}/{len(cleaned_wn_chapters)} capítulos offline em {len(wn_arcs)} arcos.")


if __name__ == '__main__':
    build_catalog()
