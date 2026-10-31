/**
 * TENSEI SHITARA SLIME DATTA KEN - APLICAÇÃO DE LEITURA & CATÁLOGO
 * Gerenciamento de Estado, Leitor, Progresso (LocalStorage), Temas e Ilustrações
 */

// Estado Global da Aplicação
const AppState = {
  catalog: null,
  currentTab: 'light-novel', // 'light-novel' | 'web-novel' | 'comparison' | 'cultural' | 'amazon'
  currentReading: {
    type: null, // 'light_novel' | 'web_novel'
    id: null, // 'vol-1' ou número do capítulo
    chapterIndex: 0,
    data: null,
    scrollRatio: 0
  },
  settings: {
    theme: 'dark',
    font: 'sans',
    fontSize: 18,
    lineHeight: 1.85,
    maxWidth: 820,
    align: 'left'
  },
  bookmarks: [],
  currentModalGallery: []
};

// Chaves do LocalStorage
const STORAGE_KEYS = {
  PROGRESS: 'tensura_reading_progress',
  SETTINGS: 'tensura_reader_settings',
  BOOKMARKS: 'tensura_bookmarks'
};

// ==========================================================================
// INICIALIZAÇÃO
// ==========================================================================

document.addEventListener('DOMContentLoaded', async () => {
  loadUserSettings();
  applyUserSettings();
  loadBookmarks();
  setupEventListeners();

  try {
    const res = await fetch('data/catalog.json');
    if (!res.ok) throw new Error('Falha ao carregar catálogo.');
    AppState.catalog = await res.json();
    
    renderAllViews();
    checkContinueReading();
    handleHashNavigation();
  } catch (err) {
    console.error('Erro na inicialização:', err);
    document.getElementById('content-area').innerHTML = `
      <div style="text-align: center; padding: 4rem 1rem;">
        <h2 style="color: #ef4444; margin-bottom: 1rem;">Erro ao Carregar Biblioteca</h2>
        <p style="color: #94a3b8;">Não foi possível carregar os dados de catálogo. Verifique se o arquivo data/catalog.json existe.</p>
      </div>
    `;
  }
});

// ==========================================================================
// CONFIGURAÇÕES DO USUÁRIO & LOCALSTORAGE
// ==========================================================================

function loadUserSettings() {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    if (saved) {
      AppState.settings = { ...AppState.settings, ...JSON.parse(saved) };
    }
  } catch (e) {
    console.warn('Erro ao ler configurações do localStorage:', e);
  }
}

function saveUserSettings() {
  try {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(AppState.settings));
  } catch (e) {
    console.warn('Erro ao salvar configurações:', e);
  }
}

function applyUserSettings() {
  const root = document.documentElement;
  root.setAttribute('data-theme', AppState.settings.theme);
  root.setAttribute('data-font', AppState.settings.font);
  root.style.setProperty('--reader-size', `${AppState.settings.fontSize}px`);
  root.style.setProperty('--reader-line-height', AppState.settings.lineHeight);
  root.style.setProperty('--reader-max-width', `${AppState.settings.maxWidth}px`);
  root.style.setProperty('--reader-align', AppState.settings.align);

  // Atualizar visual dos botões de configuração
  document.querySelectorAll('.btn-theme-opt').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === AppState.settings.theme);
  });
  document.querySelectorAll('.btn-font-opt').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.font === AppState.settings.font);
  });
  const sizeDisplay = document.getElementById('font-size-val');
  if (sizeDisplay) sizeDisplay.textContent = `${AppState.settings.fontSize}px`;
}

// ==========================================================================
// SALVAMENTO DE PROGRESSO AUTOMÁTICO (CONTINUAR LEITURA)
// ==========================================================================

