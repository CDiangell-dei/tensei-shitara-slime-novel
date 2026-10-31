import urllib.request
import ssl
from bs4 import BeautifulSoup
import json
import re
import os
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

base_url = "https://sites.google.com/view/tssdklscanptbr"

volumes_meta = [
    {"id": "vol-1", "num": 1, "title": "Volume 1: Morte e Reencarnação", "path": "/volume-1"},
    {"id": "vol-2", "num": 2, "title": "Volume 2: O Despertar da Floresta", "path": "/volume-2/volume-2"},
    {"id": "vol-3", "num": 3, "title": "Volume 3: A Ameaça de Charybdis", "path": "/volume-3/vl-3"},
    {"id": "vol-4", "num": 4, "title": "Volume 4: Rumo às Terras Humanas", "path": "/volume-4"},
    {"id": "vol-5", "num": 5, "title": "Volume 5: Nascimento do Lorde Demônio", "path": "/volume-5"},
    {"id": "vol-6", "num": 6, "title": "Volume 6: O Walpurgis", "path": "/volume-6"},
    {"id": "vol-7", "num": 7, "title": "Volume 7: Demônios e Esquemas", "path": "/volume-7"},
    {"id": "vol-8", "num": 8, "title": "Volume 8: Reconciliação e Pactos", "path": "/volume-8"},
    {"id": "vol-8-5", "num": 8.5, "title": "Volume 8.5: Histórias Extras & Fanbook", "path": "/volume-8-5"},
    {"id": "vol-9", "num": 9, "title": "Volume 9: O Festival da Fundação de Tempest", "path": "/volume-9"},
    {"id": "vol-10", "num": 10, "title": "Volume 10: O Labirinto e a Cobiça", "path": "/volume-10"},
    {"id": "vol-11", "num": 11, "title": "Volume 11: A Melancolia Dourada e o Herói do Tempo", "path": "/volume-11"},
    {"id": "vol-12", "num": 12, "title": "Volume 12: Conspiração no Império Oriental", "path": "/volume-12"},
    {"id": "vol-13", "num": 13, "title": "Volume 13: A Grande Guerra Imperial", "path": "/volume-13"}
]

os.makedirs('data/light_novel', exist_ok=True)

def parse_html_to_chapters(html, vol_title):
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p'])
    
    chapters = []
    current_chapter = None
    
    for el in elements:
        text = el.get_text().strip()
        if not text:
            continue
            
        # Check if heading
        if el.name in ['h1', 'h2', 'h3']:
            lower = text.lower()
            is_ch = any(k in lower for k in ['prólogo', 'prologo', 'capítulo', 'capitulo', 'epílogo', 'epilogo', 'interlúdio', 'interludio', 'intervalo', 'nota do autor', 'posfácio', 'posfacio'])
            if is_ch or (current_chapter is None and len(text) < 80):
                if current_chapter and current_chapter['paragraphs']:
                    chapters.append(current_chapter)
                current_chapter = {
                    'title': text,
                    'paragraphs': []
                }
                continue
                
        # Paragraph
        if el.name == 'p':
            if current_chapter is None:
                current_chapter = {'title': 'Início / Prólogo', 'paragraphs': []}
            if not text.startswith('window.') and not text.startswith('DOCS_') and len(text) > 2:
                current_chapter['paragraphs'].append(text)
                
    if current_chapter and current_chapter['paragraphs']:
        chapters.append(current_chapter)
        
    return chapters

for meta in volumes_meta:
    out_file = f"data/light_novel/{meta['id']}.json"
    if os.path.exists(out_file):
        print(f"Skipping {meta['id']}, already exists.")
        continue
        
    url = base_url + urllib.parse.quote(meta['path'])
    print(f"Downloading {meta['title']} from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            chapters = parse_html_to_chapters(html, meta['title'])
            
            data = {
                'id': meta['id'],
                'volume_number': meta['num'],
                'title': meta['title'],
                'source': 'TSSDK Scan PT-BR',
                'source_url': url,
                'chapter_count': len(chapters),
                'chapters': chapters
            }
            
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  -> Saved {meta['id']}.json with {len(chapters)} chapters and {sum(len(c['paragraphs']) for c in chapters)} paragraphs.")
    except Exception as e:
        print(f"  -> Error downloading {meta['id']}: {e}")
    time.sleep(0.5)

print("Light Novel compilation finished.")
