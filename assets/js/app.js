/**
 * TENSEI SHITARA SLIME DATTA KEN — BIBLIOTECA & LEITOR COMPLETO EM PORTUGUÊS
 * Motor de Leitura Separado (LN vs WN), Ilustrações Inline + Lightbox,
 * Notas Culturais Interativas, Alternância de Edição (Edição Ilustrada Revisada vs TSSDK Scan),
 * Salvamento Automático Exato na Página e Retomada Automática ao Reabrir o Navegador.
 */

const STORAGE_KEYS = {
  SETTINGS: 'tensura_reader_settings_v2',
  SPOILER_ONBOARDED: 'tensura_spoiler_onboarded_v1',
  PROGRESS_LAST: 'tensura_progress_last',
  PROGRESS_LN: 'tensura_progress_ln',
  PROGRESS_WN: 'tensura_progress_wn',
  HISTORY: 'tensura_reading_history',
  BOOKMARKS: 'tensura_bookmarks_v2',
  COLOR_SCHEME: 'color-scheme',
  PALETTE: 'tensura_palette'
};

// Referência oficial: o Anime adapta até o Volume 11 da Light Novel
const ANIME_ADAPTED_MAX_LN_VOL = 11;
const POST_ANIME_WN_ARCS = new Set(['arc-8', 'arc-9', 'arc-10', 'arc-extra-1', 'arc-extra-2', 'arc-extra-3']);
const POST_ANIME_CULTURAL_CONCEPT_IDXS = new Set([3, 4, 6]);
const APP_BUILD_VERSION = '20261101_v20';

const AppState = {
  catalog: null,
  currentTab: 'light-novel',
  searchQuery: '',
  isRestoringScroll: false,
  restoreTimer: null,
  revealedSpoilers: new Set(),
  manuallyHiddenSpoilers: new Set(),
  currentReading: {
    type: null,          // 'light_novel' | 'web_novel'
    id: null,            // ex: 'vol-6', 'vol-6-scan', 'cap-018-5', 'extra-001'
    baseVolumeId: null,  // ex: 'vol-6'
    chapterIndex: 0,
    data: null,
    scrollRatio: 0,
    pIndex: null,
    pOffsetPx: null,
    useRatioOnly: false
  },
  settings: {
    palette: 'sepia',         // 'sepia' (padrão) | 'mint' | 'parchment' | 'sakura' | 'light' | 'coffee' | 'midnight' | 'dark' | 'oled' | 'system'
    font: 'serif',            // 'serif' | 'lora' | 'merriweather' | 'crimson' | 'sans' | 'accessible' | 'dyslexic' | 'mono'
    fontSize: 19,
    maxWidth: 820,
    culturalHints: true,
    autoResumeOnOpen: true,
    spoilerMode: 'post_anime' // 'post_anime' (Vol. 12+) | 'all' (Vol. 1+) | 'none'
  },
  history: {},
  bookmarks: [],
  pendingBookmark: null,
  lightbox: {
    items: [],
    index: 0
  }
};

// ==========================================================================
// INICIALIZAÇÃO & FALLBACKS MODERNOS
// ==========================================================================

document.addEventListener('DOMContentLoaded', async () => {
  initDialogLightDismissFallback();
  initScrollProgressFallback();
  initScrollEndFallback();

  loadStateFromStorage();
  applySettingsToDOM();
  bindGlobalEvents();

  try {
    const res = await fetch(`data/catalog.json?v=${APP_BUILD_VERSION}`, { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    AppState.catalog = await res.json();

    renderAllCatalogViews();
    refreshContinueBanners();
    updateBookmarkBadge();
    await handleInitialStartupRoute();
    maybePromptSpoilerOnboarding();
  } catch (err) {
    console.error('Erro ao carregar data/catalog.json:', err);
    const main = document.getElementById('content-area');
    if (main) {
      main.innerHTML = `
        <section class="section-hero">
          <h2>Não foi possível carregar o catálogo local</h2>
          <p>
            Se você abriu o arquivo <code>index.html</code> diretamente via <code>file://</code>, o navegador bloqueia requisições <code>fetch()</code> por segurança.
            Execute o arquivo <strong>Iniciar_Leitor.bat</strong> (ou rode <code>python -m http.server 8080</code> na pasta do projeto e acesse <code>http://localhost:8080</code>).
          </p>
        </section>
      `;
    }
  }
});

/**
 * Fallback obrigatório para <dialog closedby="any"> onde HTMLDialogElement.prototype.closedBy não existe.
 * Exige pointerdown E pointerup fora do retângulo do dialog para não fechar ao arrastar seleção de texto.
 */
function initDialogLightDismissFallback() {
  if (!('closedBy' in HTMLDialogElement.prototype)) {
    const isOutside = (e, dialog) => {
      const r = dialog.getBoundingClientRect();
      return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
    };
    for (const dialog of document.querySelectorAll('dialog[closedby="any"]')) {
      let pressedOutside = false;
      dialog.addEventListener('pointerdown', (e) => {
        pressedOutside = isOutside(e, dialog);
      });
      dialog.addEventListener('pointerup', (e) => {
        if (pressedOutside && isOutside(e, dialog)) {
          dialog.close();
        }
      });
    }
  }

  for (const dialog of document.querySelectorAll('dialog')) {
    dialog.addEventListener('close', () => {
      dialog.returnValue = '';
    });
  }
}

/**
 * Fallback para navegadores sem suporte a CSS Scroll-Driven Animations (animation-timeline: scroll()).
 */
function initScrollProgressFallback() {
  if (!window.CSS || !CSS.supports('animation-timeline', 'scroll()')) {
    const bar = document.getElementById('reading-progress-bar');
    if (!bar) return;
    window.addEventListener('scroll', () => {
      bar.style.transform = `scaleX(${getScrollRatio()})`;
    }, { passive: true });
  }
}

/**
 * Fallback para o evento nativo scrollend em navegadores antigos.
 */
function initScrollEndFallback() {
  if (!('onscrollend' in window)) {
    let timer = null;
    window.addEventListener('scroll', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        window.dispatchEvent(new CustomEvent('scrollend'));
      }, 120);
    }, { passive: true });
  }
}

// ==========================================================================
// ARMAZENAMENTO LOCAL (SETTINGS, PROGRESSO DUPLO LN/WN, HISTÓRICO & MARCADORES)
// ==========================================================================

function loadStateFromStorage() {
  try {
    const rawSettings = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    if (rawSettings) {
      AppState.settings = { ...AppState.settings, ...JSON.parse(rawSettings) };
    } else {
      const savedPalette = localStorage.getItem(STORAGE_KEYS.PALETTE);
      if (savedPalette) {
        AppState.settings.palette = savedPalette;
      }
      const savedFont = localStorage.getItem('tensura_font');
      if (savedFont) {
        AppState.settings.font = savedFont;
      }
    }
    if (!AppState.settings.palette) {
      AppState.settings.palette = 'sepia';
    }
    const rawHist = localStorage.getItem(STORAGE_KEYS.HISTORY);
    if (rawHist) {
      AppState.history = JSON.parse(rawHist) || {};
    }
    const rawBm = localStorage.getItem(STORAGE_KEYS.BOOKMARKS);
    if (rawBm) {
      AppState.bookmarks = JSON.parse(rawBm) || [];
    } else {
      // Migrar marcadores da v1 caso existam
      const legacyBm = localStorage.getItem('tensura_bookmarks');
      if (legacyBm) AppState.bookmarks = JSON.parse(legacyBm) || [];
    }
  } catch (e) {
    console.warn('Aviso ao ler LocalStorage:', e);
  }
}

function saveSettingsToStorage() {
  try {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(AppState.settings));
  } catch (e) {
    console.warn('Aviso ao salvar configurações:', e);
  }
}

function applySettingsToDOM() {
  const root = document.documentElement;
  const metaScheme = document.querySelector('meta[name="color-scheme"]');
  const p = AppState.settings.palette || 'sepia';

  // Mapear paleta escolhida para <meta name="color-scheme"> + data-palette
  let schemeContent = 'light';
  let customPalette = p;
  if (p === 'dark') {
    schemeContent = 'dark';
    customPalette = '';
  } else if (p === 'light') {
    schemeContent = 'light';
    customPalette = '';
  } else if (p === 'oled' || p === 'midnight' || p === 'coffee') {
    schemeContent = 'dark';
    customPalette = p;
  } else if (p === 'sepia' || p === 'mint' || p === 'parchment' || p === 'sakura') {
    schemeContent = 'light';
    customPalette = p;
  } else if (p === 'system') {
    schemeContent = 'light dark';
    customPalette = '';
  }

  if (metaScheme) metaScheme.content = schemeContent;
  if (customPalette) {
    root.dataset.palette = customPalette;
  } else {
    delete root.dataset.palette;
  }

  try {
    if (p === 'system') {
      localStorage.removeItem(STORAGE_KEYS.COLOR_SCHEME);
      localStorage.removeItem(STORAGE_KEYS.PALETTE);
    } else {
      localStorage.setItem(STORAGE_KEYS.COLOR_SCHEME, schemeContent);
      localStorage.setItem(STORAGE_KEYS.PALETTE, p);
    }
    if (AppState.settings.font) {
      localStorage.setItem('tensura_font', AppState.settings.font);
    }
  } catch (_) {}

  root.dataset.font = AppState.settings.font || 'serif';
  root.style.setProperty('--reader-size', `${AppState.settings.fontSize || 19}px`);
  root.style.setProperty('--reader-max-width', `${AppState.settings.maxWidth || 820}px`);

  // Sincronizar botões do painel de configurações
  document.querySelectorAll('.btn-theme-opt').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.palette === AppState.settings.palette);
  });
  document.querySelectorAll('.btn-font-opt').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.font === AppState.settings.font);
  });
  document.querySelectorAll('.btn-width-opt').forEach(btn => {
    btn.classList.toggle('active', Number(btn.dataset.width) === Number(AppState.settings.maxWidth));
  });

  const sizeEl = document.getElementById('font-size-val');
  if (sizeEl) sizeEl.textContent = `${AppState.settings.fontSize}px`;

  const chkHints = document.getElementById('chk-cultural-hints');
  if (chkHints) chkHints.checked = Boolean(AppState.settings.culturalHints);

  const chkAutoResume = document.getElementById('chk-auto-resume');
  if (chkAutoResume) chkAutoResume.checked = AppState.settings.autoResumeOnOpen !== false;

  const spoilerMode = AppState.settings.spoilerMode || 'post_anime';
  document.querySelectorAll('.btn-spoiler-opt').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.spoiler === spoilerMode);
  });
  document.querySelectorAll('.onboarding-choice-card').forEach(card => {
    card.classList.toggle('is-selected', card.dataset.chooseSpoiler === spoilerMode);
  });

  const spoilerBtn = document.getElementById('btn-open-spoiler-modal');
  const spoilerIcon = document.getElementById('spoiler-pill-icon');
  const spoilerText = document.getElementById('spoiler-pill-text');
  if (spoilerBtn && spoilerIcon && spoilerText) {
    if (spoilerMode === 'post_anime') {
      spoilerIcon.textContent = '🛡️';
      spoilerText.textContent = 'Sem Spoilers: Vol. 12+';
      spoilerBtn.classList.remove('is-unfiltered');
    } else if (spoilerMode === 'all') {
      spoilerIcon.textContent = '🙈';
      spoilerText.textContent = 'Sem Sinopses';
      spoilerBtn.classList.remove('is-unfiltered');
    } else {
      spoilerIcon.textContent = '👁️';
      spoilerText.textContent = 'Spoilers Visíveis';
      spoilerBtn.classList.add('is-unfiltered');
    }
  }
}

function setSpoilerMode(mode) {
  if (!['post_anime', 'all', 'none'].includes(mode)) return;
  AppState.settings.spoilerMode = mode;
  AppState.revealedSpoilers.clear();
  AppState.manuallyHiddenSpoilers.clear();
  try {
    localStorage.setItem(STORAGE_KEYS.SPOILER_ONBOARDED, '1');
  } catch (_) {}
  saveSettingsToStorage();
  applySettingsToDOM();
  renderAllCatalogViews();
}

function maybePromptSpoilerOnboarding() {
  if (AppState.currentReading.type) return;
  try {
    if (localStorage.getItem(STORAGE_KEYS.SPOILER_ONBOARDED)) return;
  } catch (_) {
    return;
  }
  const dialog = document.getElementById('spoiler-dialog');
  if (dialog && !dialog.open) {
    dialog.showModal();
  }
}

function isLnVolumeNormallyProtected(volNum) {
  const mode = AppState.settings.spoilerMode || 'post_anime';
  if (mode === 'none') return false;
  if (mode === 'all') return true;
  return Number(volNum) > ANIME_ADAPTED_MAX_LN_VOL;
}

function getLnVolumeProgressPct(volId) {
  if (!volId || !AppState.history) return 0;
  const baseKey = `ln:${volId.replace('-scan', '')}`;
  const hist = AppState.history[baseKey];
  return (hist && typeof hist.pct === 'number') ? hist.pct : 0;
}

function isLnVolumeProgressUnlocked(volNum, volId) {
  // Desbloqueia sinopse se o leitor já leu pelo menos 75% deste volume ou o concluiu
  const pct = getLnVolumeProgressPct(volId);
  if (pct >= 75) return true;

  // Se o leitor já começou a ler qualquer volume posterior na Light Novel
  const targetNum = Number(volNum);
  if (!isNaN(targetNum) && AppState.catalog?.light_novel?.volumes) {
    for (const v of AppState.catalog.light_novel.volumes) {
      const vNum = Number(v.volume_number);
      if (!isNaN(vNum) && vNum > targetNum) {
        const vPct = getLnVolumeProgressPct(v.id);
        if (vPct >= 10) return true;
      }
    }
  }
  return false;
}

function isLnVolumeSpoilerHidden(volNum, spoilerKey, volId) {
  if (!isLnVolumeNormallyProtected(volNum)) return false;
  if (AppState.manuallyHiddenSpoilers && AppState.manuallyHiddenSpoilers.has(spoilerKey)) return true;
  if (AppState.revealedSpoilers.has(spoilerKey)) return false;
  if (volId && isLnVolumeProgressUnlocked(volNum, volId)) return false;
  return true;
}

function isWnArcNormallyProtected(arcId) {
  const mode = AppState.settings.spoilerMode || 'post_anime';
  if (mode === 'none') return false;
  if (mode === 'all') return true;
  return POST_ANIME_WN_ARCS.has(arcId);
}