function saveReadingProgress(scrollRatio = null) {
  if (!AppState.currentReading.type || !AppState.currentReading.id) return;

  const currentScroll = scrollRatio !== null ? scrollRatio : getScrollRatio();
  
  let title = '';
  if (AppState.currentReading.type === 'light_novel' && AppState.currentReading.data) {
    const ch = AppState.currentReading.data.chapters[AppState.currentReading.chapterIndex];
    title = `${AppState.currentReading.data.title} - ${ch ? ch.title : 'Capítulo'}`;
  } else if (AppState.currentReading.type === 'web_novel' && AppState.currentReading.data) {
    title = `Web Novel - ${AppState.currentReading.data.title}`;
  }

  const progress = {
    type: AppState.currentReading.type,
    id: AppState.currentReading.id,
    chapterIndex: AppState.currentReading.chapterIndex,
    scrollRatio: Math.min(Math.max(currentScroll, 0), 1),
    title: title,
    timestamp: Date.now()
  };

  try {
    localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify(progress));
    updateContinueBanner(progress);
  } catch (e) {
    console.warn('Erro ao salvar progresso:', e);
  }
}

function getScrollRatio() {
  const h = document.documentElement;
  const b = document.body;
  const st = 'scrollTop' in h ? h.scrollTop : b.scrollTop;
  const sh = 'scrollHeight' in h ? h.scrollHeight : b.scrollHeight;
  const ch = h.clientHeight;
  const maxScroll = sh - ch;
  return maxScroll > 0 ? st / maxScroll : 0;
}

function checkContinueReading() {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.PROGRESS);
    if (saved) {
      const progress = JSON.parse(saved);
      if (progress && progress.title) {
        updateContinueBanner(progress);
        const banner = document.getElementById('continue-banner');
        if (banner) banner.style.display = 'block';
      }
    }
  } catch (e) {
    console.warn(e);
  }
}

function updateContinueBanner(progress) {
  const banner = document.getElementById('continue-banner');
  const titleEl = document.getElementById('continue-title');
  const percentEl = document.getElementById('continue-percent');
  if (!banner || !titleEl) return;

  const pct = Math.round((progress.scrollRatio || 0) * 100);
  titleEl.textContent = progress.title || 'Última Leitura';
  if (percentEl) percentEl.textContent = `${pct}% concluído`;
  banner.style.display = 'block';
}

function resumeReading() {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.PROGRESS);
    if (!saved) return;
    const progress = JSON.parse(saved);

    if (progress.type === 'light_novel') {
      openLightNovel(progress.id, progress.chapterIndex, progress.scrollRatio);
    } else if (progress.type === 'web_novel') {
      openWebNovelChapter(progress.id, progress.scrollRatio);
    }
  } catch (e) {
    console.error('Erro ao restaurar leitura:', e);
  }
}

// ==========================================================================
// RENDERIZAÇÃO DAS TELAS PRINCIPAIS
// ==========================================================================

function renderAllViews() {
  renderLightNovelView();
  renderWebNovelView();
  renderComparisonView();
  renderCulturalView();
  renderAmazonView();
}

