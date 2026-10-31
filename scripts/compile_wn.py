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

os.makedirs('data/web_novel', exist_ok=True)

with open('web_novel_index.json', 'r', encoding='utf-8') as f:
    all_chapters = json.load(f)

print(f"Loaded {len(all_chapters)} chapters from web_novel_index.json")

def download_chapter(ch_item):
    num = ch_item['num']
    out_file = f"data/web_novel/capitulo_{num:03d}.json"
    if os.path.exists(out_file):
        return True
        
    url = ch_item['url']
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Title
            title_el = soup.find('h1')
            title = title_el.get_text().strip() if title_el else f"Capítulo {num}"
            title = re.sub(r'\s+', ' ', title)
            
            # Subtitle / chapter subtitle if exists
            sub_title = ""
            for h in soup.find_all(['h2', 'h3']):
                t = h.get_text().strip()
                if t and not any(k in t.lower() for k in ['comentários', 'deixe uma resposta', 'navegação']):
                    sub_title = t
                    break

            # Content container
            content_div = soup.find('div', class_='epcontent') or soup.find('div', class_='entry-content') or soup.find('div', class_='text-left')
            paragraphs = []
            if content_div:
                for p in content_div.find_all('p'):
                    txt = p.get_text().strip()
                    if txt and len(txt) > 2 and not any(k in txt.lower() for k in ['leia em centralnovel', 'central novel', 'todos os direitos']):
                        paragraphs.append(txt)
                        
            data = {
                'number': num,
                'title': title,
                'subtitle': sub_title,
                'url': url,
                'paragraph_count': len(paragraphs),
                'paragraphs': paragraphs
            }
            
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  -> Cap {num:03d} saved ({len(paragraphs)} paragraphs)")
            return True
    except Exception as e:
        print(f"  -> Error Cap {num}: {e}")
        return False

# Download initial batch (chapters 0 to 20 for Arc 1 & 2)
if __name__ == '__main__':
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    print(f"Downloading Web Novel chapters from {start} to {end}...")
    for ch in all_chapters:
        if start <= ch['num'] <= end:
            download_chapter(ch)
            time.sleep(0.3)
    print("Done downloading WN batch.")
