import json

with open('all_translator_notes.json', 'r', encoding='utf-8') as f:
    notes = json.load(f)

for n in notes[:25]:
    print("="*60)
    print(f"[{n['volume']} - {n['chapter']}]")
    print("NOTE:", n['note'])
    print("FULL:", n['full_paragraph'])