function isWnArcProgressUnlocked(arcId) {
  if (!AppState.catalog?.web_novel?.arcs) return false;
  const arc = AppState.catalog.web_novel.arcs.find(a => a.id === arcId);
  if (!arc || !Array.isArray(arc.chapters) || arc.chapters.length === 0) return false;

  let readCount = 0;
  for (const ch of arc.chapters) {
    const hist = AppState.history[`wn:${ch.id}`];
    if (hist && typeof hist.pct === 'number' && hist.pct >= 50) {
      readCount++;
    }
  }
  if ((readCount / arc.chapters.length) >= 0.75) return true;

  // Se o usuário já avançou para qualquer arco posterior
  const arcs = AppState.catalog.web_novel.arcs;
  const arcIdx = arcs.findIndex(a => a.id === arcId);
  if (arcIdx >= 0) {
    for (let i = arcIdx + 1; i < arcs.length; i++) {
      const nextArc = arcs[i];
      if (Array.isArray(nextArc.chapters) && nextArc.chapters.length > 0) {
        const firstCh = nextArc.chapters[0];
        const h = AppState.history[`wn:${firstCh.id}`];
        if (h && typeof h.pct === 'number' && h.pct >= 10) return true;
      }
    }
  }
  return false;
}

function isWnArcSpoilerHidden(arcId, spoilerKey) {
  if (!isWnArcNormallyProtected(arcId)) return false;
  if (AppState.manuallyHiddenSpoilers && AppState.manuallyHiddenSpoilers.has(spoilerKey)) return true;
  if (AppState.revealedSpoilers.has(spoilerKey)) return false;
  if (isWnArcProgressUnlocked(arcId)) return false;
  return true;
}

function isComparisonDiffNormallyProtected(diffIdx) {
  const mode = AppState.settings.spoilerMode || 'post_anime';
  if (mode === 'none') return false;
  if (mode === 'all') return true;
  return diffIdx >= 6;
}

function isComparisonDiffSpoilerHidden(diffIdx, spoilerKey) {
  if (!isComparisonDiffNormallyProtected(diffIdx)) return false;
  return !AppState.revealedSpoilers.has(spoilerKey);
}

function isCulturalConceptNormallyProtected(conceptIdx) {
  const mode = AppState.settings.spoilerMode || 'post_anime';
  if (mode === 'none') return false;
  if (mode === 'all') return true;
  return POST_ANIME_CULTURAL_CONCEPT_IDXS.has(conceptIdx);
}

function isCulturalConceptSpoilerHidden(conceptIdx, spoilerKey) {
  if (!isCulturalConceptNormallyProtected(conceptIdx)) return false;
  return !AppState.revealedSpoilers.has(spoilerKey);
}

function getScrollRatio() {
  const h = document.documentElement;
  const maxScroll = h.scrollHeight - h.clientHeight;
  if (maxScroll <= 0) return 0;
  return Math.min(Math.max(window.scrollY / maxScroll, 0), 1);
}

function normalizeScrollAnchor(anchorOrRatio) {
  if (anchorOrRatio && typeof anchorOrRatio === 'object') {
    return {
      scrollRatio: Math.min(Math.max(Number(anchorOrRatio.scrollRatio) || 0, 0), 1),
      pIndex: typeof anchorOrRatio.pIndex === 'number' ? anchorOrRatio.pIndex : null,
      pOffsetPx: typeof anchorOrRatio.pOffsetPx === 'number' ? anchorOrRatio.pOffsetPx : null,
      useRatioOnly: Boolean(anchorOrRatio.useRatioOnly)
    };
  }
  const num = Number(anchorOrRatio);
  return {
    scrollRatio: Number.isFinite(num) ? Math.min(Math.max(num, 0), 1) : 0,
    pIndex: null,
    pOffsetPx: null,
    useRatioOnly: false
  };
}

function getReaderToolbarClearance() {
  const readerView = document.getElementById('reader-view');
  const toolbar = readerView ? readerView.querySelector('.reader-toolbar') : null;
  if (!readerView || readerView.hidden || !toolbar) return 96;
  const rect = toolbar.getBoundingClientRect();
  return Math.max(72, Math.ceil(rect.bottom + 14));
}

function syncReaderToolbarOffset() {
  const readerView = document.getElementById('reader-view');
  const toolbar = readerView ? readerView.querySelector('.reader-toolbar') : null;
  if (!readerView || readerView.hidden || !toolbar) return;
  const bottomPx = Math.max(60, Math.ceil(toolbar.getBoundingClientRect().bottom));
  readerView.style.setProperty('--reader-toolbar-offset', `${bottomPx}px`);
}

function findExactReadingAnchor() {
  const ratio = getScrollRatio();
  if (window.scrollY < 20) {
    return { pIndex: 0, pOffsetPx: null, scrollRatio: 0 };
  }
  const clearance = getReaderToolbarClearance();
  const paras = document.querySelectorAll('#reader-text-container .novel-paragraph');
  for (const p of paras) {
    const rect = p.getBoundingClientRect();
    if (rect.bottom > clearance) {
      return {
        pIndex: Number(p.dataset.pidx || 0),
        pOffsetPx: Math.round(rect.top),
        scrollRatio: ratio
      };
    }
  }
  return { pIndex: 0, pOffsetPx: null, scrollRatio: ratio };
}

function updateAutosavePill(ratio) {
  const pill = document.getElementById('reader-autosave-pill');
  if (!pill) return;
  const pct = Math.round((ratio || 0) * 100);
  pill.textContent = `✓ Salvo auto • ${pct}%`;
}

function persistReadingProgress(options = {}) {
  const opts = typeof options === 'number'
    ? { explicitAnchor: normalizeScrollAnchor(options), force: true }
    : (options || {});

  const cur = AppState.currentReading;
  if (!cur.type || !cur.id || !cur.data) return;
  if (AppState.isRestoringScroll && !opts.force) return;

  const anchor = opts.explicitAnchor ? normalizeScrollAnchor(opts.explicitAnchor) : findExactReadingAnchor();
  const ratio = anchor.scrollRatio;
  const inReader = opts.inReader !== undefined ? Boolean(opts.inReader) : Boolean(cur.type);

  cur.scrollRatio = ratio;
  cur.pIndex = anchor.pIndex;
  cur.pOffsetPx = anchor.pOffsetPx;

  let label = '';
  if (cur.type === 'light_novel') {
    const ch = cur.data.chapters[cur.chapterIndex];
    label = `${cur.data.title} — ${ch ? ch.title : 'Seção'}`;
  } else {
    label = `Web Novel — ${cur.data.display_num || `Cap. ${cur.data.number}`}: ${cur.data.title}`;
  }

  const record = {
    type: cur.type,
    id: cur.id,
    baseVolumeId: cur.baseVolumeId || cur.id,
    chapterIndex: cur.chapterIndex,
    scrollRatio: ratio,
    pIndex: anchor.pIndex,
    pOffsetPx: anchor.pOffsetPx,
    inReader,
    title: label,
    timestamp: Date.now()
  };

  try {
    localStorage.setItem(STORAGE_KEYS.PROGRESS_LAST, JSON.stringify(record));
    if (cur.type === 'light_novel') {
      localStorage.setItem(STORAGE_KEYS.PROGRESS_LN, JSON.stringify(record));
      const baseKey = `ln:${cur.baseVolumeId || cur.id.replace('-scan', '')}`;
      const totalCh = Math.max(cur.data.chapters.length, 1);
      const overallPct = Math.min(100, Math.round(((cur.chapterIndex + ratio) / totalCh) * 100));
      AppState.history[baseKey] = {
        editionId: cur.id,
        chapterIndex: cur.chapterIndex,
        scrollRatio: ratio,
        pIndex: anchor.pIndex,
        pOffsetPx: anchor.pOffsetPx,
        pct: overallPct,
        updatedAt: Date.now()
      };
    } else {
      localStorage.setItem(STORAGE_KEYS.PROGRESS_WN, JSON.stringify(record));
      AppState.history[`wn:${cur.id}`] = {
        scrollRatio: ratio,
        pIndex: anchor.pIndex,
        pOffsetPx: anchor.pOffsetPx,
        pct: Math.round(ratio * 100),
        updatedAt: Date.now()
      };
    }
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(AppState.history));
    updateAutosavePill(ratio);
  } catch (e) {
    console.warn('Erro ao salvar progresso:', e);
  }
}

function getSavedTrackProgress(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (_) {
    return null;
  }
}

function refreshContinueBanners() {
  const last = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LAST);
  const lnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LN);
  const wnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_WN);

  const banner = document.getElementById('continue-banner');
  const titleEl = document.getElementById('continue-title');
  const pctEl = document.getElementById('continue-percent');
  const trackBadge = document.getElementById('continue-track-badge');
  const otherBtn = document.getElementById('btn-resume-other-track');

  if (banner && last && last.title) {
    trackBadge.textContent = last.type === 'light_novel' ? '📘 Light Novel • Salvo Automaticamente' : '📜 Web Novel • Salvo Automaticamente';
    titleEl.textContent = last.title;
    pctEl.textContent = `(${Math.round((last.scrollRatio || 0) * 100)}% da página)`;
    banner.hidden = false;

    const other = last.type === 'light_novel' ? wnSave : lnSave;
    if (other && other.title) {
      otherBtn.hidden = false;
      otherBtn.textContent = other.type === 'light_novel' ? '📘 Ir p/ Light Novel' : '📜 Ir p/ Web Novel';
      otherBtn.dataset.targetTrack = other.type;
    } else {
      otherBtn.hidden = true;
    }
  }

  // Resumos individuais dentro dos Heros separados de LN e WN
  const lnHeroBox = document.getElementById('ln-specific-resume');
  if (lnHeroBox) {
    if (lnSave && lnSave.title) {
      lnHeroBox.hidden = false;
      lnHeroBox.innerHTML = `
        <span>✓ <strong>Onde você parou na Light Novel:</strong> ${escapeHtml(lnSave.title)} (${Math.round((lnSave.scrollRatio || 0) * 100)}%)</span>
        <button type="button" class="btn-continue" data-action="resume-ln">Continuar Light Novel →</button>
      `;
    } else {
      lnHeroBox.hidden = true;
    }
  }

  const wnHeroBox = document.getElementById('wn-specific-resume');
  if (wnHeroBox) {
    if (wnSave && wnSave.title) {
      wnHeroBox.hidden = false;
      wnHeroBox.innerHTML = `
        <span>✓ <strong>Onde você parou na Web Novel:</strong> ${escapeHtml(wnSave.title)} (${Math.round((wnSave.scrollRatio || 0) * 100)}%)</span>
        <button type="button" class="btn-continue" data-action="resume-wn">Continuar Web Novel →</button>
      `;
    } else {
      wnHeroBox.hidden = true;
    }
  }
}

function resumeSavedRecord(record) {
  if (!record) return Promise.resolve();
  const anchor = {
    scrollRatio: record.scrollRatio || 0,
    pIndex: typeof record.pIndex === 'number' ? record.pIndex : null,
    pOffsetPx: typeof record.pOffsetPx === 'number' ? record.pOffsetPx : null
  };
  if (record.type === 'light_novel') {
    return openLightNovel(record.id, record.chapterIndex || 0, anchor);
  }
  if (record.type === 'web_novel') {
    return openWebNovelChapter(record.id, anchor);
  }
  return Promise.resolve();
}

// ==========================================================================
// RENDERIZAÇÃO DO CATÁLOGO (LN, WN, COMPARADOR, CULTURAL, AMAZON)
// ==========================================================================

function renderAllCatalogViews() {
  renderLightNovelCatalog();
  renderWebNovelCatalog();
  renderRecapCatalog();
  renderComparisonCatalog();
  renderCulturalCatalog();
  renderAmazonCatalog();
}

function matchesSearch(text) {
  if (!AppState.searchQuery) return true;
  return String(text || '').toLowerCase().includes(AppState.searchQuery);
}

