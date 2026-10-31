"""
MÓDULO DE CORREÇÃO E PADRONIZAÇÃO DE TRADUÇÃO - TENSEI SHITARA SLIME DATTA KEN
Revisa textos traduzidos de forma rápida/automática (EPUBs do Drive, JSONs e TXTs),
corrigindo erros de tradução literal, nomes próprios corrompidos, termos em inglês,
discordâncias de gênero e calques gramaticais para Português Brasileiro (PT-BR) natural.
Totalmente idempotente (executar múltiplas vezes produz exatamente o mesmo resultado).
"""

import re
import os
import json
import zipfile
import shutil
from bs4 import BeautifulSoup, NavigableString

# 1. Substituições sensíveis a maiúsculas/minúsculas (nomes próprios corrompidos por tradução automática)
CASE_SENSITIVE_RULES = [
    # Autor e Sumário
    (r'Autor:\s*Fusível', 'Autor: Fuse'),
    (r'Este é o Fusível\b', 'Aqui é o Fuse'),
    (r'\bFusível aqui\b', 'Fuse aqui'),
    (r'(?<=Índice\s)Cobrir(?=\s+Conteúdo)', 'Capa'),
    (r'^\s*Cobrir\s*$', 'Capa'),

    # Feldway traduzido como "Campo de golfe" (Fairway) no Vol. 20
    (r'\bCampo de [Gg]olfe\b', 'Feldway'),

    # Guy Crimson traduzido como "Cara" / "Cara Carmesim"
    (r'\bCara Carmesim\b', 'Guy Crimson'),
    (r'\bCara-sama\b', 'Guy-sama'),
    (r'\bCara-san\b', 'Guy-san'),
    (r'([“"\'])Cara([”"\']\.\s*Tornou-se o nome dele)', r'\1Guy\2'),
    (r'([“"\'])(?:Oi|Ei),?\s*Cara!', r'\1Ei, Guy!'),
    (r'([“"\'])Cara\?\s*Não me diga que é Guy Crimson', r'\1Guy? Não me diga que é Guy Crimson'),
    (r'\bvencer o Cara\b', 'vencer Guy'),
    (r'\batenção do Cara e de seus\b', 'atenção de Guy e de seus'),
    (r'\bCara\s+(pensou|sorriu|zombou|perguntou|murmurou|colocou|declarou|olhou|respondeu|riu)\b', r'Guy \1'),
    (r'([“"\']|\.\s+)Cara,\s+(?!intrometido\b|azarado\b|de Cavalo\b|ele é\b|isso é loucura)', r'\1Guy, '),

    # Carrera traduzida como "Carreira"
    (r'\bCarreira\b', 'Carrera'),
    (r'Como senhor de Agera,\s*ela', 'Como senhora de Agera, ela'),

    # Ultima traduzida como "Ultimo" / "Último" / "Última" em contexto de nome
    (r'Carrera\?\s*E\s*Ultimo\b', 'Carrera? E Ultima'),
    (r'(?<=\.\s)Ultimo\?(?=\s|$)', 'Ultima?'),
    (r'Senhor\s*\d*\s*Último\b', 'Senhora Ultima'),
    (r'Nome:\s*Última\b', 'Nome: Ultima'),

    # Footman e Tear (Trupe de Palhaços Moderados)
    (r'\bLacaio\b', 'Footman'),
    (r'\bTeare\b', 'Tear'),
    (r'([“"\'])Rasgue!\s*E\s*Footman', r'\1Tear! E Footman'),
    (r'Rasgue a [\'‘“"]Lágrima[\'’”"] da Trupe de Palhaços Moderados', 'Tear, a "Palhaça Chorona" da Trupe de Palhaços Moderados'),
    (r'\bLágrima murmura\b', 'Tear murmura'),
    (r'“Palhaço irritado \(Pierrot irritado\)”', '“Pierrot Furioso”'),
    (r'“Palhaço rasgando \(lágrima\)”', '“Palhaça Chorona”'),

    # Subordinados Demônios: Moss ("Musgo"), Esprit ("Espírito"), Venom ("Veneno"), Diablo ("Diabo"), Zegion ("Zegião")
    (r'Nome:\s*Musgo\b', 'Nome: Moss'),
    (r'\bMusgo\.\s*Veyron\.\s*Agera\.\s*Espírito\.\s*Zonda\.\s*Cien\.\s*Veneno\.', 'Moss. Veyron. Agera. Esprit. Zonda. Cien. Venom.'),
    (r'\bMusgo novamente\.', 'Moss novamente.'),
    (r'([“"\'])Musgo\.([”"\'])', r'\1Moss.\2'),
    (r'([“"\'])Musgo\.\s*Reúna todos', r'\1Moss. Reúna todos'),
    (r'Nome:\s*Espírito\b', 'Nome: Esprit'),
    (r'([“"\'])Espírito,\s*use meu poder!', r'\1Esprit, use meu poder!'),
    (r'([“"\'])Espírito,\s*hein\?', r'\1Esprit, hein?'),
    (r'([“"\'])Veneno([….][”"\'])', r'\1Venom\2'),
    (r'Nome:\s*Diabo\b', 'Nome: Diablo'),
    (r'([“"\'])Diabo,\s*seu nome era Veyron', r'\1Demônio, seu nome era Veyron'),
    (r'\bZegião\b', 'Zegion'),

    # Leon Cromwell traduzido como "Leão" (preservando "Máscara de Leão", "Rei Leão", "Leão Mascarado")
    (r'(?<!Rei\s)(?<!Máscara de\s)(?<!Máscara-de-)(?<!o\s)(?<!um\s)\bLeão\b(?![\s-]+M[áa]scara)(?!\s+Mascarado)(?!\s+Dourado)', 'Leon'),

    # Fichas de Status (Vol. 16 e Vol. 18)
    (r'\bCorrida:\s*', 'Raça: '),
    (r'\[PE:\s*(\d)', r'[EP: \1'),
    (r'\bNove Caldas\b', 'Nove Caudas'),
    (r'\bClassificação de Contagem\b', 'Classe Conde'),
    (r'\bClassificação de Marquês\b', 'Classe Marquês'),
    (r'\bPar Demônio\b', 'Par Demoníaco'),
    (r'\bEspírito do Caos Justo\b', 'Espírito Médio do Caos'),
    (r'\bespírito do caos maior\b', 'Espírito Superior do Caos'),
    (r'\bEspírito do Caos Maior\b', 'Espírito Superior do Caos'),
    (r'\bLorde Diabo\b', 'Lorde Demônio Espiritual'),
    (r'\bTempestade de Veldora\b', 'Veldora Tempest'),
    (r'\bTempestade de Rimuru\b', 'Rimuru Tempest'),
    (r'\bFederação da Tempestade de Jura\b', 'Federação de Jura Tempest'),
]

