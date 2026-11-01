"""
Processador e Harmonizador de Parágrafos da Web Novel — Tensei Shitara Slime Datta Ken
1. Remove blocos gigantes duplicados decorrentes de containers HTML não fechados do WordPress/Central Novel (ex: Cap. 173, Cap. 3, Cap. 4, etc.).
2. Normaliza divisores de cena (* * *) evitando duplicidades e posições orfãs.
3. Divide parágrafos extensos remanescentes (>650 caracteres) em sentenças naturais e equilibradas (200-450 caracteres).
4. Corrige espaçamentos defeituosos em acentuações (kerning quebrado como "Drag ã o", "n ã o", "voc ê", etc.).
5. Atualiza o contador 'paragraph_count' em cada capitulo_XXX.json e sincroniza o data/catalog.json.
"""

import os
import re
import json
import glob

WN_DIR = "data/web_novel"
CATALOG_PATH = "data/catalog.json"

# Correções seguras de kerning quebrado em palavras acentuadas
KERNING_PATTERNS = [
    (re.compile(r'\bDrag\s+ã\s*o\b'), 'Dragão'),
    (re.compile(r'\bdrag\s+ã\s*o\b'), 'dragão'),
    (re.compile(r'\bDrag\s+õ\s*es\b'), 'Dragões'),
    (re.compile(r'\bdrag\s+õ\s*es\b'), 'dragões'),
    (re.compile(r'\bN\s+ã\s*o\b'), 'Não'),
    (re.compile(r'\bn\s+ã\s*o\b'), 'não'),
    (re.compile(r'\bEnt\s+ã\s*o\b'), 'Então'),
    (re.compile(r'\bent\s+ã\s*o\b'), 'então'),
    (re.compile(r'\bT\s+ã\s*o\b'), 'Tão'),
    (re.compile(r'\bt\s+ã\s*o\b'), 'tão'),
    (re.compile(r'\bVoc\s+ê\b'), 'Você'),
    (re.compile(r'\bvoc\s+ê\b'), 'você'),
    (re.compile(r'\bVoc\s+ê\s*s\b'), 'Vocês'),
    (re.compile(r'\bvoc\s+ê\s*s\b'), 'vocês'),
    (re.compile(r'\bM\s+á\s*gica\b'), 'Mágica'),
    (re.compile(r'\bm\s+á\s*gica\b'), 'mágica'),
    (re.compile(r'\bM\s+á\s*gico\b'), 'Mágico'),
    (re.compile(r'\bm\s+á\s*gico\b'), 'mágico'),
    (re.compile(r'\bM\s+á\s*gicos\b'), 'Mágicos'),
    (re.compile(r'\bm\s+á\s*gicos\b'), 'mágicos'),
    (re.compile(r'\bM\s+á\s*gicas\b'), 'Mágicas'),
    (re.compile(r'\bm\s+á\s*gicas\b'), 'mágicas'),
    (re.compile(r'\bAlgu\s+é\s*m\b'), 'Alguém'),
    (re.compile(r'\balgu\s+é\s*m\b'), 'alguém'),
    (re.compile(r'\bNingu\s+é\s*m\b'), 'Ninguém'),
    (re.compile(r'\bningu\s+é\s*m\b'), 'ninguém'),
    (re.compile(r'\bTamb\s+é\s*m\b'), 'Também'),
    (re.compile(r'\btamb\s+é\s*m\b'), 'também'),
    (re.compile(r'\bAt\s+é\b'), 'Até'),
    (re.compile(r'\bat\s+é\b'), 'até'),
    (re.compile(r'\bEst\s+á\b'), 'Está'),
    (re.compile(r'\best\s+á\b'), 'está'),
    (re.compile(r'\bEst\s+ã\s*o\b'), 'Estão'),
    (re.compile(r'\best\s+ã\s*o\b'), 'estão'),
    (re.compile(r'\bSer\s+á\b'), 'Será'),
    (re.compile(r'\bser\s+á\b'), 'será'),
    (re.compile(r'\bSer\s+ã\s*o\b'), 'Serão'),
    (re.compile(r'\bser\s+ã\s*o\b'), 'serão'),
    (re.compile(r'\bPris\s+ã\s*o\b'), 'Prisão'),
    (re.compile(r'\bpris\s+ã\s*o\b'), 'prisão'),
    (re.compile(r'\bProte\s+ç\s*ã\s*o\b'), 'Proteção'),
    (re.compile(r'\bprote\s+ç\s*ã\s*o\b'), 'proteção'),
    (re.compile(r'\bDur\s+á\s*vel\b'), 'Durável'),
    (re.compile(r'\bdur\s+á\s*vel\b'), 'durável'),
    (re.compile(r'\bÚ\s+nico\b'), 'Único'),
    (re.compile(r'\bú\s+nico\b'), 'único'),
    (re.compile(r'\bÚ\s+nica\b'), 'Única'),
    (re.compile(r'\bú\s+nica\b'), 'única'),
    (re.compile(r'\bÚ\s+nicos\b'), 'Únicos'),
    (re.compile(r'\bú\s+nicos\b'), 'únicos'),
    (re.compile(r'\bÚ\s+nicas\b'), 'Únicas'),
    (re.compile(r'\bú\s+nicas\b'), 'únicas'),
    (re.compile(r'\bS\s+á\s*bio\b'), 'Sábio'),
    (re.compile(r'\bs\s+á\s*bio\b'), 'sábio'),
    (re.compile(r'\bReligi\s+õ\s*es\b'), 'Religiões'),
    (re.compile(r'\breligi\s+õ\s*es\b'), 'religiões'),
]

