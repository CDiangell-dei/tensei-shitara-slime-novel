"""
COMPILADOR E TRADUTOR PT-BR DOS VOLUMES FINAIS (21, 22 E 23) — TENSEI SHITARA SLIME DATTA KEN
Extrai texto integral e todas as ilustrações oficiais em alta resolução de Mitz Vah,
converte as artes para WebP otimizado localmente, protege todos os nomes próprios canônicos
contra tradução literal, traduz os capítulos para Português Brasileiro (PT-BR) natural com
cache em disco e aplica o motor de padronização terminológica de fix_translation.py.
"""

import os
import io
import re
import time
import json
import hashlib
import zipfile
import warnings
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from PIL import Image

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_translation import correct_text_block

LN_DATA_DIR = "data/light_novel"
ILLUS_ROOT = "assets/illustrations/ln"

SCRATCH_ROOT = os.environ.get(
    "TENSURA_SCRATCH_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scratch")
)
SRC_DIR = os.path.join(SCRATCH_ROOT, "v21_23_sources")
CACHE_DIR = os.path.join(SCRATCH_ROOT, "ptbr_translation_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

V21_EPUB = os.path.join(SRC_DIR, "v21_gdoc.epub")
V21_PDF_IMGS = os.path.join(SCRATCH_ROOT, "v21_pdf_imgs")
V22_EPUB = os.environ.get(
    "TENSURA_V22_EPUB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drive_files", "Tensura LN V_22.epub")
)
V23_EPUB = os.path.join(SRC_DIR, "v23_gdoc.epub")

SCENE_BREAK_TEXT_RE = re.compile(r'^(?:[*＊][\s*＊]*[*＊]|[-—–]{3,}|[◇♦◆●○]{2,}|[~～]{3,}|[…\.]{6,}|\*)$')

