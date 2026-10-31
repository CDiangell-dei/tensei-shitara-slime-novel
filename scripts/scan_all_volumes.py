import urllib.request
import ssl
import re
from bs4 import BeautifulSoup
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

base_url = "https://sites.google.com/view/tssdklscanptbr"

# Check all possible volume pages
volume_candidates = [
    ("Volume 1", "/volume-1"),
    ("Volume 1 - Ilustrações", "/volume-1/ilustrações"),
    ("Volume 2", "/volume-2/volume-2"),
    ("Volume 2 - Ilustrações", "/volume-2/ilustrações"),
    ("Volume 3", "/volume-3/vl-3"),
    ("Volume 3 - Ilustrações", "/volume-3/ilustrações-3"),
    ("Volume 4", "/volume-4"),
    ("Volume 4 - Ilustrações", "/volume-4/ilustrações-4"),
    ("Volume 5", "/volume-5"),
    ("Volume 5 - Ilustrações", "/volume-5/ilustrações"),
    ("Volume 6", "/volume-6"),
    ("Volume 6 - Ilustrações", "/volume-6/ilustrações"),
    ("Volume 7", "/volume-7"),
    ("Volume 7 - Ilustrações", "/volume-7/ilustrações"),
    ("Volume 8", "/volume-8"),
    ("Volume 8.5", "/volume-8-5"),
    ("Volume 8 - Ilustrações", "/volume-8/ilustrações"),
    ("Volume 9", "/volume-9"),
    ("Volume 9 - Ilustrações", "/volume-9/ilustrações"),
    ("Volume 10", "/volume-10"),
    ("Volume 10 - Ilustrações", "/volume-10/ilustrações"),
    ("Volume 11", "/volume-11"),
    ("Volume 12", "/volume-12"),
    ("Volume 13", "/volume-13"),
    ("Volume 14", "/volume-14/aviso-14"),
    ("Volume 15", "/volume-15/aviso-15"),
    ("Volume 16", "/volume-16/aviso-16"),
    ("Volume 17", "/volume-17"),
    ("Volume 18", "/volume-18"),
    ("Volume 19", "/volume-19"),
    ("Volume 20", "/volume-20"),
    ("Volume 21", "/volume-21"),
]

print("Checking TSSDK Scan pages...")
results = []
for label, path in volume_candidates:
    full_url = base_url + urllib.parse.quote(path)
    try:
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(content, 'html.parser')
            ps = soup.find_all('p')
            h2s = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])]
            # search for drive links in this page
            drive_links = re.findall(r'https://drive\.google\.com/[^\s"\'<>]+', content)
            results.append({
                'label': label,
                'path': path,
                'status': resp.status,
                'paragraphs': len(ps),
                'headings': h2s[:5],
                'drive_links': list(set(drive_links))
            })
            print(f"[OK] {label}: {len(ps)} paragraphs, {len(h2s)} headings, {len(drive_links)} drive links")
    except Exception as e:
        print(f"[FAIL] {label} ({path}): {e}")
    time.sleep(0.2)

import json
with open('tssdk_scan_summary.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Finished scanning TSSDK site.")