SENTENCE_SPLIT_RE = re.compile(r'([.!?……]+[\)\]”"』」]*\s+)(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ\(\[“"『「0-9])')

def fix_kerning(text: str) -> str:
    for pat, rep in KERNING_PATTERNS:
        text = pat.sub(rep, text)
    return text

def split_long_paragraph(p: str, target_len: int = 400, max_len: int = 650) -> list[str]:
    p = p.strip()
    if len(p) <= max_len:
        return [p]
        
    # Preservar fichas de atributos/habilidades técnicas completas
    if p.startswith('Habilidade') or ('[' in p and ']' in p and '|' in p) or ('》 Características 《' in p):
        return [p]
        
    parts = []
    last_end = 0
    for m in SENTENCE_SPLIT_RE.finditer(p):
        end = m.end()
        parts.append(p[last_end:end].strip())
        last_end = end
    if last_end < len(p):
        parts.append(p[last_end:].strip())
        
    if not parts or len(parts) == 1:
        return [p]
        
    chunks = []
    current_chunk = []
    current_len = 0
    
    for s in parts:
        if current_len + len(s) > target_len and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [s]
            current_len = len(s)
        else:
            current_chunk.append(s)
            current_len += len(s) + 1
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def process_chapter_paragraphs(paragraphs: list[str]) -> tuple[list[str], int, int]:
    n = len(paragraphs)
    to_remove = set()
    
    # 1. Identificar blocos gigantes duplicados (concatenados por containers do tema)
    for i in range(n):
        p = paragraphs[i].strip()
        if len(p) < 350:
            continue
            
        # Busca direta por repetição para a frente
        k = i + 1
        while k < n and paragraphs[k].strip() in ('* * *', '***', '---'):
            k += 1
            
        matched_fwd = 0
        matched_fwd_len = 0
        consecutive_misses = 0
        
        for j in range(k, min(n, k + 100)):
            sub = paragraphs[j].strip()
            if sub in ('* * *', '***', '---'):
                continue
            if len(sub) < 15:
                continue
            core = sub[:min(40, len(sub))]
            if core in p or (len(sub) > 40 and sub[10:40] in p):
                matched_fwd += 1
                matched_fwd_len += len(sub)
                consecutive_misses = 0
            else:
                consecutive_misses += 1
                if consecutive_misses >= 3:
                    break
                    
        if matched_fwd >= 3 and matched_fwd_len >= 400:
            to_remove.add(i)
            continue
            
        # Busca direta por repetição para trás
        k = i - 1
        while k >= 0 and paragraphs[k].strip() in ('* * *', '***', '---'):
            k -= 1
        matched_bwd = 0
        matched_bwd_len = 0
        consecutive_misses = 0
        for j in range(k, max(-1, k - 100), -1):
            sub = paragraphs[j].strip()
            if sub in ('* * *', '***', '---'):
                continue
            if len(sub) < 15:
                continue
            core = sub[:min(40, len(sub))]
            if core in p or (len(sub) > 40 and sub[10:40] in p):
                matched_bwd += 1
                matched_bwd_len += len(sub)
                consecutive_misses = 0
            else:
                consecutive_misses += 1
                if consecutive_misses >= 3:
                    break
        if matched_bwd >= 3 and matched_bwd_len >= 400:
            to_remove.add(i)

    # 2. Filtrar blocos duplicados e normalizar quebras de cena
    deduped = [p for idx, p in enumerate(paragraphs) if idx not in to_remove]
    
    clean_breaks = []
    for p in deduped:
        p_str = p.strip()
        is_break = p_str in ('* * *', '***', '---')
        if is_break:
            if not clean_breaks:
                continue
            if clean_breaks[-1].strip() in ('* * *', '***', '---'):
                continue
            clean_breaks.append('* * *')
        else:
            clean_breaks.append(p)
            
    while clean_breaks and clean_breaks[-1].strip() in ('* * *', '***', '---'):
        clean_breaks.pop()

    # 3. Dividir parágrafos excessivamente longos e aplicar correção de kerning
    split_count = 0
    final_paras = []
    for p in clean_breaks:
        p_fixed = fix_kerning(p)
        if len(p_fixed) > 650:
            chunks = split_long_paragraph(p_fixed)
            if len(chunks) > 1:
                split_count += 1
            final_paras.extend(chunks)
        else:
            final_paras.append(p_fixed)

    return final_paras, len(to_remove), split_count

