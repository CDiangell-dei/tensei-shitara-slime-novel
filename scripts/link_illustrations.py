import json
import os

with open('data/catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

with open('data/illustrations.json', 'r', encoding='utf-8') as f:
    illus = json.load(f)

# Update each LN volume in catalog with its illustrations count and image list
for vol in catalog['light_novel']['volumes']:
    vid = vol['id']
    if vid in illus:
        vol['illustrations_count'] = illus[vid]['images_count']
        vol['illustrations'] = illus[vid]['images']
    else:
        vol['illustrations_count'] = 0
        vol['illustrations'] = []

with open('data/catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("Catalog updated with official illustrations data!")