# Escudos de nomes próprios para impedir tradução literal por tradutor automático
PROPER_NOUN_SHIELDS = [
    # Nomes compostos primeiro
    ("Guy Crimson", "ZxGuyCrimson"),
    ("Rimuru Tempest", "ZxRimuruTempest"),
    ("Veldora Tempest", "ZxVeldoraTempest"),
    ("Luminas Valentine", "ZxLuminasValentine"),
    ("Luminous Valentine", "ZxLuminasValentine"),
    ("Twilight Valentine", "ZxTwilightValentine"),
    ("Chloe Aubert", "ZxChloeAubert"),
    ("Hinata Sakaguchi", "ZxHinataSakaguchi"),
    ("Mai Furuki", "ZxMaiFuruki"),
    ("Yuuki Kagurazaka", "ZxYuukiKagurazaka"),
    ("Masayuki Honjou", "ZxMasayukiHonjou"),
    ("Satoru Mikami", "ZxSatoruMikami"),
    ("Leon Cromwell", "ZxLeonCromwell"),
    ("Gazel Dwargo", "ZxGazelDwargo"),
    ("Milim Nava", "ZxMilimNava"),
    ("Elmesia El Ru Sarion", "ZxElmesiaSarion"),
    ("Jura Tempest", "ZxJuraTempest"),
    # Nomes individuais sensíveis a tradução literal ("Guy"->Cara, "Fuse"->Fusível, "Carrera"->Carreira, "Rain"->Chuva, etc.)
    ("Feldway", "ZxFeldway"),
    ("Guy", "ZxGuy"),
    ("Fuse", "ZxFuse"),
    ("Mitz Vah", "ZxMitzVah"),
    ("Carrera", "ZxCarrera"),
    ("Ultima", "ZxUltima"),
    ("Testarossa", "ZxTestarossa"),
    ("Diablo", "ZxDiablo"),
    ("Raine", "ZxRain"),
    ("Rain", "ZxRain"),
    ("Misery", "ZxMisery"),
    ("Footman", "ZxFootman"),
    ("Teare", "ZxTear"),
    ("Tear", "ZxTear"),
    ("Laplace", "ZxLaplace"),
    ("Kagali", "ZxKagali"),
    ("Kagari", "ZxKagali"),
    ("Moss", "ZxMoss"),
    ("Esprit", "ZxEsprit"),
    ("Venom", "ZxVenom"),
    ("Veyron", "ZxVeyron"),
    ("Agera", "ZxAgera"),
    ("Zonda", "ZxZonda"),
    ("Cien", "ZxCien"),
    ("Charys", "ZxCharys"),
    ("Beretta", "ZxBeretta"),
    ("Ramiris", "ZxRamiris"),
    ("Veldora", "ZxVeldora"),
    ("Velgrynd", "ZxVelgrynd"),
    ("Velzard", "ZxVelzard"),
    ("Veldanava", "ZxVeldanava"),
    ("Rimuru", "ZxRimuru"),
    ("Ciel", "ZxCiel"),
    ("Milim", "ZxMilim"),
    ("Luminas", "ZxLuminas"),
    ("Luminous", "ZxLuminas"),
    ("Dagruel", "ZxDagruel"),
    ("Ashura", "ZxAshura"),
    ("Fenn", "ZxFenn"),
    ("Glassord", "ZxGlassord"),
    ("Dagura", "ZxDagura"),
    ("Ryura", "ZxRyura"),
    ("Liura", "ZxRyura"),
    ("Debura", "ZxDebura"),
    ("Basara", "ZxBasara"),
    ("Zelanus", "ZxZelanus"),
    ("Zegion", "ZxZegion"),
    ("Apito", "ZxApito"),
    ("Peliod", "ZxPeliod"),
    ("Zess", "ZxZess"),
    ("Vega", "ZxVega"),
    ("Dino", "ZxDino"),
    ("Pico", "ZxPico"),
    ("Gracia", "ZxGracia"),
    ("Twilight", "ZxTwilight"),
    ("Ivaragé", "ZxIvarage"),
    ("Ivalaje", "ZxIvarage"),
    ("Ivalage", "ZxIvarage"),
    ("Ivaraj", "ZxIvarage"),
    ("Ivarage", "ZxIvarage"),
    ("Jahil", "ZxJahil"),
    ("Zalario", "ZxZalario"),
    ("Obera", "ZxObera"),
    ("Cornu", "ZxCornu"),
    ("Kakeashi", "ZxKakeashi"),
    ("Habataki", "ZxHabataki"),
    ("Suimu", "ZxSuimu"),
    ("velgaia", "ZxVelgaia"),
    ("Velgaia", "ZxVelgaia"),
    ("Gaia", "ZxGaia"),
    ("Gobuta", "ZxGobuta"),
    ("Ranga", "ZxRanga"),
    ("Benimaru", "ZxBenimaru"),
    ("Shion", "ZxShion"),
    ("Shuna", "ZxShuna"),
    ("Souei", "ZxSouei"),
    ("Souka", "ZxSouka"),
    ("Gabil", "ZxGabil"),
    ("Geld", "ZxGeld"),
    ("Adalmann", "ZxAdalmann"),
    ("Albert", "ZxAlbert"),
    ("Wenti", "ZxWenti"),
    ("Gadra", "ZxGadra"),
    ("Kumara", "ZxKumara"),
    ("Chloe", "ZxChloe"),
    ("Chronoa", "ZxChronoa"),
    ("Hinata", "ZxHinata"),
    ("Masayuki", "ZxMasayuki"),
    ("Rudra", "ZxRudra"),
    ("Elmesia", "ZxElmesia"),
    ("Sylvia", "ZxSylvia"),
    ("Leon", "ZxLeon"),
    ("Gazel", "ZxGazel"),
    ("Sarion", "ZxSarion"),
    ("Lubelius", "ZxRuberios"),
    ("Ruberios", "ZxRuberios"),
    ("Damargania", "ZxDamargania"),
    ("Ingrassia", "ZxIngrassia"),
    ("Dwargon", "ZxDwargon"),
    ("Eurazania", "ZxEurazania"),
    ("Michael", "ZxMichael"),
    ("Azathoth", "ZxAzathoth"),
    ("Shub-Niggurath", "ZxShubNiggurath"),
    ("Yog-Sothoth", "ZxYogSothoth"),
    ("Nyarlathotep", "ZxNyarlathotep"),
    ("Beelzebuth", "ZxBeelzebuth"),
    ("Satanael", "ZxSatanael"),
    ("Asmodeus", "ZxAsmodeus"),
    ("Lucifer", "ZxLucifer"),
    ("Leviathan", "ZxLeviata"),
    ("Belphegor", "ZxBelphegor"),
    ("Mammon", "ZxMammon"),
    ("Sariel", "ZxSariel"),
    ("Metatron", "ZxMetatron"),
    ("Raguel", "ZxRaguel"),
    ("Uriel", "ZxUriel"),
    ("Gabriel", "ZxGabriel"),
    ("Raphael", "ZxRaphael"),
    ("Mephisto", "ZxMephisto"),
    ("Amaterasu", "ZxAmaterasu"),
    ("Tsukuyomi", "ZxTsukuyomi"),
    ("Susanoo", "ZxSusanoo"),
    ("Ahura Mazda", "ZxAhuraMazda"),
    ("Deus Ex Machina", "ZxDeusExMachina"),
]

SHIELD_COMPILE = [
    (re.compile(rf'(?<![A-Za-z]){re.escape(orig)}(?![A-Za-z])'), tok)
    for orig, tok in PROPER_NOUN_SHIELDS
]

UNSHIELD_MAP = {}
for orig, tok in PROPER_NOUN_SHIELDS:
    # Mapear para a grafia canônica PT-BR da nossa biblioteca
    canonical = orig
    if orig in ("Luminous Valentine",):
        canonical = "Luminas Valentine"
    elif orig in ("Luminous",):
        canonical = "Luminas"
    elif orig in ("Raine",):
        canonical = "Rain"
    elif orig in ("Teare",):
        canonical = "Tear"
    elif orig in ("Kagari",):
        canonical = "Kagali"
    elif orig in ("Liura",):
        canonical = "Ryura"
    elif orig in ("Ivaragé", "Ivalaje", "Ivalage", "Ivaraj"):
        canonical = "Ivarage"
    elif orig in ("Lubelius",):
        canonical = "Ruberios"
    elif orig in ("Leviathan",):
        canonical = "Leviatã"
    elif orig in ("Lucifer",):
        canonical = "Lúcifer"
    UNSHIELD_MAP[tok] = canonical