# 2. Substituições insensíveis a caixa (Inglês residual, Habilidades, Títulos, Concordância de Gênero e Calques)
CASE_INSENSITIVE_RULES = [
    # Título da obra em inglês
    (r'That Time I Got Reincarnated as a Slime,?\s*Volume\s*(\d+)', r'Tensei Shitara Slime Datta Ken — Volume \1'),
    (r'That Time I Got Reincarnated as a Slime', 'Tensei Shitara Slime Datta Ken'),
    (r'Aquela vez que reencarnei como um Slime,?\s*Volume\s*(\d+)', r'Tensei Shitara Slime Datta Ken — Volume \1'),

    # Concordância de gênero das Primordiais (Testarossa = Branca, Carrera = Amarela, Ultima = Violeta)
    (r'\bPrimordial Branco\b', 'Primordial Branca'),
    (r'\bBranco Primordial\b', 'Primordial Branca'),
    (r'\bPrimordial Amarelo\b', 'Primordial Amarela'),
    (r'\bAmarelo Primordial\b', 'Primordial Amarela'),
    (r'\bPrimordial Roxo\b', 'Primordial Violeta'),
    (r'\bRoxo Primordial\b', 'Primordial Violeta'),
    (r'\bVioleta Primordial\b', 'Primordial Violeta'),
    (r'\bPreto Primordial\b', 'Primordial Negro'),
    (r'\bVermelho Primordial\b', 'Primordial Vermelho'),
    (r'\bAzul Primordial\b', 'Primordial Azul'),
    (r'\bVerde Primordial\b', 'Primordial Verde'),

    # Categorias do Sistema de Habilidades e Magia
    (r'\bUltimate Skills\b', 'Habilidades Supremas'),
    (r'\bUltimate Skill\b', 'Habilidade Suprema'),
    (r'\bUltimate Skil\b', 'Habilidade Suprema'),
    (r'\bUnique Skills\b', 'Habilidades Únicas'),
    (r'\bUnique Skill\b', 'Habilidade Única'),
    (r'\bExtra Skills\b', 'Habilidades Extras'),
    (r'\bExtra Skill\b', 'Habilidade Extra'),
    (r'\bIntrinsic Skills\b', 'Habilidades Intrínsecas'),
    (r'\bIntrinsic Skill\b', 'Habilidade Intrínseca'),
    (r'\bCommon Skills\b', 'Habilidades Comuns'),
    (r'\bCommon Skill\b', 'Habilidade Comum'),
    (r'\bUltimate Enchantments\b', 'Encantamentos Supremos'),
    (r'\bUltimate Enchantment\b', 'Encantamento Supremo'),
    (r'\bUltimate Gifts\b', 'Dádivas Supremas'),
    (r'\bUltimate Gift\b', 'Dádiva Suprema'),
    (r'\bUltimate Dominion\b', 'Domínio Supremo'),
    (r'\bRegalia Dominion\b', 'Domínio de Regalia'),
    (r'\bUltimate Slime\b', 'Slime Supremo'),
    (r'\bSoul Corridor\b', 'Corredor da Alma'),
    (r'\bThought Acceleration\b', 'Aceleração do Pensamento'),
    (r'\bParallel Operation\b', 'Operação Paralela'),
    (r'\bChant Annulment\b', 'Anulação de Canto'),
    (r'\bAll of Creation\b', 'Compreensão de Toda a Criação'),
    (r'\bGreat Sage\b', 'Grande Sábio'),

    # Habilidades Supremas Nomeadas (Série Angelical, Demoníaca e Lovecraftiana)
    (r'\b(?:Wisdom King|Lord of Wisdom)\s+Raphael\b', 'Rei da Sabedoria Raphael'),
    (r'\b(?:Gluttonous King|Lord of Gluttony)\s+Beelzebuth?\b', 'Rei da Gula Beelzebuth'),
    (r'\b(?:Covenant King|Lord of Vows)\s+Uriel\b', 'Rei do Pacto Uriel'),
    (r'\bStorm King Veldora\b', 'Rei da Tempestade Veldora'),
    (r'\bScorch King Velgrynd\b', 'Rei Escaldante Velgrynd'),
    (r'\bVoid God Azathoth\b', 'Deus do Vazio Azathoth'),
    (r'\b(?:Harvest King|Abundance King|Lord of Harvest)\s+Shub-Niggurath\b', 'Rei da Colheita Shub-Niggurath'),
    (r'\bHope King Sariel\b', 'Rei da Esperança Sariel'),
    (r'\bLustful King Asmodeus\b', 'Rei da Luxúria Asmodeus'),
    (r'\bJustice King Michael\b', 'Rei da Justiça Michael'),
    (r'\bGreedy King Mammon\b', 'Rei da Ganância Mammon'),
    (r'\bPurity King Metatron\b', 'Rei da Pureza Metatron'),
    (r'\bPatience King Gabriel\b', 'Rei da Paciência Gabriel'),
    (r'\bWrath(?:ful)? King Satanael\b', 'Rei da Ira Satanael'),
    (r'\bInvestigation King Faust\b', 'Rei da Investigação Faust'),
    (r'\bConviction King Sandalphon\b', 'Rei da Convicção Sandalphon'),
    (r'\bExecutioner Sandalphon\b', 'Executor Sandalphon'),
    (r'\bHeat King Amaterasu\b', 'Rei do Calor Amaterasu'),
    (r'\bDivine Flame King Cthugha\b', 'Rei da Chama Divina Cthugha'),
    (r'\bFlame God Cthugha\b', 'Deus da Chama Cthugha'),
    (r'\bIllusion King Mephisto\b', 'Rei da Ilusão Mephisto'),
    (r'\bPoison King Samael\b', 'Rei do Veneno Samael'),
    (r'\bThunder King Indra\b', 'Rei do Trovão Indra'),
    (r'\bEvil Dragon King Azi Dahaka\b', 'Rei Dragão Maligno Azi Dahaka'),
    (r'\bPride(?:ful)? King Lucifer\b', 'Rei do Orgulho Lúcifer'),
    (r'\bSloth(?:ful)? King Belphegor\b', 'Rei da Preguiça Belphegor'),
    (r'\bEnvi(?:ous|y) King Leviathan\b', 'Rei da Inveja Leviatã'),
    (r'\bCharity King Raguel\b', 'Rei da Caridade Raguel'),
    (r'\bDominion King Melchizedek\b', 'Rei do Domínio Melchizedek'),
    (r'\bTemptation King Azazel\b', 'Rei da Tentação Azazel'),
    (r'\bGlory King Haniel\b', 'Rei da Glória Haniel'),
    (r'\bRigorous King Jibril\b', 'Rei do Rigor Jibril'),
    (r'\bSalvation King Azrael\b', 'Rei da Salvação Azrael'),
    (r'\bHeavenly King Astarte\b', 'Rei Celestial Astarte'),
    (r'\bSpace-Time God Yog-Sothoth\b', 'Deus do Espaço-Tempo Yog-Sothoth'),
    (r'\bChaos King Nyarlathotep\b', 'Rei do Caos Nyarlathotep'),

    # Golpes Especiais (Idempotentes via lookaround para não duplicar parênteses)
    (r'(?<!\()\bMelt Slash\b(?!\))', 'Corte Derretedor (Melt Slash)'),
    (r'(?<!\()\bDrago Nova\b(?!\))', 'Supernova Dracônica (Drago Nova)'),
    (r'(?<!\()\bStorm Blast\b(?!\))', 'Explosão da Tempestade (Storm Blast)'),
    (r'(?<!\()\bBurst Roar\b(?!\))', 'Rugido Explosivo (Burst Roar)'),
    (r'(?<!\()\bDragon Buster\b(?!\))', 'Caçador de Dragões (Dragon Buster)'),

    # Títulos, Exércitos, Espécies e Lugares em Inglês
    (r'\bMagic Beast Corps\b', 'Corpo de Bestas Mágicas'),
    (r'\bMagic Corps\b', 'Corpo Mágico'),
    (r'\bDemon Colossus\b', 'Colosso Demoníaco'),
    (r'\bTrue Dragons\b', 'Dragões Verdadeiros'),
    (r'\bTrue Dragon\b', 'Dragão Verdadeiro'),
    (r'\bTrue Demon Lords\b', 'Verdadeiros Lordes Demônios'),
    (r'\bTrue Demon Lord\b', 'Verdadeiro Lorde Demônio'),
    (r'\bAwakened Demon Lords\b', 'Lordes Demônios Despertos'),
    (r'\bAwakened Demon Lord\b', 'Lorde Demônio Desperto'),
    (r'\bDemon Lord Seed\b', 'Semente de Lorde Demônio'),
    (r'\bDemon Lord Haki\b', 'Haki de Lorde Demônio'),
    (r'\bDemon Lords\b', 'Lordes Demônios'),
    (r'\bDemon Lord\b', 'Lorde Demônio'),
    (r'\bStorm Dragon Veldora\b', 'Dragão da Tempestade Veldora'),
    (r'\bStorm Dragon\b', 'Dragão da Tempestade'),
    (r'\bStar King Dragon\b', 'Dragão Rei Estelar'),
    (r'\bEvil Dragon Spawns\b', 'Crias de Dragão Maligno'),
    (r'\bEvil Dragon Spawn\b', 'Cria de Dragão Maligno'),
    (r'\bMaster Core\b', 'Núcleo Mestre'),
    (r'\bAvatar Core\b', 'Núcleo de Avatar'),
    (r'\bSplit Body\b', 'Corpo Dividido'),
    (r'\bCardinal World\b', 'Mundo Cardeal'),
    (r'\bHeavenly Star Palace\b', 'Palácio da Estrela Celestial'),
    (r'\bPhantom King Feldway\b', 'Rei Fantasma Feldway'),
    (r'\bInsect Lord Zelanus\b', 'Lorde Inseto Zelanus'),
    (r'\bKing Gazel\b', 'Rei Gazel'),
    (r'\bKing Drum\b', 'Rei Drum'),
    (r'\bLucky Devil\b', 'Demônio Sortudo'),
    (r'\bJura Tempest Federation\b', 'Federação de Jura Tempest'),
    (r'\bArmed Nation of Dwargon\b', 'Reino Armado de Dwargon'),
    (r'\bHoly Empire of Ruberios\b', 'Sacro Império de Ruberios'),
    (r'\bBeast Kingdom of Eurazania\b', 'Reino das Bestas de Eurazania'),
    (r'\bEastern Empire\b', 'Império Oriental'),
    (r'\bWestern Nations\b', 'Nações Ocidentais'),
    (r'\bFreedom Academy\b', 'Academia da Liberdade'),
    (r'\bFreedom Guild\b', 'Guilda da Liberdade'),
    (r'\bAngry Pierrot\b', 'Pierrot Furioso'),

    # Padronização de grafias canônicas
    (r'\bRimuro\b', 'Rimuru'),
    (r'\bLimule\b', 'Rimuru'),
    (r'\bLimuru\b', 'Rimuru'),
    (r'\bVerudora\b', 'Veldora'),
    (r'\bBerudora\b', 'Veldora'),
    (r'\bVeldra\b', 'Veldora'),
    (r'\bMilin\b', 'Milim'),
    (r'\bGuy Krimson\b', 'Guy Crimson'),
    (r'\bGee Crimson\b', 'Guy Crimson'),
    (r'\bMariabel\b', 'Mariabell'),
    (r'\bHinata Sakaguti\b', 'Hinata Sakaguchi'),
    (r'\bChloe Obel\b', 'Chloe Aubert'),
    (r'\bKuroe Oberu\b', 'Chloe Aubert'),
    (r'\bRumbling do Céu e da Terra\b', 'O Estrondo do Céu e da Terra'),

    # Erros semânticos específicos e calques literais do inglês ("shoot", "goal", "can't be helped", "summoned")
    (r'\bO gol de um santo\b', 'O Objetivo de um Santo'),
    (r'\bgol da vitória\b', 'objetivo da vitória'),
    (r'\btanto que fotografar se tornou uma segunda natureza\b', 'tanto que atirar se tornou uma segunda natureza'),
    (r'\bIsso pode realmente ser ajudado\?', 'Tem mesmo o que fazer?'),
    (r'\bnão pode ser ajudado\b', 'não há o que fazer'),
    (r'\bnão podia ser ajudado\b', 'não havia o que fazer'),
    (r'\bnão poderia ser ajudado\b', 'não haveria o que fazer'),
    (r'\bIt can\'t be helped\b', 'Não há o que fazer'),
    (r'\bMuito tempo sem ver!', 'Quanto tempo, pessoal!'),
    (r'\bA Conspiração de Majins\b', 'A Conspiração dos Majins'),
    (r'\bhouve um ([“"\'][^”"\']+[”"\']) som\b', r'houve um som de \1'),
    (r'\bCrianças Sumonadas\b', 'Crianças Invocadas'),
    (r'\bsumonad(o|a|os|as)\b', r'invocad\1'),
    (r'([“"\'])-\s*Seriamente\?', r'\1— Sério?'),

    # Reversão de parentéticos repetidos de execuções antigas se existirem
    (r'Kijin \(Ogro Divino\)(?:\s*\(Ogro Divino\))*', 'Kijin'),
    (r'Majin \(Nascido da Magia\)(?:\s*\(Nascido da Magia\))*', 'Majin'),
    (r'Megiddo \(Ira dos Deuses\)(?:\s*\(Ira dos Deuses\))*', 'Megiddo'),
    (r'Lobo da Presa \(Direwolf\)(?:\s*\(Direwolf\))*', 'Lobo da Presa'),
]

