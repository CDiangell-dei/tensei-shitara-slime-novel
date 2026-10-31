import urllib.request
import ssl
from bs4 import BeautifulSoup
import json
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

illus_sources = [
    {"vol_id": "vol-1", "title": "Volume 1", "url": "https://sites.google.com/view/tssdklscanptbr/volume-1/ilustra%C3%A7%C3%B5es"},
    {"vol_id": "vol-2", "title": "Volume 2", "url": "https://sites.google.com/view/tssdklscanptbr/volume-2/ilustra%C3%A7%C3%B5es"},
    {"vol_id": "vol-3", "title": "Volume 3", "url": "https://sites.google.com/view/tssdklscanptbr/volume-3/ilustra%C3%A7%C3%B5es-3"},
    {"vol_id": "vol-4", "title": "Volume 4", "url": "https://sites.google.com/view/tssdklscanptbr/volume-4/ilustra%C3%A7%C3%B5es-4"},
    {"vol_id": "vol-5", "title": "Volume 5", "url": "https://sites.google.com/view/tssdklscanptbr/volume-5/ilustra%C3%A7%C3%B5es"},
    {"vol_id": "vol-6", "title": "Volume 6", "url": "https://sites.google.com/view/tssdklscanptbr/volume-6/ilustra%C3%A7%C3%B5es"},
    {"vol_id": "vol-7", "title": "Volume 7", "url": "https://sites.google.com/view/tssdklscanptbr/volume-7/ilustra%C3%A7%C3%B5es"},
    {"vol_id": "vol-8", "title": "Volume 8", "url": "https://sites.google.com/view/tssdklscanptbr/volume-8/ilustra%C3%A7%C3%B5es"},
    {"vol_id": "vol-9", "title": "Volume 9", "url": "https://sites.google.com/view/tssdklscanptbr/volume-9/ilustra%C3%A7%C3%B5es"},
    {"vol_id": "vol-10", "title": "Volume 10", "url": "https://sites.google.com/view/tssdklscanptbr/volume-10/ilustra%C3%A7%C3%B5es"},
]

illustrations_by_vol = {}

for item in illus_sources:
    vol_id = item['vol_id']
    try:
        req = urllib.request.Request(item['url'], headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            soup = BeautifulSoup(resp.read().decode('utf-8', errors='ignore'), 'html.parser')
            imgs = []
            for img in soup.find_all('img'):
                src = img.get('src')
                # Ignore tiny icons or header background
                if src and 'sitesv-images-rt' in src and not src.endswith('=w16383'):
                    imgs.append(src)
            illustrations_by_vol[vol_id] = {
                'title': item['title'],
                'page_url': item['url'],
                'images_count': len(imgs),
                'images': imgs
            }
            print(f"[{item['title']}] Found {len(imgs)} official illustrations!")
    except Exception as e:
        print(f"Error {item['title']}: {e}")

with open('data/illustrations.json', 'w', encoding='utf-8') as f:
    json.dump(illustrations_by_vol, f, ensure_ascii=False, indent=2)

print("Saved data/illustrations.json successfully!")