# Sufixos honoríficos japoneses para manter intactos
HONORIFIC_RE = re.compile(r'-(sama|san|kun|chan|dono|sensei)\b')


def save_optimized_webp(raw_bytes: bytes, dest_rel_path: str, max_dim: int = 1250, quality: int = 84):
    os.makedirs(os.path.dirname(dest_rel_path), exist_ok=True)
    with Image.open(io.BytesIO(raw_bytes)) as im:
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


def pre_clean_english_paragraph(txt: str) -> str:
    if not txt:
        return ""
    s = txt.strip()
    # Remover notas editoriais duplas ((...)) do rascunho em inglês do Vol. 22
    s = re.sub(r'\(\([^)]*\)\)', '', s)
    # Normalizar falas da Ciel: <<...>> ou 《...》 -> ZxLCIEL ... ZxRCIEL
    s = s.replace('《', 'ZxLCIEL ').replace('》', ' ZxRCIEL')
    s = re.sub(r'<<\s*', 'ZxLCIEL ', s)
    s = re.sub(r'\s*>>', ' ZxRCIEL', s)
    s = s.replace('«', 'ZxLCIEL ').replace('»', ' ZxRCIEL')
    # Proteger honoríficos (-sama, -san, etc.)
    s = HONORIFIC_RE.sub(r'ZxHON_\1', s)
    # Aplicar escudos de nomes próprios
    for rgx, tok in SHIELD_COMPILE:
        s = rgx.sub(tok, s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def post_restore_ptbr_paragraph(txt: str, full_ciel: bool = False) -> str:
    if not txt:
        return ""
    s = txt
    # Restaurar falas da Ciel «...»
    s = re.sub(r'ZxLCIEL\s*', '«', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*ZxRCIEL', '»', s, flags=re.IGNORECASE)
    if full_ciel and '«' in s and not s.lstrip().startswith('«'):
        # Caso o tradutor tenha movido o artigo/sujeito para antes de « (ex: "A interferência do «com...")
        s = re.sub(r'^([^«»]{1,65}?)\s+(?:do|da|de)\s+«\s*', r'«\1 ', s)
        if not s.lstrip().startswith('«'):
            s = '«' + s.replace('«', '')
    # Restaurar honoríficos
    s = re.sub(r'\s*ZxHON_(sama|san|kun|chan|dono|sensei)', lambda m: f"-{m.group(1).lower()}", s, flags=re.IGNORECASE)
    # Restaurar nomes próprios (ordenar por tamanho decrescente de token para não colidir prefixos como ZxGuy vs ZxGuyCrimson)
    for tok, canonical in sorted(UNSHIELD_MAP.items(), key=lambda x: -len(x[0])):
        s = re.sub(re.escape(tok), canonical, s, flags=re.IGNORECASE)
    return correct_text_block(s)


def call_gtx_translate(text: str, retries: int = 5) -> str:
    data = urllib.parse.urlencode({
        'client': 'gtx',
        'sl': 'en',
        'tl': 'pt',
        'dt': 't',
        'q': text,
    }).encode('utf-8')

    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                'https://translate.googleapis.com/translate_a/single',
                data=data,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
                }
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
            return ''.join(seg[0] for seg in payload[0] if seg and seg[0])
        except Exception as e:
            last_err = e
            time.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"Falha ao traduzir lote após {retries} tentativas: {last_err}")


def translate_batch_safe(shielded_items: list[str]) -> list[str]:
    if not shielded_items:
        return []
    if len(shielded_items) == 1:
        raw_out = call_gtx_translate(shielded_items[0])
        return [raw_out.strip()]

    delim = "\nZxPARA\n"
    joined = delim.join(shielded_items)
    raw_out = call_gtx_translate(joined)
    parts = [p.strip() for p in re.split(r'\s*ZxPARA\s*', raw_out, flags=re.IGNORECASE)]
    if len(parts) == len(shielded_items):
        return parts

    # Fallback recursivo garantidor de alinhamento 1-para-1 caso o delimitador sofra fusão
    mid = len(shielded_items) // 2
    left = translate_batch_safe(shielded_items[:mid])
    right = translate_batch_safe(shielded_items[mid:])
    return left + right