// 1. Catálogo da Light Novel (24 Volumes Offline + Capas WebP + Barra de Progresso + Filtro Anti-Spoilers)
function renderLightNovelCatalog() {
  const grid = document.getElementById('ln-volumes-grid');
  const futureSection = document.getElementById('ln-future-section');
  const futureGrid = document.getElementById('ln-future-grid');
  const statsEl = document.getElementById('ln-hero-stats');
  if (!grid || !AppState.catalog) return;

  const info = AppState.catalog.light_novel.info;
  if (statsEl && info) {
    statsEl.textContent = `${info.available_volumes_count} Volumes Offline • ${(info.total_illustrations || 0).toLocaleString('pt-BR')} Ilustrações WebP • ${(info.total_footnotes || 0)} Notas Culturais`;
  }

  const volumes = (AppState.catalog.light_novel.volumes || []).filter(v => {
    const spKey = `ln:${v.id}`;
    const hidden = isLnVolumeSpoilerHidden(v.volume_number, spKey, v.id);
    const searchable = hidden
      ? `Volume ${v.volume_number} ${v.edition} vol ${v.volume_number}`
      : `${v.title} ${v.desc} ${v.edition} volume ${v.volume_number}`;
    return matchesSearch(searchable);
  });

  grid.innerHTML = volumes.map((vol, idx) => {
    const deferredCls = idx >= 6 ? 'deferred-card' : '';
    const hist = AppState.history[`ln:${vol.id}`];
    const pct = hist ? hist.pct : 0;
    const readBtnLabel = hist ? `Continuar (${pct}%) →` : 'Ler Volume →';

    const spKey = `ln:${vol.id}`;
    const isHidden = isLnVolumeSpoilerHidden(vol.volume_number, spKey, vol.id);
    const isProgressUnlocked = !isHidden && isLnVolumeNormallyProtected(vol.volume_number) && isLnVolumeProgressUnlocked(vol.volume_number, vol.id);
    const isManuallyRevealed = !isHidden && isLnVolumeNormallyProtected(vol.volume_number) && AppState.revealedSpoilers.has(spKey) && !isProgressUnlocked;
    const displayTitle = isHidden ? `Volume ${vol.volume_number}` : vol.title;

    const imgPriorityAttr = idx === 0
      ? 'fetchpriority="high"'
      : (idx >= 4 ? 'loading="lazy"' : '');

    const coverHtml = vol.cover_image
      ? `<div class="vol-cover-wrap" data-action="open-ln" data-vol="${vol.id}">
           <img src="${escapeAttr(vol.cover_image)}" alt="Capa oficial — ${escapeAttr(displayTitle)}" width="192" height="288" ${imgPriorityAttr}>
         </div>`
      : '';

    const coloredBadge = vol.is_colored_edition
      ? `<span class="badge-colored">🎨 Edição Colorida</span>`
      : '';
    const dualBadge = vol.has_scan_alternative
      ? `<span class="badge-dual">⇄ 2 Traduções</span>`
      : '';
    const illusBtn = vol.illustrations_count > 0
      ? `<button type="button" class="meta-pill-illus" data-action="open-gallery" data-vol="${vol.id}">🖼️ ${vol.illustrations_count} artes</button>`
      : '';

    const amzVol = Math.floor(Number(vol.volume_number)) || 1;
    const shieldReason = Number(vol.volume_number) > ANIME_ADAPTED_MAX_LN_VOL
      ? 'Sinopse e subtítulo ocultados (Pós-Anime • Vol. 12+)'
      : 'Sinopse e subtítulo ocultados (Modo Sem Spoilers)';

    const unlockedNotice = isProgressUnlocked
      ? `
        <div class="spoiler-unlocked-note">
          <span class="badge-unlocked-pill">✓ ${pct >= 100 ? 'Volume Concluído' : `${pct}% Lido`} • Sinopse Desbloqueada</span>
          <button type="button" class="btn-text-subtle" data-action="hide-spoiler" data-spoiler-id="${escapeAttr(spKey)}" title="Ocultar sinopse">🙈 Ocultar</button>
        </div>
      `
      : '';
    const manualNotice = isManuallyRevealed
      ? `<div class="spoiler-revealed-note"><button type="button" class="btn-reveal-item" data-action="hide-spoiler" data-spoiler-id="${escapeAttr(spKey)}">🙈 Ocultar novamente</button></div>`
      : '';

    const descBlockHtml = isHidden
      ? `
        <div class="spoiler-shield-box">
          <span class="spoiler-shield-label">🔒 ${shieldReason}</span>
          <button type="button" class="btn-reveal-item" data-action="reveal-spoiler" data-spoiler-id="${escapeAttr(spKey)}">
            👁️ Mostrar sinopse deste volume
          </button>
        </div>
      `
      : `
        ${unlockedNotice}
        <p class="volume-desc">${escapeHtml(vol.desc)}</p>
        ${manualNotice}
      `;

    return `
      <article class="volume-card ${deferredCls}">
        <div>
          <div class="vol-card-top">
            ${coverHtml}
            <div class="vol-card-info">
              <div class="volume-badge">
                <span class="badge-num">Vol. ${vol.volume_number}</span>
                ${coloredBadge}
                ${dualBadge}
              </div>
              <h3>${escapeHtml(displayTitle)}</h3>
              <div class="volume-kanji">${escapeHtml(vol.kanji || '')} • ${escapeHtml(vol.edition || '')}</div>
            </div>
          </div>
          ${descBlockHtml}
        </div>

        <div>
          ${pct > 0 ? `<div class="vol-progress-strip" aria-hidden="true"><div class="vol-progress-fill" style="width:${pct}%"></div></div>` : ''}
          <div class="volume-meta">
            <span>📖 ${vol.chapter_count} seções • ${(vol.paragraph_count || 0).toLocaleString('pt-BR')} §</span>
            ${illusBtn}
          </div>
          <div class="volume-actions">
            <button type="button" class="btn-read" data-action="open-ln" data-vol="${vol.id}">
              ${readBtnLabel}
            </button>
            <a href="https://www.amazon.com.br/s?k=That+Time+I+Got+Reincarnated+as+a+Slime+Vol+${amzVol}+light+novel" target="_blank" rel="noopener" class="btn-amazon-quick">
              🛒 Amazon
            </a>
          </div>
        </div>
      </article>
    `;
  }).join('');

  if (futureGrid) {
    const fut = (AppState.catalog.light_novel.future_volumes || []).filter(f => {
      const spKey = `fut:${f.id}`;
      const hidden = isLnVolumeSpoilerHidden(f.num, spKey, f.id);
      return matchesSearch(hidden ? `Volume ${f.num} ${f.status}` : `${f.title} ${f.desc} ${f.status}`);
    });
    if (futureSection) {
      futureSection.hidden = fut.length === 0;
    }
    futureGrid.innerHTML = fut.map(f => {
      const spKey = `fut:${f.id}`;
      const isHidden = isLnVolumeSpoilerHidden(f.num, spKey, f.id);
      const isManuallyRevealed = isLnVolumeNormallyProtected(f.num) && AppState.revealedSpoilers.has(spKey);

      if (isHidden) {
        return `
          <article class="future-card deferred-card">
            <span class="badge-num">Volume ${f.num} • ${escapeHtml(f.status)}</span>
            <h4>Volume ${f.num}</h4>
            <div class="spoiler-shield-box">
              <span class="spoiler-shield-label">🔒 Sinopse ocultada (Pós-Anime • Vol. 12+)</span>
              <button type="button" class="btn-reveal-item" data-action="reveal-spoiler" data-spoiler-id="${escapeAttr(spKey)}">
                👁️ Mostrar sinopse
              </button>
            </div>
          </article>
        `;
      }

      return `
        <article class="future-card deferred-card">
          <span class="badge-num">Volume ${f.num} • ${escapeHtml(f.status)}</span>
          <h4>${escapeHtml(f.title)}</h4>
          <p>${escapeHtml(f.desc)}</p>
          ${isManuallyRevealed ? `<div class="spoiler-revealed-note"><button type="button" class="btn-reveal-item" data-action="hide-spoiler" data-spoiler-id="${escapeAttr(spKey)}">🙈 Ocultar novamente</button></div>` : ''}
        </article>
      `;
    }).join('');
  }
}

// 2. Catálogo da Web Novel (303 Capítulos em <details>/<summary> nativos + Filtro Anti-Spoilers)
function renderWebNovelCatalog() {
  const container = document.getElementById('wn-arcs-container');
  const statsEl = document.getElementById('wn-hero-stats');
  if (!container || !AppState.catalog) return;

  const info = AppState.catalog.web_novel.info;
  if (statsEl && info) {
    statsEl.textContent = `${info.downloaded_count}/${info.total_chapters} Capítulos Offline • ${info.main_chapters_count} Principais + ${info.extra_chapters_count} Extras`;
  }

  const arcs = AppState.catalog.web_novel.arcs || [];
  const allChapters = AppState.catalog.web_novel.chapters || [];

  container.innerHTML = arcs.map((arc, idx) => {
    const spKey = `wn:${arc.id}`;
    const isHidden = isWnArcSpoilerHidden(arc.id, spKey);
    const isProgressUnlocked = !isHidden && isWnArcNormallyProtected(arc.id) && isWnArcProgressUnlocked(arc.id);
    const isManuallyRevealed = !isHidden && isWnArcNormallyProtected(arc.id) && AppState.revealedSpoilers.has(spKey) && !isProgressUnlocked;

    let safeArcTitle = arc.title;
    if (isHidden) {
      safeArcTitle = arc.is_extra
        ? `Arco Extra ${idx - 9} • Pós-Final da Web Novel`
        : `Arco ${idx + 1}${POST_ANIME_WN_ARCS.has(arc.id) ? ' • Pós-Anime' : ''}`;
    } else if (arc.id === 'arc-7' && AppState.settings.spoilerMode === 'post_anime') {
      safeArcTitle = 'Arco 7: O Despertar da Heroína';
    }

    const safeArcDesc = isHidden
      ? (POST_ANIME_WN_ARCS.has(arc.id)
          ? '🔒 Sinopse e títulos dos capítulos ocultados (Pós-Anime • equivalente aos Vols. 12+)'
          : '🔒 Sinopse e títulos dos capítulos ocultados (Modo Sem Spoilers)')
      : arc.desc;

    const arcChs = allChapters.filter(c => {
      if (c.arc_id !== arc.id) return false;
      const searchable = isHidden ? `${c.display_num} ${safeArcTitle}` : `${c.display_num} ${c.title} ${arc.title}`;
      return matchesSearch(searchable);
    });
    if (AppState.searchQuery && arcChs.length === 0) return '';

    const shouldOpen = AppState.searchQuery ? 'open' : (idx === 0 ? 'open' : '');
    const extraCls = arc.is_extra ? 'is-extra-arc' : '';

    const spoilerTopBar = isHidden
      ? `
        <div class="wn-arc-spoiler-bar">
          <span>🛡️ Os títulos deste arco estão ocultos para evitar spoilers.</span>
          <button type="button" class="btn-reveal-item" data-action="reveal-spoiler" data-spoiler-id="${escapeAttr(spKey)}">
            👁️ Mostrar sinopse e títulos deste arco
          </button>
        </div>
      `
      : (isProgressUnlocked
          ? `
            <div class="wn-arc-spoiler-bar">
              <span>✓ <strong>Progresso:</strong> Você já leu 75%+ deste arco ou capítulos posteriores. Sinopse e títulos liberados!</span>
              <button type="button" class="btn-reveal-item" data-action="hide-spoiler" data-spoiler-id="${escapeAttr(spKey)}">
                🙈 Ocultar
              </button>
            </div>
          `
          : (isManuallyRevealed
              ? `
                <div class="wn-arc-spoiler-bar">
                  <span>👁️ Sinopse e títulos revelados temporariamente.</span>
                  <button type="button" class="btn-reveal-item" data-action="hide-spoiler" data-spoiler-id="${escapeAttr(spKey)}">
                    🙈 Ocultar novamente
                  </button>
                </div>
              `
              : ''));

    const chButtons = arcChs.map(ch => {
      const chId = ch.id || `cap-${String(ch.num).padStart(3, '0')}`;
      const hist = AppState.history[`wn:${chId}`];
      const readCls = hist && hist.pct >= 85 ? 'is-read' : '';
      const statusLabel = hist
        ? (hist.pct >= 85 ? '✓ Lido' : `${hist.pct}%`)
        : (ch.is_downloaded ? 'Offline' : 'Online');
      const showChTitle = !isHidden || (hist && hist.pct > 0);

      return `
        <button type="button" class="chapter-item-btn ${readCls}" data-action="open-wn" data-chid="${escapeAttr(chId)}">
          <span class="ch-info">
            <span class="ch-num">${escapeHtml(ch.display_num || `Capítulo ${ch.num}`)}</span>
            <span class="ch-title ${showChTitle ? '' : 'is-masked-spoiler'}">${showChTitle ? escapeHtml(ch.title) : 'Título ocultado contra spoilers'}</span>
          </span>
          <span class="ch-status-pill">${statusLabel}</span>
        </button>
      `;
    }).join('');

    return `
      <details class="arc-details ${extraCls}" ${shouldOpen}>
        <summary class="arc-summary">
          <span>
            <span class="arc-title-text">${escapeHtml(safeArcTitle)} (${arcChs.length} capítulos)</span>
            <span class="arc-desc-text">${escapeHtml(safeArcDesc)}</span>
          </span>
        </summary>
        ${spoilerTopBar}
        <div class="chapter-list">
          ${chButtons}
        </div>
      </details>
    `;
  }).join('');
}

