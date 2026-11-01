/**
 * soundtrack.js - Player de Trilha Sonora Oficial & Imersiva de Tensura
 * Conecta momentos e conferências da Light Novel às faixas oficiais das temporadas 1, 2, 4 e Tensura Nikki.
 */

(function () {
  'use strict';

  const STORAGE_KEYS = {
    VOLUME: 'tensura_soundtrack_vol',
    AUTOPLAY_CHAPTER: 'tensura_soundtrack_auto_suggest',
    MUTED: 'tensura_soundtrack_muted',
    LAST_TRACK: 'tensura_soundtrack_last_track',
    DOCK_COLLAPSED: 'tensura_soundtrack_collapsed'
  };

  const TRACK_CATALOG = [
    {
      id: 'tempest_meeting_dynamic',
      title: '🏛️ Reunião em Tempest',
      subtitle: 'Going Forward & Backward (35:02)',
      season: '2ª Temporada',
      videoId: 's2p-7sfYkM8',
      start: 2102,
      desc: 'Trilha clássica dos debates e planejamento na sala de reuniões de Tempest.'
    },
    {
      id: 'council_diplomacy',
      title: '⚖️ O Conselho Parlamentar',
      subtitle: 'Hyōgikai / 評議会 (12:36)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 756,
      desc: 'Trilha solene e séria para conferências diplomáticas e políticas de alto escalão.'
    },
    {
      id: 'sarion_dynasty',
      title: '🏰 Dinastia Feiticeira de Sarion',
      subtitle: 'Sarion no Monogatari (41:42)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 2502,
      desc: 'Tema oficial da nobreza e das histórias antigas da Dinastia Feiticeira de Sarion.'
    },
    {
      id: 'peaceful_village',
      title: '🌿 Cotidiano & Paz em Tempest',
      subtitle: 'Village / Tensura Nikki (10:07)',
      season: 'Tensura Nikki',
      videoId: 'wD694z2iB1w',
      start: 607,
      desc: 'Trilha suave de descanso, colheita, agricultura e vida pacífica na federação.'
    },
    {
      id: 'battle_counterattack',
      title: '⚔️ Contra-Ataque & Batalha',
      subtitle: 'Counterattack (30:55)',
      season: '2ª Temporada',
      videoId: 's2p-7sfYkM8',
      start: 1855,
      desc: 'Trilha épica de superação, virada militar e batalha de Rimuru e seus generais.'
    },
    {
      id: 'conspiracy_takurami',
      title: '🎭 Conspiração & Mistério',
      subtitle: 'Takurami / Dokeshi (02:00)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 120,
      desc: 'Tema de conspirações secretas, palhaços moderados e acordos sombrios.'
    }
  ];

  // Mapeamento de capítulos sugeridos para o teste inicial (Volume 6 e Volume 7)
  const CHAPTER_SUGGESTIONS = {
    // Volume 6
    'vol-6:0': 'peaceful_village', // Capa / Ilustrações
    'vol-6:1': 'conspiracy_takurami', // Prólogo: A Conspiração dos Majins (Laplace & Sarion)
    'vol-6:2': 'tempest_meeting_dynamic', // Cap. 1: Encontro entre Homem e Monstro (A Grande Reunião)
    'vol-6:3': 'tempest_meeting_dynamic', // Cap. 2: Palavra de Ramiris (Ramiris invade a reunião)
    'vol-6:4': 'council_diplomacy', // Cap. 3: Véspera da Batalha
    'vol-6:5': 'conspiracy_takurami', // Interlúdio: Os Lordes Demônios
    'vol-6:6': 'battle_counterattack', // Cap. 4: No Lugar do Destino
    'vol-6:7': 'council_diplomacy', // Cap. 5: Walpurgis
    'vol-6:8': 'council_diplomacy', // Cap. 6: O Octagrama

    // Volume 7
    'vol-7:1': 'conspiracy_takurami', // Prólogo
    'vol-7:2': 'council_diplomacy', // Cap. 1: Um acordo com o diabo
    'vol-7:3': 'tempest_meeting_dynamic', // Cap. 2: Funções a serem mantidas
    'vol-7:4': 'council_diplomacy', // Cap. 3: O Objetivo de um Santo
    'vol-7:5': 'conspiracy_takurami', // Interlúdio: A Reunião Secreta
    'vol-7:6': 'battle_counterattack', // Cap. 4: O Segundo Confronto
    'vol-7:7': 'battle_counterattack', // Cap. 5: Santos e Monstros Colidem
    'vol-7:8': 'battle_counterattack'  // Cap. 6: Deus e Lorde Demônio
  };

  let ytPlayer = null;
  let isApiReady = false;
  let isApiLoading = false;
  let currentTrack = TRACK_CATALOG[0];
  let isPlaying = false;
  let currentVolume = parseInt(localStorage.getItem(STORAGE_KEYS.VOLUME) || '22', 10);
  let isMuted = localStorage.getItem(STORAGE_KEYS.MUTED) === 'true';
  let isCollapsed = localStorage.getItem(STORAGE_KEYS.DOCK_COLLAPSED) === 'true';
  let isAutoSuggest = localStorage.getItem(STORAGE_KEYS.AUTOPLAY_CHAPTER) !== 'false';

  function initSoundtrack() {
    createSoundtrackElements();
    attachGlobalEvents();
    syncUiState();
  }

  function loadYouTubeIframeApi() {
    if (window.YT && window.YT.Player) {
      isApiReady = true;
      return Promise.resolve();
    }
    if (isApiLoading) {
      return new Promise((resolve) => {
        const check = setInterval(() => {
          if (isApiReady) {
            clearInterval(check);
            resolve();
          }
        }, 100);
      });
    }

    isApiLoading = true;
    return new Promise((resolve) => {
      const prevCallback = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = function () {
        isApiReady = true;
        isApiLoading = false;
        if (typeof prevCallback === 'function') prevCallback();
        resolve();
      };

      const tag = document.createElement('script');
      tag.id = 'youtube-iframe-api';
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    });
  }

  function createSoundtrackElements() {
    if (document.getElementById('soundtrack-dock')) return;

    const dock = document.createElement('aside');
    dock.id = 'soundtrack-dock';
    dock.className = `soundtrack-dock ${isCollapsed ? 'is-collapsed' : ''}`;
    dock.setAttribute('aria-label', 'Player de Trilha Sonora Oficial');

    dock.innerHTML = `
      <!-- Cabeçalho / Pílula Minimizada -->
      <div class="soundtrack-dock-bar" id="soundtrack-dock-bar">
        <button type="button" class="btn-soundtrack-toggle" id="btn-soundtrack-toggle" aria-expanded="${!isCollapsed}" aria-label="Expandir ou recolher tocador de música">
          <span class="soundtrack-icon-anim ${isPlaying ? 'is-playing' : ''}">🎧</span>
          <span class="soundtrack-pill-title" id="soundtrack-pill-title">${escapeHtml(currentTrack.title)}</span>
          <span class="soundtrack-pill-time">${formatTime(currentTrack.start)}</span>
        </button>

        <div class="soundtrack-bar-quick-controls">
          <button type="button" class="btn-soundtrack-play" id="btn-soundtrack-play" aria-label="Reproduzir ou pausar trilha">
            <span id="soundtrack-play-icon" aria-hidden="true">${isPlaying ? '⏸' : '▶'}</span>
          </button>
          <button type="button" class="btn-soundtrack-minimize" id="btn-soundtrack-minimize" aria-label="Recolher player">
            <span aria-hidden="true">${isCollapsed ? '▲' : '▼'}</span>
          </button>
        </div>
      </div>

      <!-- Corpo Expandido do Dock -->
      <div class="soundtrack-dock-body" id="soundtrack-dock-body">
        <div class="soundtrack-track-card">
          <div class="soundtrack-now-playing">
            <span class="soundtrack-season-tag" id="soundtrack-season-tag">${escapeHtml(currentTrack.season)}</span>
            <h4 class="soundtrack-track-title" id="soundtrack-track-title">${escapeHtml(currentTrack.title)}</h4>
            <p class="soundtrack-track-desc" id="soundtrack-track-desc">${escapeHtml(currentTrack.desc)}</p>
          </div>

          <!-- Container do player oficial do YouTube (invisível/mini para compliant audio stream) -->
          <div class="soundtrack-yt-wrap" id="soundtrack-yt-wrap">
            <div id="yt-player-target"></div>
          </div>
        </div>

        <!-- Barra de Volume e Controles -->
        <div class="soundtrack-controls-row">
          <button type="button" class="btn-soundtrack-mute" id="btn-soundtrack-mute" aria-label="Mutar ou desmutar volume">
            <span id="soundtrack-mute-icon" aria-hidden="true">${isMuted ? '🔇' : (currentVolume > 40 ? '🔊' : '🔉')}</span>
          </button>
          <label for="soundtrack-vol-slider" class="sr-only">Volume da Trilha Sonora</label>
          <input type="range" id="soundtrack-vol-slider" class="soundtrack-vol-slider" min="0" max="100" value="${isMuted ? 0 : currentVolume}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${currentVolume}" title="Volume de leitura">
          <span class="soundtrack-vol-text" id="soundtrack-vol-text">${isMuted ? 'Mudo' : `${currentVolume}%`}</span>
        </div>

        <!-- Seletor Rápido de Atmosferas / Trilhas -->
        <div class="soundtrack-presets-section">
          <span class="soundtrack-presets-label">Escolher Atmosfera da Cena:</span>
          <div class="soundtrack-presets-grid" id="soundtrack-presets-grid">
            ${TRACK_CATALOG.map(t => `
              <button type="button" class="btn-soundtrack-preset ${t.id === currentTrack.id ? 'is-active' : ''}" data-track-id="${t.id}" title="${escapeHtml(t.desc)}">
                <span class="preset-name">${escapeHtml(t.title)}</span>
                <span class="preset-season">${escapeHtml(t.season)}</span>
              </button>
            `).join('')}
          </div>
        </div>

        <div class="soundtrack-dock-footer">
          <label class="soundtrack-auto-label">
            <input type="checkbox" id="chk-soundtrack-auto" ${isAutoSuggest ? 'checked' : ''}>
            <span>Sugerir trilha automaticamente por capítulo</span>
          </label>
        </div>
      </div>
    `;

    document.body.appendChild(dock);
  }

  function attachGlobalEvents() {
    const btnPlay = document.getElementById('btn-soundtrack-play');
    const btnToggle = document.getElementById('btn-soundtrack-toggle');
    const btnMinimize = document.getElementById('btn-soundtrack-minimize');
    const sliderVol = document.getElementById('soundtrack-vol-slider');
    const btnMute = document.getElementById('btn-soundtrack-mute');
    const chkAuto = document.getElementById('chk-soundtrack-auto');
    const presetsGrid = document.getElementById('soundtrack-presets-grid');

    if (btnPlay) {
      btnPlay.addEventListener('click', () => togglePlay());
    }

    if (btnToggle) {
      btnToggle.addEventListener('click', (e) => {
        if (e.target.closest('#btn-soundtrack-play') || e.target.closest('#btn-soundtrack-minimize')) return;
        toggleCollapse();
      });
    }

    if (btnMinimize) {
      btnMinimize.addEventListener('click', () => toggleCollapse());
    }

    if (sliderVol) {
      sliderVol.addEventListener('input', (e) => {
        const val = parseInt(e.target.value, 10);
        setVolume(val);
      });
    }

    if (btnMute) {
      btnMute.addEventListener('click', () => toggleMute());
    }

    if (chkAuto) {
      chkAuto.addEventListener('change', (e) => {
        isAutoSuggest = e.target.checked;
        localStorage.setItem(STORAGE_KEYS.AUTOPLAY_CHAPTER, isAutoSuggest);
      });
    }

    if (presetsGrid) {
      presetsGrid.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-soundtrack-preset');
        if (!btn) return;
        const trackId = btn.getAttribute('data-track-id');
        const track = TRACK_CATALOG.find(t => t.id === trackId);
        if (track) {
          playTrack(track);
        }
      });
    }

    // Botão de fone de ouvido na barra de ferramentas do leitor
    const btnReaderSound = document.getElementById('btn-reader-soundtrack');
    if (btnReaderSound) {
      btnReaderSound.addEventListener('click', () => {
        const dock = document.getElementById('soundtrack-dock');
        if (dock) {
          dock.classList.remove('is-collapsed');
          dock.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
      });
    }
  }

  function toggleCollapse() {
    const dock = document.getElementById('soundtrack-dock');
    const btnMin = document.getElementById('btn-soundtrack-minimize');
    if (!dock) return;
    isCollapsed = !isCollapsed;
    dock.classList.toggle('is-collapsed', isCollapsed);
    if (btnMin) btnMin.innerHTML = `<span aria-hidden="true">${isCollapsed ? '▲' : '▼'}</span>`;
    localStorage.setItem(STORAGE_KEYS.DOCK_COLLAPSED, isCollapsed);
  }

  async function ensurePlayerCreated() {
    await loadYouTubeIframeApi();

    return new Promise((resolve) => {
      if (ytPlayer && ytPlayer.loadVideoById) {
        resolve(ytPlayer);
        return;
      }

      ytPlayer = new window.YT.Player('yt-player-target', {
        height: '100',
        width: '180',
        videoId: currentTrack.videoId,
        playerVars: {
          autoplay: 0,
          controls: 0,
          disablekb: 1,
          fs: 0,
          modestbranding: 1,
          rel: 0,
          start: currentTrack.start,
          enablejsapi: 1,
          playsinline: 1,
          ...(window.location.protocol.startsWith('http') && window.location.origin !== 'null' ? { origin: window.location.origin } : {})
        },
        events: {
          onReady: (event) => {
            event.target.setVolume(isMuted ? 0 : currentVolume);
            resolve(ytPlayer);
          },
          onStateChange: (event) => {
            if (event.data === window.YT.PlayerState.PLAYING) {
              isPlaying = true;
            } else if (event.data === window.YT.PlayerState.PAUSED || event.data === window.YT.PlayerState.ENDED) {
              isPlaying = false;
            }
            syncUiState();
          },
          onError: (err) => {
            console.warn('[Soundtrack] YouTube player error:', err);
          }
        }
      });
    });
  }

  async function playTrack(track, shouldPlay = true) {
    currentTrack = track;
    localStorage.setItem(STORAGE_KEYS.LAST_TRACK, track.id);
    syncUiState();

    try {
      const player = await ensurePlayerCreated();
      if (player && player.loadVideoById) {
        player.loadVideoById({
          videoId: track.videoId,
          startSeconds: track.start
        });
        player.setVolume(isMuted ? 0 : currentVolume);
        if (shouldPlay) {
          player.playVideo();
          isPlaying = true;
        }
      }
    } catch (e) {
      console.error('[Soundtrack] Erro ao reproduzir faixa:', e);
    }
    syncUiState();
  }

  async function togglePlay() {
    try {
      const player = await ensurePlayerCreated();
      if (!player) return;

      if (isPlaying) {
        player.pauseVideo();
        isPlaying = false;
      } else {
        player.setVolume(isMuted ? 0 : currentVolume);
        player.playVideo();
        isPlaying = true;
      }
    } catch (e) {
      console.error('[Soundtrack] Erro ao alternar play/pause:', e);
    }
    syncUiState();
  }

  function setVolume(val) {
    currentVolume = Math.max(0, Math.min(100, val));
    isMuted = currentVolume === 0;
    localStorage.setItem(STORAGE_KEYS.VOLUME, currentVolume);
    localStorage.setItem(STORAGE_KEYS.MUTED, isMuted);

    if (ytPlayer && ytPlayer.setVolume) {
      ytPlayer.setVolume(currentVolume);
      if (isMuted && ytPlayer.mute) ytPlayer.mute();
      else if (!isMuted && ytPlayer.unMute) ytPlayer.unMute();
    }
    syncUiState();
  }

  function toggleMute() {
    isMuted = !isMuted;
    localStorage.setItem(STORAGE_KEYS.MUTED, isMuted);
    if (ytPlayer) {
      if (isMuted && ytPlayer.mute) ytPlayer.mute();
      else if (!isMuted && ytPlayer.unMute) {
        ytPlayer.unMute();
        ytPlayer.setVolume(currentVolume);
      }
    }
    syncUiState();
  }

  function syncUiState() {
    const pillTitle = document.getElementById('soundtrack-pill-title');
    const playIcon = document.getElementById('soundtrack-play-icon');
    const trackTitle = document.getElementById('soundtrack-track-title');
    const trackDesc = document.getElementById('soundtrack-track-desc');
    const seasonTag = document.getElementById('soundtrack-season-tag');
    const volSlider = document.getElementById('soundtrack-vol-slider');
    const volText = document.getElementById('soundtrack-vol-text');
    const muteIcon = document.getElementById('soundtrack-mute-icon');
    const iconAnim = document.querySelector('.soundtrack-icon-anim');

    if (pillTitle) pillTitle.textContent = currentTrack.title;
    if (playIcon) playIcon.textContent = isPlaying ? '⏸' : '▶';
    if (trackTitle) trackTitle.textContent = currentTrack.title;
    if (trackDesc) trackDesc.textContent = currentTrack.desc;
    if (seasonTag) seasonTag.textContent = currentTrack.season;

    if (volSlider) {
      volSlider.value = isMuted ? 0 : currentVolume;
      volSlider.setAttribute('aria-valuenow', isMuted ? 0 : currentVolume);
    }
    if (volText) {
      volText.textContent = isMuted ? 'Mudo' : `${currentVolume}%`;
    }
    if (muteIcon) {
      muteIcon.textContent = isMuted ? '🔇' : (currentVolume > 40 ? '🔊' : '🔉');
    }
    if (iconAnim) {
      iconAnim.classList.toggle('is-playing', isPlaying);
    }

    // Atualiza botões ativos na lista de presets
    const presetBtns = document.querySelectorAll('.btn-soundtrack-preset');
    presetBtns.forEach(btn => {
      btn.classList.toggle('is-active', btn.getAttribute('data-track-id') === currentTrack.id);
    });

    // Atualiza badge de capítulo inline no leitor se existir
    const inlineBadge = document.getElementById('soundtrack-chapter-badge');
    const inlineBtn = document.getElementById('btn-soundtrack-play-inline');
    if (inlineBadge && inlineBtn) {
      inlineBtn.textContent = isPlaying && inlineBadge.getAttribute('data-track-id') === currentTrack.id
        ? '⏸ Pausar Trilha'
        : '▶ Ouvir Trilha';
    }
  }

  /**
   * Chamado pelo leitor (app.js) quando o usuário abre ou troca de capítulo.
   */
  function handleChapterChange(volumeId, chapterIndex, chapterTitle) {
    if (!volumeId) return;

    const baseVol = String(volumeId).replace(/-scan$/, '');
    const keyWithIdx = `${baseVol}:${chapterIndex}`;
    
    // Tenta encontrar uma sugestão específica para este capítulo
    let suggestedTrackId = CHAPTER_SUGGESTIONS[keyWithIdx];

    // Se não encontrou por índice, tenta por palavras-chave do título
    if (!suggestedTrackId && chapterTitle) {
      const lower = chapterTitle.toLowerCase();
      if (lower.includes('reunião') || lower.includes('encontro entre homem e monstro') || lower.includes('conferência') || lower.includes('conselho')) {
        suggestedTrackId = 'tempest_meeting_dynamic';
      } else if (lower.includes('sarion')) {
        suggestedTrackId = 'sarion_dynasty';
      } else if (lower.includes('palhaço') || lower.includes('conspiração') || lower.includes('majins')) {
        suggestedTrackId = 'conspiracy_takurami';
      } else if (lower.includes('walpurgis') || lower.includes('octagrama') || lower.includes('lorde demônio')) {
        suggestedTrackId = 'council_diplomacy';
      } else if (lower.includes('batalha') || lower.includes('confronto') || lower.includes('colidem')) {
        suggestedTrackId = 'battle_counterattack';
      }
    }

    const suggestedTrack = suggestedTrackId ? TRACK_CATALOG.find(t => t.id === suggestedTrackId) : null;
    renderChapterSoundtrackBadge(suggestedTrack);

    // Se o usuário já estava ouvindo música e tem auto-suggest ligado:
    if (isPlaying && isAutoSuggest && suggestedTrack && suggestedTrack.id !== currentTrack.id) {
      playTrack(suggestedTrack, true);
    }
  }

  function renderChapterSoundtrackBadge(track) {
    const headerArea = document.getElementById('reader-header-area');
    if (!headerArea) return;

    let badge = document.getElementById('soundtrack-chapter-badge');
    if (!track) {
      if (badge) badge.remove();
      return;
    }

    if (!badge) {
      badge = document.createElement('div');
      badge.id = 'soundtrack-chapter-badge';
      badge.className = 'soundtrack-chapter-badge';
      headerArea.appendChild(badge);
    }

    badge.setAttribute('data-track-id', track.id);
    badge.innerHTML = `
      <div class="soundtrack-badge-left">
        <span class="soundtrack-badge-icon">🎧</span>
        <div class="soundtrack-badge-meta">
          <span class="soundtrack-badge-label">Trilha Sonora Sugerida para este Capítulo (${escapeHtml(track.season)})</span>
          <strong class="soundtrack-badge-title">${escapeHtml(track.title)}</strong>
          <span class="soundtrack-badge-sub">${escapeHtml(track.subtitle)}</span>
        </div>
      </div>
      <button type="button" class="btn-soundtrack-play-inline" id="btn-soundtrack-play-inline">
        ${isPlaying && track.id === currentTrack.id ? '⏸ Pausar Trilha' : '▶ Ouvir Trilha'}
      </button>
    `;

    const btnInline = badge.querySelector('#btn-soundtrack-play-inline');
    if (btnInline) {
      btnInline.addEventListener('click', () => {
        if (currentTrack.id === track.id) {
          togglePlay();
        } else {
          playTrack(track, true);
        }
      });
    }
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Exporta para uso global no app
  window.TensuraSoundtrack = {
    init: initSoundtrack,
    playTrack: playTrack,
    togglePlay: togglePlay,
    handleChapterChange: handleChapterChange,
    getCurrentTrack: () => currentTrack,
    isPlaying: () => isPlaying
  };

  // Auto-inicialização quando o DOM estiver pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSoundtrack);
  } else {
    initSoundtrack();
  }
})();