def translate_volume_paragraphs(vol_key: str, en_paragraphs: list[str], max_chars_per_batch: int = 3800, workers: int = 8) -> list[str]:
    cache_path = os.path.join(CACHE_DIR, f"{vol_key}_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    shielded_all = [pre_clean_english_paragraph(p) for p in en_paragraphs]
    missing_indices = []
    for idx, sh in enumerate(shielded_all):
        if not sh:
            continue
        h = hashlib.md5(sh.encode('utf-8')).hexdigest()
        if h not in cache:
            missing_indices.append((idx, h, sh))

    print(f"[{vol_key}] Total parágrafos: {len(en_paragraphs)} | Em cache: {len(en_paragraphs) - len(missing_indices)} | A traduzir: {len(missing_indices)}")

    if missing_indices:
        # Agrupar únicos para não traduzir falas idênticas ("What?", "Yes!", etc.) repetidas vezes
        unique_map = {}
        for _, h, sh in missing_indices:
            if h not in unique_map:
                unique_map[h] = sh

        unique_items = list(unique_map.items())  # [(hash, shielded_str), ...]
        batches = []
        cur_batch = []
        cur_len = 0
        for h, sh in unique_items:
            add_len = len(sh) + 10
            if cur_batch and (cur_len + add_len > max_chars_per_batch or len(cur_batch) >= 38):
                batches.append(cur_batch)
                cur_batch = []
                cur_len = 0
            cur_batch.append((h, sh))
            cur_len += add_len
        if cur_batch:
            batches.append(cur_batch)

        print(f"[{vol_key}] Traduzindo {len(unique_items)} segmentos únicos em {len(batches)} lotes (workers={workers})...")
        completed = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            future_to_batch = {
                ex.submit(translate_batch_safe, [item[1] for item in b]): b
                for b in batches
            }
            for fut in as_completed(future_to_batch):
                b = future_to_batch[fut]
                translated_list = fut.result()
                for (h, _), tr_txt in zip(b, translated_list):
                    cache[h] = tr_txt
                completed += 1
                if completed % 15 == 0 or completed == len(batches):
                    print(f"  [{vol_key}] Progresso: {completed}/{len(batches)} lotes concluídos...")
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, ensure_ascii=False)

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False)

    final_ptbr = []
    for sh in shielded_all:
        if not sh:
            final_ptbr.append("")
            continue
        h = hashlib.md5(sh.encode('utf-8')).hexdigest()
        raw_pt = cache.get(h, sh)
        is_full_ciel = sh.startswith('ZxLCIEL') and sh.endswith('ZxRCIEL')
        final_ptbr.append(post_restore_ptbr_paragraph(raw_pt, full_ciel=is_full_ciel))
    return final_ptbr