// 1. Light Novel (Volumes com ilustrações e capítulos)
function renderLightNovelView() {
  const container = document.getElementById('ln-volumes-grid');
  if (!container || !AppState.catalog) return;

  const volumes = AppState.catalog.light_novel.volumes || [];
  container.innerHTML = volumes.map(vol => {
    const hasIllus = vol.illustrations_count > 0;
    const illusBadge = hasIllus ? `<span style="background: rgba(245,158,11,0.15); color: #f59e0b; padding: 0.2rem 0.5rem; border-radius: 9999px; font-size: 0.72rem; font-weight: 700;">🖼️ ${vol.illustrations_count} Ilustrações</span>` : '';
    
    return `
      <article class="volume-card">
        <div>
          <div class="volume-badge">
            <span class="badge-num">Volume ${vol.volume_number}</span>
            <span class="badge-status">Pronto para Ler</span>
          </div>
          <h3>${vol.title}</h3>
          <div class="volume-kanji">${vol.kanji || ''}</div>
          <p class="volume-desc">${vol.desc}</p>
        </div>
        <div>
          <div class="volume-meta">
            <span>📖 ${vol.chapter_count} Seções (${vol.paragraph_count.toLocaleString()} §)</span>
            ${illusBadge}
          </div>
          <div class="volume-actions">
            <button class="btn-read" onclick="openLightNovel('${vol.id}', 0)">
              <span>Ler Agora</span> →
            </button>
            <a href="https://www.amazon.com.br/s?k=That+Time+I+Got+Reincarnated+as+a+Slime+Vol+${vol.volume_number}+light+novel" target="_blank" rel="noopener" class="btn-amazon-quick" title="Ver ou comprar edição oficial na Amazon Brasil">
              🛒 Amazon
            </a>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

// 2. Web Novel (Arcos e 255 Capítulos)
function renderWebNovelView() {
  const container = document.getElementById('wn-arcs-container');
  if (!container || !AppState.catalog) return;

  const arcs = AppState.catalog.web_novel.arcs || [];
  const chapters = AppState.catalog.web_novel.chapters || [];

  container.innerHTML = arcs.map((arc, idx) => {
    const arcChapters = chapters.filter(c => c.arc_id === arc.id);
    const isOpen = idx === 0 ? 'open' : '';

    const chaptersHtml = arcChapters.map(ch => {
      const isDownloaded = ch.is_downloaded;
      const statusIcon = isDownloaded ? `<span class="ch-status-dot" title="Texto completo baixado e disponível para leitura offline"></span>` : `<span style="font-size: 0.7rem; color: #94a3b8;">🌐 Online</span>`;
      
      return `
        <button class="chapter-item-btn" onclick="openWebNovelChapter(${ch.num})">
          <div class="ch-info">
            <span class="ch-num">Capítulo ${ch.num}</span>
            <span class="ch-title" title="${ch.title}">${ch.title}</span>
          </div>
          ${statusIcon}
        </button>
      `;
    }).join('');

    return `
      <div class="arc-container ${isOpen}" id="arc-card-${arc.id}">
        <div class="arc-header" onclick="toggleArc('${arc.id}')">
          <div class="arc-title-area">
            <h3>${arc.title}</h3>
            <p>${arc.desc} (${arcChapters.length} capítulos)</p>
          </div>
          <span class="arc-toggle-icon">▼</span>
        </div>
        <div class="chapter-list">
          ${chaptersHtml}
        </div>
      </div>
    `;
  }).join('');
}

function toggleArc(arcId) {
  const el = document.getElementById(`arc-card-${arcId}`);
  if (el) el.classList.toggle('open');
}

// 3. Comparador WN vs LN
function renderComparisonView() {
  const overviewEl = document.getElementById('comparison-overview-text');
  const gridEl = document.getElementById('comparison-diffs-list');
  if (!AppState.catalog) return;

  const comp = AppState.catalog.comparison;
  if (overviewEl) overviewEl.textContent = comp.overview;

  if (gridEl) {
    gridEl.innerHTML = comp.key_differences.map(diff => `
      <div class="comparison-card">
        <h3>⚖️ ${diff.topic}</h3>
        <div class="comparison-grid">
          <div class="comparison-column col-wn">
            <div class="col-header">📜 Web Novel (Original da Internet)</div>
            <div class="col-body">${diff.wn}</div>
          </div>
          <div class="comparison-column col-ln">
            <div class="col-header">📘 Light Novel (Oficial & Revisada)</div>
            <div class="col-body">${diff.ln}</div>
          </div>
        </div>
      </div>
    `).join('');
  }
}

// 4. Guia Cultural & Termos Japoneses
function renderCulturalView() {
  if (!AppState.catalog) return;
  const guide = AppState.catalog.cultural_guide;
  if (!guide) return;

  const honEl = document.getElementById('cultural-honorifics-list');
  const conEl = document.getElementById('cultural-concepts-list');
  const aspEl = document.getElementById('cultural-aspects-list');

  if (honEl) {
    honEl.innerHTML = guide.honorifics.map(h => `
      <div class="term-card">
        <div class="term-name">${h.term}</div>
        <div class="term-desc">${h.meaning}</div>
      </div>
    `).join('');
  }

  if (conEl) {
    conEl.innerHTML = guide.tensura_concepts.map(c => `
      <div class="term-card">
        <div class="term-name">${c.term}</div>
        <div class="term-desc">${c.desc}</div>
      </div>
    `).join('');
  }

  if (aspEl) {
    aspEl.innerHTML = guide.cultural_aspects.map(a => `
      <div class="term-card">
        <div class="term-name">${a.element}</div>
        <div class="term-desc">${a.desc}</div>
      </div>
    `).join('');
  }
}

// 5. Loja Oficial Amazon Brasil
function renderAmazonView() {
  const gridEl = document.getElementById('amazon-volumes-grid');
  if (!gridEl || !AppState.catalog) return;

  const items = AppState.catalog.amazon_br.volumes || [];
  gridEl.innerHTML = items.map(item => `
    <div class="amazon-card">
      <div>
        <span style="font-size: 0.72rem; font-weight: 800; color: #f59e0b; text-transform: uppercase;">Volume ${item.volume}</span>
        <h4>${item.title}</h4>
        <div class="amazon-formats">Formatos: ${item.formats.join(' • ')}</div>
      </div>
      <a href="${item.search_url}" target="_blank" rel="noopener" class="btn-amazon-buy">
        🛒 Comprar na Amazon.com.br
      </a>
    </div>
  `).join('');
}

// ==========================================================================
// MECANISMO DE LEITURA (READER ENGINE)
// ==========================================================================

async function openLightNovel(volumeId, chapterIndex = 0, initialScrollRatio = 0) {
  try {
    showLoading();
    const res = await fetch(`data/light_novel/${volumeId}.json`);
    if (!res.ok) throw new Error(`Arquivo data/light_novel/${volumeId}.json não encontrado.`);
    const data = await res.json();

    AppState.currentReading = {
      type: 'light_novel',
      id: volumeId,
      chapterIndex: chapterIndex,
      data: data,
      scrollRatio: initialScrollRatio
    };

    renderReaderContent();
    window.location.hash = `#ln-${volumeId}-${chapterIndex}`;
    saveReadingProgress(initialScrollRatio);
  } catch (err) {
    console.error('Erro ao abrir volume da Light Novel:', err);
    alert(`Não foi possível carregar este volume: ${err.message}`);
  } finally {
    hideLoading();
  }
}

async function openWebNovelChapter(chapterNum, initialScrollRatio = 0) {
  try {
    showLoading();
    const padNum = String(chapterNum).padStart(3, '0');
    const res = await fetch(`data/web_novel/capitulo_${padNum}.json`);
    
    let data;
    if (res.ok) {
      data = await res.json();
    } else {
      // Se ainda não foi baixado localmente, redireciona ou oferece link
      const chMeta = AppState.catalog.web_novel.chapters.find(c => c.num === chapterNum);
      const url = chMeta ? chMeta.url : `https://centralnovel.com/tensei-shitara-slime-datta-ken-capitulo-${chapterNum}/`;
      
      const confirmOpen = confirm(`O Capítulo ${chapterNum} ainda não foi baixado para leitura offline local.\n\nDeseja abrir a leitura online oficial no Central Novel?`);
      if (confirmOpen) {
        window.open(url, '_blank');
      }
      hideLoading();
      return;
    }

    AppState.currentReading = {
      type: 'web_novel',
      id: chapterNum,
      chapterIndex: 0,
      data: data,
      scrollRatio: initialScrollRatio
    };

    renderReaderContent();
    window.location.hash = `#wn-${chapterNum}`;
    saveReadingProgress(initialScrollRatio);
  } catch (err) {
    console.error('Erro ao abrir capítulo da Web Novel:', err);
    alert(`Erro ao abrir capítulo: ${err.message}`);
  } finally {
    hideLoading();
  }
}

function renderReaderContent() {
  const readerView = document.getElementById('reader-view');
  const mainContent = document.getElementById('content-area');
  const container = document.getElementById('reader-text-container');
  const headerInfo = document.getElementById('reader-header-area');
  const footerNav = document.getElementById('reader-footer-nav');
  const currentTitleNav = document.getElementById('reader-toolbar-title');

  if (!readerView || !container) return;

  // Trocar visualização
  mainContent.style.display = 'none';
  readerView.style.display = 'block';
  window.scrollTo(0, 0);

  let paragraphs = [];
  let headingTitle = '';
  let subHeading = '';
  let metaInfo = '';
  let volMeta = null;

  if (AppState.currentReading.type === 'light_novel') {
    const vol = AppState.currentReading.data;
    const ch = vol.chapters[AppState.currentReading.chapterIndex];
    if (!ch) return;

    headingTitle = ch.title;
    subHeading = vol.title;
    paragraphs = ch.paragraphs || [];
    volMeta = AppState.catalog.light_novel.volumes.find(v => v.id === vol.id);
    
    metaInfo = `Capítulo ${AppState.currentReading.chapterIndex + 1} de ${vol.chapters.length} • ${paragraphs.length} parágrafos • Tempo estimado: ~${Math.ceil(paragraphs.length / 8)} min`;
    currentTitleNav.textContent = `${vol.title} - ${ch.title}`;
  } else {
    const ch = AppState.currentReading.data;
    headingTitle = ch.title;
    subHeading = 'Tensei Shitara Slime Datta Ken (Web Novel)';
    paragraphs = ch.paragraphs || [];
    metaInfo = `Capítulo ${ch.number} • ${paragraphs.length} parágrafos • Central Novel PT-BR`;
    currentTitleNav.textContent = `Web Novel - Cap. ${ch.number}: ${ch.title}`;
  }

  // Ilustrações disponíveis?
  let illusBtn = '';
  if (volMeta && volMeta.illustrations && volMeta.illustrations.length > 0) {
    illusBtn = `
      <button onclick="openIllustrationsModal('${volMeta.id}')" style="margin-top: 1rem; background: linear-gradient(135deg, #f59e0b, #d97706); color: #000; font-weight: 700; border: none; padding: 0.5rem 1rem; border-radius: 9999px; cursor: pointer; display: inline-flex; align-items: center; gap: 0.4rem; box-shadow: 0 2px 6px rgba(245, 158, 11, 0.4);">
        🖼️ Ver Ilustrações Oficiais deste Volume (${volMeta.illustrations.length})
      </button>
    `;
  }

  // Header do Leitor
  headerInfo.innerHTML = `
    <div class="vol-title">${subHeading}</div>
    <h1 class="ch-main-heading">${headingTitle}</h1>
    <div class="ch-meta-row">${metaInfo}</div>
    ${illusBtn}
  `;

  // Renderizar Parágrafos com identificadores para clique e bookmark
  container.innerHTML = paragraphs.map((p, idx) => {
    return `<p class="novel-paragraph" id="p-${idx}" onclick="handleParagraphClick(${idx})">${escapeHtml(p)}</p>`;
  }).join('');

  // Renderizar Botões de Navegação (Anterior / Próximo)
  renderFooterNav(footerNav);

  // Restaurar Scroll Salvo (se houver)
  if (AppState.currentReading.scrollRatio > 0) {
    setTimeout(() => {
      const sh = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      if (sh > 0) {
        window.scrollTo({
          top: sh * AppState.currentReading.scrollRatio,
          behavior: 'smooth'
        });
      }
    }, 150);
  }
}

function renderFooterNav(container) {
  if (!container) return;
  const isLN = AppState.currentReading.type === 'light_novel';
  
  let hasPrev = false;
  let hasNext = false;
  let prevAction = '';
  let nextAction = '';

  if (isLN) {
    const vol = AppState.currentReading.data;
    const curIdx = AppState.currentReading.chapterIndex;
    hasPrev = curIdx > 0;
    hasNext = curIdx < vol.chapters.length - 1;
    prevAction = `openLightNovel('${vol.id}', ${curIdx - 1})`;
    nextAction = `openLightNovel('${vol.id}', ${curIdx + 1})`;
  } else {
    const curNum = AppState.currentReading.data.number;
    hasPrev = curNum > 0;
    hasNext = curNum < 249;
    prevAction = `openWebNovelChapter(${curNum - 1})`;
    nextAction = `openWebNovelChapter(${curNum + 1})`;
  }

  container.innerHTML = `
    <button class="btn-nav-ch" ${hasPrev ? `onclick="${prevAction}"` : 'disabled'}>
      ← Capítulo Anterior
    </button>
    <button class="btn-nav-ch" onclick="closeReader()">
      📚 Voltar ao Índice
    </button>
    <button class="btn-nav-ch" ${hasNext ? `onclick="${nextAction}"` : 'disabled'}>
      Próximo Capítulo →
    </button>
  `;
}

function closeReader() {
  saveReadingProgress();
  const readerView = document.getElementById('reader-view');
  const mainContent = document.getElementById('content-area');
  if (readerView) readerView.style.display = 'none';
  if (mainContent) mainContent.style.display = 'block';
  window.location.hash = AppState.currentTab;
  checkContinueReading();
}

// ==========================================================================
// ROLAGEM, PROGRESSO E MARCADORES
// ==========================================================================

let scrollTimeout = null;
window.addEventListener('scroll', () => {
  const progressBar = document.getElementById('reading-progress-bar');
  const ratio = getScrollRatio();

  if (progressBar) {
    progressBar.style.width = `${Math.min(ratio * 100, 100)}%`;
  }

  // Debounce para não sobrecarregar o localStorage
  if (AppState.currentReading.type) {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      saveReadingProgress(ratio);
    }, 400);
  }
});

