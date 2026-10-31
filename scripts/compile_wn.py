"""
COMPILADOR COMPLETO DA WEB NOVEL - TENSEI SHITARA SLIME DATTA KEN
Extrai todos os capítulos principais (0 a 249, incluindo intermissões .5)
e todos os 48 Capítulos Extras (Jogo de Fuga Elegante do Rimuru, Visita ao Desconhecido e Side Stories)
diretamente do Central Novel, limpando artefatos e traduzindo títulos residuais em inglês.
"""

import urllib.request
import ssl
from bs4 import BeautifulSoup
import json
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

SERIES_URL = "https://centralnovel.com/series/tensei-shitara-slime-datta-ken/"
OUT_DIR = "data/web_novel"
INDEX_PATH = "web_novel_index.json"

TITLE_TRANSLATIONS = [
    (r'\bDragon Aircraft Exterior\b', 'Exterior da Aeronave Dragão'),
    (r'^SS\s*-\s*', 'História Especial - '),
    (r'\bvs\b', 'vs.'),
    (r'-Ultima Parte-', '-Última Parte-'),
    (r'\bO Inicio\b', 'O Início'),
    (r'\bApostolo\b', 'Apóstolo'),
]

NOISE_SUBSTRINGS = [
    'leia em centralnovel',
    'central novel',
    'centralnovel.com',
    'todos os direitos reservados',
    'apoie o site',
    'desative o adblock',
]

def clean_wn_title(title: str) -> str:
    t = re.sub(r'\s+', ' ', (title or '')).strip()
    for pat, rep in TITLE_TRANSLATIONS:
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)
    return t

def clean_wn_paragraph(text: str) -> str:
    t = re.sub(r'[ \t]+', ' ', text).strip()
    # Remover possíveis artefatos duplicados se houver
    t = re.sub(r'\s+([,.;:?!])', r'\1', t)
    return t