# ==============================================================================
# 1. VOLUME 21 (Texto revisado GDoc + 14 Ilustrações HD extraídas do PDF oficial)
# ==============================================================================
def build_volume_21():
    vol_id = "vol-21"
    vol_title = "Volume 21: Erosão do Labirinto & Além do Fim"
    illus_dir = os.path.join(ILLUS_ROOT, vol_id)
    os.makedirs(illus_dir, exist_ok=True)

    all_illustrations = []
    img_counter = 0

    def register_hd_image(src_file_path: str, cat: str, label: str, max_dim: int = 1280):
        nonlocal img_counter
        img_counter += 1
        dest_rel = os.path.join(illus_dir, f"img_{img_counter:02d}.webp")
        with open(src_file_path, 'rb') as f:
            raw_bytes = f.read()
        rel_posix, w, h = save_optimized_webp(raw_bytes, dest_rel, max_dim=max_dim, quality=84)
        entry = {
            'src': rel_posix,
            'width': w,
            'height': h,
            'category': cat,
            'caption': f"{label} — {vol_title} (Arte: Mitz Vah)",
        }
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

    # Galeria de abertura em alta resolução (Capa + 3 Artes Coloridas do PDF)
    opening_images = [
        register_hd_image(os.path.join(V21_PDF_IMGS, "pdf_img_01_1350x1920.jpg"), "cover", "Capa Oficial"),
        register_hd_image(os.path.join(V21_PDF_IMGS, "pdf_img_04_2250x1600.jpg"), "insert", "Ilustração Colorida Dupla (#1)", max_dim=1400),
        register_hd_image(os.path.join(V21_PDF_IMGS, "pdf_img_05_1350x1920.jpg"), "insert", "Ilustração Colorida (#2)"),
        register_hd_image(os.path.join(V21_PDF_IMGS, "pdf_img_29_2250x1600.jpg"), "insert", "Arte Completa da Sobrecapa", max_dim=1400),
    ]

    # Mapeamento 1-para-1 das ilustrações inline para as versões HD 1350x1920 do PDF
    inline_hd_map = {
        "images/image2.png": ("pdf_img_11_1350x1920.jpg", "Ilustração Oficial — Veldora vs. Dagruel"),
        "images/image11.png": ("pdf_img_12_1350x1920.jpg", "Ilustração Oficial — O Despertar de Ashura"),
        "images/image12.png": ("pdf_img_14_1350x1920.jpg", "Ilustração Oficial — Sala de Controle do Labirinto"),
        "images/image8.png": ("pdf_img_15_1350x1920.jpg", "Ilustração Oficial — Apito vs. Mai Furuki"),
        "images/image13.png": ("pdf_img_17_1350x1920.jpg", "Ilustração Oficial — A Determinação de Shuna"),
        "images/image16.png": ("pdf_img_18_1350x1920.jpg", "Ilustração Oficial — Diablo & Zegion"),
        "images/image1.png": ("pdf_img_19_1350x1920.jpg", "Ilustração Oficial — Zegion vs. Zelanus"),
        "images/image15.png": ("pdf_img_21_1350x1920.jpg", "Ilustração Oficial — Os Quatro Reis Dragões"),
        "images/image10.png": ("pdf_img_22_1350x1920.jpg", "Ilustração Oficial — A Queda de Vega"),
        "images/image14.png": ("pdf_img_24_1350x1920.jpg", "Ilustração Oficial — Rimuru no Fim do Espaço-Tempo"),
    }
    scenebreak_imgs = {"images/image3.png", "images/image4.png", "images/image9.png"}
    skip_imgs = {"images/image5.png", "images/image6.png", "images/image7.png"}

    chapter_starts = {
        0: "Prólogo: Hora da Decisão",
        92: "Capítulo 1: A Cidade Moribunda",
        907: "Interlúdio: O Rei dos Insetos",
        916: "Capítulo 2: Erosão do Labirinto",
        2301: "Capítulo 3: Pai e Filho",
        2453: "Capítulo 4: Além da Obsessão",
        3112: "Epílogo: Além do Fim",
        3216: "Posfácio do Autor (Fuse)",
    }

    with zipfile.ZipFile(V21_EPUB, 'r') as z:
        soup = BeautifulSoup(z.read("GoogleDoc/V21.xhtml").decode('utf-8', errors='ignore'), 'html.parser')
        blocks = (soup.body or soup).find_all(['h1', 'h2', 'h3', 'h4', 'p'])

    raw_chapters = []
    cur_ch = None
    all_en_texts = []

    for idx, b in enumerate(blocks):
        # Pular trecho colado duplicado acidentalmente no GDoc (blocos 820..877)
        if 820 <= idx <= 877:
            continue

        if idx in chapter_starts:
            if cur_ch and cur_ch['raw_blocks']:
                raw_chapters.append(cur_ch)
            cur_ch = {'title': chapter_starts[idx], 'raw_blocks': []}

        if cur_ch is None:
            cur_ch = {'title': "Prólogo: Hora da Decisão", 'raw_blocks': []}

        for im in b.find_all('img'):
            src = im.get('src', '')
            if src in inline_hd_map:
                pdf_fname, lbl = inline_hd_map[src]
                ib = register_hd_image(os.path.join(V21_PDF_IMGS, pdf_fname), "inline", lbl)
                cur_ch['raw_blocks'].append(ib)
            elif src in scenebreak_imgs:
                if cur_ch['raw_blocks'] and cur_ch['raw_blocks'][-1].get('type') != 'hr':
                    cur_ch['raw_blocks'].append({'type': 'hr', 'variant': 'soft'})
            elif src in skip_imgs:
                pass
            im.decompose()

        txt = re.sub(r'\s+', ' ', b.get_text(" ", strip=True)).strip()
        if not txt:
            continue
        # Remover marcadores puros de intervalo de página do japonês ("87-92", "(164-170)", "(NOTE: Illustration...)")
        if re.match(r'^\(?\d{1,3}\s*[-–]\s*\d{1,3}\)?$', txt):
            continue
        if txt.startswith('(NOTE: Illustration provided'):
            continue
        # Remover prefixo numérico de página colado no início do parágrafo ("56-66 <Confirmed..." ou "(149-155) Thus...")
        txt = re.sub(r'^\(?\d{1,3}\s*[-–]\s*\d{1,3}\)?\s+', '', txt).strip()
        if not txt:
            continue

        if SCENE_BREAK_TEXT_RE.match(txt):
            if cur_ch['raw_blocks'] and cur_ch['raw_blocks'][-1].get('type') != 'hr':
                cur_ch['raw_blocks'].append({'type': 'hr', 'variant': 'soft'})
            continue

        p_ref_idx = len(all_en_texts)
        all_en_texts.append(txt)
        cur_ch['raw_blocks'].append({'type': 'p_ref', 'ref': p_ref_idx})

    if cur_ch and cur_ch['raw_blocks']:
        raw_chapters.append(cur_ch)

    ptbr_texts = translate_volume_paragraphs(vol_id, all_en_texts)

    final_chapters = [{
        'title': 'Capa & Ilustrações Coloridas',
        'blocks': opening_images,
        'paragraphs': [f"[Galeria de Abertura com {len(opening_images)} ilustrações oficiais em alta definição de Mitz Vah]"],
    }]

    for rch in raw_chapters:
        ch_blocks = []
        for blk in rch['raw_blocks']:
            if blk['type'] == 'p_ref':
                t_pt = ptbr_texts[blk['ref']]
                if t_pt:
                    ch_blocks.append({'type': 'p', 'text': t_pt})
            else:
                ch_blocks.append(blk)
        # Limpar <hr> órfãos no início ou fim
        while ch_blocks and ch_blocks[0]['type'] == 'hr':
            ch_blocks.pop(0)
        while ch_blocks and ch_blocks[-1]['type'] == 'hr':
            ch_blocks.pop()
        p_list = [x['text'] for x in ch_blocks if x['type'] == 'p']
        final_chapters.append({
            'title': rch['title'],
            'blocks': ch_blocks,
            'paragraphs': p_list,
        })

    out_data = {
        'id': vol_id,
        'base_volume_id': vol_id,
        'volume_number': 21,
        'title': vol_title,
        'edition': 'Edição Ilustrada Completa — Revisada PT-BR',
        'is_colored_edition': False,
        'has_scan_alternative': False,
        'scan_alternative_id': None,
        'source': 'Edição Ilustrada Compilada & Revisada em PT-BR',
        'cover_image': all_illustrations[0]['src'],
        'illustrations_count': len(all_illustrations),
        'illustrations': all_illustrations,
        'footnotes': {},
        'chapter_count': len(final_chapters),
        'chapters': final_chapters,
    }

    out_path = os.path.join(LN_DATA_DIR, f"{vol_id}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Salvo {out_path}: {len(final_chapters)} seções, {sum(len(c['paragraphs']) for c in final_chapters)} parágrafos, {len(all_illustrations)} ilustrações WebP.")