function handleParagraphClick(pIndex) {
  const pEl = document.getElementById(`p-${pIndex}`);
  if (!pEl) return;

  const note = prompt('Adicionar anotação ou marcador neste parágrafo:\n\n' + pEl.textContent.slice(0, 100) + '...', '');
  if (note !== null) {
    const bm = {
      id: Date.now(),
      type: AppState.currentReading.type,
      readingId: AppState.currentReading.id,
      chapterIndex: AppState.currentReading.chapterIndex,
      pIndex: pIndex,
      textSnippet: pEl.textContent.slice(0, 120),
      note: note.trim(),
      date: new Date().toLocaleDateString('pt-BR')
    };
    AppState.bookmarks.push(bm);
    saveBookmarks();
    pEl.classList.add('bookmarked');
    alert('Marcador salvo com sucesso!');
  }
}

function loadBookmarks() {
  try {
    const b = localStorage.getItem(STORAGE_KEYS.BOOKMARKS);
    if (b) AppState.bookmarks = JSON.parse(b);
  } catch (e) {
    console.warn(e);
  }
}

function saveBookmarks() {
  try {
    localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(AppState.bookmarks));
  } catch (e) {
    console.warn(e);
  }
}

// ==========================================================================
// MODAL DE ILUSTRAÇÕES (MITZ VAH ART GALLERY)
// ==========================================================================