COMPILED_CS = [(re.compile(p), r) for p, r in CASE_SENSITIVE_RULES]
COMPILED_CI = [(re.compile(p, re.IGNORECASE), r) for p, r in CASE_INSENSITIVE_RULES]


def correct_text_block(text: str) -> str:
    """Aplica todas as regras de correção léxica, canônica e gramatical de forma idempotente."""
    if not text:
        return ""
    cleaned = text

    for regex, repl in COMPILED_CS:
        cleaned = regex.sub(repl, cleaned)

    for regex, repl in COMPILED_CI:
        cleaned = regex.sub(repl, cleaned)

    # Limpeza tipográfica preservando marcadores de nota [nota N]
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\s+([,.;:?!])', r'\1', cleaned)
    cleaned = re.sub(r'([«‹“])\s+', r'\1', cleaned)
    cleaned = re.sub(r'\s+([»›”])', r'\1', cleaned)
    cleaned = re.sub(r'^[-\u2013\u2014]\s*', '— ', cleaned)
    return cleaned.strip()


def repair_xhtml_bytes(raw_bytes: bytes) -> bytes:
    """Corrige nós de texto dentro de um arquivo XHTML/HTML de EPUB preservando tags, imagens e links."""
    html_str = raw_bytes.decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html_str, 'html.parser')

    # Corrigir <title> se existir
    if soup.title and soup.title.string:
        soup.title.string.replace_with(correct_text_block(str(soup.title.string)))

    root = soup.body or soup
    for text_node in list(root.find_all(string=True)):
        parent_name = text_node.parent.name if text_node.parent else ''
        if parent_name in ('script', 'style'):
            continue
        orig = str(text_node)
        if not orig.strip():
            continue
        # Preservar espaços nas bordas entre spans adjacentes
        lead = ' ' if orig[0].isspace() else ''
        trail = ' ' if orig[-1].isspace() else ''
        fixed = correct_text_block(orig)
        if fixed != orig.strip():
            text_node.replace_with(NavigableString(f"{lead}{fixed}{trail}"))

    return str(soup).encode('utf-8')