def main():
    chapter_files = sorted(glob.glob(os.path.join(WN_DIR, "*.json")))
    print(f"Iniciando harmonização de {len(chapter_files)} capítulos da Web Novel...")
    
    total_dups_removed = 0
    total_splits = 0
    modified_files = 0
    
    catalog_updated_counts = {}

    for fpath in chapter_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        old_paras = data.get('paragraphs', [])
        new_paras, dups_removed, splits = process_chapter_paragraphs(old_paras)
        
        if dups_removed > 0 or splits > 0 or len(new_paras) != len(old_paras) or new_paras != old_paras:
            data['paragraphs'] = new_paras
            data['paragraph_count'] = len(new_paras)
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            total_dups_removed += dups_removed
            total_splits += splits
            modified_files += 1
            catalog_updated_counts[data['id']] = len(new_paras)

    print(f"\nResumo da Harmonização:")
    print(f"  - Capítulos atualizados: {modified_files} de {len(chapter_files)}")
    print(f"  - Blocos duplicados concatenados eliminados: {total_dups_removed}")
    print(f"  - Parágrafos longos subdivididos: {total_splits}")

    # Atualizar data/catalog.json se aplicável
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            cat = json.load(f)
            
        wn_chapters = cat.get('web_novel', {}).get('chapters', [])
        cat_mod = False
        for ch in wn_chapters:
            cid = ch.get('id')
            if cid in catalog_updated_counts:
                if ch.get('paragraph_count') != catalog_updated_counts[cid]:
                    ch['paragraph_count'] = catalog_updated_counts[cid]
                    cat_mod = True
                    
        if cat_mod:
            with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
                json.dump(cat, f, ensure_ascii=False, indent=2)
            print("  - data/catalog.json atualizado com as novas contagens de parágrafos.")

if __name__ == '__main__':
    main()