function openIllustrationsModal(volumeId) {
  const vol = AppState.catalog.light_novel.volumes.find(v => v.id === volumeId);
  if (!vol || !vol.illustrations || vol.illustrations.length === 0) {
    alert('Nenhuma ilustração disponível para este volume.');
    return;
  }

  AppState.currentModalGallery = vol.illustrations;
  const modal = document.getElementById('illustrations-modal');
  const title = document.getElementById('illus-modal-title');
  const grid = document.getElementById('illus-modal-grid');

  if (title) title.textContent = `Ilustrações Oficiais - ${vol.title} (Arte: Mitz Vah)`;
  if (grid) {
    grid.innerHTML = vol.illustrations.map((imgUrl, i) => `
      <div style="background: #111827; border-radius: 8px; overflow: hidden; border: 1px solid #374151; display: flex; flex-direction: column;">
        <a href="${imgUrl}" target="_blank" rel="noopener">
          <img src="${imgUrl}" alt="Ilustração oficial ${i + 1}" loading="lazy" style="width: 100%; height: auto; display: block; cursor: zoom-in;" />
        </a>
        <div style="padding: 0.5rem; font-size: 0.75rem; color: #9ca3af; text-align: center;">Ilustração ${i + 1}</div>
      </div>
    `).join('');
  }

  if (modal) modal.style.display = 'flex';
}

