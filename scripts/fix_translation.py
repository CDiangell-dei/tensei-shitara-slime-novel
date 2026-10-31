"""
MÓDULO DE CORREÇÃO E PADRONIZAÇÃO DE TRADUÇÃO - TENSEI SHITARA SLIME DATTA KEN
Revisa textos com tradução mecânica/rápida, aplicando termos canônicos,
regras gramaticais em Português Brasileiro (PT-BR) e terminologia oficial de Tensura.
"""

import re
import os
import json

# Dicionário de padronização de nomes canônicos e termos de Tensura
GLOSSARY_REPLACEMENTS = [
    # Nomes e Sobrenomes
    (r'\bRimuro\b', 'Rimuru'),
    (r'\bLimule\b', 'Rimuru'),
    (r'\bLimuru\b', 'Rimuru'),
    (r'\bVerudora\b', 'Veldora'),
    (r'\bBerudora\b', 'Veldora'),
    (r'\bVeldra\b', 'Veldora'),
    (r'\bMilin\b', 'Milim'),
    (r'\bMirimu\b', 'Milim'),
    (r'\bGuy\s+Krimson\b', 'Guy Crimson'),
    (r'\bGee\s+Crimson\b', 'Guy Crimson'),
    (r'\bGai\s+Crimson\b', 'Guy Crimson'),
    (r'\bDiaburo\b', 'Diablo'),
    (r'\bKuro\b(?=\s+o\s+demônio|\s+demônio)', 'Noir (Preto)'),
    (r'\bBenimalu\b', 'Benimaru'),
    (r'\bHakurou\b', 'Hakurou'),
    (r'\bSouei\b', 'Souei'),
    (r'\bSoei\b', 'Souei'),
    (r'\bShiona\b', 'Shion'),
    (r'\bSion\b', 'Shion'),
    (r'\bSyuna\b', 'Shuna'),
    (r'\bGobuta\b', 'Gobuta'),
    (r'\bGobzo\b', 'Gobzo'),
    (r'\bRangha\b', 'Ranga'),
    (r'\bRiguldo\b', 'Rigurd'),
    (r'\bRiguru\b', 'Rigur'),
    (r'\bKaido\b', 'Kaido'),
    (r'\bKaijin\b', 'Kaijin'),
    (r'\bGarm\b', 'Garm'),
    (r'\bDold\b', 'Dold'),
    (r'\bMyrd\b', 'Myrd'),
    (r'\bTreyni\b', 'Treyni'),
    (r'\bToran\b', 'Toran'),
    (r'\bLuminous\s+Valentine\b', 'Luminous Valentine'),
    (r'\bRuminas\s+Valentine\b', 'Luminous Valentine'),
    (r'\bHinata\s+Sakaguti\b', 'Hinata Sakaguchi'),
    (r'\bChloe\s+Obel\b', 'Chloe Aubert'),
    (r'\bKuroe\s+Oberu\b', 'Chloe Aubert'),
    (r'\bChronoa\b', 'Chronoa'),
    (r'\bKuronoa\b', 'Chronoa'),
    (r'\bYuuki\s+Kagurazaka\b', 'Yuuki Kagurazaka'),
    (r'\bYuki\s+Kagurazaka\b', 'Yuuki Kagurazaka'),
    (r'\bVelgrynd\b', 'Velgrynd'),
    (r'\bBerugurando\b', 'Velgrynd'),
    (r'\bVelzard\b', 'Velzard'),
    (r'\bBeruzado\b', 'Velzard'),
    (r'\bVeldanava\b', 'Veldanava'),
    (r'\bBerudanava\b', 'Veldanava'),

    # Habilidades Canônicas
    (r'\bGreat\s+Sage\b', 'Grande Sábio'),
    (r'\bDai-Madoushi\b', 'Grande Sábio'),
    (r'\bWisdom\s+King\s+Raphael\b', 'Rei da Sabedoria Raphael'),
    (r'\bLord\s+of\s+Wisdom\s+Raphael\b', 'Rei da Sabedoria Raphael'),
    (r'\bRaphael\b(?=\s+o\s+rei|\s+habilidade)', 'Raphael'),
    (r'\bGluttony\b', 'Gula'),
    (r'\bLord\s+of\s+Gluttony\s+Beelzebuth?\b', 'Rei da Gula Belzebu'),
    (r'\bBeelzebuth?\b', 'Belzebu'),
    (r'\bPredator\b', 'Predador'),
    (r'\bDevourer\b', 'Devorador'),
    (r'\bDegenerate\b', 'Degenerado'),
    (r'\bShapeshifter\b', 'Metamorfo'),
    (r'\bHeartless\s+One\b', 'Sem Coração'),
    (r'\bMerciless\b', 'Impiedoso'),
    (r'\bMegiddo\b', 'Megiddo (Ira dos Deuses)'),
    (r'\bGod\'s\s+Wrath\b', 'Ira dos Deuses (Megiddo)'),
    (r'\bSoul\s+Corridor\b', 'Corredor das Almas'),
    (r'\bThought\s+Acceleration\b', 'Aceleração do Pensamento'),
    (r'\bParallel\s+Operation\b', 'Operação Paralela'),
    (r'\bChant\s+Annulment\b', 'Anulação de Encantamento'),
    (r'\bAll\s+of\s+Creation\b', 'Toda a Criação'),
    (r'\bUltimate\s+Skill\b', 'Habilidade Definitiva'),
    (r'\bUnique\s+Skill\b', 'Habilidade Única'),
    (r'\bExtra\s+Skill\b', 'Habilidade Extra'),
    (r'\bIntrinsic\s+Skill\b', 'Habilidade Intrínseca'),

    # Espécies e Classes
    (r'\bTrue\s+Dragon\b', 'Dragão Verdadeiro'),
    (r'\bTrue\s+Demon\s+Lord\b', 'Verdadeiro Lorde Demônio'),
    (r'\bAwakened\s+Demon\s+Lord\b', 'Lorde Demônio Desperto'),
    (r'\bDemon\s+Lord\s+Seed\b', 'Semente de Lorde Demônio'),
    (r'\bDemon\s+Lord\b', 'Lorde Demônio'),
    (r'\bKijin\b', 'Kijin (Ogro Divino)'),
    (r'\bDragonoid\b', 'Dragonoide'),
    (r'\bDirewolf\b', 'Lobo da Presa (Direwolf)'),
    (r'\bTempest\s+Star\s+Wolf\b', 'Lobo Estelar de Tempest'),
    (r'\bOrc\s+Lord\b', 'Lorde Orc'),
    (r'\bOrc\s+Disaster\b', 'Orc Desastre'),
    (r'\bMajin\b', 'Majin (Nascido da Magia)'),

    # Nações e Cidades
    (r'\bJura\s+Tempest\s+Federation\b', 'Federação de Jura Tempest'),
    (r'\bArmed\s+Nation\s+of\s+Dwargon\b', 'Reino Armado de Dwargon'),
    (r'\bKingdom\s+of\s+Falmuth\b', 'Reino de Farmas (Falmuth)'),
    (r'\bFarmus\b', 'Farmas'),
    (r'\bKingdom\s+of\s+Blumund\b', 'Reino de Blumund'),
    (r'\bHoly\s+Empire\s+of\s+Ruberios\b', 'Sacro Império de Ruberius'),
    (r'\bBeast\s+Kingdom\s+of\s+Eurazania\b', 'Reino das Bestas de Eurazania'),
    (r'\bEastern\s+Empire\b', 'Império Oriental'),
    (r'\bWestern\s+Nations\b', 'Nações Ocidentais'),
    (r'\bFreedom\s+Academy\b', 'Academia da Liberdade'),
    (r'\bFreedom\s+Guild\b', 'Guilda da Liberdade'),

    # Expressões e Calques Comuns de Tradução Mecânica
    (r'\bIt\s+can\'t\s+be\s+helped\b', 'Não há o que fazer'),
    (r'\bshoganai\b', 'não tem jeito'),
    (r'\bmou\b', 'ora essa'),
    (r'\bcomo\s+esperado\s+de\b', 'como era de se esperar de'),
    (r'\beu\s+acho\s+que\s+sim\b', 'acredito que sim'),
    (r'\bele\s+disse\s+com\s+um\s+sorriso\s+amargo\b', 'ele comentou com um sorriso amarelo'),
]