# ==============================================================================
# 2. VOLUME 22 (Tensura LN V_22.epub — 15 Ilustrações + Designs Oficiais Mitz Vah)
# ==============================================================================
def build_volume_22():
    vol_id = "vol-22"
    vol_title = "Volume 22: Destruição Divina & O Retorno Triunfal"
    illus_dir = os.path.join(ILLUS_ROOT, vol_id)
    os.makedirs(illus_dir, exist_ok=True)

    all_illustrations = []
    img_counter = 0
    extracted_zip_map = {}

    # Cartões divisores verde-azulados de título de capítulo (não são ilustrações de Mitz Vah)
    splash_cards = {"images/image-2.png", "images/image-5.png", "images/image-8.png", "images/image-15.png"}

    chapter_split_map = {
        "index_split_003.html": "Prólogo: Pura Malícia",
        "index_split_005.html": "Capítulo 1: Senhor do Vício",
        "index_split_007.html": "Capítulo 2: Tempo de Desespero",
        "index_split_010.html": "Capítulo 3: Batalha Decisiva",
        "index_split_017.html": "Epílogo: O Despertar do Deus Maligno",
    }

    with zipfile.ZipFile(V22_EPUB, 'r') as z:
        def register_zip_img(zpath: str, cat: str, label: str, max_dim: int = 1250):
            nonlocal img_counter
            if zpath in extracted_zip_map:
                return extracted_zip_map[zpath]
            img_counter += 1
            dest_rel = os.path.join(illus_dir, f"img_{img_counter:02d}.webp")
            rel_posix, w, h = save_optimized_webp(z.read(zpath), dest_rel, max_dim=max_dim, quality=84)
            entry = {
                'src': rel_posix,
                'width': w,
                'height': h,
                'category': cat,
                'caption': f"{label} — {vol_title} (Arte: Mitz Vah)",
            }
            all_illustrations.append(entry)
            blk = {
                'type': 'img',
                'src': rel_posix,
                'width': w,
                'height': h,
                'category': cat,
                'alt': entry['caption'],
                'caption': label,
            }
            extracted_zip_map[zpath] = blk
            return blk

        opening_images = [
            register_zip_img("images/image.png", "cover", "Capa Oficial"),
            register_zip_img("images/image.jpeg", "insert", "Ilustração Colorida de Abertura (#1)", max_dim=1350),
            register_zip_img("images/image-1.png", "insert", "Ilustração Colorida Dupla (#2 — Guy vs. Velzard)", max_dim=1350),
        ]

        opf = [n for n in z.namelist() if n.endswith('.opf')][0]
        root = ET.fromstring(z.read(opf).decode('utf-8', errors='ignore'))
        manifest = {it.attrib['id']: it.attrib['href'] for it in root.findall('.//{http://www.idpf.org/2007/opf}item')}
        spine = [manifest[ir.attrib['idref']] for ir in root.findall('.//{http://www.idpf.org/2007/opf}itemref')]

        raw_chapters = []
        cur_ch = None
        all_en_texts = []

        for sf in spine:
            if sf in ("titlepage.xhtml", "index_split_000.html", "index_split_001.html", "index_split_002.html"):
                continue

            if sf in chapter_split_map:
                if cur_ch and cur_ch['raw_blocks']:
                    raw_chapters.append(cur_ch)
                cur_ch = {'title': chapter_split_map[sf], 'raw_blocks': []}

            if cur_ch is None:
                continue

            bs = BeautifulSoup(z.read(sf).decode('utf-8', errors='ignore'), 'html.parser')
            body = bs.body or bs

            for node in body.find_all(['h1', 'h2', 'h3', 'p', 'img', 'image']):
                # Evitar processar <img> duas vezes se estiver dentro de <p>
                if node.name in ('img', 'image') and node.find_parent(['p', 'h1', 'h2', 'h3']):
                    continue

                if node.name in ('img', 'image'):
                    src = (node.get('src') or node.get('xlink:href') or '').lstrip('./')
                    if src and src not in splash_cards:
                        is_sketch = src in ("images/image-16.png", "images/image-17.png")
                        cat = "chart" if is_sketch else "inline"
                        lbl = "Design Oficial de Personagens (Mitz Vah)" if is_sketch else f"Ilustração Oficial {len(all_illustrations) + 1}"
                        cur_ch['raw_blocks'].append(register_zip_img(src, cat, lbl))
                    continue

                for im in node.find_all(['img', 'image']):
                    src = (im.get('src') or im.get('xlink:href') or '').lstrip('./')
                    if src and src not in splash_cards:
                        is_sketch = src in ("images/image-16.png", "images/image-17.png")
                        cat = "chart" if is_sketch else "inline"
                        lbl = "Design Oficial de Personagens (Mitz Vah)" if is_sketch else f"Ilustração Oficial {len(all_illustrations) + 1}"
                        cur_ch['raw_blocks'].append(register_zip_img(src, cat, lbl))
                    im.decompose()

                if node.name in ('h1', 'h2', 'h3'):
                    # Já estruturamos os títulos oficiais pelo chapter_split_map
                    continue

                txt = re.sub(r'\s+', ' ', node.get_text(" ", strip=True)).strip()
                if not txt:
                    continue
                if SCENE_BREAK_TEXT_RE.match(txt):
                    if cur_ch['raw_blocks'] and cur_ch['raw_blocks'][-1].get('type') != 'hr':
                        cur_ch['raw_blocks'].append({'type': 'hr', 'variant': 'soft'})
                    continue

                p_ref_idx = len(all_en_texts)
                all_en_texts.append(txt)
                cur_ch['raw_blocks'].append({'type': 'p_ref', 'ref': p_ref_idx})

        if cur_ch and cur_ch['raw_blocks']:
            raw_chapters.append(cur_ch)

    ptbr_texts = translate_volume_paragraphs(vol_id, all_en_texts)

    final_chapters = [{
        'title': 'Capa & Ilustrações Coloridas',
        'blocks': opening_images,
        'paragraphs': [f"[Galeria de Abertura com {len(opening_images)} ilustrações oficiais de Mitz Vah]"],
    }]

    for rch in raw_chapters:
        ch_blocks = []
        for blk in rch['raw_blocks']:
            if blk['type'] == 'p_ref':
                t_pt = ptbr_texts[blk['ref']]
                if t_pt:
                    ch_blocks.append({'type': 'p', 'text': t_pt})
            else:
                ch_blocks.append(blk)
        p_list = [x['text'] for x in ch_blocks if x['type'] == 'p']
        final_chapters.append({
            'title': rch['title'],
            'blocks': ch_blocks,
            'paragraphs': p_list,
        })

    out_data = {
        'id': vol_id,
        'base_volume_id': vol_id,
        'volume_number': 22,
        'title': vol_title,
        'edition': 'Edição Ilustrada Completa — Revisada PT-BR',
        'is_colored_edition': False,
        'has_scan_alternative': False,
        'scan_alternative_id': None,
        'source': 'Edição Ilustrada Compilada & Revisada em PT-BR',
        'cover_image': all_illustrations[0]['src'],
        'illustrations_count': len(all_illustrations),
        'illustrations': all_illustrations,
        'footnotes': {},
        'chapter_count': len(final_chapters),
        'chapters': final_chapters,
    }

    out_path = os.path.join(LN_DATA_DIR, f"{vol_id}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Salvo {out_path}: {len(final_chapters)} seções, {sum(len(c['paragraphs']) for c in final_chapters)} parágrafos, {len(all_illustrations)} ilustrações WebP.")


