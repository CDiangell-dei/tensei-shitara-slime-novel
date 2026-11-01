import json

with open('all_translator_notes.json', 'r', encoding='utf-8') as f:
    notes = json.load(f)

# Deduplicate by volume and note
by_vol = {}
for n in notes:
    v = n['volume']
    if v not in by_vol:
        by_vol[v] = []
    # check if note text already in by_vol[v]
    if not any(x['note'] == n['note'] for x in by_vol[v]):
        by_vol[v].append(n)

for v in sorted(by_vol.keys(), key=lambda x: float(x.replace('-5', '.5'))):
    print(f"\n==================== VOLUME {v} ({len(by_vol[v])} notes) ====================")
    for i, n in enumerate(by_vol[v]):
        print(f"[{i+1}] {n['note']}")