// 2.5 Resumo da História e Guia para Iniciantes / Pós-Anime
function renderRecapCatalog() {
  if (!AppState.catalog || !AppState.catalog.story_recap) return;
  const recap = AppState.catalog.story_recap;

  const isZeroSpoilerMode = AppState.settings.spoilerMode === 'all';
  const hasQuery = Boolean(AppState.searchQuery);

  // 0. Guia para Iniciantes (Nunca Viu o Anime)
  if (recap.beginner_pitch) {
    const pitch = recap.beginner_pitch;
    const tagEl = document.getElementById('recap-beginner-tagline');
    if (tagEl && pitch.tagline) tagEl.textContent = pitch.tagline;

    const synEl = document.getElementById('beginner-synopsis-text');
    if (synEl && pitch.synopsis) {
      synEl.innerHTML = escapeHtml(pitch.synopsis)
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    }

    const recomEl = document.getElementById('beginner-recom-text');
    if (recomEl && pitch.recommendation) {
      recomEl.innerHTML = escapeHtml(pitch.recommendation)
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    }

    const pillarsGrid = document.getElementById('beginner-pillars-grid');
    if (pillarsGrid && Array.isArray(pitch.pillars)) {
      pillarsGrid.innerHTML = pitch.pillars.map(p => `
        <div class="pillar-card">
          <div class="pillar-icon">${escapeHtml(p.icon)}</div>
          <h4 class="pillar-title">${escapeHtml(p.title)}</h4>
          <p class="pillar-desc">${escapeHtml(p.desc)}</p>
        </div>
      `).join('');
    }
  }

  // 0.5 Linha de Progressão de Escala (Volumes 1 a 23 + 8.5)
  const progGrid = document.getElementById('progression-timeline-grid');
  if (progGrid && Array.isArray(recap.progression_timeline)) {
    const filteredProg = recap.progression_timeline.filter(item => {
      return matchesSearch(`${item.vol_num} ${item.title} ${item.scale} ${item.theme_scope} ${item.summary_two_lines}`);
    });

    progGrid.innerHTML = filteredProg.map(item => {
      const lines = (item.summary_two_lines || '').split('\n').filter(Boolean);
      const line1 = lines[0] || '';
      const line2 = lines[1] || '';

      return `
        <article class="progression-card" data-vol-id="${escapeAttr(item.vol_id)}">
          <div class="progression-card-top">
            <span class="progression-vol-badge">${escapeHtml(item.vol_num)}</span>
            <span class="progression-scale-badge">${escapeHtml(item.scale)}</span>
          </div>
          <h4 class="progression-title">${escapeHtml(item.title)}</h4>
          <p class="progression-theme"><span class="progression-theme-label">Escopo &amp; Foco:</span> ${escapeHtml(item.theme_scope)}</p>
          <div class="progression-spoiler-box" aria-label="Resumo em 2 Linhas com spoiler leve">
            <div class="progression-spoiler-header">
              <span aria-hidden="true">👁️</span> <strong>Resumo em 2 Linhas:</strong>
            </div>
            <p class="progression-two-lines">
              <span class="p2-line"><span class="p2-bullet">•</span> ${escapeHtml(line1)}</span>
              <span class="p2-line"><span class="p2-bullet">•</span> ${escapeHtml(line2)}</span>
            </p>
          </div>
          <div class="progression-card-footer">
            <button type="button" class="btn-secondary-pill btn-progression-read" data-action="open-ln" data-vol="${escapeAttr(item.vol_id)}">
              📖 Ler ${escapeHtml(item.vol_num)} →
            </button>
          </div>
        </article>
      `;
    }).join('');
  }

  const subEl = document.getElementById('recap-subtitle-text');
  if (subEl && recap.meta && recap.meta.subtitle) {
    subEl.textContent = recap.meta.subtitle;
  }

  const noticeEl = document.getElementById('recap-zero-spoiler-notice');
  if (noticeEl) {
    noticeEl.hidden = !isZeroSpoilerMode;
  }

  // 1. De onde começar a ler
  const startGrid = document.getElementById('recap-start-grid');
  if (startGrid && Array.isArray(recap.start_guides)) {
    startGrid.innerHTML = recap.start_guides
      .filter(g => matchesSearch(`${g.badge} ${g.title} ${g.desc}`))
      .map(g => `
        <article class="recap-start-card">
          <div>
            <span class="recap-kicker">${escapeHtml(g.badge)}</span>
            <h4>${escapeHtml(g.title)}</h4>
            <p>${escapeHtml(g.desc)}</p>
          </div>
          <button type="button" class="btn-continue btn-recap-start" data-action="open-ln" data-vol="${escapeAttr(g.target_vol)}">
            ${escapeHtml(g.btn_label)}
          </button>
        </article>
      `).join('');
  }

  // 2. Panorama em 4 Fases
  const phasesDetails = document.getElementById('recap-phases-details');
  const phasesGrid = document.getElementById('recap-phases-grid');
  if (phasesGrid && Array.isArray(recap.phases)) {
    const filteredPhases = recap.phases.filter(p => matchesSearch(`${p.kicker} ${p.title} ${p.summary}`));
    if (phasesDetails) {
      phasesDetails.hidden = hasQuery && filteredPhases.length === 0;
      phasesDetails.open = hasQuery ? true : !isZeroSpoilerMode;
    }
    phasesGrid.innerHTML = filteredPhases.map(p => `
      <article class="recap-phase-card">
        <div class="recap-phase-kicker">${escapeHtml(p.kicker)}</div>
        <h4>${escapeHtml(p.title)}</h4>
        <p>${escapeHtml(p.summary)}</p>
      </article>
    `).join('');
  }

  // 3. Resumo Volume a Volume (Vol. 1 ao Vol. 11 + 8.5)
  const volsContainer = document.getElementById('recap-volumes-container');
  if (volsContainer && Array.isArray(recap.volumes)) {
    const filteredVols = recap.volumes.filter(v => {
      const hlText = (v.highlights || []).join(' ');
      const kfText = (v.key_figures || []).join(' ');
      return matchesSearch(`${v.num_label} ${v.anime_ref} ${v.title} ${v.summary} ${hlText} ${kfText}`);
    });

    volsContainer.innerHTML = filteredVols.map((v, idx) => {
      const shouldOpen = hasQuery
        ? 'open'
        : (!isZeroSpoilerMode && idx === 0 ? 'open' : '');
      const postS3Cls = v.is_post_s3 ? 'is-post-s3' : '';
      const deferredRecapCls = idx >= 4 ? 'deferred-card' : '';
      const safeHeaderTitle = isZeroSpoilerMode ? `${v.num_label} — Resumo do Volume` : v.title;

      const highlightsHtml = (v.highlights || []).map(item => `<li>${escapeHtml(item)}</li>`).join('');
      const figuresHtml = (v.key_figures || []).map(tag => `<span class="recap-tag">${escapeHtml(tag)}</span>`).join('');
      const nextVolCta = v.id === 'vol-11'
        ? `<button type="button" class="btn-continue" data-action="open-ln" data-vol="vol-12">🚀 Continuar História no Volume 12 →</button>`
        : '';

      return `
        <details class="arc-details recap-vol-details ${postS3Cls} ${deferredRecapCls}" data-post-s3="${v.is_post_s3 ? 'true' : 'false'}" ${shouldOpen}>
          <summary class="arc-summary recap-vol-summary">
            <span class="recap-summary-inner">
              <span class="recap-summary-badges">
                <span class="badge-num">${escapeHtml(v.num_label)}</span>
                <span class="recap-anime-badge ${v.is_post_s3 ? 'is-post-anime-s3' : ''}">${escapeHtml(v.anime_ref)}</span>
              </span>
              <span class="arc-title-text">${escapeHtml(safeHeaderTitle)}</span>
            </span>
          </summary>

          <div class="recap-vol-body">
            <div class="recap-vol-layout">
              <div class="recap-cover-col">
                <img
                  src="${escapeAttr(v.cover)}"
                  alt="Capa de ${escapeAttr(v.title)}"
                  width="150"
                  height="215"
                  loading="lazy"
                  class="recap-cover-img"
                >
              </div>
              <div class="recap-text-col">
                <p class="recap-main-summary">${escapeHtml(v.summary)}</p>
                <h4 class="recap-sub-heading">📌 Acontecimentos Essenciais para Lembrar</h4>
                <ul class="recap-highlights-list">
                  ${highlightsHtml}
                </ul>
                <div class="recap-tags-row" aria-label="Personagens e elementos-chave">
                  ${figuresHtml}
                </div>
                <div class="recap-actions-row">
                  <button type="button" class="btn-secondary-pill" data-action="open-ln" data-vol="${escapeAttr(v.id)}">
                    📘 Abrir ${escapeHtml(v.num_label)} no Leitor →
                  </button>
                  ${nextVolCta}
                </div>
              </div>
            </div>
          </div>
        </details>
      `;
    }).join('');
  }

  // 4. Estado do Mundo no Fim do Volume 11
  const worldDetails = document.getElementById('recap-world-details');
  const worldGrid = document.getElementById('recap-world-state-grid');
  if (worldGrid && Array.isArray(recap.world_state)) {
    const filteredWorld = recap.world_state.filter(w => matchesSearch(`${w.title} ${w.body}`));
    if (worldDetails) {
      worldDetails.hidden = hasQuery && filteredWorld.length === 0;
      worldDetails.open = hasQuery ? true : !isZeroSpoilerMode;
    }
    worldGrid.innerHTML = filteredWorld.map(w => `
      <article class="term-card recap-world-card">
        <div class="term-name">${escapeHtml(w.icon)} ${escapeHtml(w.title)}</div>
        <div class="term-desc">${escapeHtml(w.body)}</div>
      </article>
    `).join('');
  }
}

// 3. Comparador (Edições em Português + Diferenças WN vs LN + Filtro Anti-Spoilers)
function renderComparisonCatalog() {
  if (!AppState.catalog) return;
  const comp = AppState.catalog.comparison;
  if (!comp) return;

  const ovEl = document.getElementById('comparison-overview-text');
  if (ovEl) ovEl.textContent = comp.overview;

  const audit = comp.translation_audit;
  if (audit) {
    const aOv = document.getElementById('audit-overview-text');
    if (aOv) {
      const countTxt = audit.total_paragraphs_repaired
        ? ` Mais de ${audit.total_paragraphs_repaired.toLocaleString('pt-BR')} parágrafos e títulos foram revisados e padronizados automaticamente ao longo da coleção.`
        : '';
      aOv.textContent = audit.overview + countTxt;
    }

    const tbody = document.getElementById('audit-table-body');
    if (tbody && audit.edition_comparison) {
      tbody.innerHTML = audit.edition_comparison.map(row => `
        <tr>
          <td><strong>${escapeHtml(row.aspect)}</strong></td>
          <td>${escapeHtml(row.tssdk_scan)}</td>
          <td>${escapeHtml(row.drive_original)}</td>
          <td>${escapeHtml(row.repaired_repo)}</td>
        </tr>
      `).join('');
    }

    const hlGrid = document.getElementById('audit-highlights-grid');
    if (hlGrid && audit.curated_highlights) {
      hlGrid.innerHTML = audit.curated_highlights
        .filter(h => matchesSearch(`${h.category} ${h.before} ${h.after} ${h.why}`))
        .map(h => `
          <article class="repair-card">
            <div class="repair-cat">${escapeHtml(h.category)}</div>
            <div class="repair-before"><strong>Antes (Tradução Bruta):</strong> ${escapeHtml(h.before)}</div>
            <div class="repair-after"><strong>Revisado PT-BR:</strong> ${escapeHtml(h.after)}</div>
            <p class="repair-why">${escapeHtml(h.why)}</p>
          </article>
        `).join('');
    }

    const samplesDetails = document.getElementById('audit-samples-details');
    const samplesGrid = document.getElementById('audit-real-samples-grid');
    if (samplesDetails && samplesGrid && Array.isArray(audit.real_samples) && audit.real_samples.length > 0) {
      const filteredSamples = audit.real_samples.filter(s => {
        const chLabel = s.chapter || s.context || '';
        const beforeTxt = s.before || s.raw_drive || '';
        const afterTxt = s.after || s.repaired_ptbr || '';
        return matchesSearch(`${s.volume} ${chLabel} ${beforeTxt} ${afterTxt}`);
      });
      samplesDetails.hidden = filteredSamples.length === 0;
      samplesGrid.innerHTML = filteredSamples.map(s => {
        const chLabel = s.chapter || s.context || '';
        const beforeTxt = s.before || s.raw_drive || '';
        const afterTxt = s.after || s.repaired_ptbr || '';
        return `
          <article class="repair-card">
            <div class="repair-cat">${escapeHtml(s.volume)}${chLabel ? ` • ${escapeHtml(chLabel)}` : ''}</div>
            <div class="repair-before"><strong>Texto Original (Antes):</strong> ${escapeHtml(beforeTxt)}</div>
            <div class="repair-after"><strong>Revisado PT-BR:</strong> ${escapeHtml(afterTxt)}</div>
          </article>
        `;
      }).join('');
    }
  }

  const diffsEl = document.getElementById('comparison-diffs-list');
  if (diffsEl && comp.key_differences) {
    diffsEl.innerHTML = comp.key_differences
      .map((diff, origIdx) => ({ diff, origIdx }))
      .filter(({ diff, origIdx }) => {
        const spKey = `comp:${origIdx}`;
        const hidden = isComparisonDiffSpoilerHidden(origIdx, spKey);
        return matchesSearch(hidden ? `Diferença ${origIdx + 1}` : `${diff.topic} ${diff.wn} ${diff.ln}`);
      })
      .map(({ diff, origIdx }, i) => {
        const spKey = `comp:${origIdx}`;
        const isHidden = isComparisonDiffSpoilerHidden(origIdx, spKey);
        const isManuallyRevealed = isComparisonDiffNormallyProtected(origIdx) && AppState.revealedSpoilers.has(spKey);

        if (isHidden) {
          const scopeLabel = origIdx >= 6 ? 'Pós-Anime (Volumes 12+)' : 'Ocultado contra Spoilers';
          return `
            <article class="comparison-card ${i >= 3 ? 'deferred-card' : ''}">
              <h4>⚖️ Diferença #${origIdx + 1} — ${scopeLabel}</h4>
              <div class="spoiler-shield-box">
                <span class="spoiler-shield-label">🔒 Comparativo de enredo ocultado para evitar spoilers.</span>
                <button type="button" class="btn-reveal-item" data-action="reveal-spoiler" data-spoiler-id="${escapeAttr(spKey)}">
                  👁️ Mostrar este comparativo
                </button>
              </div>
            </article>
          `;
        }

        return `
          <article class="comparison-card ${i >= 3 ? 'deferred-card' : ''}">
            <h4>⚖️ ${escapeHtml(diff.topic)}</h4>
            <div class="comparison-grid">
              <div class="comparison-column col-wn">
                <div class="col-header">📜 Web Novel (Original)</div>
                <div class="col-body">${escapeHtml(diff.wn)}</div>
              </div>
              <div class="comparison-column col-ln">
                <div class="col-header">📘 Light Novel (Oficial)</div>
                <div class="col-body">${escapeHtml(diff.ln)}</div>
              </div>
            </div>
            ${isManuallyRevealed ? `<div class="spoiler-revealed-note"><button type="button" class="btn-reveal-item" data-action="hide-spoiler" data-spoiler-id="${escapeAttr(spKey)}">🙈 Ocultar novamente</button></div>` : ''}
          </article>
        `;
      }).join('');
  }
}

// 4. Guia Cultural Japonês & Nomes Canônicos
function renderCulturalCatalog() {
  if (!AppState.catalog || !AppState.catalog.cultural_guide) return;
  const g = AppState.catalog.cultural_guide;

  const honEl = document.getElementById('cultural-honorifics-list');
  const conEl = document.getElementById('cultural-concepts-list');
  const aspEl = document.getElementById('cultural-aspects-list');

  if (honEl) {
    honEl.innerHTML = (g.honorifics || [])
      .filter(h => matchesSearch(`${h.term} ${h.meaning}`))
      .map(h => `
        <article class="term-card">
          <div class="term-name">${escapeHtml(h.term)}</div>
          <div class="term-desc">${escapeHtml(h.meaning)}</div>
        </article>
      `).join('');
  }

  if (conEl) {
    conEl.innerHTML = (g.tensura_concepts || [])
      .map((c, origIdx) => ({ c, origIdx }))
      .filter(({ c, origIdx }) => {
        const spKey = `cult:${origIdx}`;
        const hidden = isCulturalConceptSpoilerHidden(origIdx, spKey);
        const safeName = origIdx === 6 ? 'Grande Sábio & Evoluções' : c.term;
        return matchesSearch(hidden ? safeName : `${c.term} ${c.desc}`);
      })
      .map(({ c, origIdx }) => {
        const spKey = `cult:${origIdx}`;
        const isHidden = isCulturalConceptSpoilerHidden(origIdx, spKey);
        const isManuallyRevealed = isCulturalConceptNormallyProtected(origIdx) && AppState.revealedSpoilers.has(spKey);

        if (isHidden) {
          const safeTerm = origIdx === 6 ? 'Grande Sábio → Evoluções Posteriores' : c.term;
          return `
            <article class="term-card">
              <div class="term-name">${escapeHtml(safeTerm)}</div>
              <div class="spoiler-shield-box">
                <span class="spoiler-shield-label">🔒 Explicação ocultada por conter detalhes pós-Volume 11.</span>
                <button type="button" class="btn-reveal-item" data-action="reveal-spoiler" data-spoiler-id="${escapeAttr(spKey)}">
                  👁️ Mostrar explicação
                </button>
              </div>
            </article>
          `;
        }

        return `
          <article class="term-card">
            <div class="term-name">${escapeHtml(c.term)}</div>
            <div class="term-desc">${escapeHtml(c.desc)}</div>
            ${isManuallyRevealed ? `<div class="spoiler-revealed-note"><button type="button" class="btn-reveal-item" data-action="hide-spoiler" data-spoiler-id="${escapeAttr(spKey)}">🙈 Ocultar novamente</button></div>` : ''}
          </article>
        `;
      }).join('');
  }

  if (aspEl) {
    aspEl.innerHTML = (g.cultural_aspects || [])
      .filter(a => matchesSearch(`${a.element} ${a.desc}`))
      .map(a => `
        <article class="term-card">
          <div class="term-name">${escapeHtml(a.element)}</div>
          <div class="term-desc">${escapeHtml(a.desc)}</div>
        </article>
      `).join('');
  }
}