# ==============================================================================
# 3. VOLUME 23 — VOLUME FINAL DA OBRA (14 Ilustrações HD + 9 Capítulos/Posfácio)
# ==============================================================================
def build_volume_23():
    vol_id = "vol-23"
    vol_title = "Volume 23: Mito da Criação & Pós-Reencarnação (Final)"
    illus_dir = os.path.join(ILLUS_ROOT, vol_id)
    os.makedirs(illus_dir, exist_ok=True)

    all_illustrations = []
    img_counter = 0
    extracted_zip_map = {}

    heading_pt_map = {
        "Prologue: An Uneasy Feeling": "Prólogo: Um Pressentimento Inquietante",
        "Chapter 1: Flowing Tears": "Capítulo 1: Lágrimas que Fluem",
        "Chapter 2: Hope and Despair": "Capítulo 2: Esperança e Desespero",
        "Interlude: Second Coming": "Interlúdio: A Segunda Vinda",
        "Chapter 3: The Evil God’s Great War": "Capítulo 3: A Grande Guerra do Deus Maligno",
        "Chapter 3: The Evil God's Great War": "Capítulo 3: A Grande Guerra do Deus Maligno",
        "Chapter 4: The Dragon of Ruin": "Capítulo 4: O Dragão da Ruína",
        "Chapter 5: Creation Myth": "Capítulo 5: Mito da Criação",
        "Epilogue: After Reincarnation": "Epílogo: Após a Reencarnação",
        "Afterword": "Posfácio do Autor (Fuse)",
    }

    with zipfile.ZipFile(V23_EPUB, 'r') as z:
        def register_v23_img(rel_src: str, cat: str, label: str, max_dim: int = 1280):
            nonlocal img_counter
            zpath = f"GoogleDoc/{rel_src.lstrip('./')}"
            if zpath in extracted_zip_map:
                return extracted_zip_map[zpath]
            img_counter += 1
            dest_rel = os.path.join(illus_dir, f"img_{img_counter:02d}.webp")
            rel_posix, w, h = save_optimized_webp(z.read(zpath), dest_rel, max_dim=max_dim, quality=84)
            entry = {
                'src': rel_posix,
                'width': w,
                'height': h,
                'category': cat,
                'caption': f"{label} — {vol_title} (Arte: Mitz Vah)",
            }
            all_illustrations.append(entry)
            blk = {
                'type': 'img',
                'src': rel_posix,
                'width': w,
                'height': h,
                'category': cat,
                'alt': entry['caption'],
                'caption': label,
            }
            extracted_zip_map[zpath] = blk
            return blk

        opening_images = [
            register_v23_img("images/image5.jpg", "cover", "Capa Oficial do Volume Final"),
            register_v23_img("images/image9.jpg", "insert", "Ilustração Colorida Dupla (#1 — Batalha Final)", max_dim=1400),
            register_v23_img("images/image10.jpg", "insert", "Ilustração Colorida Dupla (#2 — A Espada de Rimuru)", max_dim=1400),
        ]

        bs = BeautifulSoup(z.read("GoogleDoc/ThatTimeIGotReincarnatedasaSlimeVol.23.xhtml").decode('utf-8', errors='ignore'), 'html.parser')
        blocks = (bs.body or bs).find_all(['h1', 'h2', 'h3', 'p'])

        raw_chapters = []
        cur_ch = None
        all_en_texts = []

        for idx, b in enumerate(blocks):
            # Pular bloco inicial de capa/sumário antes do <h1> Prologue (idx < 23)
            if idx < 23:
                continue

            if b.name in ('h1', 'h2', 'h3'):
                htxt = re.sub(r'\s+', ' ', b.get_text(" ", strip=True)).strip()
                pt_title = heading_pt_map.get(htxt, htxt)
                if cur_ch and cur_ch['raw_blocks']:
                    raw_chapters.append(cur_ch)
                cur_ch = {'title': pt_title, 'raw_blocks': []}
                continue

            if cur_ch is None:
                continue

            for im in b.find_all('img'):
                src = im.get('src', '')
                if src:
                    # Se for image9.jpg ou image10.jpg repetida inline, reutilizar bloco sem duplicar na galeria
                    lbl = f"Ilustração Oficial {len(all_illustrations) + 1}"
                    ib = register_v23_img(src, "inline", lbl)
                    cur_ch['raw_blocks'].append(ib)
                im.decompose()

            txt = re.sub(r'\s+', ' ', b.get_text(" ", strip=True)).strip()
            if not txt:
                continue
            if SCENE_BREAK_TEXT_RE.match(txt):
                if cur_ch['raw_blocks'] and cur_ch['raw_blocks'][-1].get('type') != 'hr':
                    cur_ch['raw_blocks'].append({'type': 'hr', 'variant': 'soft'})
                continue

            p_ref_idx = len(all_en_texts)
            all_en_texts.append(txt)
            cur_ch['raw_blocks'].append({'type': 'p_ref', 'ref': p_ref_idx})

        if cur_ch and cur_ch['raw_blocks']:
            raw_chapters.append(cur_ch)

    ptbr_texts = translate_volume_paragraphs(vol_id, all_en_texts)

    final_chapters = [{
        'title': 'Capa & Ilustrações Coloridas',
        'blocks': opening_images,
        'paragraphs': [f"[Galeria de Abertura com {len(opening_images)} ilustrações oficiais de Mitz Vah]"],
    }]

    for rch in raw_chapters:
        ch_blocks = []
        for blk in rch['raw_blocks']:
            if blk['type'] == 'p_ref':
                t_pt = ptbr_texts[blk['ref']]
                if t_pt:
                    ch_blocks.append({'type': 'p', 'text': t_pt})
            else:
                ch_blocks.append(blk)
        p_list = [x['text'] for x in ch_blocks if x['type'] == 'p']
        final_chapters.append({
            'title': rch['title'],
            'blocks': ch_blocks,
            'paragraphs': p_list,
        })

    out_data = {
        'id': vol_id,
        'base_volume_id': vol_id,
        'volume_number': 23,
        'title': vol_title,
        'edition': 'Edição Ilustrada Completa — Revisada PT-BR',
        'is_colored_edition': False,
        'has_scan_alternative': False,
        'scan_alternative_id': None,
        'source': 'Edição Ilustrada Compilada & Revisada em PT-BR',
        'cover_image': all_illustrations[0]['src'],
        'illustrations_count': len(all_illustrations),
        'illustrations': all_illustrations,
        'footnotes': {},
        'chapter_count': len(final_chapters),
        'chapters': final_chapters,
    }

    out_path = os.path.join(LN_DATA_DIR, f"{vol_id}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Salvo {out_path}: {len(final_chapters)} seções, {sum(len(c['paragraphs']) for c in final_chapters)} parágrafos, {len(all_illustrations)} ilustrações WebP.")


if __name__ == '__main__':
    t0 = time.time()
    build_volume_21()
    build_volume_22()
    build_volume_23()
    print(f"\nConcluído em {time.time() - t0:.1f}s!")
