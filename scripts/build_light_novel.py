"""
PIPELINE UNIFICADO DA LIGHT NOVEL - TENSEI SHITARA SLIME DATTA KEN
1. Extrai Volumes 1 a 5 e 8.5 da TSSDK Scan PT-BR (com CookieJar para baixar todas as ilustrações inline em WebP).
2. Extrai Volumes 6 a 13 da TSSDK Scan PT-BR como edições alternativas comparativas (vol-6-scan .. vol-13-scan).
3. Extrai, corrige e compila Volumes 6 a 20 a partir dos EPUBs de drive_files/ (incluindo Edições Coloridas,
   ilustrações inline, gráficos de poder do Vol. 16, mangás bônus, posfácios e notas culturais interativas).
4. Gera cópias .epub revisadas em drive_files_corrigidos/ e o relatório data/translation_comparison.json.
"""

import os
import io
import re
import ssl
import json
import glob
import time
import zipfile
import urllib.request
import urllib.parse
import http.cookiejar
import warnings
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, NavigableString, Tag, XMLParsedAsHTMLWarning
from PIL import Image

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from fix_translation import correct_text_block, fix_epub_file

BASE_TSSDK = "https://sites.google.com/view/tssdklscanptbr"
EPUB_DIR = "drive_files"
FIXED_EPUB_DIR = "drive_files_corrigidos"
LN_DATA_DIR = "data/light_novel"
ILLUS_ROOT = "assets/illustrations/ln"

# Banner global do topo do Google Sites que não é ilustração da novel
TSSDK_BANNER_TOKEN = "AMxu72tCBmUSYqVpC0AFMTW4n3W-59FcRVcUvUqQOD9WPUyZFDNUF3XDv_N2mvx91bCZ"

TSSDK_VOLUMES = [
    {"id": "vol-1", "num": 1, "title": "Volume 1: Morte e Reencarnação", "path": "/volume-1", "primary": True},
    {"id": "vol-2", "num": 2, "title": "Volume 2: O Despertar da Floresta & O Lorde Orc", "path": "/volume-2/volume-2", "primary": True},
    {"id": "vol-3", "num": 3, "title": "Volume 3: A Ameaça de Charybdis & O Tratado das Bestas", "path": "/volume-3/vl-3", "primary": True},
    {"id": "vol-4", "num": 4, "title": "Volume 4: Rumo às Terras Humanas & As Crianças Invocadas", "path": "/volume-4", "primary": True},
    {"id": "vol-5", "num": 5, "title": "Volume 5: Nascimento do Lorde Demônio & Megiddo", "path": "/volume-5", "primary": True},
    {"id": "vol-6", "num": 6, "title": "Volume 6: O Banquete de Walpurgis (Tradução TSSDK Scan)", "path": "/volume-6", "primary": False},
    {"id": "vol-7", "num": 7, "title": "Volume 7: Santos e Monstros Colidem (Tradução TSSDK Scan)", "path": "/volume-7", "primary": False},
    {"id": "vol-8", "num": 8, "title": "Volume 8: Reconciliação e Pactos (Tradução TSSDK Scan)", "path": "/volume-8", "primary": False},
    {"id": "vol-8-5", "num": 8.5, "title": "Volume 8.5: Histórias Extras & Guia Oficial", "path": "/volume-8-5", "primary": True},
    {"id": "vol-9", "num": 9, "title": "Volume 9: O Festival da Fundação (Tradução TSSDK Scan)", "path": "/volume-9", "primary": False},
    {"id": "vol-10", "num": 10, "title": "Volume 10: O Labirinto e Mariabell (Tradução TSSDK Scan)", "path": "/volume-10", "primary": False},
    {"id": "vol-11", "num": 11, "title": "Volume 11: O Despertar da Heroína do Tempo (Tradução TSSDK Scan)", "path": "/volume-11", "primary": False},
    {"id": "vol-12", "num": 12, "title": "Volume 12: A Marcha do Império Oriental (Tradução TSSDK Scan)", "path": "/volume-12", "primary": False},
    {"id": "vol-13", "num": 13, "title": "Volume 13: Cerco ao Labirinto (Tradução TSSDK Scan)", "path": "/volume-13", "primary": False},
]