// 5. Loja Amazon Brasil
function renderAmazonCatalog() {
  const grid = document.getElementById('amazon-volumes-grid');
  if (!grid || !AppState.catalog || !AppState.catalog.amazon_br) return;

  const desc = document.getElementById('amazon-store-desc');
  if (desc && AppState.catalog.amazon_br.store_info) {
    desc.textContent = AppState.catalog.amazon_br.store_info;
  }

  const vols = (AppState.catalog.amazon_br.volumes || []).filter(v => {
    const hidden = isLnVolumeSpoilerHidden(v.volume, `ln:vol-${v.volume}`);
    return matchesSearch(hidden ? `Volume ${v.volume}` : `${v.title} volume ${v.volume}`);
  });

  grid.innerHTML = vols.map((item, idx) => {
    const hidden = isLnVolumeSpoilerHidden(item.volume, `ln:vol-${item.volume}`);
    const safeTitle = hidden ? `Volume ${item.volume}: Light Novel Oficial` : item.title;
    return `
      <article class="amazon-card ${idx >= 8 ? 'deferred-card' : ''}">
        <div>
          <span class="badge-num">Volume ${item.volume}</span>
          <h3>${escapeHtml(safeTitle)}</h3>
          <div class="amazon-formats">${escapeHtml((item.formats || []).join(' • '))}</div>
        </div>
        <a href="${escapeAttr(item.search_url)}" target="_blank" rel="noopener" class="btn-amazon-buy">
          🛒 Ver na Amazon.com.br
        </a>
      </article>
    `;
  }).join('');
}

// ==========================================================================
// MOTOR DE LEITURA (LIGHT NOVEL & WEB NOVEL)
// ==========================================================================

async function openLightNovel(volumeId, chapterIndex = 0, anchorOrRatio = 0, preferredChapterTitle = '') {
  try {
    const initialBaseGuess = String(volumeId).replace(/-scan$/, '');
    const savedHist = AppState.history[`ln:${initialBaseGuess}`];
    const effectiveVolumeId = initialBaseGuess;

    const res = await fetch(`data/light_novel/${effectiveVolumeId}.json?v=${APP_BUILD_VERSION}`);
    if (!res.ok) throw new Error(`Volume ${effectiveVolumeId} não encontrado.`);
    const data = await res.json();

    const safeIdx = Math.min(Math.max(Number(chapterIndex) || 0, 0), Math.max(data.chapters.length - 1, 0));
    const baseId = data.base_volume_id || effectiveVolumeId.replace(/-scan$/, '');

    // Se o usuário alternou edição (Edição Ilustrada Revisada <-> TSSDK Scan), parear capítulo equivalente pelo título
    let targetIdx = safeIdx;
    let anchor = normalizeScrollAnchor(anchorOrRatio);

    if (preferredChapterTitle) {
      const mCap = preferredChapterTitle.match(/\b(cap[íi]tulo\s*\d+|pr[óo]logo|ep[íi]logo|interl[úu]dio|posf[áa]cio|capa)/i);
      if (mCap) {
        const key = mCap[1].toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        const matchedIdx = data.chapters.findIndex(c =>
          (c.title || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').includes(key)
        );
        if (matchedIdx >= 0) targetIdx = matchedIdx;
      }
      anchor.useRatioOnly = true;
    } else if (chapterIndex === null) {
      const lnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LN);
      if (lnSave && lnSave.id === effectiveVolumeId) {
        targetIdx = Math.min(lnSave.chapterIndex || 0, Math.max(data.chapters.length - 1, 0));
        anchor = normalizeScrollAnchor(lnSave);
      } else if (AppState.history[`ln:${baseId}`]) {
        const hist = AppState.history[`ln:${baseId}`];
        targetIdx = Math.min(hist.chapterIndex || 0, Math.max(data.chapters.length - 1, 0));
        anchor = normalizeScrollAnchor(hist);
      }
    }

    AppState.currentReading = {
      type: 'light_novel',
      id: effectiveVolumeId,
      baseVolumeId: baseId,
      chapterIndex: targetIdx,
      data,
      scrollRatio: anchor.scrollRatio,
      pIndex: anchor.pIndex,
      pOffsetPx: anchor.pOffsetPx,
      useRatioOnly: anchor.useRatioOnly
    };

    renderReaderScreen();
    history.replaceState(null, '', `#ln/${effectiveVolumeId}/${targetIdx}`);
  } catch (err) {
    console.error('Erro ao abrir Light Novel:', err);
    showCulturalNoteDialog('Erro ao Carregar Volume', err.message);
  }
}

async function openWebNovelChapter(chapterIdOrNum, anchorOrRatio = 0) {
  try {
    const chList = AppState.catalog ? AppState.catalog.web_novel.chapters : [];
    let meta = null;

    if (typeof chapterIdOrNum === 'number' || /^\d+$/.test(String(chapterIdOrNum))) {
      const n = Number(chapterIdOrNum);
      meta = chList.find(c => !c.is_extra && Number(c.num) === n);
    } else {
      meta = chList.find(c => c.id === chapterIdOrNum);
    }

    const fileName = meta ? meta.file : `capitulo_${String(chapterIdOrNum).padStart(3, '0')}.json`;
    const resolvedId = meta ? meta.id : `cap-${String(chapterIdOrNum).padStart(3, '0')}`;

    const res = await fetch(`data/web_novel/${fileName}?v=${APP_BUILD_VERSION}`);
    if (!res.ok) {
      if (meta && meta.url) {
        window.open(meta.url, '_blank', 'noopener');
      }
      return;
    }
    const data = await res.json();

    let anchor = normalizeScrollAnchor(anchorOrRatio);
    if (anchorOrRatio === null) {
      const wnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_WN);
      const hist = AppState.history[`wn:${resolvedId}`];
      if (wnSave && wnSave.id === resolvedId) {
        anchor = normalizeScrollAnchor(wnSave);
      } else if (hist && hist.pct > 0 && hist.pct < 95) {
        anchor = normalizeScrollAnchor(hist);
      }
    }

    AppState.currentReading = {
      type: 'web_novel',
      id: resolvedId,
      baseVolumeId: null,
      chapterIndex: 0,
      data,
      scrollRatio: anchor.scrollRatio,
      pIndex: anchor.pIndex,
      pOffsetPx: anchor.pOffsetPx,
      useRatioOnly: anchor.useRatioOnly
    };

    renderReaderScreen();
    history.replaceState(null, '', `#wn/${resolvedId}`);
  } catch (err) {
    console.error('Erro ao abrir Web Novel:', err);
    showCulturalNoteDialog('Erro ao Carregar Capítulo', err.message);
  }
}

function applyAnchorScrollOnce(cur) {
  const hasSavedSpot = (typeof cur.pIndex === 'number' && (cur.pIndex > 0 || cur.scrollRatio > 0.005)) || cur.scrollRatio > 0.005;
  if (!hasSavedSpot) {
    window.scrollTo({ top: 0, behavior: 'instant' });
    return;
  }

  if (!cur.useRatioOnly && typeof cur.pIndex === 'number') {
    const pEl = document.getElementById(`p-${cur.pIndex}`);
    if (pEl) {
      const clearance = getReaderToolbarClearance();
      const offset = typeof cur.pOffsetPx === 'number'
        ? Math.max(cur.pOffsetPx, clearance - 6)
        : clearance;
      const targetTop = Math.max(0, window.scrollY + pEl.getBoundingClientRect().top - offset);
      window.scrollTo({ top: targetTop, behavior: 'instant' });
      return;
    }
  }

  const maxS = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  if (maxS > 0 && cur.scrollRatio > 0) {
    window.scrollTo({ top: maxS * cur.scrollRatio, behavior: 'instant' });
  } else {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }
}

function restoreReaderScrollPosition(cur) {
  clearTimeout(AppState.restoreTimer);
  AppState.isRestoringScroll = true;

  applyAnchorScrollOnce(cur);
  requestAnimationFrame(() => {
    applyAnchorScrollOnce(cur);
  });

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => {
      if (AppState.isRestoringScroll && AppState.currentReading.type) {
        applyAnchorScrollOnce(AppState.currentReading);
      }
    }).catch(() => {});
  }

  AppState.restoreTimer = setTimeout(() => {
    if (AppState.currentReading.type) {
      applyAnchorScrollOnce(AppState.currentReading);
      AppState.isRestoringScroll = false;
      persistReadingProgress({ force: true, inReader: true });
    } else {
      AppState.isRestoringScroll = false;
    }
  }, 260);
}

function renderReaderScreen() {
  const siteHeader = document.getElementById('site-header');
  const readerView = document.getElementById('reader-view');
  const mainArea = document.getElementById('content-area');
  const banner = document.getElementById('continue-banner');
  const headerArea = document.getElementById('reader-header-area');
  const proseArea = document.getElementById('reader-text-container');
  const footerNav = document.getElementById('reader-footer-nav');
  const toolbarTitle = document.getElementById('reader-toolbar-title');
  const trackPill = document.getElementById('reader-track-pill');
  const chSelect = document.getElementById('reader-chapter-select');
  const btnGallery = document.getElementById('btn-reader-gallery');
  const btnSwitchTrack = document.getElementById('btn-reader-switch-track');

  if (!readerView || !proseArea) return;

  if (siteHeader) siteHeader.hidden = true;
  mainArea.hidden = true;
  if (banner) banner.hidden = true;
  readerView.hidden = false;

  const cur = AppState.currentReading;
  const inlineGlossary = (AppState.catalog && AppState.catalog.cultural_guide && AppState.catalog.cultural_guide.inline_glossary) || {};
  const seenTermsInChapter = new Set();

  if (cur.type === 'light_novel') {
    const vol = cur.data;
    const ch = vol.chapters[cur.chapterIndex] || vol.chapters[0];
    const baseVolMeta = AppState.catalog.light_novel.volumes.find(v => v.id === cur.baseVolumeId);
    const wnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_WN);

    trackPill.textContent = '📘 Light Novel';
    trackPill.classList.remove('is-wn');
    toolbarTitle.textContent = `${vol.title} — ${ch.title}`;

    if (btnSwitchTrack) {
      btnSwitchTrack.textContent = wnSave ? '⇄ Voltar p/ Web Novel' : '⇄ Ir p/ Web Novel';
      btnSwitchTrack.setAttribute('aria-label', wnSave
        ? 'Salvar ponto atual na Light Novel e voltar para onde parou na Web Novel'
        : 'Salvar ponto atual na Light Novel e abrir a Web Novel');
    }

    // Preencher seletor de seções/capítulos do volume
    chSelect.innerHTML = vol.chapters.map((c, idx) =>
      `<option value="${idx}" ${idx === cur.chapterIndex ? 'selected' : ''}>${idx + 1}. ${escapeHtml(c.title)}</option>`
    ).join('');

    // Botão de galeria
    const illusList = (vol.illustrations && vol.illustrations.length > 0)
      ? vol.illustrations
      : (baseVolMeta && baseVolMeta.illustrations ? baseVolMeta.illustrations : []);
    btnGallery.hidden = illusList.length === 0;
    btnGallery.dataset.vol = cur.baseVolumeId;

    const pCount = (ch.paragraphs || []).length;
    const estMin = Math.max(1, Math.ceil(pCount / 10));

    headerArea.innerHTML = `
      <div class="vol-title">${escapeHtml(vol.title)} • ${escapeHtml(vol.edition || '')}</div>
      <h2 class="ch-main-heading">${escapeHtml(ch.title)}</h2>
      <div class="ch-meta-row">
        <span>Seção ${cur.chapterIndex + 1} de ${vol.chapters.length}</span>
        <span>•</span>
        <span>Leitura estimada: ~${estMin} min</span>
        ${illusList.length > 0 ? `<button type="button" class="meta-pill-illus" data-action="open-gallery-current">🖼️ Galeria do Volume (${illusList.length})</button>` : ''}
      </div>
    `;

    // Renderizar blocos estruturados (parágrafos, ilustrações inline e quebras de cena)
    const blocks = ch.blocks && ch.blocks.length > 0
      ? ch.blocks
      : (ch.paragraphs || []).map(t => ({ type: 'p', text: t }));

    let pCounter = 0;
    proseArea.innerHTML = blocks.map((block, bIdx) => {
      if (block.type === 'hr') {
        const hardCls = block.variant === 'hard' ? 'scene-break-hard' : '';
        return `<hr class="scene-break ${hardCls}">`;
      }
      if (block.type === 'img') {
        const imgIdx = illusList.findIndex(it => it.src === block.src);
        const w = block.width || 800;
        const h = block.height || 1100;
        const inlineLoadAttr = bIdx === 0 ? 'fetchpriority="high"' : 'loading="lazy"';
        return `
          <figure class="novel-illustration">
            <img
              src="${escapeAttr(block.src)}"
              alt="${escapeAttr(block.alt || block.caption || 'Ilustração oficial')}"
              width="${w}"
              height="${h}"
              ${inlineLoadAttr}
              data-action="zoom-inline-img"
              data-imgidx="${imgIdx >= 0 ? imgIdx : 0}"
              data-src="${escapeAttr(block.src)}"
            >
            ${block.caption ? `<figcaption>${escapeHtml(block.caption)} — clique na imagem para ampliar</figcaption>` : ''}
          </figure>
        `;
      }
      const pidx = pCounter++;
      const isBm = AppState.bookmarks.some(
        b => b.type === 'light_novel' && b.readingId === cur.id && b.chapterIndex === cur.chapterIndex && b.pIndex === pidx
      );
      const combinedFootnotes = Object.assign({}, vol.footnotes || {}, ch.footnotes || {});
      const richHtml = formatRichParagraph(block.text, combinedFootnotes, inlineGlossary, seenTermsInChapter);
      return `<p class="novel-paragraph ${isBm ? 'bookmarked' : ''}" id="p-${pidx}" data-pidx="${pidx}">${richHtml}</p>`;
    }).join('');

    AppState.lightbox.items = illusList;
  } else {
    // WEB NOVEL
    const ch = cur.data;
    const wnChapters = AppState.catalog.web_novel.chapters || [];
    const lnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LN);

    trackPill.textContent = ch.is_extra ? '📜 Web Novel • Extra' : '📜 Web Novel';
    trackPill.classList.add('is-wn');
    toolbarTitle.textContent = `${ch.display_num || `Cap. ${ch.number}`} — ${ch.title}`;
    btnGallery.hidden = true;

    if (btnSwitchTrack) {
      btnSwitchTrack.textContent = lnSave ? '⇄ Voltar p/ Light Novel' : '⇄ Ir p/ Light Novel';
      btnSwitchTrack.setAttribute('aria-label', lnSave
        ? 'Salvar ponto atual na Web Novel e voltar para onde parou na Light Novel'
        : 'Salvar ponto atual na Web Novel e abrir a Light Novel');
    }

    chSelect.innerHTML = wnChapters.map(c =>
      `<option value="${escapeAttr(c.id)}" ${c.id === cur.id ? 'selected' : ''}>${escapeHtml(c.display_num)}: ${escapeHtml(c.title)}</option>`
    ).join('');

    const paras = ch.paragraphs || [];
    const estMin = Math.max(1, Math.ceil(paras.length / 10));

    headerArea.innerHTML = `
      <div class="vol-title is-wn-kicker">Tensei Shitara Slime Datta Ken — Web Novel Original</div>
      <h2 class="ch-main-heading">${escapeHtml(ch.display_num || `Capítulo ${ch.number}`)}: ${escapeHtml(ch.title)}</h2>
      <div class="ch-meta-row">
        <span>${paras.length} parágrafos</span>
        <span>•</span>
        <span>Leitura estimada: ~${estMin} min</span>
        <span>•</span>
        <span>Fonte: Central Novel PT-BR</span>
      </div>
    `;

    proseArea.innerHTML = paras.map((p, pidx) => {
      if (p.trim() === '* * *' || p.trim() === '***') {
        return `<hr class="scene-break">`;
      }
      const isBm = AppState.bookmarks.some(
        b => b.type === 'web_novel' && b.readingId === cur.id && b.pIndex === pidx
      );
      const combinedFootnotes = Object.assign({}, ch.footnotes || {});
      const richHtml = formatRichParagraph(p, combinedFootnotes, inlineGlossary, seenTermsInChapter);
      return `<p class="novel-paragraph ${isBm ? 'bookmarked' : ''}" id="p-${pidx}" data-pidx="${pidx}">${richHtml}</p>`;
    }).join('');
  }

  // Notificar tocador de trilha sonora sobre o capítulo atual
  if (window.TensuraSoundtrack && window.TensuraSoundtrack.handleChapterChange) {
    if (cur.type === 'light_novel') {
      const vol = cur.data;
      const ch = vol.chapters[cur.chapterIndex] || vol.chapters[0];
      window.TensuraSoundtrack.handleChapterChange(cur.baseVolumeId || cur.volumeId, cur.chapterIndex, ch.title);
    } else if (cur.data) {
      window.TensuraSoundtrack.handleChapterChange('wn', cur.chapterIndex || 0, cur.data.title || '');
    }
  }

  renderReaderFooterNav(footerNav);
  updateAutosavePill(cur.scrollRatio || 0);
  syncReaderToolbarOffset();
  restoreReaderScrollPosition(cur);
}

