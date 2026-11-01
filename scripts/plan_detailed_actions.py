import json
import re

with open('all_translator_notes.json', 'r', encoding='utf-8') as f:
    notes = json.load(f)

# Group by note text and examine
# We will classify each of the 234 notes:
# 1. 'DELETE': Remove paragraph completely.
# 2. 'INLINE_MERGE': If it's a measurement like (NT: 91 metros), merge into previous paragraph cleanly, then delete note paragraph.
# 3. 'CLEAN_NOTE': If it's a footnote or inline text, strip the meme/reaction part.

actions = []

# List of measurements to integrate inline into prev paragraph if desired:
# e.g., 'cem jardas' -> 'cem jardas (cerca de 91 metros)'
# e.g., '20 milhas por hora' -> '20 milhas por hora (cerca de 32 km/h)'

for n in notes:
    text = n['note'].strip()
    full = n['full_paragraph'].strip()
    v = n['volume']
    ch = n['chapter']
    
    # Is it inline inside a paragraph?
    if full != text and full != text + '.' and full != '(' + text + ')':
        actions.append({
            'volume': v,
            'chapter': ch,
            'type': 'inline',
            'full': full,
            'note': text,
            'action': 'strip_from_paragraph'
        })
    else:
        # It's a standalone paragraph!
        actions.append({
            'volume': v,
            'chapter': ch,
            'type': 'standalone',
            'full': full,
            'note': text,
            'action': 'delete_paragraph'
        })

print(f"Total actions: {len(actions)}")
inline_actions = [a for a in actions if a['type'] == 'inline']
print(f"Inline actions: {len(inline_actions)}")
for a in inline_actions:
    print(f"[{a['volume']}] {a['note']} in: {a['full'][:100]}")