EPUB_VOLUMES = [
    {"id": "vol-6", "num": 6, "colored": False, "file": "Volume 06 (Traduzido Português).epub", "title": "Volume 6: O Banquete de Walpurgis & O Octagrama"},
    {"id": "vol-7", "num": 7, "colored": False, "file": "Volume 07 Links Corrigidos (Traduzido Português).epub", "title": "Volume 7: Confronto entre Santos e Monstros"},
    {"id": "vol-8", "num": 8, "colored": False, "file": "Volume 08 (Traduzido Português).epub", "title": "Volume 8: Reconciliação, Pactos e Preparativos"},
    {"id": "vol-9", "num": 9, "colored": False, "file": "Volume 09 (Traduzido Português).epub", "title": "Volume 9: O Grande Festival da Fundação de Tempest"},
    {"id": "vol-10", "num": 10, "colored": False, "file": "Volume 10 (Traduzido Português).epub", "title": "Volume 10: O Labirinto e a Armadilha da Ganância"},
    {"id": "vol-11", "num": 11, "colored": True, "file": "Volume 11 - Colored Edition (Traduzido Português).epub", "title": "Volume 11: A Melancolia Dourada & O Herói do Tempo"},
    {"id": "vol-12", "num": 12, "colored": True, "file": "Volume 12 - Colored Edition (Traduzido Português).epub", "title": "Volume 12: Guerra no Horizonte — A Marcha do Império"},
    {"id": "vol-13", "num": 13, "colored": True, "file": "Volume 13 - Colored Edition (Traduzido Português).epub", "title": "Volume 13: A Grande Devastação no Labirinto"},
    {"id": "vol-14", "num": 14, "colored": True, "file": "Volume 14 - Colored Edition (Traduzido Português).epub", "title": "Volume 14: A Purificação do Lótus Vermelho & A Ira"},
    {"id": "vol-15", "num": 15, "colored": True, "file": "Volume 15 - Colored Edition (Traduzido Português).epub", "title": "Volume 15: Dragão Escaldante vs. Dragão da Tempestade"},
    {"id": "vol-16", "num": 16, "colored": True, "file": "Volume 16 - Colored Edition (Traduzido Português).epub", "title": "Volume 16: A Desintegração da Ordem & Entrevistas"},
    {"id": "vol-17", "num": 17, "colored": True, "file": "Volume 17 - Colored Edition (Traduzido Português).epub", "title": "Volume 17: Memórias Distantes — Contos Paralelos"},
    {"id": "vol-18", "num": 18, "colored": False, "file": "Volume 18 (Traduzido Português).epub", "title": "Volume 18: O Segundo Walpurgis & Ambição Despedaçada"},
    {"id": "vol-19", "num": 19, "colored": False, "file": "Volume 19 (Traduzido Português).epub", "title": "Volume 19: A Investida do Arcanjo & A Capital em Chamas"},
    {"id": "vol-20", "num": 20, "colored": True, "file": "Volume 20 - Colored Edition (Traduzido Português).epub", "title": "Volume 20: Feldway & A Batalha da Árvore Sagrada"},
]

SPLASH_RE = re.compile(r'^(prologue|chapter[-_]\d+|interlude(?:[-_]\d+)?|epilogue)\.(?:png|jpe?g|webp|gif)$', re.IGNORECASE)
SCENE_BREAK_TEXT_RE = re.compile(r'^(?:[*＊][\s*＊]*[*＊]|[-—–]{3,}|[◇♦◆●○]{2,}|[~～]{3,}|[…\.]{6,})$')


def save_optimized_webp(raw_bytes: bytes, dest_rel_path: str, max_dim: int = 1200, quality: int = 83):
    """Converte bytes de imagem para WebP otimizado e retorna (rel_path_posix, width, height)."""
    os.makedirs(os.path.dirname(dest_rel_path), exist_ok=True)
    with Image.open(io.BytesIO(raw_bytes)) as im:
        # Converter paleta/transparência de forma limpa
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            im = im.convert('RGBA')
        else:
            im = im.convert('RGB')

        w, h = im.size
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            w = max(1, int(round(w * scale)))
            h = max(1, int(round(h * scale)))
            im = im.resize((w, h), Image.Resampling.LANCZOS)

        im.save(dest_rel_path, format='WEBP', quality=quality, method=4)
        return dest_rel_path.replace('\\', '/'), w, h


def format_heading_case(h: str) -> str:
    """Melhora títulos em CAIXA ALTA da scan preservando siglas/nomes."""
    h = re.sub(r'\s+', ' ', h).strip()
    if h.isupper() and len(h) > 4:
        h = h.title()
        for small in ('De', 'Da', 'Do', 'Das', 'Dos', 'E', 'Em', 'Na', 'No', 'Nas', 'Nos', 'Para', 'Com', 'Um', 'Uma', 'O', 'A', 'Os', 'As'):
            h = re.sub(rf'(?<!^)(?<!:\s)(?<!-\s)\b{small}\b', small.lower(), h)
    return correct_text_block(h)