/**
 * Formata texto escapado com:
 * 1. Notas de rodapé culturais {{FN:N}} -> botão interativo [Nota N]
 * 2. Voz do Grande Sábio / Raphael / Ciel «...» -> .voice-sage
 * 3. Comunicação por Pensamento ‹...› -> .voice-telepathy
 * 4. Destaque opcional na 1ª ocorrência de termos culturais japoneses
 */
function formatRichParagraph(rawText, footnotesMap, inlineGlossary, seenTermsSet) {
  let safe = escapeHtml(rawText || '');

  // 1. Notas de rodapé {{FN:N}}
  safe = safe.replace(/\{\{FN:(\d+)\}\}/g, (_, num) => {
    if (footnotesMap && footnotesMap[num]) {
      return `<button type="button" class="fn-badge" data-action="show-fn" data-fn="${num}">[Nota ${num}]</button>`;
    }
    return '';
  });

  // 2. Voz de Grande Sábio / Raphael / Ciel «...»
  safe = safe.replace(/«([^»]+)»/g, '<span class="voice-sage">«$1»</span>');

  // 3. Telepatia ‹...›
  safe = safe.replace(/‹([^›]+)›/g, '<span class="voice-telepathy">‹$1›</span>');

  // 4. Glossário cultural & Guia de Tensura (apenas 1ª ocorrência por capítulo se ativo)
  if (AppState.settings.culturalHints && inlineGlossary) {
    const terms = Object.keys(inlineGlossary).sort((a, b) => b.length - a.length);
    for (const term of terms) {
      const cleanTerm = term.startsWith('-') ? term.slice(1) : term;
      if (seenTermsSet.has(cleanTerm.toLowerCase())) continue;
      const isSuffix = term.startsWith('-');
      const regex = isSuffix
        ? new RegExp(`(-${cleanTerm})\\b`, 'i')
        : new RegExp(`(?<![A-Za-zÀ-ÿ0-9])(${cleanTerm})(?![A-Za-zÀ-ÿ0-9])`, 'i');
      if (regex.test(safe)) {
        seenTermsSet.add(cleanTerm.toLowerCase());
        safe = safe.replace(regex, `<button type="button" class="cultural-term" data-action="show-term" data-term="${term}">$1</button>`);
      }
    }
  }

  return safe;
}

function renderReaderFooterNav(footerNav) {
  if (!footerNav) return;
  const cur = AppState.currentReading;

  if (cur.type === 'light_novel') {
    const vol = cur.data;
    const allVols = AppState.catalog.light_novel.volumes || [];
    const volPos = allVols.findIndex(v => v.id === cur.baseVolumeId);

    const hasPrevCh = cur.chapterIndex > 0;
    const hasNextCh = cur.chapterIndex < vol.chapters.length - 1;
    const prevVol = !hasPrevCh && volPos > 0 ? allVols[volPos - 1] : null;
    const nextVol = !hasNextCh && volPos >= 0 && volPos < allVols.length - 1 ? allVols[volPos + 1] : null;

    const prevDisabled = !hasPrevCh && !prevVol ? 'disabled' : '';
    const nextDisabled = !hasNextCh && !nextVol ? 'disabled' : '';
    const prevLabel = hasPrevCh ? '← Seção Anterior' : (prevVol ? `← Vol. ${prevVol.volume_number}` : '← Início');
    const nextLabel = hasNextCh ? 'Próxima Seção →' : (nextVol ? `Ir para Vol. ${nextVol.volume_number} →` : 'Fim dos Volumes');

    footerNav.innerHTML = `
      <button type="button" class="btn-nav-ch" data-action="ln-prev" ${prevDisabled}>${prevLabel}</button>
      <button type="button" class="btn-nav-ch" data-action="close-reader">📚 Índice da Biblioteca</button>
      <button type="button" class="btn-nav-ch" data-action="ln-next" ${nextDisabled}>${nextLabel}</button>
    `;
  } else {
    const wnChapters = AppState.catalog.web_novel.chapters || [];
    const idx = wnChapters.findIndex(c => c.id === cur.id);
    const prevCh = idx > 0 ? wnChapters[idx - 1] : null;
    const nextCh = idx >= 0 && idx < wnChapters.length - 1 ? wnChapters[idx + 1] : null;

    footerNav.innerHTML = `
      <button type="button" class="btn-nav-ch" data-action="wn-nav" data-chid="${prevCh ? escapeAttr(prevCh.id) : ''}" ${!prevCh ? 'disabled' : ''}>
        ← ${prevCh ? escapeHtml(prevCh.display_num) : 'Início'}
      </button>
      <button type="button" class="btn-nav-ch" data-action="close-reader">📚 Índice da Web Novel</button>
      <button type="button" class="btn-nav-ch" data-action="wn-nav" data-chid="${nextCh ? escapeAttr(nextCh.id) : ''}" ${!nextCh ? 'disabled' : ''}>
        ${nextCh ? escapeHtml(nextCh.display_num) : 'Fim'} →
      </button>
    `;
  }
}

function closeReader() {
  clearTimeout(AppState.restoreTimer);
  AppState.isRestoringScroll = false;
  persistReadingProgress({ force: true, inReader: false });

  const siteHeader = document.getElementById('site-header');
  const readerView = document.getElementById('reader-view');
  const mainArea = document.getElementById('content-area');
  if (readerView) readerView.hidden = true;
  if (siteHeader) siteHeader.hidden = false;
  if (mainArea) mainArea.hidden = false;

  AppState.currentReading.type = null;
  renderAllCatalogViews();
  refreshContinueBanners();
  history.replaceState(null, '', `#${AppState.currentTab}`);
  maybePromptSpoilerOnboarding();
}

// ==========================================================================
// MODAIS NATIVOS (<dialog>.showModal()): GALERIA, LIGHTBOX, NOTAS & MARCADORES
// ==========================================================================

function openVolumeGalleryModal(volumeId) {
  let illus = [];
  let titleText = 'Galeria Oficial de Ilustrações';

  if (AppState.currentReading.type === 'light_novel' && AppState.currentReading.data &&
      (AppState.currentReading.id === volumeId || AppState.currentReading.baseVolumeId === volumeId)) {
    illus = AppState.currentReading.data.illustrations || [];
    titleText = `🖼️ Ilustrações — ${AppState.currentReading.data.title}`;
  } else if (AppState.catalog) {
    const vol = AppState.catalog.light_novel.volumes.find(v => v.id === volumeId);
    if (vol) {
      illus = vol.illustrations || [];
      titleText = `🖼️ Ilustrações — ${vol.title}`;
    }
  }

  if (!illus.length) return;
  AppState.lightbox.items = illus;

  const dialog = document.getElementById('gallery-dialog');
  const titleEl = document.getElementById('gallery-dialog-title');
  const grid = document.getElementById('gallery-dialog-grid');
  if (!dialog || !grid) return;

  titleEl.textContent = titleText;
  grid.innerHTML = illus.map((item, idx) => `
    <button type="button" class="gallery-card" data-action="open-lightbox-idx" data-idx="${idx}">
      <img src="${escapeAttr(item.src)}" alt="${escapeAttr(item.caption || `Ilustração ${idx + 1}`)}" width="${item.width || 400}" height="${item.height || 560}" loading="lazy">
      <span>${escapeHtml(item.caption || `Ilustração ${idx + 1}`)}</span>
    </button>
  `).join('');

  if (!dialog.open) dialog.showModal();
}

function openLightboxAtIndex(idx) {
  const items = AppState.lightbox.items || [];
  if (!items.length) return;
  AppState.lightbox.index = (idx + items.length) % items.length;
  updateLightboxDOM();

  const dialog = document.getElementById('lightbox-dialog');
  if (dialog && !dialog.open) dialog.showModal();
}

function updateLightboxDOM() {
  const items = AppState.lightbox.items || [];
  const item = items[AppState.lightbox.index];
  if (!item) return;

  const img = document.getElementById('lightbox-img');
  const cap = document.getElementById('lightbox-caption');
  const counter = document.getElementById('lightbox-counter');
  if (img) {
    img.src = item.src;
    img.alt = item.caption || 'Ilustração oficial ampliada';
    if (item.width) img.width = item.width;
    if (item.height) img.height = item.height;
  }
  if (cap) cap.textContent = item.caption || '';
  if (counter) counter.textContent = `${AppState.lightbox.index + 1} / ${items.length}`;
}

function showCulturalNoteDialog(heading, bodyText) {
  const dialog = document.getElementById('note-dialog');
  const hEl = document.getElementById('note-dialog-title');
  const pEl = document.getElementById('note-dialog-content');
  if (!dialog || !hEl || !pEl) return;
  hEl.textContent = heading;
  pEl.textContent = bodyText;
  if (!dialog.open) dialog.showModal();
}

function openBookmarksModal(pendingContext = null) {
  const dialog = document.getElementById('bookmarks-dialog');
  const form = document.getElementById('bookmark-add-form');
  const pinBar = document.getElementById('manual-pin-bar');
  const quoteEl = document.getElementById('bookmark-quote-preview');
  const noteInput = document.getElementById('bookmark-note-input');
  if (!dialog) return;

  if (AppState.currentReading.type) {
    persistReadingProgress({ force: true, inReader: true });
  }

  AppState.pendingBookmark = pendingContext;
  if (pendingContext && form) {
    form.hidden = false;
    quoteEl.textContent = pendingContext.snippet;
    noteInput.value = '';
    if (pinBar) pinBar.hidden = true;
  } else {
    if (form) form.hidden = true;
    if (pinBar) pinBar.hidden = !AppState.currentReading.type;
  }

  renderBookmarksListInsideDialog();
  if (!dialog.open) dialog.showModal();
  if (pendingContext && noteInput) noteInput.focus();
}

