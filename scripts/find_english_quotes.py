import glob
import json
import re

files = sorted(glob.glob('data/light_novel/vol-*.json'))

# Let's find all words enclosed in quotes: ‘...’, '...', “...”, "...", 『...』, [...]
# that look like English (letters and spaces, no Portuguese accents or common PT words)
pt_stop_words = set([
    'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
    'em', 'no', 'na', 'nos', 'nas', 'por', 'pelo', 'pela', 'pelos', 'pelas', 'para', 'pra',
    'com', 'sem', 'sob', 'sobre', 'que', 'se', 'mas', 'e', 'ou', 'nem', 'como', 'quando',
    'não', 'sim', 'ele', 'ela', 'eles', 'elas', 'eu', 'você', 'nós', 'meu', 'minha',
    'seu', 'sua', 'este', 'esta', 'esse', 'essa', 'aquele', 'aquela', 'habilidade',
    'suprema', 'única', 'extra', 'rei', 'lorde', 'demônio', 'deus', 'alma', 'magia'
])

english_candidates = {}

quote_patterns = [
    r'‘([^’]+)’',
    r'\'([^\']+)\'',
    r'“([^”]+)”',
    r'\"([^\"]+)\"',
    r'『([^』]+)』',
    r'\[([^\]]+)\]',
]

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    file_hits = []
    for q_pat in quote_patterns:
        for match in re.findall(q_pat, c):
            m_clean = match.strip()
            # Ignore if very short or very long
            if len(m_clean) < 3 or len(m_clean) > 40:
                continue
            # Check if pure ASCII and contains English words
            # Common English markers: 'King', 'of', 'The', 'Lord', 'Soul', 'Death', 'Fire', 'Flame', 'Dark', 'Light', 'Space', 'Time', 'Skill', 'Barrier', 'Dragon', 'God', 'Eater', 'Steal', 'Eye', 'Break', 'Burst', 'Warp', 'Overlord', 'Master', 'Star'
            eng_markers = [
                'King', 'Lord', 'Soul', 'Death', 'Flame', 'Dark', 'Light', 'Space',
                'Time', 'Skill', 'Barrier', 'Dragon', 'Eater', 'Steal', 'Eye',
                'Break', 'Burst', 'Warp', 'Master', 'Star', 'Pure', 'End', 'World',
                'Heart', 'Speed', 'Mind', 'Shadow', 'Blade', 'Sword', 'Wind',
                'Strike', 'Storm', 'Thunder', 'Puppet', 'Gourmet', 'Predation'
            ]
            for em in eng_markers:
                if re.search(r'\b' + em + r'\b', m_clean, re.IGNORECASE):
                    # Check if it has obvious Portuguese words (de, do, da, o, a, etc.)
                    words = m_clean.lower().split()
                    if not any(w in pt_stop_words for w in words):
                        file_hits.append(m_clean)
                    break
    
    if file_hits:
        english_candidates[f] = sorted(list(set(file_hits)))

print(f"Files with English quoted candidates: {len(english_candidates)}")
for f, hits in english_candidates.items():
    print(f"=== {f} ({len(hits)}) ===")
    print("  ", hits[:20])
