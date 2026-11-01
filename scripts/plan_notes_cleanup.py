import json
import re

with open('all_translator_notes.json', 'r', encoding='utf-8') as f:
    notes = json.load(f)

# Deduplicate
by_note = {}
for n in notes:
    v = n['volume']
    note_text = n['note']
    key = (v, note_text)
    if key not in by_note:
        by_note[key] = n

print(f"Total unique notes to classify: {len(by_note)}")

# Let's inspect them and categorize
# We will create a dictionary mapping note_text -> action: 'DELETE' or 'REPLACE' with new text
# If REPLACE, we specify the cleaned text.

cleaned_actions = {}

# Criteria for DELETE:
# - Reaction to scene ("kkkk", "jkk", "mds", "pobre é uma coisa triste", "veio do futuro só pra lamentar", "foda-se", "porra", "fdp", "si fudeu", "muito bom", "gostei", "manga está muito melhor", "caraio", "mano", "tadinha", "best waifu", "ovo destronar meu pai", "stonks", etc.)
# - Complaining about translation or author ("não me pergunte", "fiquei todo perdido", "não sei como colocar", "deixei em inglês mesmo muito mais legal", "preguiça", "frescura", "ficou muito merda em português", etc.)
# - Unnecessary subjective comments on characters ("Rimuru é muito inseguro", "Rimuru muito vacilão", "Gabil é muito burro", "Gobuta é um gênio", etc.)

for (v, note_text), item in by_note.items():
    t = note_text
    # Check if pure chatter
    # Let's write rules
    pass