function closeIllustrationsModal() {
  const modal = document.getElementById('illustrations-modal');
  if (modal) modal.style.display = 'none';
}

// ==========================================================================
// MODAL DE CONFIGURAÇÕES DO LEITOR
// ==========================================================================

function toggleSettingsModal() {
  const modal = document.getElementById('settings-modal');
  if (modal) modal.classList.toggle('open');
}

function changeTheme(themeName) {
  AppState.settings.theme = themeName;
  saveUserSettings();
  applyUserSettings();
}

function changeFont(fontName) {
  AppState.settings.font = fontName;
  saveUserSettings();
  applyUserSettings();
}

function adjustFontSize(delta) {
  const newSize = Math.min(Math.max(AppState.settings.fontSize + delta, 14), 28);
  AppState.settings.fontSize = newSize;
  saveUserSettings();
  applyUserSettings();
}

// ==========================================================================
// ROTEAMENTO POR ABAS
// ==========================================================================

function switchTab(tabName) {
  AppState.currentTab = tabName;

  // Esconder leitor se estiver ativo
  const readerView = document.getElementById('reader-view');
  const mainContent = document.getElementById('content-area');
  if (readerView) readerView.style.display = 'none';
  if (mainContent) mainContent.style.display = 'block';

  // Atualizar abas visuais
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.tab === tabName);
  });

  // Mostrar seção
  document.querySelectorAll('.view-section').forEach(sec => {
    sec.classList.remove('active');
  });
  const activeSec = document.getElementById(`view-${tabName}`);
  if (activeSec) activeSec.classList.add('active');

  window.location.hash = `#${tabName}`;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function handleHashNavigation() {
  const hash = window.location.hash.replace('#', '');
  if (!hash) return;

  if (['light-novel', 'web-novel', 'comparison', 'cultural', 'amazon'].includes(hash)) {
    switchTab(hash);
  } else if (hash.startsWith('ln-')) {
    const parts = hash.split('-');
    const volId = `vol-${parts[1]}`;
    const chIdx = parts[2] ? parseInt(parts[2]) : 0;
    openLightNovel(volId, chIdx);
  } else if (hash.startsWith('wn-')) {
    const chNum = parseInt(hash.replace('wn-', ''));
    if (!isNaN(chNum)) openWebNovelChapter(chNum);
  }
}

// ==========================================================================
// EVENT LISTENERS GERAIS
// ==========================================================================

function setupEventListeners() {
  // Abas de navegação
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });

  // Fechar modals ao clicar fora
  window.addEventListener('click', (e) => {
    const sModal = document.getElementById('settings-modal');
    const sBtn = document.getElementById('btn-open-settings');
    if (sModal && sModal.classList.contains('open') && !sModal.contains(e.target) && e.target !== sBtn && !sBtn.contains(e.target)) {
      sModal.classList.remove('open');
    }

    const iModal = document.getElementById('illustrations-modal');
    if (iModal && e.target === iModal) {
      closeIllustrationsModal();
    }
  });

  // Teclas de atalho no leitor
  window.addEventListener('keydown', (e) => {
    if (AppState.currentReading.type) {
      if (e.key === 'Escape') {
        closeReader();
      }
    }
  });
}

function showLoading() {
  const loader = document.getElementById('global-loader');
  if (loader) loader.style.display = 'flex';
}

function hideLoading() {
  const loader = document.getElementById('global-loader');
  if (loader) loader.style.display = 'none';
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
