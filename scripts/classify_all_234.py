import json
import re

with open('all_translator_notes.json', 'r', encoding='utf-8') as f:
    notes = json.load(f)

unique = {}
for n in notes:
    key = (n['volume'], n['note'])
    if key not in unique:
        unique[key] = n

# Keywords strongly indicating intrusive chatter
chatter_patterns = [
    r'\b(?:kkk+|haha+|rsrs+|jkk+|ksks+|akaka+|kakaka+)\b',
    r'\b(?:fodase|fds|foda|foder|fudeu|fuder|fdp|porra|pora|merda|droga|caralho|crlh|kraio|poha)\b',
    r'\b(?:mds|mdssss+|wtf|stonks|press f|ovo|surprise motherfucker)\b',
    r'\b(?:tadinh[ao]|sdds|ranço|best waifu|gasosa|delicia|tesão|lolicon)\b',
    r'\b(?:burr[ao]|safad[ao]|salafrário|idiota|vagabundo|mendigos|corrupto|folgado)\b',
    r'\b(?:anime|mangá|manga|web novel)\b',
    r'\b(?:deixei em inglês|ingles pq|ficou muito merda|preguiça|frescura|não me pergunte|não sei como)\b',
    r'\b(?:sinceramente|eu acho|na minha opinião|minha shizu|gostei|chorei|to triste|perdi)\b',
    r'\( ͡° ͜ʖ ͡°\)',
    r':v',
    r':x',
    r';-;|\.-_|\._\.|,-,',
    r'\b(?:nossa|carai|mano|seloco|pobre|fetiche|mente poluída)\b',
    r'\b(?:einstein|vidente|baderna|acerto, mizeravi)\b',
]

def is_chatter(text):
    for pat in chatter_patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

chatter_list = []
explanatory_list = []

for key, n in unique.items():
    if is_chatter(n['note']):
        chatter_list.append(n)
    else:
        explanatory_list.append(n)

print(f"Chatter / Opinion notes to DELETE: {len(chatter_list)}")
print(f"Explanatory notes to CHECK: {len(explanatory_list)}")

print("\n--- EXPLANATORY NOTES ---")
for i, n in enumerate(explanatory_list):
    print(f"[{n['volume']}] {n['note']}")
