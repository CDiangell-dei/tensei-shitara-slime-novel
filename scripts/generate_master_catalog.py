import json
import os
import re

def build_catalog():
    # 1. Load Web Novel index
    with open('web_novel_index.json', 'r', encoding='utf-8') as f:
        wn_raw = json.load(f)
        
    wn_downloaded = set()
    if os.path.exists('data/web_novel'):
        for f in os.listdir('data/web_novel'):
            if f.endswith('.json'):
                m = re.search(r'capitulo_(\d+)', f)
                if m:
                    wn_downloaded.add(int(m.group(1)))
                    
    wn_arcs = [
        {
            "id": "arc-1",
            "num": 1,
            "title": "Arco 1: Empoderamento dos Monstros (Reencarnação)",
            "range": [0, 16],
            "desc": "Satoru Mikami reencarna no mundo de fantasia como um Slime, conhece o Dragão da Tempestade Veldora, assume o nome Rimuru Tempest, salva os Goblins e lobos da presa (Direwolves) e viaja ao Reino Armado de Dwargon."
        },
        {
            "id": "arc-2",
            "num": 2,
            "title": "Arco 2: Agitação na Floresta de Jura",
            "range": [17, 34],
            "desc": "A chegada dos Ogros sobreviventes (que evoluem para Kijin), a grande invasão de 200 mil Orcs comandados pelo Lorde Orc Geld e a fundação da Federação de Jura Tempest."
        },
        {
            "id": "arc-3",
            "num": 3,
            "title": "Arco 3: A Vida na Cidade dos Monstros & Shizu",
            "range": [35, 64],
            "desc": "O crescimento civilizatório de Tempest, a herança e os desejos de Shizu Izawa, a visita da Lorde Demônio Milim Nava e a ida de Rimuru à capital humana de Ingrassia."
        },
        {
            "id": "arc-4",
            "num": 4,
            "title": "Arco 4: O Nascimento do Lorde Demônio",
            "range": [65, 81],
            "desc": "A invasão covarde e violenta das tropas do Reino de Farmas, a trágica perda de companheiros, o uso do feitiço Megiddo e o despertar de Rimuru como Verdadeiro Lorde Demônio."
        },
        {
            "id": "arc-5",
            "num": 5,
            "title": "Arco 5: O Despertar dos Espíritos & Walpurgis",
            "range": [82, 104],
            "desc": "A reunião secreta dos Lordes Demônios (Walpurgis), a queda definitiva do conspirador Clayman e o estabelecimento do Octagrama (Os Oito Lordes Demônios das Estrelas)."
        },
        {
            "id": "arc-6",
            "num": 6,
            "title": "Arco 6: O Retorno da Paz e a Abertura do Labirinto",
            "range": [105, 122],
            "desc": "A consagração de Tempest no cenário mundial, festivais de artes marciais e a criação do labirinto subterrâneo com Ramiris e Veldora."
        },
        {
            "id": "arc-7",
            "num": 7,
            "title": "Arco 7: A Invasão do Império Oriental",
            "range": [123, 145],
            "desc": "O Império Oriental sob o Imperador Rudra inicia sua marcha devastadora com forças mecanizadas e tropas blindadas, colidindo com as defesas do Labirinto de Tempest."
        },
        {
            "id": "arc-8",
            "num": 8,
            "title": "Arco 8: A Guerra entre Dragões e Demônios",
            "range": [146, 170],
            "desc": "O confronto direto com os Dragões Verdadeiros (Velgrynd e Veldora) e a evolução dos 12 principais subordinados de Rimuru para Lordes Demônios Despertos."
        },
        {
            "id": "arc-9",
            "num": 9,
            "title": "Arco 9: Choque dos Céus e da Terra (Guerra Final)",
            "range": [171, 240],
            "desc": "A grande guerra celestial multiverso contra o exército angelical e os poderes divinos da Origem, culminando na revelação dos segredos de Yuuki Kagurazaka."
        },
        {
            "id": "arc-10",
            "num": 10,
            "title": "Arco 10: Conclusão, Pós-Guerra & Histórias Finais",
            "range": [241, 249],
            "desc": "O epílogo da saga cósmica, a paz restaurada no multiverso e o retorno de Rimuru ao mundo original para fechar o ciclo de sua vida humana anterior."
        }
    ]
    
    cleaned_wn_chapters = []
    for ch in wn_raw:
        raw_t = ch['title']
        clean_t = raw_t
        m = re.search(r'Cap\.\s*\d+\s*(?:\[Fim\])?\s*(.*?)(?:novembro|dezembro|janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|\d{4}|$)', raw_t, re.IGNORECASE)
        if m and m.group(1).strip():
            clean_t = m.group(1).strip()
        else:
            parts = re.split(r'Cap\.\s*\d+\s*', raw_t)
            if len(parts) > 1:
                clean_t = parts[-1].strip()
        
        ch_num = ch['num']
        arc_id = "arc-10"
        for a in wn_arcs:
            if a['range'][0] <= ch_num <= a['range'][1]:
                arc_id = a['id']
                break
                
        cleaned_wn_chapters.append({
            'num': ch_num,
            'title': clean_t if clean_t else f"Capítulo {ch_num}",
            'url': ch['url'],
            'arc_id': arc_id,
            'is_downloaded': ch_num in wn_downloaded
        })
        
    ln_metadata = [
        {"id": "vol-1", "num": 1, "title": "Volume 1: Morte e Reencarnação", "kanji": "転生したらスライムだった件 1", "chapters_summary": "Prólogo, Capítulos 1 a 4, Capítulo Final, Posfácio do Autor, História Especial de Hinata Sakaguchi", "desc": "Satoru Mikami, um assalariado comum de 37 anos, é assassinado em Tóquio e reencarna em uma caverna mágica como um Slime. Ele aprende habilidades de predação, faz pacto de fraternidade com o temido Dragão da Tempestade Veldora e sai da caverna para nomear e salvar a aldeia dos Goblins."},
        {"id": "vol-2", "num": 2, "title": "Volume 2: O Despertar da Floresta & O Lorde Orc", "kanji": "転生したらスライムだった件 2", "chapters_summary": "Prólogo, Capítulos 1 a 6, Epílogo", "desc": "Seis Ogros nobres chegam à vila de Rimuru após terem sua aldeia aniquilada. Ao receberem nomes, evoluem para temíveis Kijin. Logo em seguida, surge o pesadelo de um exército faminto de 200 mil Orcs guiados pela terrível habilidade 'Faminto' do Lorde Orc Geld."},
        {"id": "vol-3", "num": 3, "title": "Volume 3: A Ameaça de Charybdis & O Tratado com as Bestas", "kanji": "転生したらスライムだった件 3", "chapters_summary": "Prólogo: A Cúpula dos Lordes Demônios, Capítulos 1 a 4, Epílogo", "desc": "O nascimento oficial da Federação de Jura Tempest. Rimuru recebe a visita extravagante da Lorde Demônio Milim Nava. Pouco depois, uma antiga calamidade dos céus conhecida como Charybdis (Caríbdis) desperta e avança para arrasar a nova nação dos monstros."},
        {"id": "vol-4", "num": 4, "title": "Volume 4: Rumo às Terras Humanas & O Ensino dos Invocados", "kanji": "転生したらスライムだった件 4", "chapters_summary": "Prólogo: Beleza em Ação, Capítulos 1 a 4, Epílogo", "desc": "Em memória e respeito ao último desejo de Shizu Izawa, Rimuru parte disfarçado para o Reino de Ingrassia. Lá, assume como professor da Academia da Liberdade para guiar cinco crianças de outro mundo marcadas pela morte prematura devido ao descontrole de energia mágica."},
        {"id": "vol-5", "num": 5, "title": "Volume 5: Nascimento do Lorde Demônio & Megiddo", "kanji": "転生したらスライムだった件 5", "chapters_summary": "Prólogo: O Dia da Ruína, Capítulos 1 a 4, O Feitiço Megiddo, A Invocação de Diablo", "desc": "Enquanto Rimuru está fora, uma barreira anti-magia enfraquece Tempest e o exército sanguinário do Reino de Farmas massacra dezenas de cidadãos pacíficos, incluindo Shion. Em meio ao desespero, Rimuru toma uma decisão irrevogável: sacrificar o exército invasor com o feitiço de luz 'Megiddo' e colher suas 20 mil almas para se transformar em um Verdadeiro Lorde Demônio."},
        {"id": "vol-6", "num": 6, "title": "Volume 6: O Walpurgis & O Julgamento de Clayman", "kanji": "転生したらスライムだった件 6", "chapters_summary": "Prólogo: O Ardil dos Nascidos da Magia, Capítulos 1 a 6, O Octagrama", "desc": "Agora um Lorde Demônio Desperto, Rimuru é convocado para o lendário banquete dos governantes do mundo: o Walpurgis. Ele desmascara diante de Guy Crimson, Milim e Leon Cromwell as manipulações covardes de Clayman, eliminando-o de uma vez por todas e refundando a aliança dos oito lordes supremos: o Octagrama."},
        {"id": "vol-7", "num": 7, "title": "Volume 7: Demônios e Esquemas & O Confronto com a Santa Igreja", "kanji": "転生したらスライムだった件 7", "chapters_summary": "Prólogo: Memorial do Nascido da Magia, Capítulos 1 a 5, Reconciliação Sagrada", "desc": "A Igreja Santa Ocidental, manipulada pelos Sete Dias Celestiais e pelo ódio doutrinário contra monstros, mobiliza os Santos Cavaleiros liderados pela paladina Hinata Sakaguchi. Rimuru orquestra um duelo honroso e resolve o conflito com diplomacia, inteligência e um lendário banquete de reconciliação regado a ramen e comida típica japonesa."},
        {"id": "vol-8", "num": 8, "title": "Volume 8: Reconciliação, Tratados e Preparativos", "kanji": "転senしたらスライムだった件 8", "chapters_summary": "Prólogo, Relatório de Progresso, Capítulos 1 a 4, Epílogo", "desc": "Com as nações ocidentais pacificadas, Rimuru planeja a maior celebração cultural e tecnológica já vista: o Grande Festival da Fundação de Tempest. Representantes de todos os impérios e reinos são convidados para conhecer o poder e a hospitalidade dos monstros."},
        {"id": "vol-8-5", "num": 8.5, "title": "Volume 8.5: Histórias Extras & Livro de Dados Oficial", "kanji": "転生したらスライムだった件 8.5", "chapters_summary": "O Diário dos Aventureiros, Psychidae Gobuta, Enciclopédia de Personagens e Habilidades", "desc": "Um volume complementar recheado de histórias inéditas, contos do cotidiano divertido de Tempest, fichas técnicas de habilidades e a lendária aventura de Gobuta na Casa Noturna das Elfas."},
        {"id": "vol-9", "num": 9, "title": "Volume 9: O Festival da Fundação de Tempest & O Torneio", "kanji": "転生したらスライムだった件 9", "chapters_summary": "Prólogo: O Herói Brilhante, O Festival da Fundação, O Torneio de Artes Marciais, A Inauguração do Labirinto", "desc": "O festival explode em celebração! Há torneios de artes marciais onde o herói Masayuki ganha fama repentina, espetáculos teatrais, delícias gastronômicas e a grande inauguração do Labirinto Subterrâneo de 100 andares projetado por Ramiris como a atração definitiva para aventureiros."},
        {"id": "vol-10", "num": 10, "title": "Volume 10: O Labirinto e a Cobiça (Mariabell Rosso)", "kanji": "転生したらスライムだった件 10", "chapters_summary": "Prólogo: Homens em Movimento, Capítulos 1 a 5, O Cerco Econômico", "desc": "A família mercante Rosso e a misteriosa garota de outro mundo Mariabell (possuidora da habilidade 'Ganância') tentam derrubar o sistema monetário e comercial de Tempest, gerando um conflito de inteligência econômica e batalhas no fundo das ruínas ancestrais."},
        {"id": "vol-11", "num": 11, "title": "Volume 11: A Melancolia Dourada e Chronoa (O Herói do Tempo)", "kanji": "転生したらスライムだった件 11", "chapters_summary": "Prólogo: Melancolia Dourada, Capítulos 1 a 5, O Despertar do Herói, O Paradoxo Temporal", "desc": "O maior mistério temporal da franquia é revelado: Chloe Aubert não é uma mera estudante invocada, mas a encarnação do lendário Herói que selou Veldora séculos atrás, presa em múltiplos loops temporais de amor e sacrifício para salvar Rimuru da ruína."},
        {"id": "vol-12", "num": 12, "title": "Volume 12: Conspiração no Império Oriental & A Marcha Imperial", "kanji": "転生したらスライムだった件 12", "chapters_summary": "Prólogo: Palhaços em Fuga, Capítulos 1 a 4, Interlúdio Imperial", "desc": "O gigantesco Império Oriental comandado pelo Imperador Rudra mobiliza um contingente impressionante de 1 milhão de soldados equipados com tecnologia bélica avançada e magitecnologia para marchar diretamente contra as fronteiras da Floresta de Jura."},
        {"id": "vol-13", "num": 13, "title": "Volume 13: A Grande Guerra Imperial & O Massacre no Labirinto", "kanji": "転生したらスライムだった件 13", "chapters_summary": "Prólogo: Dúvidas, Capítulos 1 a 4, O Triunfo dos Guardiões do Labirinto", "desc": "As forças invasoras do Império invadem os 100 andares do Labirinto Subterrâneo, subestimando grosseiramente os guardiões de Tempest. Zegion, Kumara, Adalman, Apito e os demônios de elite mostram o verdadeiro abismo de poder que separa meros humanos dos protetores de Rimuru."}
    ]
    
    ln_volumes = []
    for v in ln_metadata:
        file_path = f"data/light_novel/{v['id']}.json"
        has_file = os.path.exists(file_path)
        ch_count = 0
        p_count = 0
        if has_file:
            with open(file_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
                ch_count = d.get('chapter_count', 0)
                p_count = sum(len(c.get('paragraphs', [])) for c in d.get('chapters', []))
        
        ln_volumes.append({
            **v,
            'is_downloaded': has_file,
            'chapter_count': ch_count,
            'paragraph_count': p_count,
            'scan_source': 'TSSDK Scan PT-BR'
        })
        
    future_ln = [
        {"id": "vol-14", "num": 14, "title": "Volume 14: Duelo com a Guarda Imperial", "status": "Traduzido no Scan (PDF/Drive)", "desc": "Rimuru contra os Guardas Imperiais de Elite do Imperador Rudra."},
        {"id": "vol-15", "num": 15, "title": "Volume 15: O Despertar dos 12 Patronos", "status": "Traduzido no Scan (PDF/Drive)", "desc": "A captura de Veldora por Velgrynd, a fúria descontrolada de Rimuru e o despertar dos 12 Lordes de Tempest."},
        {"id": "vol-16", "num": 16, "title": "Volume 16: O Epílogo da Grande Guerra", "status": "Traduzido no Scan (PDF/Drive)", "desc": "A resolução da guerra do Império e as revelações sobre Michael e o mundo espiritual."},
        {"id": "vol-17", "num": 17, "title": "Volume 17: Coleção de Histórias Paralelas", "status": "Publicado no Japão / Tradução em Andamento", "desc": "Contos sobre Phantom King Feldway, Guy Crimson, Velgrynd e Rain."},
        {"id": "vol-18", "num": 18, "title": "Volume 18: A Invasão dos Insetos e Fantasmas", "status": "Publicado no Japão / Tradução em Andamento", "desc": "O início da Grande Guerra Tenma e a invasão de Feldway."},
        {"id": "vol-19", "num": 19, "title": "Volume 19: A Fúria de Michael", "status": "Publicado no Japão", "desc": "Rimuru vs Michael e a luta titânica pela alma de Rudra."},
        {"id": "vol-20", "num": 20, "title": "Volume 20: Guerra Celestial Total", "status": "Publicado no Japão", "desc": "Batalha decisiva dos lordes demônios nos céus e na terra."},
        {"id": "vol-21", "num": 21, "title": "Volume 21: O Fim do Espaço-Tempo", "status": "Publicado no Japão", "desc": "O clímax da série com Rimuru no fim dos tempos."}
    ]
    
    # 3. Amazon Links in Portuguese
    amazon_catalog = []
    for n in range(1, 22):
        amazon_catalog.append({
            'volume': n,
            'title': f"Tensei Shitara Slime Datta Ken - Light Novel Vol. {n} (Edição Oficial)",
            'search_url': f"https://www.amazon.com.br/s?k=That+Time+I+Got+Reincarnated+as+a+Slime+Vol+{n}+light+novel",
            'direct_search': f"https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+volume+{n}+light+novel",
            'publisher': "Micro Magazine (JP) / Yen Press (EN/Oficial)",
            'formats': ["Livro Digital Kindle (eBook)", "Livro Físico (Capa Comum)"]
        })
        
    # 4. Comparison Guide in Rich Portuguese
    comparison = {
        'overview': "Tensei Shitara Slime Datta Ken nasceu originalmente como uma Web Novel (história seriada na internet) publicada por Fuse no site japonês Shousetsuka ni Narou entre 2013 e 2015. Devido ao estrondoso sucesso, a editora Micro Magazine convidou Fuse para publicar a versão profissional Light Novel, ilustrada por Mitz Vah. Na Light Novel, o autor reescreveu mais de 50% de todo o enredo, criando personagens novos, refinando profundamente a geopolítica, expandindo os sistemas de combate e alterando o próprio antagonista final.",
        'key_differences': [
            {
                'topic': 'Charybdis (Caríbdis) e o Reino das Bestas de Eurazania',
                'wn': 'Charybdis não existe na Web Novel. A chegada de Milim Nava é rápida e casual, sem a ameaça do monstro celestial.',
                'ln': 'Exclusivo do Volume 3 da Light Novel! Um monstro colossal com rank de Calamidade composto de partículas mágicas de Veldora. Serve para selar a amizade com Milim, estreitar alianças com Eurazania e o Lorde Demônio Carrion, e provar o poder defensivo de Tempest.'
            },
            {
                'topic': 'O Massacre de Farmas e a Invocação de Diablo',
                'wn': 'Rimuru aniquila os 20 mil invasores humanos com o feitiço Megiddo, mas Diablo só aparece bem mais tarde de forma genérica quando Rimuru precisa de administradores para seu território.',
                'ln': 'No Volume 5, Diablo é invocado diretamente durante o ritual do despertar do Lorde Demônio, usando os corpos dos soldados invasores como sacrifício. Sua devoção absoluta a Rimuru e sua rivalidade com os outros demônios tornou-se um dos pilares mais amados da franquia.'
            },
            {
                'topic': 'A Conferência de Walpurgis e a Queda de Clayman',
                'wn': 'O banquete dos Lordes Demônios é rápido e pouco explorado politicamente. Rimuru derrota Clayman com relativa facilidade.',
                'ln': 'O Volume 6 expande profundamente o evento: há uma guerra em múltiplas frentes com Benimaru comandando o exército de Tempest, Shion e Hakurou enfrentando generais de Clayman, e Guy Crimson avaliando o equilíbrio global do Octagrama.'
            },
            {
                'topic': 'Conflito com Hinata Sakaguchi e a Santa Igreja Ocidental',
                'wn': 'Hinata tem uma participação muito menor como antagonista passageira, sem grande desenvolvimento pessoal.',
                'ln': 'O Volume 7 dedica um arco completo à diplomacia de Ruberius, ao plano secreto dos Sete Dias Celestiais e à verdadeira identidade da divindade Luminous Valentine. Culmina em um combate lendário e no famoso banquete onde os cavaleiros sagrados se rendem ao ramen e gyoza de Tempest.'
            },
            {
                'topic': 'A Família Rosso e Mariabell',
                'wn': 'Completamente inexistentes na Web Novel.',
                'ln': 'O Volume 10 introduz Mariabell Rosso, uma reencarnada com a Habilidade Única Ganância que lidera o clã de banqueiros que controla secretamente os reis humanos. Ela trava com Rimuru uma sofisticada guerra econômica, bancária e territorial.'
            },
            {
                'topic': 'O Enigma do Herói do Tempo (Chloe Aubert & Chronoa)',
                'wn': 'A mecânica do Herói do Tempo existe de forma direta e sem a complexidade dos múltiplos ciclos de tempo.',
                'ln': 'O Volume 11 atinge um dos ápices da literatura de fantasia moderna: revela-se que a pequena aluna Chloe Aubert viveu loops temporais de quase 2000 anos, saltando no tempo para salvar Rimuru da aniquilação, abrigando o espírito protetor Chronoa e a alma de Hinata.'
            },
            {
                'topic': 'As Três Progenitoras Demônios (Trio Primordial)',
                'wn': 'As demônios Testarossa (Branca), Ultima (Violeta) e Carrera (Amarela) não faziam parte do círculo interno original de Tempest.',
                'ln': 'Diablo viaja pessoalmente ao Mundo Espiritual nos Volumes 11 a 13 e recruta as três demônios primordiais mais temidas da história. Elas juram lealdade incondicional a Rimuru, assumem funções executivas e se tornam parte dos 12 Patronos de Tempest.'
            },
            {
                'topic': 'A Grande Guerra contra o Império Oriental',
                'wn': 'O exército imperial de Rudra invade a floresta e é aniquilado de forma veloz dentro do labirinto.',
                'ln': 'Os Volumes 12 a 16 transformam esse conflito em uma campanha militar épica: tanques mágicos, dirigíveis de combate, generais lendários armados com Habilidades Definitivas (Kondo, Damrada) e a intervenção da temível Dragão Verdadeira Velgrynd.'
            },
            {
                'topic': 'O Vilão Final e a Conclusão da História',
                'wn': 'Yuuki Kagurazaka é o vilão supremo final que adquire os Registros Akáshicos e tenta desintegrar o universo no Fim dos Tempos.',
                'ln': 'Na Light Novel, Yuuki é apenas uma peça manipulada por forças cósmicas ainda mais antigas: Michael, Feldway, os Espíritos da Criação e o Rei das Feras do Caos Ivaraje, levando à Grande Guerra Tenma (Guerra dos Céus e Demônios).'
            }
        ]
    }
    
    # 5. Cultural Guide and Original Nomenclature
    cultural_guide = {
        'title': 'Glossário de Nomes Originais e Guia Cultural de Tensura',
        'honorifics': [
            {'term': '-sama (様)', 'meaning': 'Sufixo de reverência suprema, usado para nobres, deuses ou mestres. Subordinados como Diablo, Shion e Rigurd dirigem-se a Rimuru exclusivamente como "Rimuru-sama" (Senhor/Mestre Rimuru).'},
            {'term': '-san (さん)', 'meaning': 'Tratamento respeitoso padrão para iguais ou colegas em situações sociais cotidianas.'},
            {'term': '-kun (君) / -chan (ちゃん)', 'meaning': 'Sufixos afetivos ou informais. "-kun" é comumente usado para jovens masculinos ou subordinados próximos; "-chan" é diminutivo afetuoso para crianças, garotas ou mascotes.'},
            {'term': 'Senpai (先輩) / Kouhai (後輩)', 'meaning': 'Relação tradicional japonesa entre veterano e novato no trabalho ou escola. Na vida anterior, Tamura chamava Satoru de "Senpai", o que explica sua atitude de mentor.'},
            {'term': 'Danna (旦那)', 'meaning': 'Significa "Mestre", "Chefe" ou "Patrão". É como aventureiros e comerciantes informais chamam Rimuru.'}
        ],
        'tensura_concepts': [
            {'term': 'O Poder dos Nomes (Naming)', 'desc': 'No mundo de Tensura, monstros nascem sem nome próprio. Quando um ser superior concede um nome a um monstro, consome sua própria mana (energia mágica), gravando uma identidade em sua alma. Isso desencadeia uma evolução de espécie drástica (ex: Goblins viram Hobgoblins; Ogros viram Kijin). Se a mana consumida for excessiva, o doador corre risco de vida.'},
            {'term': 'Majin (魔人 - Ser Mágico / Nascido da Magia)', 'desc': 'Monstros de alto intelecto e densidade de mana que possuem forma semelhente à humana ou grande soberania mágica. Diferem de animais selvagens ou feras brutas (Mamono).'},
            {'term': 'Kijin (鬼人 - Ogro Iluminado / Divino)', 'desc': 'A forma evoluída e nobre dos Ogros, caracterizada por extrema beleza, chifres refinados e habilidades marciais divinas (Benimaru, Shuna, Hakurou, Souei, Shion, Kurobee).'},
            {'term': 'True Dragon (竜種 - Dragão Verdadeiro)', 'desc': 'A cúspide máxima das espécies mágicas, entidades da natureza com consciência e mana inesgotável. Existem apenas 4: Veldanava (o Criador), Velzard (Gelo Branco), Velgrynd (Chamas Ardentes) e Veldora (Tempestade).'},
            {'term': 'Walpurgis (ワルプルギス - Banquete dos Lordes Demônios)', 'desc': 'Referência à lendária Noite de Santa Valpúrgia (noite pagã alemã das bruxas). Em Tensura, é a assembleia sagrada em que os Lordes Demônios se reúnem para deliberar assuntos que afetam o planeta inteiro.'},
            {'term': 'Megiddo (神之怒 - Ira dos Deuses)', 'desc': 'Feitiço físico original desenvolvido por Rimuru e o Grande Sábio. Utiliza milhares de gotículas de água em formato de lentes convexas no céu para concentrar a luz do sol em feixes de laser que penetram crânios na velocidade da luz, gastando quase zero de mana e burlando barreiras mágicas.'},
            {'term': 'Evolução da Voz da Consciência: Grande Sábio -> Raphael -> Ciel', 'desc': 'A inteligência interior que auxilia Rimuru evolui de Grande Sábio (Habilidade Única analítica) para Raphael (Rei da Sabedoria, Habilidade Definitiva) e, por fim, ao receber um nome de Rimuru, desperta como uma consciência com alma e sentimentos: Ciel.'}
        ],
        'cultural_aspects': [
            {'element': 'Culinária Japonesa como Instrumento Diplomático', 'desc': 'Rimuru usa sua memória do Japão para reconstruir comidas como ramen, shoyu (molho de soja), tofu, gyoza, hambúrguer e sake (bebida alcoólica fermentada). Em Tensura, isso não é apenas entretenimento: o sabor das comidas japonesas conquista o Rei Gazel de Dwargon, os Santos Cavaleiros de Hinata e até mesmo Lordes Demônios milenares como Luminous Valentine.'},
            {'element': 'Onsen (Águas Termais Japonesas)', 'desc': 'Rimuru constrói casas de banho termais comunitárias na capital de Tempest. O banho compartilhado é um dos maiores pilares da cultura de relaxamento japonesa, servindo de palco para reuniões políticas descontraídas entre reis e ministros.'},
            {'element': 'Harmonia entre Raças (Wa - 和)', 'desc': 'A filosofia de governo de Rimuru reflete o conceito japonês de "Wa" (paz, harmonia e convivência coletiva). Em vez de dominar pela opressão militar, Tempest integra monstros, elfos, anões e humanos através de cooperação econômica e comércio mútuo.'}
        ]
    }
    
    catalog = {
        'title': 'Tensei Shitara Slime Datta Ken - Biblioteca Completa',
        'sources': {
            'google_drive_fan_folder': 'https://drive.google.com/drive/u/0/folders/1GM_wQEc6KIp5F3GmqUOLY8XGN8dkUv45',
            'fan_scan_site': 'https://sites.google.com/view/tssdklscanptbr/p%C3%A1gina-inicial',
            'web_novel_site': 'https://centralnovel.com/series/tensei-shitara-slime-datta-ken/',
            'amazon_br_search': 'https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+light+novel'
        },
        'web_novel': {
            'info': {
                'title': 'Web Novel (Original da Internet)',
                'author': 'Fuse',
                'platform': 'Shousetsuka ni Narou (Syosetu)',
                'ptbr_source': 'Central Novel (Tradução em Português)',
                'total_chapters': len(cleaned_wn_chapters),
                'downloaded_count': len(wn_downloaded),
                'status': 'Completa (249 Capítulos + Epílogo + Histórias Extras)'
            },
            'arcs': wn_arcs,
            'chapters': cleaned_wn_chapters
        },
        'light_novel': {
            'info': {
                'title': 'Light Novel (Versão Impressa Oficial e Revisada)',
                'author': 'Fuse',
                'illustrator': 'Mitz Vah',
                'publisher_jp': 'GC Novels (Micro Magazine)',
                'publisher_en': 'Yen Press',
                'scan_ptbr': 'TSSDK Scan PT-BR (Tradução de Fãs)',
                'available_volumes_count': len(ln_volumes),
                'status': 'Em andamento (Volume 21+ no Japão)'
            },
            'volumes': ln_volumes,
            'future_volumes': future_ln
        },
        'amazon_br': {
            'general_search': 'https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+light+novel',
            'store_info': 'Catálogo oficial de Light Novels de That Time I Got Reincarnated as a Slime disponíveis para compra no Brasil através da Amazon.com.br.',
            'volumes': amazon_catalog
        },
        'comparison': comparison,
        'cultural_guide': cultural_guide
    }
    
    with open('data/catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print("data/catalog.json gerado com sucesso com termos em português, guia cultural e separação completa!")

if __name__ == '__main__':
    build_catalog()