function renderBookmarksListInsideDialog() {
  const tracksEl = document.getElementById('saved-tracks-summary');
  const listEl = document.getElementById('bookmarks-list-container');

  const lnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LN);
  const wnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_WN);
  const isReadingLN = AppState.currentReading.type === 'light_novel';
  const isReadingWN = AppState.currentReading.type === 'web_novel';

  if (tracksEl) {
    const lnPct = lnSave ? Math.round((lnSave.scrollRatio || 0) * 100) : 0;
    const wnPct = wnSave ? Math.round((wnSave.scrollRatio || 0) * 100) : 0;

    tracksEl.innerHTML = `
      <div class="track-save-card ${isReadingLN ? 'is-active-track' : ''}">
        <div>
          <strong>📘 Posição na Light Novel</strong>
          ${isReadingLN ? `<span class="track-active-tag">● Lendo agora • salvo automaticamente</span>` : ''}
          <p>${lnSave ? escapeHtml(lnSave.title) : 'Nenhuma leitura iniciada na Light Novel ainda.'}</p>
          ${lnSave ? `<div class="track-card-meta">Posição salva: ${lnPct}% da página</div>` : ''}
        </div>
        ${lnSave
          ? `<button type="button" class="btn-continue track-card-btn" data-action="resume-ln">${isReadingLN ? 'Já está neste ponto ✓' : 'Voltar p/ Light Novel →'}</button>`
          : `<button type="button" class="btn-secondary-pill track-card-btn" data-action="goto-tab-ln">Abrir Catálogo da Light Novel →</button>`
        }
      </div>
      <div class="track-save-card ${isReadingWN ? 'is-active-track' : ''}">
        <div>
          <strong>📜 Posição na Web Novel</strong>
          ${isReadingWN ? `<span class="track-active-tag">● Lendo agora • salvo automaticamente</span>` : ''}
          <p>${wnSave ? escapeHtml(wnSave.title) : 'Nenhuma leitura iniciada na Web Novel ainda.'}</p>
          ${wnSave ? `<div class="track-card-meta">Posição salva: ${wnPct}% da página</div>` : ''}
        </div>
        ${wnSave
          ? `<button type="button" class="btn-continue track-card-btn" data-action="resume-wn">${isReadingWN ? 'Já está neste ponto ✓' : 'Voltar p/ Web Novel →'}</button>`
          : `<button type="button" class="btn-secondary-pill track-card-btn" data-action="goto-tab-wn">Abrir Catálogo da Web Novel →</button>`
        }
      </div>
    `;
  }

  if (!listEl) return;
  if (!AppState.bookmarks.length) {
    listEl.innerHTML = `<p class="empty-bookmarks-hint">Nenhuma marcação extra salva. Não é necessário marcar nada para continuar lendo depois — use o botão acima apenas se quiser guardar algum trecho específico para comparar entre as versões.</p>`;
    return;
  }

  listEl.innerHTML = AppState.bookmarks.slice().reverse().map(bm => `
    <article class="bookmark-item">
      <div>
        <div class="bm-meta">${bm.type === 'light_novel' ? '📘 Light Novel' : '📜 Web Novel'} • ${escapeHtml(bm.label || bm.readingId)} • ${escapeHtml(bm.date || '')}</div>
        <div class="bm-snippet">“${escapeHtml(bm.textSnippet)}”</div>
        ${bm.note ? `<div class="bm-note">📝 ${escapeHtml(bm.note)}</div>` : ''}
      </div>
      <div class="bm-actions">
        <button type="button" class="btn-secondary-pill" data-action="jump-bm" data-bmid="${bm.id}">Abrir</button>
        <button type="button" class="btn-secondary-pill" data-action="del-bm" data-bmid="${bm.id}" aria-label="Excluir marcação">🗑️</button>
      </div>
    </article>
  `).join('');
}

function updateBookmarkBadge() {
  const badge = document.getElementById('bookmark-count-badge');
  if (!badge) return;
  const count = AppState.bookmarks.length;
  badge.hidden = count === 0;
  badge.textContent = String(count);
}

// ==========================================================================
// NAVEGAÇÃO DE ABAS E ROTEAMENTO DE INICIALIZAÇÃO / REABERTURA DO NAVEGADOR
// ==========================================================================

function switchTab(tabName) {
  if (!['light-novel', 'web-novel', 'recap', 'comparison', 'cultural', 'amazon'].includes(tabName)) return;
  AppState.currentTab = tabName;

  const siteHeader = document.getElementById('site-header');
  const readerView = document.getElementById('reader-view');
  const mainArea = document.getElementById('content-area');
  if (readerView && !readerView.hidden) {
    clearTimeout(AppState.restoreTimer);
    AppState.isRestoringScroll = false;
    persistReadingProgress({ force: true, inReader: false });
    readerView.hidden = true;
    if (siteHeader) siteHeader.hidden = false;
    mainArea.hidden = false;
    AppState.currentReading.type = null;
  } else if (siteHeader) {
    siteHeader.hidden = false;
  }

  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  document.querySelectorAll('.view-section').forEach(sec => {
    sec.classList.toggle('active', sec.id === `view-${tabName}`);
  });

  renderAllCatalogViews();
  refreshContinueBanners();
  history.replaceState(null, '', `#${tabName}`);
  window.scrollTo({ top: 0, behavior: 'smooth' });
  maybePromptSpoilerOnboarding();
}

async function handleInitialStartupRoute() {
  const hash = window.location.hash.replace(/^#/, '');
  if (hash) {
    await handleInitialHash(hash);
    return;
  }

  // Sem hash na URL: ao reabrir o navegador/site, retomar automaticamente onde parou se a opção estiver ativa
  if (AppState.settings.autoResumeOnOpen !== false) {
    const last = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LAST);
    if (last && last.type && last.inReader !== false) {
      await resumeSavedRecord(last);
    }
  }
}

async function handleInitialHash(rawHash = null) {
  const hash = rawHash !== null ? rawHash : window.location.hash.replace(/^#/, '');
  if (!hash) return;

  if (['light-novel', 'web-novel', 'recap', 'comparison', 'cultural', 'amazon'].includes(hash)) {
    switchTab(hash);
  } else if (hash.startsWith('ln/')) {
    const [, volId, chStr] = hash.split('/');
    const targetCh = Number(chStr) || 0;
    const baseId = String(volId || '').replace(/-scan$/, '');
    const lnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LN);
    const hist = AppState.history[`ln:${baseId}`];

    let anchor = 0;
    if (lnSave && lnSave.id === volId && Number(lnSave.chapterIndex) === targetCh) {
      anchor = normalizeScrollAnchor(lnSave);
    } else if (hist && Number(hist.chapterIndex) === targetCh) {
      anchor = normalizeScrollAnchor(hist);
    }
    await openLightNovel(volId, targetCh, anchor);
  } else if (hash.startsWith('wn/')) {
    const [, chId] = hash.split('/');
    const wnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_WN);
    const hist = AppState.history[`wn:${chId}`];

    let anchor = 0;
    if (wnSave && wnSave.id === chId) {
      anchor = normalizeScrollAnchor(wnSave);
    } else if (hist) {
      anchor = normalizeScrollAnchor(hist);
    }
    await openWebNovelChapter(chId, anchor);
  }
}

// ==========================================================================
// EXPORTAR / IMPORTAR PROGRESSO JSON (PORTABILIDADE GITHUB PAGES)
// ==========================================================================

