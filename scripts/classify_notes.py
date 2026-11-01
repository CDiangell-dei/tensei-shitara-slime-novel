import json
import re

with open('inline_nt_notes.json', 'r', encoding='utf-8') as f:
    notes = json.load(f)

# Deduplicate by note text and file
unique_notes = {}
for n in notes:
    key = (n['file'], n['note'])
    if key not in unique_notes:
        unique_notes[key] = n

print(f"Unique inline notes: {len(unique_notes)}")

opinion_markers = [
    r'\bkkk+\b',
    r'\brsrs+\b',
    r'\bhaha+\b',
    r'\blol\b',
    r'\bmds\b',
    r'\bpqp\b',
    r'\bmano\b',
    r'\bgente\b',
    r'\bnossa\b',
    r'\beita\b',
    r'\bcaraca\b',
    r'\bcaramba\b',
    r'\bputz\b',
    r'\baff\b',
    r'\bcoitad[oa]\b',
    r'\bsafad[oa]\b',
    r'\bburr[oa]\b',
    r'eu acho',
    r'na minha opinião',
    r'minha opinião',
    r'sinceramente',
    r'não acredito',
    r'olha isso',
    r'morri',
    r'berro',
    r'odeio',
    r'adoro',
    r'gosto',
    r'pra mim',
    r'para mim',
    r'meu deus',
    r'ai ai',
    r'fazer o que',
    r'fazer o quê',
    r'foda',
    r'merda',
    r'droga',
    r'velho',
    r'né\?',
    r'né',
    r'né!',
    r'kk',
    r'haha',
]

suspect_notes = []
other_notes = []

for key, item in unique_notes.items():
    text = item['note']
    is_suspect = False
    matched_markers = []
    for m in opinion_markers:
        if re.search(m, text, re.IGNORECASE):
            is_suspect = True
            matched_markers.append(m)
    if is_suspect:
        suspect_notes.append((item, matched_markers))
    else:
        other_notes.append(item)

print(f"Suspect opinion/reaction notes: {len(suspect_notes)}")
print(f"Other explanatory notes: {len(other_notes)}")

with open('suspect_notes.json', 'w', encoding='utf-8') as out:
    json.dump([{'file': s[0]['file'], 'markers': s[1], 'note': s[0]['note'], 'context': s[0]['context']} for s in suspect_notes], out, ensure_ascii=False, indent=2)

for s, markers in suspect_notes[:30]:
    print(f"[{s['file']}] ({', '.join(markers)}) --> {s['note']}")