def compile_tssdk_volume(meta: dict, force_refresh: bool = False):
    """Baixa e estrutura um volume da TSSDK Scan PT-BR com ilustrações locais."""
    vol_id = meta['id']
    is_primary = meta['primary']
    out_id = vol_id if is_primary else f"{vol_id}-scan"
    out_file = os.path.join(LN_DATA_DIR, f"{out_id}.json")
    illus_dir = os.path.join(ILLUS_ROOT, out_id)

    if not force_refresh and os.path.exists(out_file) and os.path.getsize(out_file) > 10000:
        with open(out_file, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        if cached.get('illustrations_count', 0) > 0 and cached.get('chapter_count', 0) > 0:
            print(f"[TSSDK] Usando cache existente de {out_id}.json ({cached['illustrations_count']} ilustrações WebP).")
            return cached

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ctx),
        urllib.request.HTTPCookieProcessor(cj),
    )
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
    ]

    url = BASE_TSSDK + urllib.parse.quote(meta['path'])
    print(f"[TSSDK] Baixando {out_id} de {url} ...")
    html = opener.open(url, timeout=30).read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')

    chapters = []
    opening_images = []
    all_illustrations = []
    current_ch = None
    pending_heading = None
    in_toc = False
    seen_page_title = False
    seen_img_tokens = set()
    img_counter = 0

    def flush_chapter():
        nonlocal current_ch
        if current_ch and current_ch['blocks']:
            current_ch['paragraphs'] = [b['text'] for b in current_ch['blocks'] if b['type'] == 'p']
            chapters.append(current_ch)
        current_ch = None

    def download_tssdk_img(src_url: str):
        nonlocal img_counter
        if not src_url or TSSDK_BANNER_TOKEN in src_url or '=w16383' in src_url:
            return None
        if 'sitesv-images-rt' not in src_url and 'googleusercontent' not in src_url:
            return None

        # Normalizar token para evitar duplicatas
        base_token = src_url.split('=')[0]
        if base_token in seen_img_tokens:
            return None
        seen_img_tokens.add(base_token)

        dl_url = base_token + "=w1280"
        img_counter += 1
        dest_rel = os.path.join(illus_dir, f"img_{img_counter:02d}.webp")

        if os.path.exists(dest_rel) and os.path.getsize(dest_rel) > 1024:
            with Image.open(dest_rel) as existing_im:
                w, h = existing_im.size
            rel_posix = dest_rel.replace('\\', '/')
        else:
            try:
                raw_img = opener.open(dl_url, timeout=20).read()
                if len(raw_img) < 800:
                    img_counter -= 1
                    return None
                rel_posix, w, h = save_optimized_webp(raw_img, dest_rel, max_dim=1150, quality=82)
            except Exception as e:
                print(f"  [Aviso] Falha ao baixar imagem {img_counter} de {out_id}: {e}")
                img_counter -= 1
                return None

        if w < 90 and h < 90:
            # Ícone decorativo pequeno
            return None

        cat = 'cover' if len(all_illustrations) == 0 else ('insert' if current_ch is None else 'inline')
        label = 'Capa Oficial' if cat == 'cover' else ('Ilustração de Abertura' if cat == 'insert' else f"Ilustração {len(all_illustrations) + 1}")
        entry = {
            'src': rel_posix,
            'width': w,
            'height': h,
            'category': cat,
            'caption': f"{label} — {meta['title']} (Arte: Mitz Vah)",
        }
        all_illustrations.append(entry)
        return {
            'type': 'img',
            'src': rel_posix,
            'width': w,
            'height': h,
            'alt': entry['caption'],
            'caption': label,
        }

    def walk(node):
        nonlocal seen_page_title, in_toc, pending_heading, current_ch
        for child in node.children:
            if not isinstance(child, Tag):
                continue
            name = child.name.lower()
            if name in ('script', 'style', 'nav', 'header', 'footer'):
                continue

            if name == 'img':
                if not seen_page_title:
                    continue
                img_block = download_tssdk_img(child.get('src', ''))
                if img_block:
                    if pending_heading:
                        flush_chapter()
                        current_ch = {'title': pending_heading, 'blocks': []}
                        pending_heading = None
                    if current_ch is None:
                        opening_images.append(img_block)
                    else:
                        current_ch['blocks'].append(img_block)
                continue

            if name in ('h1', 'h2', 'h3', 'h4'):
                # Verificar se há imagens dentro do heading
                for sub_img in child.find_all('img'):
                    if seen_page_title:
                        ib = download_tssdk_img(sub_img.get('src', ''))
                        if ib:
                            (opening_images if current_ch is None else current_ch['blocks']).append(ib)

                htxt = re.sub(r'\s+', ' ', child.get_text(" ", strip=True)).strip()
                if not htxt:
                    continue
                low = htxt.lower()
                if not seen_page_title and 'light novel' in low:
                    seen_page_title = True
                    continue
                seen_page_title = True

                if low in ('sumário', 'sumario', 'índice', 'indice'):
                    in_toc = True
                    continue

                in_toc = False
                clean_h = format_heading_case(htxt)
                if len(clean_h) > 130:
                    # Provavelmente um parágrafo estilizado como heading
                    if current_ch is None:
                        current_ch = {'title': 'Prólogo', 'blocks': []}
                    current_ch['blocks'].append({'type': 'p', 'text': clean_h})
                    continue

                if pending_heading:
                    # Mesclar ex: "Capítulo 1" + "Meu Primeiro Amigo"
                    if ':' not in pending_heading and '-' not in pending_heading:
                        pending_heading = f"{pending_heading}: {clean_h}"
                    else:
                        pending_heading = f"{pending_heading} — {clean_h}"
                else:
                    pending_heading = clean_h
                continue

            if name == 'p':
                if seen_page_title:
                    for sub_img in child.find_all('img'):
                        ib = download_tssdk_img(sub_img.get('src', ''))
                        if ib:
                            if pending_heading:
                                flush_chapter()
                                current_ch = {'title': pending_heading, 'blocks': []}
                                pending_heading = None
                            (opening_images if current_ch is None else current_ch['blocks']).append(ib)

                ptxt = child.get_text(" ", strip=True)
                if not ptxt or ptxt.startswith('window.') or ptxt.startswith('DOCS_'):
                    continue
                if not seen_page_title:
                    continue
                if in_toc and len(ptxt) < 95:
                    continue
                if in_toc and len(ptxt) >= 95:
                    in_toc = False

                if pending_heading:
                    flush_chapter()
                    current_ch = {'title': pending_heading, 'blocks': []}
                    pending_heading = None

                if current_ch is None:
                    # Nota da scan antes do primeiro capítulo ou início direto
                    current_ch = {'title': 'Abertura / Prólogo', 'blocks': []}

                if SCENE_BREAK_TEXT_RE.match(ptxt.strip()):
                    if current_ch['blocks'] and current_ch['blocks'][-1]['type'] != 'hr':
                        current_ch['blocks'].append({'type': 'hr', 'variant': 'soft'})
                else:
                    cleaned_p = correct_text_block(ptxt)
                    if cleaned_p:
                        current_ch['blocks'].append({'type': 'p', 'text': cleaned_p})
                continue

            # Outras tags container (div, section, main, article, etc.)
            walk(child)

    walk(soup.body or soup)
    if pending_heading and current_ch is None:
        current_ch = {'title': pending_heading, 'blocks': []}
    flush_chapter()

    if opening_images:
        chapters.insert(0, {
            'title': 'Capa & Ilustrações de Abertura',
            'blocks': opening_images,
            'paragraphs': [f"[Galeria de Abertura com {len(opening_images)} ilustrações oficiais de Mitz Vah]"],
        })

    data = {
        'id': out_id,
        'base_volume_id': vol_id,
        'volume_number': meta['num'],
        'title': meta['title'],
        'edition': 'TSSDK Scan PT-BR (Tradução de Fã)',
        'is_colored_edition': meta['num'] in (11, 12, 13),
        'source': 'TSSDK Scan PT-BR',
        'source_url': url,
        'cover_image': all_illustrations[0]['src'] if all_illustrations else None,
        'illustrations_count': len(all_illustrations),
        'illustrations': all_illustrations,
        'footnotes': {},
        'chapter_count': len(chapters),
        'chapters': chapters,
    }

    os.makedirs(LN_DATA_DIR, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    p_total = sum(len(c['paragraphs']) for c in chapters)
    print(f"  -> Salvo {out_id}.json: {len(chapters)} seções, {p_total} parágrafos, {len(all_illustrations)} ilustrações WebP.")
    return data


def parse_epub_toc_titles(z: zipfile.ZipFile, names: list[str]) -> list[str]:
    """Lê toc.ncx para obter a lista ordenada de títulos dos capítulos (revisados em PT-BR)."""
    ncx_files = [n for n in names if n.lower().endswith('.ncx')]
    if not ncx_files:
        return []
    raw = z.read(ncx_files[0]).decode('utf-8', errors='ignore')
    soup = BeautifulSoup(raw, 'html.parser')
    titles = []
    for np in soup.find_all('navpoint'):
        lbl = np.find('text')
        if lbl:
            t = correct_text_block(lbl.get_text(" ", strip=True))
            if t and t.lower() not in ('conteúdo', 'índice', 'cobrir', 'capa', 'notas', 'mangá', 'posfácio'):
                titles.append(t)
    return titles


def extract_epub_footnotes(z: zipfile.ZipFile, spine_files: list[str]):
    """Localiza o arquivo de Notas e retorna (notes_filename, raw_footnotes_dict, fixed_footnotes_dict)."""
    candidate_files = list(reversed(spine_files)) + [
        n for n in reversed(sorted(z.namelist()))
        if n.lower().endswith(('.html', '.xhtml', '.htm')) and n not in spine_files
    ]
    for sf in candidate_files:
        if sf not in z.namelist():
            continue
        raw = z.read(sf).decode('utf-8', errors='ignore')
        if 'id="id_Top_of_notes_xhtml"' in raw or ('←' in raw and 'Notas' in raw):
            soup = BeautifulSoup(raw, 'html.parser')
            body = soup.body or soup
            raw_notes = {}
            cur_num = None
            cur_parts = []
            for p in body.find_all('p'):
                txt = p.get_text(" ", strip=True)
                if not txt or txt.lower() == 'notas':
                    continue
                m = re.match(r'^\[\s*←\s*(\d+)\s*\]\s*(.*)$', txt)
                if m:
                    if cur_num is not None and cur_parts:
                        raw_notes[cur_num] = " ".join(cur_parts).strip()
                    cur_num = m.group(1)
                    rest = m.group(2).strip()
                    cur_parts = [rest] if rest else []
                elif cur_num is not None:
                    cur_parts.append(txt)
            if cur_num is not None and cur_parts:
                raw_notes[cur_num] = " ".join(cur_parts).strip()

            if raw_notes:
                fixed_notes = {k: correct_text_block(v) for k, v in raw_notes.items() if v}
                return os.path.basename(sf), raw_notes, fixed_notes
    return None, {}, {}


def resolve_zip_href(base_file: str, rel_href: str) -> str:
    """Resolve caminho relativo dentro do arquivo ZIP do EPUB."""
    rel_clean = rel_href.split('#')[0]
    base_dir = os.path.dirname(base_file)
    joined = os.path.normpath(os.path.join(base_dir, rel_clean)).replace('\\', '/')
    return joined.lstrip('/')


def compile_epub_volume(meta: dict, comparison_samples: list):
    """Extrai, repara e compila um volume da Light Novel a partir do EPUB em drive_files/."""
    vol_id = meta['id']
    epub_path = os.path.join(EPUB_DIR, meta['file'])
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB não encontrado: {epub_path}")

    # 1. Gerar também o EPUB corrigido em drive_files_corrigidos/ (se ainda não existir)
    fixed_epub_name = f"Volume {meta['num']:02d}{' - Edição Colorida' if meta['colored'] else ''} (Revisado PT-BR).epub"
    fixed_epub_path = os.path.join(FIXED_EPUB_DIR, fixed_epub_name)
    if not (os.path.exists(fixed_epub_path) and os.path.getsize(fixed_epub_path) > 100000):
        fix_epub_file(epub_path, fixed_epub_path)

    illus_dir = os.path.join(ILLUS_ROOT, vol_id)
    out_file = os.path.join(LN_DATA_DIR, f"{vol_id}.json")

    print(f"[EPUB] Compilando {vol_id} ({meta['file']}) ...")

    with zipfile.ZipFile(epub_path, 'r') as z:
        names = z.namelist()
        opf_files = [n for n in names if n.lower().endswith('.opf')]
        if not opf_files:
            raise RuntimeError(f"OPF ausente em {epub_path}")
        opf_path = opf_files[0]
        opf_base = os.path.dirname(opf_path)

        root = ET.fromstring(z.read(opf_path).decode('utf-8', errors='ignore'))
        manifest = {
            it.attrib.get('id'): it.attrib.get('href')
            for it in root.findall('.//{http://www.idpf.org/2007/opf}item')
        }
        spine_files = []
        for ir in root.findall('.//{http://www.idpf.org/2007/opf}itemref'):
            href = manifest.get(ir.attrib.get('idref'))
            if href:
                full = f"{opf_base}/{href}".lstrip('/') if opf_base else href
                spine_files.append(full)

        toc_titles = parse_epub_toc_titles(z, names)
        toc_cursor = 0
        notes_basename, _, footnotes_map = extract_epub_footnotes(z, spine_files)

        chapters = []
        opening_images = []
        all_illustrations = []
        extracted_zip_imgs = {}  # zip_img_path -> entry dict
        img_counter = 0

        current_ch = None
        pending_break_kind = None  # 'story' | 'manga' | 'afterword'
        corrections_count = 0

        def flush_chapter():
            nonlocal current_ch
            if current_ch and current_ch['blocks']:
                p_list = [b['text'] for b in current_ch['blocks'] if b['type'] == 'p']
                if not p_list:
                    img_cnt = sum(1 for b in current_ch['blocks'] if b['type'] == 'img')
                    p_list = [f"[{current_ch['title']} — {img_cnt} páginas ilustradas oficiais]"]
                current_ch['paragraphs'] = p_list
                chapters.append(current_ch)
            current_ch = None

        def extract_epub_image(zip_img_path: str):
            nonlocal img_counter
            if zip_img_path not in names:
                return None
            bname = os.path.basename(zip_img_path)
            low_b = bname.lower()

            if 'hardscenebreak' in low_b:
                return {'type': 'hr', 'variant': 'hard'}
            if 'softscenebreak' in low_b:
                return {'type': 'hr', 'variant': 'soft'}
            if SPLASH_RE.match(bname):
                return {'type': 'splash', 'stem': os.path.splitext(low_b)[0]}

            if zip_img_path in extracted_zip_imgs:
                # Evitar duplicar a capa (titlepage.xhtml + index_split_001.html)
                return None

            img_counter += 1
            dest_rel = os.path.join(illus_dir, f"img_{img_counter:02d}.webp")

            is_chart_or_manga = low_b.startswith('chart') or low_b.startswith('manga')
            max_dim = 1350 if is_chart_or_manga else 1200

            if os.path.exists(dest_rel) and os.path.getsize(dest_rel) > 1024:
                with Image.open(dest_rel) as eim:
                    w, h = eim.size
                rel_posix = dest_rel.replace('\\', '/')
            else:
                raw_img = z.read(zip_img_path)
                rel_posix, w, h = save_optimized_webp(raw_img, dest_rel, max_dim=max_dim, quality=84)

            if 'cover' in low_b:
                cat, label = 'cover', 'Capa Oficial'
            elif low_b.startswith('insert'):
                cat, label = 'insert', f"Ilustração Colorida de Abertura ({bname.split('.')[0].replace('insert', '#')})"
            elif low_b.startswith('chart'):
                char_name = re.sub(r'^Chart|\..*$', '', bname)
                cat, label = 'chart', f"Gráfico Oficial de Poder — {char_name}"
            elif low_b.startswith('manga'):
                cat, label = 'manga', f"Mangá Bônus ({bname.split('.')[0]})"
            elif 'endcard' in low_b or low_b.startswith('promo'):
                cat, label = 'endcard', 'Arte Promocional / Encerramento'
            else:
                cat, label = 'inline', f"Ilustração Oficial {len(all_illustrations) + 1}"

            entry = {
                'src': rel_posix,
                'width': w,
                'height': h,
                'category': cat,
                'caption': f"{label} — {meta['title']} (Arte: Mitz Vah)",
            }
            extracted_zip_imgs[zip_img_path] = entry
            all_illustrations.append(entry)
            return {
                'type': 'img',
                'src': rel_posix,
                'width': w,
                'height': h,
                'category': cat,
                'alt': entry['caption'],
                'caption': label,
            }

        for sf in spine_files:
            if sf not in names:
                continue
            sf_base = os.path.basename(sf)
            if notes_basename and sf_base == notes_basename:
                continue

            raw_html = z.read(sf).decode('utf-8', errors='ignore')

            # Pular páginas puras de índice, créditos ou navegação final
            if any(marker in raw_html for marker in ('id_Top_of_credits_xhtml', 'id_Top_of_contents_xhtml', 'id_Top_of_nav_xhtml')):
                continue

            soup = BeautifulSoup(raw_html, 'html.parser')
            body = soup.body or soup

            h_texts = [h.get_text(" ", strip=True) for h in body.find_all(['h1', 'h2', 'h3'])]
            if h_texts and h_texts[0].lower() in ('índice', 'conteúdo'):
                continue

            body_plain = body.get_text(" ", strip=True)
            img_tags_in_file = body.find_all(['img', 'image'])
            if not img_tags_in_file and body_plain in ('Mangá Posfácio', 'Posfácio Notas', 'Cover', ''):
                continue

            # Pré-processar âncoras de notas de rodapé para {{FN:N}}
            for a_tag in list(body.find_all('a')):
                href = a_tag.get('href', '')
                aid = a_tag.get('id', '')
                is_fn = (notes_basename and notes_basename in href) or bool(re.search(r'#id_\d+_', href))
                if is_fn:
                    atxt = a_tag.get_text(strip=True)
                    m_num = re.match(r'^(\d+)$', atxt)
                    if m_num and m_num.group(1) in footnotes_map:
                        a_tag.replace_with(NavigableString(f"{{{{FN:{m_num.group(1)}}}}}"))
                    elif not atxt:
                        a_tag.decompose()

            # Verificar se é início do Posfácio
            if 'id_Top_of_afterword_xhtml' in raw_html or re.match(r'^Posfácio\b', body_plain):
                flush_chapter()
                current_ch = {'title': 'Posfácio do Autor (Fuse)', 'blocks': []}
                pending_break_kind = None

            # Percorrer nós do arquivo atual
            pending_label_prefix = None  # Ex: "Prólogo", "Capítulo 1", "Interlúdio", "Epílogo"

            def walk_epub(node):
                nonlocal current_ch, pending_break_kind, pending_label_prefix, toc_cursor, corrections_count
                for child in node.children:
                    if not isinstance(child, Tag):
                        continue
                    tname = child.name.lower()
                    if tname in ('script', 'style'):
                        continue

                    if tname in ('img', 'image'):
                        src = child.get('src') or child.get('xlink:href') or child.get('href')
                        if not src:
                            continue
                        zpath = resolve_zip_href(sf, src)
                        res = extract_epub_image(zpath)
                        if not res:
                            continue
                        if res['type'] == 'splash':
                            flush_chapter()
                            pending_break_kind = 'story'
                            continue
                        if res['type'] == 'hr':
                            if current_ch and current_ch['blocks'] and current_ch['blocks'][-1]['type'] != 'hr':
                                current_ch['blocks'].append(res)
                            continue
                        if res['type'] == 'img':
                            cat = res.get('category')
                            if cat in ('cover', 'insert') and current_ch is None and not chapters:
                                opening_images.append(res)
                            elif cat == 'manga':
                                if current_ch is None or current_ch['title'] != 'Mangá Bônus':
                                    flush_chapter()
                                    current_ch = {'title': 'Mangá Bônus', 'blocks': []}
                                current_ch['blocks'].append(res)
                            else:
                                if current_ch is None:
                                    # Caso promo/endcard venha após mangá/posfácio
                                    current_ch = {'title': 'Galeria Extra & Encerramento', 'blocks': []}
                                current_ch['blocks'].append(res)
                        continue

                    if tname in ('h1', 'h2', 'h3', 'p'):
                        # Primeiro processar quaisquer imagens embutidas dentro de <p> ou <h1> (ex: scenebreaks)
                        inner_imgs = child.find_all(['img', 'image'])
                        for im_el in inner_imgs:
                            src = im_el.get('src') or im_el.get('xlink:href') or im_el.get('href')
                            if src:
                                zpath = resolve_zip_href(sf, src)
                                res = extract_epub_image(zpath)
                                if res:
                                    if res['type'] == 'splash':
                                        flush_chapter()
                                        pending_break_kind = 'story'
                                    elif res['type'] == 'hr':
                                        if current_ch and current_ch['blocks'] and current_ch['blocks'][-1]['type'] != 'hr':
                                            current_ch['blocks'].append(res)
                                    elif res['type'] == 'img':
                                        if res.get('category') in ('cover', 'insert') and current_ch is None and not chapters:
                                            opening_images.append(res)
                                        elif res.get('category') == 'manga':
                                            if current_ch is None or current_ch['title'] != 'Mangá Bônus':
                                                flush_chapter()
                                                current_ch = {'title': 'Mangá Bônus', 'blocks': []}
                                            current_ch['blocks'].append(res)
                                        else:
                                            if current_ch is None:
                                                current_ch = {'title': 'Galeria Extra & Encerramento', 'blocks': []}
                                            current_ch['blocks'].append(res)
                            im_el.decompose()

                        raw_txt = child.get_text(" ", strip=True)
                        if not raw_txt or raw_txt == 'Cover':
                            continue

                        # Se estivermos no Posfácio e a primeira linha for apenas "Posfácio", não repetir
                        if current_ch and current_ch['title'].startswith('Posfácio') and not current_ch['blocks'] and raw_txt.strip().lower() == 'posfácio':
                            continue

                        # Início de novo capítulo após splash (ou Vol 17 Cap 1)
                        if pending_break_kind == 'story' or (current_ch is None and (tname in ('h1', 'h2') or re.match(r'^(Prólogo|Capítulo\s*\d+|Interlúdio(?:\s*\d+)?|Epílogo)$', raw_txt.strip(), re.IGNORECASE))):
                            if tname == 'p' and re.match(r'^(Prólogo|Capítulo\s*\d+|Interlúdio(?:\s*\d+)?|Epílogo)$', raw_txt.strip(), re.IGNORECASE):
                                pending_label_prefix = correct_text_block(raw_txt.strip()).title()
                                continue
                            if tname in ('h1', 'h2', 'h3'):
                                raw_h = raw_txt.strip()
                                fixed_h = correct_text_block(raw_h)
                                if raw_h != fixed_h:
                                    corrections_count += 1
                                    if len(comparison_samples) < 24:
                                        comparison_samples.append({
                                            'volume': f"Volume {meta['num']}",
                                            'context': 'Título de Capítulo',
                                            'raw_drive': raw_h,
                                            'repaired_ptbr': fixed_h,
                                        })
                                # Preferir título completo do TOC quando bate com a posição atual
                                if toc_cursor < len(toc_titles):
                                    ch_title = toc_titles[toc_cursor]
                                    toc_cursor += 1
                                elif pending_label_prefix:
                                    ch_title = f"{pending_label_prefix}: {fixed_h}"
                                else:
                                    ch_title = fixed_h
                                pending_label_prefix = None
                                pending_break_kind = None
                                flush_chapter()
                                current_ch = {'title': ch_title, 'blocks': []}
                                continue
                            elif pending_break_kind == 'story':
                                # Fallback caso o capítulo comece direto com parágrafo sem <h1>
                                ch_title = toc_titles[toc_cursor] if toc_cursor < len(toc_titles) else (pending_label_prefix or f"Capítulo {len(chapters) + 1}")
                                if toc_cursor < len(toc_titles):
                                    toc_cursor += 1
                                pending_label_prefix = None
                                pending_break_kind = None
                                flush_chapter()
                                current_ch = {'title': ch_title, 'blocks': []}

                        if current_ch is None:
                            current_ch = {'title': 'Abertura', 'blocks': []}

                        if SCENE_BREAK_TEXT_RE.match(raw_txt.strip()):
                            if current_ch['blocks'] and current_ch['blocks'][-1]['type'] != 'hr':
                                current_ch['blocks'].append({'type': 'hr', 'variant': 'soft'})
                            continue

                        fixed_p = correct_text_block(raw_txt)
                        # Contabilizar amostras reais de correção substancial (não apenas espaços)
                        norm_raw = re.sub(r'\s+', ' ', raw_txt).strip()
                        if fixed_p != norm_raw:
                            corrections_count += 1
                            # Guardar amostras interessantes para o Comparador
                            if len(comparison_samples) < 28 and any(
                                kw in norm_raw for kw in (
                                    'Ultimate Skill', 'Campo de golfe', 'Cara Carmesim', 'Cara,', 'Lacaio',
                                    'Carreira', 'Corrida:', 'fotografar', 'pode realmente ser ajudado',
                                    'Primordial Branco', 'Primordial Amarelo', 'Magic Beast Corps', 'Fusível'
                                )
                            ):
                                clean_disp_raw = re.sub(r'\{\{FN:\d+\}\}', '', norm_raw)
                                clean_disp_fix = re.sub(r'\{\{FN:\d+\}\}', '', fixed_p)
                                if not any(s['raw_drive'][:55] == clean_disp_raw[:55] for s in comparison_samples):
                                    comparison_samples.append({
                                        'volume': f"Volume {meta['num']}",
                                        'context': current_ch['title'],
                                        'raw_drive': clean_disp_raw[:280],
                                        'repaired_ptbr': clean_disp_fix[:280],
                                    })

                        if fixed_p:
                            current_ch['blocks'].append({'type': 'p', 'text': fixed_p})
                        continue

                    walk_epub(child)

            walk_epub(body)

        flush_chapter()

        if opening_images:
            chapters.insert(0, {
                'title': 'Capa & Ilustrações Coloridas',
                'blocks': opening_images,
                'paragraphs': [f"[Galeria de Abertura com {len(opening_images)} ilustrações oficiais de Mitz Vah]"],
            })

        if footnotes_map:
            fn_blocks = [
                {'type': 'p', 'text': f"[Nota {k}] {v}"}
                for k, v in sorted(footnotes_map.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)
            ]
            chapters.append({
                'title': f"Notas Culturais & de Tradução ({len(footnotes_map)})",
                'blocks': fn_blocks,
                'paragraphs': [b['text'] for b in fn_blocks],
            })

    edition_label = (
        "Edição Colorida Ilustrada — Revisada PT-BR"
        if meta['colored']
        else "Edição Ilustrada Completa — Revisada PT-BR"
    )
    has_scan_alt = 6 <= meta['num'] <= 13

    data = {
        'id': vol_id,
        'base_volume_id': vol_id,
        'volume_number': meta['num'],
        'title': meta['title'],
        'edition': edition_label,
        'is_colored_edition': meta['colored'],
        'has_scan_alternative': has_scan_alt,
        'scan_alternative_id': f"{vol_id}-scan" if has_scan_alt else None,
        'source': 'Drive EPUB Oficial (Revisado & Padronizado em PT-BR)',
        'cover_image': all_illustrations[0]['src'] if all_illustrations else None,
        'illustrations_count': len(all_illustrations),
        'illustrations': all_illustrations,
        'footnotes': footnotes_map,
        'corrections_applied': corrections_count,
        'chapter_count': len(chapters),
        'chapters': chapters,
    }

    os.makedirs(LN_DATA_DIR, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    p_total = sum(len(c['paragraphs']) for c in chapters)
    print(f"  -> Salvo {vol_id}.json: {len(chapters)} seções, {p_total} parágrafos, "
          f"{len(all_illustrations)} ilustrações WebP, {len(footnotes_map)} notas culturais, "
          f"{corrections_count} parágrafos reparados.")
    return data


def main():
    start = time.time()
    all_illus_index = {}
    comparison_samples = []
    total_corrections = 0

    # 1. Compilar volumes TSSDK (1..5 + 8.5 primários, e 6..13 edições alternativas da scan)
    for tmeta in TSSDK_VOLUMES:
        try:
            d = compile_tssdk_volume(tmeta)
            all_illus_index[d['id']] = d['illustrations']
            time.sleep(0.3)
        except Exception as e:
            print(f"[ERRO TSSDK {tmeta['id']}]: {e}")

    # 2. Compilar e corrigir todos os 15 EPUBs do Drive (Volumes 6 a 20)
    for emeta in EPUB_VOLUMES:
        d = compile_epub_volume(emeta, comparison_samples)
        all_illus_index[d['id']] = d['illustrations']
        total_corrections += d.get('corrections_applied', 0)

    # 3. Salvar índice consolidado de ilustrações locais (zero URLs externas expiradas!)
    with open('data/illustrations.json', 'w', encoding='utf-8') as f:
        json.dump(all_illus_index, f, ensure_ascii=False, indent=2)

    # 4. Salvar dossiê comparativo das traduções (Drive Original vs Revisado vs TSSDK Scan)
    comp_report = {
        'total_paragraphs_repaired': total_corrections,
        'epubs_repaired_count': len(EPUB_VOLUMES),
        'overlapping_volumes': [6, 7, 8, 9, 10, 11, 12, 13],
        'samples': comparison_samples[:18],
    }
    with open('data/translation_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(comp_report, f, ensure_ascii=False, indent=2)

    print(f"\nPipeline da Light Novel finalizado em {time.time() - start:.1f}s! "
          f"Total de blocos reparados nos EPUBs: {total_corrections}.")


if __name__ == '__main__':
    main()