def fix_epub_file(input_epub: str, output_epub: str) -> str:
    """Gera uma cópia revisada de um arquivo .epub corrigindo texto XHTML, TOC (.ncx) e metadados (.opf)."""
    os.makedirs(os.path.dirname(os.path.abspath(output_epub)), exist_ok=True)
    with zipfile.ZipFile(input_epub, 'r') as zin:
        with zipfile.ZipFile(output_epub, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            # 1. mimetype deve ser o primeiro item sem compressão no padrão EPUB
            if 'mimetype' in zin.namelist():
                zout.writestr('mimetype', zin.read('mimetype'), compress_type=zipfile.ZIP_STORED)

            for item in zin.infolist():
                if item.filename == 'mimetype':
                    continue
                data = zin.read(item.filename)
                low = item.filename.lower()
                if low.endswith(('.html', '.xhtml', '.htm')):
                    data = repair_xhtml_bytes(data)
                elif low.endswith(('.ncx', '.opf')):
                    txt = data.decode('utf-8', errors='ignore')
                    txt = txt.replace('Fusível', 'Fuse')
                    txt = txt.replace('Cara Carmesim', 'Guy Crimson')
                    txt = txt.replace('Campo de golfe', 'Feldway').replace('Campo de Golfe', 'Feldway')
                    txt = txt.replace('O gol de um santo', 'O Objetivo de um Santo')
                    txt = re.sub(r'That Time I Got Reincarnated as a Slime,?\s*Volume\s*(\d+)', r'Tensei Shitara Slime Datta Ken - Volume \1', txt)
                    data = txt.encode('utf-8')
                zout.writestr(item, data)
    return output_epub


def fix_file(input_path: str, output_path: str = None) -> str:
    """Corrige arquivos .epub, .json ou .txt."""
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_corrigido{ext}"

    if input_path.lower().endswith('.epub'):
        fix_epub_file(input_path, output_path)
    elif input_path.lower().endswith('.json'):
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'title' in data and isinstance(data['title'], str):
            data['title'] = correct_text_block(data['title'])
        if 'paragraphs' in data:
            data['paragraphs'] = [correct_text_block(p) for p in data['paragraphs']]
        if 'chapters' in data:
            for ch in data['chapters']:
                if 'title' in ch and isinstance(ch['title'], str):
                    ch['title'] = correct_text_block(ch['title'])
                if 'paragraphs' in ch:
                    ch['paragraphs'] = [correct_text_block(p) for p in ch['paragraphs']]
                if 'blocks' in ch:
                    for b in ch['blocks']:
                        if b.get('type') == 'p' and 'text' in b:
                            b['text'] = correct_text_block(b['text'])
        if 'footnotes' in data and isinstance(data['footnotes'], dict):
            data['footnotes'] = {k: correct_text_block(v) for k, v in data['footnotes'].items()}
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        corrected = [correct_text_block(line) + '\n' for line in lines]
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(corrected)

    print(f"Arquivo corrigido com sucesso: {output_path}")
    return output_path


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        inp = sys.argv[1]
        outp = sys.argv[2] if len(sys.argv) > 2 else None
        fix_file(inp, outp)
    else:
        print("Uso: python scripts/fix_translation.py <arquivo.epub|arquivo.json|arquivo.txt> [caminho_saida]")