def correct_text_block(text):
    """Aplica correções léxicas, estilísticas e gramaticais."""
    cleaned = text

    # Aplicar substituições do glossário canônico
    for pattern, replacement in GLOSSARY_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # Correções gramaticais de espaçamento e pontuação
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s+([,.:;?!])', r'\1', cleaned)
    cleaned = re.sub(r'([«“"\'‘])\s+', r'\1', cleaned)
    cleaned = re.sub(r'\s+([»”"\'’])', r'\1', cleaned)
    
    # Padronizar aspas e travessões para diálogos literários
    cleaned = re.sub(r'^[-\u2013\u2014]\s*', '— ', cleaned)
    
    return cleaned.strip()

def fix_file(input_path, output_path=None):
    """Lê um arquivo de texto ou JSON e gera a versão revisada e polida."""
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_corrigido{ext}"

    if input_path.endswith('.json'):
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Percorrer seções e parágrafos
        if 'paragraphs' in data:
            data['paragraphs'] = [correct_text_block(p) for p in data['paragraphs']]
        if 'chapters' in data:
            for ch in data['chapters']:
                if 'paragraphs' in ch:
                    ch['paragraphs'] = [correct_text_block(p) for p in ch['paragraphs']]
                    
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
        print("Uso: python fix_translation.py <caminho_do_arquivo> [caminho_de_saida]")