def fetch_series_index():
    if os.path.exists(INDEX_PATH):
        try:
            with open(INDEX_PATH, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            if isinstance(cached, list) and len(cached) >= 300 and 'id' in cached[0] and 'file' in cached[0]:
                print(f"Carregado índice existente de {INDEX_PATH} ({len(cached)} capítulos).")
                return cached
        except Exception:
            pass

    print(f"Buscando índice completo da Web Novel em {SERIES_URL} ...")
    req = urllib.request.Request(SERIES_URL, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
        html = resp.read().decode('utf-8', errors='ignore')

    soup = BeautifulSoup(html, 'html.parser')
    eplisters = soup.find_all('div', class_='eplister')
    print(f"Encontrados {len(eplisters)} blocos .eplister.")

    entries = []
    seen_urls = set()

    for ep_div in eplisters:
        for li in ep_div.find_all('li'):
            a = li.find('a')
            if not a or not a.get('href'):
                continue
            url = a['href'].strip()
            if url in seen_urls:
                continue
            seen_urls.add(url)

            num_div = li.find('div', class_='epl-num')
            title_div = li.find('div', class_='epl-title')
            raw_num = num_div.get_text(" ", strip=True) if num_div else ""
            raw_title = title_div.get_text(" ", strip=True) if title_div else a.get_text(" ", strip=True)

            is_extra = 'extra' in raw_num.lower() or '-extra-' in url.lower()

            if is_extra:
                m_ex = re.search(r'Cap\.\s*(\d+(?:\.\d+)?)', raw_num, re.IGNORECASE) or re.search(r'extra-(\d+)', url, re.IGNORECASE)
                ex_num = int(float(m_ex.group(1))) if m_ex else 0
                ch_id = f"extra-{ex_num:03d}"
                file_name = f"extra_{ex_num:03d}.json"
                sort_key = (1, ex_num)
                vol_num = 11
                display_num = f"Extra {ex_num:02d}"
            else:
                m_vol = re.search(r'Vol\.\s*(\d+)', raw_num, re.IGNORECASE)
                vol_num = int(m_vol.group(1)) if m_vol else 1
                m_cap = re.search(r'Cap\.\s*(\d+(?:\.\d+)?)', raw_num, re.IGNORECASE) or re.search(r'capitulo-(\d+(?:-\d+)?)', url, re.IGNORECASE)
                cap_str = m_cap.group(1).replace('-', '.') if m_cap else "0"
                cap_float = float(cap_str)
                if cap_float.is_integer():
                    cap_int = int(cap_float)
                    ch_id = f"cap-{cap_int:03d}"
                    file_name = f"capitulo_{cap_int:03d}.json"
                    display_num = f"Capítulo {cap_int}"
                else:
                    parts = cap_str.split('.')
                    ch_id = f"cap-{int(parts[0]):03d}-{parts[1]}"
                    file_name = f"capitulo_{int(parts[0]):03d}_{parts[1]}.json"
                    display_num = f"Capítulo {cap_str}"
                sort_key = (0, cap_float)

            clean_t = clean_wn_title(raw_title)
            entries.append({
                'id': ch_id,
                'is_extra': is_extra,
                'vol_wn': vol_num,
                'num': ex_num if is_extra else (int(cap_float) if cap_float.is_integer() else cap_float),
                'display_num': display_num,
                'raw_label': raw_num,
                'title': clean_t if clean_t else display_num,
                'url': url,
                'file': file_name,
                '_sort': sort_key,
            })

    entries.sort(key=lambda x: x['_sort'])
    for e in entries:
        del e['_sort']

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Índice salvo em {INDEX_PATH}: {len(entries)} capítulos totais "
          f"({sum(1 for e in entries if not e['is_extra'])} principais + {sum(1 for e in entries if e['is_extra'])} extras).")
    return entries

def download_one(entry, force_refresh_early=True):
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, entry['file'])

    # Rebaixar capítulos 0..30 caso tenham parentéticos repetidos da execução antiga
    if os.path.exists(out_path):
        if not force_refresh_early:
            return entry['id'], True, 0
        try:
            with open(out_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            sample_txt = " ".join(existing.get('paragraphs', [])[:20])
            if 'Kijin (Ogro Divino)' not in sample_txt and 'Majin (Nascido da Magia)' not in sample_txt and existing.get('id') == entry['id'] and len(existing.get('paragraphs', [])) > 3:
                return entry['id'], True, len(existing['paragraphs'])
        except Exception:
            pass

    for attempt in range(4):
        try:
            if attempt > 0:
                time.sleep(3.5 * attempt)
            else:
                time.sleep(1.5)
            req = urllib.request.Request(entry['url'], headers={
                **HEADERS,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': SERIES_URL,
            })
            with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            soup = BeautifulSoup(html, 'html.parser')
            content_div = (
                soup.find('div', class_='epcontent')
                or soup.find('div', class_='entry-content')
                or soup.find('div', class_='text-left')
            )

            paragraphs = []
            if content_div:
                # Extrair parágrafos e divisores de cena
                for el in content_div.find_all(['p', 'h2', 'h3', 'h4', 'hr']):
                    if el.name == 'hr':
                        if paragraphs and paragraphs[-1] != '* * *':
                            paragraphs.append('* * *')
                        continue
                    txt = clean_wn_paragraph(el.get_text(" ", strip=True))
                    if not txt:
                        continue
                    low = txt.lower()
                    if any(ns in low for ns in NOISE_SUBSTRINGS):
                        continue
                    if len(txt) == 1 and txt not in ('…', '*'):
                        continue
                    paragraphs.append(txt)

                # Fallback caso o capítulo use <br> direto sem <p>
                if len(paragraphs) < 3:
                    raw_lines = [clean_wn_paragraph(line) for line in content_div.get_text('\n').splitlines()]
                    paragraphs = [
                        ln for ln in raw_lines
                        if ln and not any(ns in ln.lower() for ns in NOISE_SUBSTRINGS)
                    ]

            data = {
                'id': entry['id'],
                'number': entry['num'],
                'display_num': entry['display_num'],
                'is_extra': entry['is_extra'],
                'vol_wn': entry['vol_wn'],
                'title': entry['title'],
                'url': entry['url'],
                'paragraph_count': len(paragraphs),
                'paragraphs': paragraphs,
            }

            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return entry['id'], True, len(paragraphs)
        except Exception as e:
            if attempt == 2:
                return entry['id'], False, str(e)
            time.sleep(2.5 * (attempt + 1))

def fallback_from_blogger_feed(failed_entries: list[dict]) -> int:
    """Fallback oficial via feed JSON do Blog do Amon Novels caso o Wordfence do Central Novel limite alguma URL."""
    if not failed_entries:
        return 0
    print(f"\nAcionando fallback via feed JSON (categoria 'Rimuru') para {len(failed_entries)} capítulos...")
    all_posts = []
    start = 1
    while True:
        feed_url = f"https://www.blogdoamonnovels.com/feeds/posts/default/-/Rimuru?alt=json&max-results=100&start-index={start}"
        req = urllib.request.Request(feed_url, headers=HEADERS)
        raw = urllib.request.urlopen(req, context=ctx, timeout=25).read().decode('utf-8', errors='ignore')
        feed_data = json.loads(raw)
        total_res = int(feed_data.get('feed', {}).get('openSearch$totalResults', {}).get('$t', 0))
        batch = feed_data.get('feed', {}).get('entry', [])
        if not batch:
            break
        all_posts.extend(batch)
        start += len(batch)
        if start > total_res:
            break

    recovered = 0
    for entry in failed_entries:
        target_num = int(entry['num'])
        is_extra = entry['is_extra']
        matched = None
        for p in all_posts:
            pt = p.get('title', {}).get('$t', '').strip()
            low = pt.lower()
            if is_extra and re.search(rf'cap[íi]tulo extra\s*0*{target_num}\b', low):
                matched = p
                break
            elif not is_extra and 'extra' not in low and re.search(rf'cap[íi]tulo\s*0*{target_num}\b(?!\.)', low):
                matched = p
                break
        if not matched:
            continue

        soup = BeautifulSoup(matched.get('content', {}).get('$t', ''), 'html.parser')
        for bad in soup.find_all(['script', 'style']):
            bad.decompose()
        for hr in soup.find_all('hr'):
            hr.replace_with('\n* * *\n')
        for br in soup.find_all('br'):
            br.replace_with('\n')
        for blk in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'li']):
            blk.insert_before('\n')
            blk.insert_after('\n')

        paras = []
        for raw_ln in soup.get_text().splitlines():
            txt = clean_wn_paragraph(raw_ln)
            if not txt or any(ns in txt.lower() for ns in NOISE_SUBSTRINGS):
                continue
            if any(txt.startswith(k) for k in ('Web Novel Sobre a Minha', 'Leia online em português', 'Acesse o capítulo completo', 'https://drive.google.com/')):
                continue
            if txt == '* * *':
                if paras and paras[-1] != '* * *':
                    paras.append('* * *')
                continue
            paras.append(txt)

        while paras and (paras[0] == '* * *' or paras[0].startswith('Capítulo ') or paras[0].startswith('Extra ')):
            paras.pop(0)
        if len(paras) >= 2 and paras[-2:] == ['Sobre a Minha Reencarnação Como Um Slime', 'Fuse']:
            paras = paras[:-2]

        out_path = os.path.join(OUT_DIR, entry['file'])
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                'id': entry['id'],
                'number': entry['num'],
                'display_num': entry['display_num'],
                'is_extra': entry['is_extra'],
                'vol_wn': entry['vol_wn'],
                'title': entry['title'],
                'url': entry['url'],
                'paragraph_count': len(paras),
                'paragraphs': paras,
            }, f, ensure_ascii=False, indent=2)
        recovered += 1
        print(f"  [RECUPERADO] {entry['id']} ({len(paras)} parágrafos)")
    return recovered


def main():
    entries = fetch_series_index()
    entries_by_id = {e['id']: e for e in entries}
    total = len(entries)
    done = 0
    failed = []
    start_t = time.time()

    print(f"Verificando / baixando {total} capítulos da Web Novel (sequencial com retry suave)...", flush=True)
    with ThreadPoolExecutor(max_workers=1) as pool:
        futures = {pool.submit(download_one, e): e for e in entries}
        for fut in as_completed(futures):
            ch_id, ok, info = fut.result()
            done += 1
            if not ok:
                failed.append((ch_id, info))
                print(f"  [FALHA] {ch_id}: {info}")
            elif done % 25 == 0 or done == total:
                elapsed = time.time() - start_t
                print(f"  Progresso: {done}/{total} capítulos ({elapsed:.1f}s)")

    if failed:
        rec = fallback_from_blogger_feed([entries_by_id[cid] for cid, _ in failed if cid in entries_by_id])
        print(f"Recuperados via fallback: {rec}/{len(failed)}")

    saved_count = sum(1 for e in entries if os.path.exists(os.path.join(OUT_DIR, e['file'])))
    print(f"\nConcluído! {saved_count}/{total} capítulos salvos em {OUT_DIR}/.")

if __name__ == '__main__':
    main()