function exportUserProgressJson() {
  if (AppState.currentReading.type) {
    persistReadingProgress({ force: true, inReader: true });
  }
  const payload = {
    exportedAt: new Date().toISOString(),
    settings: AppState.settings,
    progressLast: getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LAST),
    progressLN: getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LN),
    progressWN: getSavedTrackProgress(STORAGE_KEYS.PROGRESS_WN),
    history: AppState.history,
    bookmarks: AppState.bookmarks
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `tensura_progresso_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function importUserProgressJson(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(String(reader.result));
      if (data.settings) {
        AppState.settings = { ...AppState.settings, ...data.settings };
        saveSettingsToStorage();
        applySettingsToDOM();
      }
      if (data.progressLast) localStorage.setItem(STORAGE_KEYS.PROGRESS_LAST, JSON.stringify(data.progressLast));
      if (data.progressLN) localStorage.setItem(STORAGE_KEYS.PROGRESS_LN, JSON.stringify(data.progressLN));
      if (data.progressWN) localStorage.setItem(STORAGE_KEYS.PROGRESS_WN, JSON.stringify(data.progressWN));
      if (data.history) {
        AppState.history = data.history;
        localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(AppState.history));
      }
      if (Array.isArray(data.bookmarks)) {
        AppState.bookmarks = data.bookmarks;
        localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(AppState.bookmarks));
      }
      renderAllCatalogViews();
      refreshContinueBanners();
      updateBookmarkBadge();
      showCulturalNoteDialog('Progresso Restaurado!', 'Seus pontos de leitura da Light Novel e Web Novel, preferências e marcações foram importados com sucesso.');
    } catch (e) {
      showCulturalNoteDialog('Arquivo Inválido', 'Não foi possível ler o arquivo JSON selecionado.');
    }
  };
  reader.readAsText(file);
}

// ==========================================================================
// EVENT DELEGATION CENTRALIZADA (ZERO INLINE ONCLICK)
// ==========================================================================

function bindGlobalEvents() {
  // Abas principais
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  document.getElementById('logo-home-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    switchTab('light-novel');
  });

  // Abrir diálogos principais
  const settingsDialog = document.getElementById('settings-dialog');
  document.getElementById('btn-open-settings')?.addEventListener('click', () => settingsDialog?.showModal());
  document.getElementById('btn-reader-settings')?.addEventListener('click', () => settingsDialog?.showModal());

  const spoilerDialog = document.getElementById('spoiler-dialog');
  document.getElementById('btn-open-spoiler-modal')?.addEventListener('click', () => spoilerDialog?.showModal());
  spoilerDialog?.addEventListener('close', () => {
    try {
      if (!localStorage.getItem(STORAGE_KEYS.SPOILER_ONBOARDED)) {
        localStorage.setItem(STORAGE_KEYS.SPOILER_ONBOARDED, '1');
        saveSettingsToStorage();
      }
    } catch (_) {}
  });
  document.querySelectorAll('[data-choose-spoiler]').forEach(btn => {
    btn.addEventListener('click', () => {
      setSpoilerMode(btn.dataset.chooseSpoiler);
      spoilerDialog?.close();
    });
  });
  document.getElementById('btn-onboarding-open-recap')?.addEventListener('click', () => {
    setSpoilerMode('post_anime');
    spoilerDialog?.close();
    switchTab('recap');
  });

  document.getElementById('btn-open-bookmarks')?.addEventListener('click', () => openBookmarksModal(null));
  document.getElementById('btn-reader-bookmarks')?.addEventListener('click', () => openBookmarksModal(null));

  document.getElementById('btn-reader-back')?.addEventListener('click', closeReader);
  document.getElementById('btn-reader-gallery')?.addEventListener('click', (e) => {
    openVolumeGalleryModal(e.currentTarget.dataset.vol);
  });

  // Botão rápido na barra do leitor para alternar entre Light Novel <-> Web Novel
  document.getElementById('btn-reader-switch-track')?.addEventListener('click', () => {
    const curType = AppState.currentReading.type;
    if (!curType) return;

    clearTimeout(AppState.restoreTimer);
    AppState.isRestoringScroll = false;
    persistReadingProgress({ force: true, inReader: true });

    if (curType === 'light_novel') {
      const wnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_WN);
      if (wnSave && wnSave.id) {
        resumeSavedRecord(wnSave);
      } else {
        switchTab('web-novel');
      }
    } else {
      const lnSave = getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LN);
      if (lnSave && lnSave.id) {
        resumeSavedRecord(lnSave);
      } else {
        switchTab('light-novel');
      }
    }
  });

  // Banner Continuar Leitura
  document.getElementById('btn-resume-main')?.addEventListener('click', () => {
    resumeSavedRecord(getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LAST));
  });
  document.getElementById('btn-resume-other-track')?.addEventListener('click', (e) => {
    const t = e.currentTarget.dataset.targetTrack;
    resumeSavedRecord(getSavedTrackProgress(t === 'light_novel' ? STORAGE_KEYS.PROGRESS_LN : STORAGE_KEYS.PROGRESS_WN));
  });
  document.getElementById('btn-dismiss-banner')?.addEventListener('click', () => {
    document.getElementById('continue-banner').hidden = true;
  });

  // Busca instantânea
  const searchInput = document.getElementById('catalog-search-input');
  const clearBtn = document.getElementById('btn-clear-search');
  searchInput?.addEventListener('input', () => {
    AppState.searchQuery = searchInput.value.trim().toLowerCase();
    if (clearBtn) clearBtn.hidden = !AppState.searchQuery;
    renderAllCatalogViews();
  });
  clearBtn?.addEventListener('click', () => {
    if (!searchInput) return;
    searchInput.value = '';
    AppState.searchQuery = '';
    clearBtn.hidden = true;
    renderAllCatalogViews();
    searchInput.focus();
  });

  // Expandir / Recolher Arcos da Web Novel
  document.getElementById('btn-expand-all-arcs')?.addEventListener('click', () => {
    document.querySelectorAll('#wn-arcs-container details').forEach(d => { d.open = true; });
  });
  document.getElementById('btn-collapse-all-arcs')?.addEventListener('click', () => {
    document.querySelectorAll('#wn-arcs-container details').forEach(d => { d.open = false; });
  });

  // Expandir / Recolher Volumes do Resumo (Até Vol. 11)
  document.getElementById('btn-recap-expand-s3')?.addEventListener('click', () => {
    document.querySelectorAll('#recap-volumes-container details').forEach(d => {
      d.open = d.dataset.postS3 !== 'true';
    });
  });
  document.getElementById('btn-recap-expand-all')?.addEventListener('click', () => {
    document.querySelectorAll('#recap-volumes-container details').forEach(d => { d.open = true; });
    const pDet = document.getElementById('recap-phases-details');
    const wDet = document.getElementById('recap-world-details');
    if (pDet) pDet.open = true;
    if (wDet) wDet.open = true;
  });
  document.getElementById('btn-recap-collapse-all')?.addEventListener('click', () => {
    document.querySelectorAll('#recap-volumes-container details').forEach(d => { d.open = false; });
  });

  // Alternar Público do Guia/Resumo (Iniciante vs Pós-Anime)
  function setRecapAudience(audience) {
    const isBeginner = audience === 'beginner';
    const btnBeg = document.getElementById('btn-recap-audience-beginner');
    const btnAni = document.getElementById('btn-recap-audience-anime');
    const panelBeg = document.getElementById('recap-panel-beginner');
    const panelAni = document.getElementById('recap-panel-anime');

    if (btnBeg) {
      btnBeg.classList.toggle('active', isBeginner);
      btnBeg.setAttribute('aria-selected', isBeginner ? 'true' : 'false');
    }
    if (btnAni) {
      btnAni.classList.toggle('active', !isBeginner);
      btnAni.setAttribute('aria-selected', !isBeginner ? 'true' : 'false');
    }
    if (panelBeg) {
      panelBeg.classList.toggle('active', isBeginner);
      panelBeg.hidden = !isBeginner;
    }
    if (panelAni) {
      panelAni.classList.toggle('active', !isBeginner);
      panelAni.hidden = isBeginner;
    }
    try {
      localStorage.setItem('slime_recap_audience', audience);
    } catch (_) {}
  }

  document.getElementById('btn-recap-audience-beginner')?.addEventListener('click', () => {
    setRecapAudience('beginner');
  });
  document.getElementById('btn-recap-audience-anime')?.addEventListener('click', () => {
    setRecapAudience('anime');
  });

  // Inicializar audiência salva ou padrão (beginner)
  try {
    const savedAudience = localStorage.getItem('slime_recap_audience') || 'beginner';
    setRecapAudience(savedAudience);
  } catch (_) {
    setRecapAudience('beginner');
  }

  // Alternar Modo de Spoiler da Linha de Progressão (Sem Spoilers vs Resumo em 2 Linhas)
  function setProgressionSpoilerMode(mode) {
    const isTwoLines = mode === 'two-lines';
    const btnFree = document.getElementById('btn-progression-spoiler-free');
    const btnTwo = document.getElementById('btn-progression-spoiler-two-lines');
    const progGrid = document.getElementById('progression-timeline-grid');
    const section = document.querySelector('.progression-timeline-section');

    if (btnFree) {
      btnFree.classList.toggle('active', !isTwoLines);
      btnFree.setAttribute('aria-checked', !isTwoLines ? 'true' : 'false');
    }
    if (btnTwo) {
      btnTwo.classList.toggle('active', isTwoLines);
      btnTwo.setAttribute('aria-checked', isTwoLines ? 'true' : 'false');
    }
    if (progGrid) {
      progGrid.classList.toggle('mode-spoiler-free', !isTwoLines);
      progGrid.classList.toggle('mode-with-spoilers', isTwoLines);
    }
    if (section) {
      section.classList.toggle('has-spoilers-active', isTwoLines);
    }
    try {
      localStorage.setItem('slime_progression_spoiler_mode', mode);
    } catch (_) {}
  }

  document.getElementById('btn-progression-spoiler-free')?.addEventListener('click', () => {
    setProgressionSpoilerMode('free');
  });
  document.getElementById('btn-progression-spoiler-two-lines')?.addEventListener('click', () => {
    setProgressionSpoilerMode('two-lines');
  });

  // Inicializar modo de progressão salvo ou padrão (free)
  try {
    const savedProgMode = localStorage.getItem('slime_progression_spoiler_mode') || 'free';
    setProgressionSpoilerMode(savedProgMode);
  } catch (_) {
    setProgressionSpoilerMode('free');
  }

  // Seletor de capítulo na barra do leitor
  document.getElementById('reader-chapter-select')?.addEventListener('change', (e) => {
    const val = e.target.value;
    if (AppState.currentReading.type === 'light_novel') {
      openLightNovel(AppState.currentReading.id, Number(val), 0);
    } else if (AppState.currentReading.type === 'web_novel') {
      openWebNovelChapter(val, 0);
    }
  });

  // Controles de Configurações
  document.querySelectorAll('.btn-theme-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      AppState.settings.palette = btn.dataset.palette;
      saveSettingsToStorage();
      applySettingsToDOM();
    });
  });
  document.querySelectorAll('.btn-font-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      AppState.settings.font = btn.dataset.font;
      saveSettingsToStorage();
      applySettingsToDOM();
    });
  });
  document.querySelectorAll('.btn-width-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      AppState.settings.maxWidth = Number(btn.dataset.width);
      saveSettingsToStorage();
      applySettingsToDOM();
    });
  });
  document.querySelectorAll('.btn-spoiler-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      setSpoilerMode(btn.dataset.spoiler);
    });
  });
  document.getElementById('btn-font-dec')?.addEventListener('click', () => {
    AppState.settings.fontSize = Math.max(14, AppState.settings.fontSize - 1);
    saveSettingsToStorage();
    applySettingsToDOM();
  });
  document.getElementById('btn-font-inc')?.addEventListener('click', () => {
    AppState.settings.fontSize = Math.min(28, AppState.settings.fontSize + 1);
    saveSettingsToStorage();
    applySettingsToDOM();
  });
  document.getElementById('chk-auto-resume')?.addEventListener('change', (e) => {
    AppState.settings.autoResumeOnOpen = e.target.checked;
    saveSettingsToStorage();
  });
  document.getElementById('chk-cultural-hints')?.addEventListener('change', (e) => {
    AppState.settings.culturalHints = e.target.checked;
    saveSettingsToStorage();
    if (AppState.currentReading.type) {
      const savedSpot = findExactReadingAnchor();
      AppState.currentReading.scrollRatio = savedSpot.scrollRatio;
      AppState.currentReading.pIndex = savedSpot.pIndex;
      AppState.currentReading.pOffsetPx = savedSpot.pOffsetPx;
      renderReaderScreen();
    }
  });

  // Exportar / Importar JSON
  document.getElementById('btn-export-progress')?.addEventListener('click', exportUserProgressJson);
  document.getElementById('input-import-progress')?.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      importUserProgressJson(e.target.files[0]);
      e.target.value = '';
    }
  });

  // Lightbox Anterior / Próxima
  document.getElementById('btn-lightbox-prev')?.addEventListener('click', () => {
    openLightboxAtIndex(AppState.lightbox.index - 1);
  });
  document.getElementById('btn-lightbox-next')?.addEventListener('click', () => {
    openLightboxAtIndex(AppState.lightbox.index + 1);
  });

  // Botão opcional para guardar marcação extra no ponto atual da página
  document.getElementById('btn-pin-current-spot')?.addEventListener('click', () => {
    const cur = AppState.currentReading;
    if (!cur.type) return;
    const anchor = findExactReadingAnchor();
    const pEl = document.getElementById(`p-${anchor.pIndex}`);
    const snippet = pEl ? pEl.textContent.trim().slice(0, 160) : `Posição ${Math.round(anchor.scrollRatio * 100)}% do capítulo`;
    const lbl = cur.type === 'light_novel'
      ? `${cur.data.title} — ${cur.data.chapters[cur.chapterIndex]?.title || ''}`
      : `${cur.data.display_num || ''}: ${cur.data.title}`;

    openBookmarksModal({
      type: cur.type,
      readingId: cur.id,
      chapterIndex: cur.chapterIndex,
      pIndex: anchor.pIndex,
      pOffsetPx: anchor.pOffsetPx,
      scrollRatio: anchor.scrollRatio,
      label: lbl,
      snippet
    });
  });

  // Formulário de Marcação Extra
  document.getElementById('btn-cancel-bm-form')?.addEventListener('click', () => {
    AppState.pendingBookmark = null;
    document.getElementById('bookmark-add-form').hidden = true;
    const pinBar = document.getElementById('manual-pin-bar');
    if (pinBar) pinBar.hidden = !AppState.currentReading.type;
  });
  document.getElementById('bookmark-add-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const ctx = AppState.pendingBookmark;
    if (!ctx) return;
    const note = document.getElementById('bookmark-note-input')?.value.trim() || '';

    AppState.bookmarks.push({
      id: Date.now(),
      type: ctx.type,
      readingId: ctx.readingId,
      chapterIndex: ctx.chapterIndex,
      pIndex: ctx.pIndex,
      pOffsetPx: ctx.pOffsetPx,
      scrollRatio: ctx.scrollRatio || 0,
      label: ctx.label,
      textSnippet: ctx.snippet,
      note,
      date: new Date().toLocaleDateString('pt-BR')
    });
    localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(AppState.bookmarks));

    const pEl = document.getElementById(`p-${ctx.pIndex}`);
    if (pEl) pEl.classList.add('bookmarked');

    AppState.pendingBookmark = null;
    document.getElementById('bookmark-add-form').hidden = true;
    const pinBar = document.getElementById('manual-pin-bar');
    if (pinBar) pinBar.hidden = !AppState.currentReading.type;
    updateBookmarkBadge();
    renderBookmarksListInsideDialog();
  });

  // Event Delegation Geral para cliques em elementos renderizados dinamicamente
  document.addEventListener('click', (e) => {
    const target = e.target.closest('[data-action]');
    if (!target) return;
    const action = target.dataset.action;

    if (action === 'open-ln') {
      openLightNovel(target.dataset.vol, null, null);
    } else if (action === 'open-wn') {
      openWebNovelChapter(target.dataset.chid, null);
    } else if (action === 'open-gallery') {
      openVolumeGalleryModal(target.dataset.vol);
    } else if (action === 'open-gallery-current') {
      openVolumeGalleryModal(AppState.currentReading.baseVolumeId);
    } else if (action === 'open-lightbox-idx') {
      openLightboxAtIndex(Number(target.dataset.idx) || 0);
    } else if (action === 'zoom-inline-img') {
      openLightboxAtIndex(Number(target.dataset.imgidx) || 0);
    } else if (action === 'switch-edition') {
      const targetVolId = target.dataset.vol;
      if (targetVolId && targetVolId !== AppState.currentReading.id) {
        const curChTitle = AppState.currentReading.data?.chapters?.[AppState.currentReading.chapterIndex]?.title || '';
        openLightNovel(targetVolId, AppState.currentReading.chapterIndex, { scrollRatio: getScrollRatio(), useRatioOnly: true }, curChTitle);
      }
    } else if (action === 'show-fn') {
      const fnNum = target.dataset.fn;
      const curData = AppState.currentReading.data;
      const curCh = curData?.chapters?.[AppState.currentReading.chapterIndex];
      const fnTxt = curCh?.footnotes?.[fnNum] || curData?.footnotes?.[fnNum];
      if (fnTxt) {
        const isLore = fnTxt.toLowerCase().includes('lore') || fnTxt.toLowerCase().includes('continuidade') || fnTxt.toLowerCase().includes('web novel');
        const heading = isLore ? `🧭 Nota de Lore & Continuidade [${fnNum}]` : `📖 Nota Cultural / Tradução [${fnNum}]`;
        showCulturalNoteDialog(heading, fnTxt);
      }
    } else if (action === 'show-term') {
      const term = target.dataset.term;
      const gl = AppState.catalog?.cultural_guide?.inline_glossary?.[term];
      if (gl) {
        const cleanName = term.startsWith('-') ? term.slice(1) : term;
        const formattedTitle = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
        showCulturalNoteDialog(`💡 Guia de Tensura: ${formattedTitle}`, gl);
      }
    } else if (action === 'jump-bm') {
      const bm = AppState.bookmarks.find(b => String(b.id) === String(target.dataset.bmid));
      if (!bm) return;
      document.getElementById('bookmarks-dialog')?.close();
      const bmAnchor = {
        scrollRatio: bm.scrollRatio || 0,
        pIndex: typeof bm.pIndex === 'number' ? bm.pIndex : 0,
        pOffsetPx: typeof bm.pOffsetPx === 'number' ? bm.pOffsetPx : 110
      };
      if (bm.type === 'light_novel') {
        openLightNovel(bm.readingId, bm.chapterIndex || 0, bmAnchor);
      } else {
        openWebNovelChapter(bm.readingId, bmAnchor);
      }
    } else if (action === 'del-bm') {
      AppState.bookmarks = AppState.bookmarks.filter(b => String(b.id) !== String(target.dataset.bmid));
      localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(AppState.bookmarks));
      updateBookmarkBadge();
      renderBookmarksListInsideDialog();
    } else if (action === 'resume-ln') {
      document.getElementById('bookmarks-dialog')?.close();
      resumeSavedRecord(getSavedTrackProgress(STORAGE_KEYS.PROGRESS_LN));
    } else if (action === 'resume-wn') {
      document.getElementById('bookmarks-dialog')?.close();
      resumeSavedRecord(getSavedTrackProgress(STORAGE_KEYS.PROGRESS_WN));
    } else if (action === 'goto-tab-ln') {
      document.getElementById('bookmarks-dialog')?.close();
      switchTab('light-novel');
    } else if (action === 'goto-tab-wn') {
      document.getElementById('bookmarks-dialog')?.close();
      switchTab('web-novel');
    } else if (action === 'goto-tab-recap') {
      switchTab('recap');
    } else if (action === 'reveal-spoiler') {
      const spId = target.dataset.spoilerId;
      if (spId) {
        AppState.revealedSpoilers.add(spId);
        AppState.manuallyHiddenSpoilers?.delete(spId);
        renderAllCatalogViews();
      }
    } else if (action === 'hide-spoiler') {
      const spId = target.dataset.spoilerId;
      if (spId) {
        AppState.revealedSpoilers.delete(spId);
        AppState.manuallyHiddenSpoilers?.add(spId);
        renderAllCatalogViews();
      }
    } else if (action === 'close-reader') {
      closeReader();
    } else if (action === 'ln-prev') {
      const cur = AppState.currentReading;
      if (cur.chapterIndex > 0) {
        openLightNovel(cur.id, cur.chapterIndex - 1, 0);
      } else {
        const vols = AppState.catalog.light_novel.volumes || [];
        const pos = vols.findIndex(v => v.id === cur.baseVolumeId);
        if (pos > 0) openLightNovel(vols[pos - 1].id, 0, 0);
      }
    } else if (action === 'ln-next') {
      const cur = AppState.currentReading;
      if (cur.chapterIndex < cur.data.chapters.length - 1) {
        openLightNovel(cur.id, cur.chapterIndex + 1, 0);
      } else {
        const vols = AppState.catalog.light_novel.volumes || [];
        const pos = vols.findIndex(v => v.id === cur.baseVolumeId);
        if (pos >= 0 && pos < vols.length - 1) openLightNovel(vols[pos + 1].id, 0, 0);
      }
    } else if (action === 'wn-nav') {
      if (target.dataset.chid) openWebNovelChapter(target.dataset.chid, 0);
    }
  });

  // Manter altura da barra suspensa do leitor sincronizada em qualquer tela/quebra de linha
  const readerToolbar = document.querySelector('#reader-view .reader-toolbar');
  if (readerToolbar && typeof ResizeObserver !== 'undefined') {
    const toolbarObserver = new ResizeObserver(() => {
      syncReaderToolbarOffset();
    });
    toolbarObserver.observe(readerToolbar);
  }
  window.addEventListener('resize', syncReaderToolbarOffset, { passive: true });

  // Salvar progresso automaticamente ao parar de rolar (scrollend), minimizar aba ou fechar o navegador
  window.addEventListener('scrollend', () => {
    if (AppState.currentReading.type && !AppState.isRestoringScroll) {
      persistReadingProgress({ inReader: true });
    }
  });

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden' && AppState.currentReading.type) {
      persistReadingProgress({ force: true, inReader: true });
    }
  });

  window.addEventListener('pagehide', () => {
    if (AppState.currentReading.type) {
      persistReadingProgress({ force: true, inReader: true });
    }
  });

  // Sincronizar entre múltiplas abas abertas (storage event)
  window.addEventListener('storage', (e) => {
    if (e.key === STORAGE_KEYS.SETTINGS || e.key === STORAGE_KEYS.COLOR_SCHEME || e.key === STORAGE_KEYS.PALETTE) {
      loadStateFromStorage();
      applySettingsToDOM();
      renderAllCatalogViews();
    } else if (e.key === STORAGE_KEYS.PROGRESS_LAST || e.key === STORAGE_KEYS.HISTORY) {
      loadStateFromStorage();
      refreshContinueBanners();
    }
  });
}

// ==========================================================================
// UTILITÁRIOS DE SEGURANÇA HTML
// ==========================================================================

function escapeHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escapeAttr(str) {
  return escapeHtml(str);
}
