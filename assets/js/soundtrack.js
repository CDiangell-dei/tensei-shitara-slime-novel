/**
 * soundtrack.js - Player de Trilha Sonora Oficial & Imersiva de Tensura
 * Conecta todos os momentos, conferências e trocas de cena dentro de cada capítulo da obra.
 */

(function () {
  'use strict';

  const STORAGE_KEYS = {
    VOLUME: 'tensura_soundtrack_vol',
    AUTOPLAY_CHAPTER: 'tensura_soundtrack_auto_suggest',
    MUTED: 'tensura_soundtrack_muted',
    LAST_TRACK: 'tensura_soundtrack_last_track',
    DOCK_COLLAPSED: 'tensura_soundtrack_collapsed',
    LOOP: 'tensura_soundtrack_loop'
  };

  const TRACK_CATALOG = [
    {
      id: 'tempest_meeting_dynamic',
      title: '🏛️ Reunião em Tempest',
      subtitle: 'Going Forward & Backward (35:02)',
      season: '2ª Temporada',
      videoId: 's2p-7sfYkM8',
      start: 2098, // 34:58
      end: 2525,   // 42:05 (bloco com todas as variações da reunião!)
      desc: 'Trilha clássica dos debates e planejamento na sala de reuniões de Tempest.'
    },
    {
      id: 'council_diplomacy',
      title: '⚖️ O Conselho Parlamentar',
      subtitle: 'Hyōgikai / 評議会 (12:36)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 756,  // 12:36
      end: 888,    // 14:48
      desc: 'Trilha solene e séria para conferências diplomáticas e políticas de alto escalão.'
    },
    {
      id: 'dungeon_management',
      title: '🌀 Gerenciamento do Labirinto',
      subtitle: 'Dungeon Unei / ダンジョン運営 (14:48)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 888,  // 14:48
      end: 991,    // 16:31
      desc: 'Tema divertido e focado de Rimuru e Ramiris administrando as armadilhas da Dungeon.'
    },
    {
      id: 'festival_banquet',
      title: '🎊 Banquete & Festival',
      subtitle: 'Sōen / 奏宴 (01:48:01)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 6481, // 01:48:01
      end: 6617,   // 01:50:17
      desc: 'O clima alegre e festivo das celebrações e do Festival de Fundação de Tempest.'
    },
    {
      id: 'sarion_dynasty',
      title: '🏰 Dinastia Feiticeira de Sarion',
      subtitle: 'Sarion no Monogatari (41:42)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 2502, // 41:42
      end: 2602,   // 43:22
      desc: 'Tema oficial da nobreza e das histórias antigas da Dinastia Feiticeira de Sarion.'
    },
    {
      id: 'peaceful_village',
      title: '🌿 Cotidiano & Paz em Tempest',
      subtitle: 'Village / Tensura Nikki (10:07)',
      season: 'Tensura Nikki',
      videoId: 'wD694z2iB1w',
      start: 607,  // 10:07
      end: 715,    // 11:55
      desc: 'Trilha suave de descanso, colheita, agricultura e vida pacífica na federação.'
    },
    {
      id: 'primordials_dialogue',
      title: '🔮 Conversa dos Primordiais',
      subtitle: 'Gensho no Danshō (01:23:21)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 5001, // 01:23:21
      end: 5110,   // 01:25:10
      desc: 'Tema nobre e imponente para diálogos com Diablo, Guy Crimson e demônios primordiais.'
    },
    {
      id: 'battle_counterattack',
      title: '⚔️ Contra-Ataque & Batalha',
      subtitle: 'Counterattack (30:55)',
      season: '2ª Temporada',
      videoId: 's2p-7sfYkM8',
      start: 1855, // 30:55
      end: 1976,   // 32:56
      desc: 'Trilha épica de superação, virada militar e batalha de Rimuru e seus generais.'
    },
    {
      id: 'conspiracy_takurami',
      title: '🎭 Conspiração & Mistério',
      subtitle: 'Takurami / Dokeshi (02:00)',
      season: '4ª Temporada',
      videoId: 'JFKlCKKI3hU',
      start: 120,  // 02:00
      end: 220,    // 03:40
      desc: 'Tema de conspirações secretas, palhaços moderados e acordos sombrios.'
    },
    {
      id: 'reincarnation_determination',
      title: '🌌 Determinação & Origem',
      subtitle: 'Reincarnation & Determination (00:00)',
      season: '1ª Temporada',
      videoId: 'ty5HNb8yYS0',
      start: 0,    // 00:00
      end: 172,    // 02:52
      desc: 'A clássica trilha de abertura onde tudo começa, na caverna selada com Veldora.'
    }
  ];

  // Mapeamento minucioso de transições de cena internas dentro do mesmo capítulo
  const CHAPTER_SCENE_MAPPINGS = {
    // Volume 6: Prólogo (Laplace & Sarion -> Castelo de Clayman)
    'vol-6:1': [
      { pIndex: 0, trackId: 'sarion_dynasty', title: 'Laplace & O Homúnculo de Sarion' },
      { pIndex: 220, trackId: 'conspiracy_takurami', title: '🎭 Conspiração no Castelo de Clayman' }
    ],

    // Volume 6: Capítulo 1 - Encontro entre Homem e Monstro (Clayman -> Gazel -> Sarion -> Grande Reunião)
    'vol-6:2': [
      { pIndex: 0, trackId: 'conspiracy_takurami', title: '🎭 Conspiração & Planos de Clayman' },
      { pIndex: 217, trackId: 'peaceful_village', title: '🌿 Chegada do Rei Gazel & Pégasos' },
      { pIndex: 355, trackId: 'sarion_dynasty', title: '🏰 Chegada da Comitiva de Sarion' },
      { pIndex: 467, trackId: 'tempest_meeting_dynamic', title: '🏛️ O Encontro entre Homem e Monstro (A Grande Reunião)' }
    ],

    // Volume 6: Capítulo 2 - Palavra de Ramiris
    'vol-6:3': [
      { pIndex: 0, trackId: 'tempest_meeting_dynamic', title: '🏛️ Continuação da Conferência de Tempest' },
      { pIndex: 540, trackId: 'conspiracy_takurami', title: '⚡ Alerta de Ramiris: "Tempest vai ser destruída!"' }
    ],

    // Volume 6: Capítulo 5 - Walpurgis
    'vol-6:7': [
      { pIndex: 0, trackId: 'council_diplomacy', title: '⚖️ Walpurgis: O Banquete dos Lordes Demônios' },
      { pIndex: 600, trackId: 'battle_counterattack', title: '⚔️ O Julgamento de Clayman & Batalha' }
    ],

    // Volume 7: Capítulo 1 - Um acordo com o diabo
    'vol-7:2': [
      { pIndex: 0, trackId: 'primordials_dialogue', title: '🔮 O Acordo de Diablo & Estratégia de Farmus' },
      { pIndex: 500, trackId: 'council_diplomacy', title: '⚖️ Conferência Militar com Rimuru' }
    ],

    // Volume 7: Capítulo 4 - O Segundo Confronto
    'vol-7:6': [
      { pIndex: 0, trackId: 'conspiracy_takurami', title: '🎭 Tramas dos Cavaleiros Sagrados' },
      { pIndex: 450, trackId: 'battle_counterattack', title: '⚔️ Santos e Monstros Colidem' }
    ],

    // Volume 8: Capítulo 2 - O Banquete da Véspera
    'vol-8:2': [
      { pIndex: 0, trackId: 'peaceful_village', title: '🌿 Preparativos Finais em Tempest' },
      { pIndex: 300, trackId: 'festival_banquet', title: '🎊 O Grande Banquete da Véspera' }
    ],

    // Volume 8: Capítulo 4 - A Inauguração da Masmorra
    'vol-8:4': [
      { pIndex: 0, trackId: 'festival_banquet', title: '🎊 Cerimônia do Festival' },
      { pIndex: 250, trackId: 'dungeon_management', title: '🌀 Abertura Oficial do Labirinto de Ramiris' }
    ],

    // Volume 10: Capítulo 1 - A Operação Suave do Labirinto
    'vol-10:2': [
      { pIndex: 0, trackId: 'dungeon_management', title: '🌀 Administração dos 100 Andares do Labirinto' },
      { pIndex: 400, trackId: 'conspiracy_takurami', title: '🎭 As Tramas Ocultas da Família Rozzo' }
    ]
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
  let isLooping = localStorage.getItem(STORAGE_KEYS.LOOP) !== 'false'; // Padrão: TRUE
  let loopWatcherInterval = null;
  let sceneScrollObserver = null;
  let activeSceneTrackId = null;

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
            <div class="soundtrack-meta-line">
              <span class="soundtrack-season-tag" id="soundtrack-season-tag">${escapeHtml(currentTrack.season)}</span>
              <span class="soundtrack-loop-indicator" id="soundtrack-loop-indicator" title="Status de repetição">
                ${isLooping ? '🔂 Loop ativo' : '⏭ Modo contínuo'}
              </span>
            </div>
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
          
          <!-- Botão de Alternância de Loop -->
          <button type="button" class="btn-soundtrack-loop ${isLooping ? 'is-active' : ''}" id="btn-soundtrack-loop" title="${isLooping ? 'Loop ativo: a música repete para manter a atmosfera da cena' : 'Modo contínuo: o vídeo segue tocando as próximas faixas'}">
            <span id="soundtrack-loop-icon" aria-hidden="true">${isLooping ? '🔂' : '⏭'}</span>
            <span class="soundtrack-loop-text" id="soundtrack-loop-text">${isLooping ? 'Loop' : 'Seguir'}</span>
          </button>
        </div>

        <!-- Seletor Rápido de Atmosferas / Trilhas -->
        <div class="soundtrack-presets-section">
          <span class="soundtrack-presets-label">Escolher Atmosfera da Cena (10 Temas Canônicos):</span>
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
            <span>Trocar trilha automaticamente ao mudar de cena ou capítulo</span>
          </label>
        </div>
      </div>
    `;

    document.body.appendChild(dock);

    // Toast de notificação de troca de cena flutuante
    if (!document.getElementById('soundtrack-scene-toast')) {
      const toast = document.createElement('div');
      toast.id = 'soundtrack-scene-toast';
      toast.className = 'soundtrack-scene-toast';
      toast.setAttribute('aria-live', 'polite');
      document.body.appendChild(toast);
    }
  }

  function showSceneToast(message) {
    const toast = document.getElementById('soundtrack-scene-toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.classList.remove('is-visible');
    }, 2800);
  }

  function attachGlobalEvents() {
    const btnPlay = document.getElementById('btn-soundtrack-play');
    const btnToggle = document.getElementById('btn-soundtrack-toggle');
    const btnMinimize = document.getElementById('btn-soundtrack-minimize');
    const sliderVol = document.getElementById('soundtrack-vol-slider');
    const btnMute = document.getElementById('btn-soundtrack-mute');
    const btnLoop = document.getElementById('btn-soundtrack-loop');
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

    if (btnLoop) {
      btnLoop.addEventListener('click', () => toggleLoop());
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

  function toggleLoop() {
    isLooping = !isLooping;
    localStorage.setItem(STORAGE_KEYS.LOOP, isLooping);
    if (isLooping && isPlaying) {
      startLoopWatcher();
    } else if (!isLooping) {
      stopLoopWatcher();
    }
    syncUiState();
  }

  function startLoopWatcher() {
    stopLoopWatcher();
    loopWatcherInterval = setInterval(() => {
      if (!isPlaying || !isLooping || !ytPlayer || typeof ytPlayer.getCurrentTime !== 'function') return;
      try {
        const curTime = ytPlayer.getCurrentTime();
        if (currentTrack.end && curTime >= currentTrack.end) {
          ytPlayer.seekTo(currentTrack.start, true);
        }
      } catch (e) {
        // Ignora atrasos transitórios da API
      }
    }, 800);
  }

  function stopLoopWatcher() {
    if (loopWatcherInterval) {
      clearInterval(loopWatcherInterval);
      loopWatcherInterval = null;
    }
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
              if (isLooping) startLoopWatcher();
            } else if (event.data === window.YT.PlayerState.ENDED) {
              if (isLooping) {
                ytPlayer.seekTo(currentTrack.start, true);
                ytPlayer.playVideo();
              } else {
                isPlaying = false;
                stopLoopWatcher();
              }
            } else {
              isPlaying = false;
              stopLoopWatcher();
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
    activeSceneTrackId = track.id;
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
          if (isLooping) startLoopWatcher();
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
        stopLoopWatcher();
      } else {
        player.setVolume(isMuted ? 0 : currentVolume);
        player.playVideo();
        isPlaying = true;
        if (isLooping) startLoopWatcher();
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
    const loopIndicator = document.getElementById('soundtrack-loop-indicator');
    const btnLoop = document.getElementById('btn-soundtrack-loop');
    const loopIcon = document.getElementById('soundtrack-loop-icon');
    const loopText = document.getElementById('soundtrack-loop-text');
    const volSlider = document.getElementById('soundtrack-vol-slider');
    const volText = document.getElementById('soundtrack-vol-text');
    const muteIcon = document.getElementById('soundtrack-mute-icon');
    const iconAnim = document.querySelector('.soundtrack-icon-anim');

    if (pillTitle) pillTitle.textContent = currentTrack.title;
    if (playIcon) playIcon.textContent = isPlaying ? '⏸' : '▶';
    if (trackTitle) trackTitle.textContent = currentTrack.title;
    if (trackDesc) trackDesc.textContent = currentTrack.desc;
    if (seasonTag) seasonTag.textContent = currentTrack.season;

    if (loopIndicator) {
      loopIndicator.textContent = isLooping ? '🔂 Loop ativo' : '⏭ Modo contínuo';
    }

    if (btnLoop) {
      btnLoop.classList.toggle('is-active', isLooping);
      btnLoop.title = isLooping
        ? 'Loop ativo: a música repete para manter a atmosfera da cena'
        : 'Modo contínuo: o vídeo segue tocando as próximas faixas';
    }
    if (loopIcon) loopIcon.textContent = isLooping ? '🔂' : '⏭';
    if (loopText) loopText.textContent = isLooping ? 'Loop' : 'Seguir';

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

    // Atualiza badge de capítulo inline no topo do leitor
    const inlineBadge = document.getElementById('soundtrack-chapter-badge');
    const inlineBtn = document.getElementById('btn-soundtrack-play-inline');
    if (inlineBadge && inlineBtn) {
      inlineBtn.textContent = isPlaying && inlineBadge.getAttribute('data-track-id') === currentTrack.id
        ? '⏸ Pausar Trilha'
        : '▶ Ouvir Trilha';
    }

    // Atualiza botões de cena no meio do texto
    const sceneCues = document.querySelectorAll('.soundtrack-scene-cue');
    sceneCues.forEach(cue => {
      const isThisActive = cue.getAttribute('data-track-id') === currentTrack.id;
      cue.classList.toggle('is-active', isThisActive);
      const btnCue = cue.querySelector('.btn-cue-play');
      if (btnCue) {
        btnCue.textContent = isPlaying && isThisActive ? '⏸ Tocando' : '▶ Sintonizar';
      }
    });
  }

  /**
   * Classificador universal inteligente para capítulos.
   */
  function determineChapterTrack(volumeId, chapterIndex, chapterTitle) {
    const t = String(chapterTitle || '').toLowerCase();
    const cleanVol = String(volumeId || '').replace(/-scan$/, '');
    const volNum = parseFloat(cleanVol.replace('vol-', '').replace('-', '.'));

    if (t.includes('capa') || t.includes('ilustraç') || t.includes('mangá') || t.includes('posfácio') || t.includes('nota do autor') || t.includes('notas culturais')) {
      return 'peaceful_village';
    }
    if (t.includes('sarion')) return 'sarion_dynasty';
    if (t.includes('labirinto') || t.includes('dungeon') || (volNum === 10 && chapterIndex <= 2) || (volNum === 8 && t.includes('masmorra'))) {
      return 'dungeon_management';
    }
    if (t.includes('festival') || t.includes('banquete') || t.includes('celebração') || t.includes('fundação') || (volNum === 8 && chapterIndex >= 2) || (volNum === 9 && chapterIndex <= 3)) {
      return 'festival_banquet';
    }
    if (t.includes('primordial') || t.includes('diablo') || t.includes('guy crimson') || t.includes('números negros') || t.includes('black numbers')) {
      return 'primordials_dialogue';
    }
    if (t.includes('conspiração') || t.includes('palhaço') || t.includes('secreta') || t.includes('esquema') || t.includes('sombra') || t.includes('traição') || t.includes('maquinações') || t.includes('tributo')) {
      return 'conspiracy_takurami';
    }
    if (t.includes('reunião') || t.includes('conferência') || t.includes('conselho') || t.includes('homem e monstro') || t.includes('palavra de ramiris') || t.includes('acordo') || t.includes('parlamento')) {
      if (t.includes('octagrama') || t.includes('walpurgis') || t.includes('santo') || t.includes('deus')) return 'council_diplomacy';
      return 'tempest_meeting_dynamic';
    }
    if (t.includes('batalha') || t.includes('guerra') || t.includes('confronto') || t.includes('colidem') || t.includes('ataque') || t.includes('invasão') || t.includes('combate') || t.includes('destino')) {
      return 'battle_counterattack';
    }
    if (t.includes('reencarnação') || t.includes('despertar') || t.includes('amigo') || t.includes('dragão') || t.includes('lorde demônio') || (volNum === 1 && chapterIndex <= 2) || (volNum === 5 && chapterIndex >= 4)) {
      return 'reincarnation_determination';
    }
    if ([13, 14, 15, 19, 20, 21, 22].includes(volNum) && chapterIndex >= 3) {
      return 'battle_counterattack';
    }
    if (t.includes('vida diária') || t.includes('cotidiano') || t.includes('paz') || t.includes('descanso') || t.includes('aldeia') || t.includes('vila')) {
      return 'peaceful_village';
    }

    return 'tempest_meeting_dynamic';
  }

  /**
   * Inicializa o observador de rolagem e insere os marcadores visuais de cena no texto.
   */
  function setupSceneScrollTransitions(volumeId, chapterIndex, chapterTitle) {
    if (sceneScrollObserver) {
      sceneScrollObserver.disconnect();
      sceneScrollObserver = null;
    }

    const proseArea = document.getElementById('reader-text-container');
    if (!proseArea) return;

    const baseVol = String(volumeId || '').replace(/-scan$/, '');
    const key = `${baseVol}:${chapterIndex}`;
    const explicitCues = CHAPTER_SCENE_MAPPINGS[key] || [];

    // Se temos mapeamento explícito para este capítulo (ex: Volume 6 Cap 1)
    if (explicitCues.length > 0) {
      explicitCues.forEach((cue) => {
        const targetP = document.getElementById(`p-${cue.pIndex}`);
        if (targetP && cue.pIndex > 0) { // Não duplica no primeiro parágrafo pois já tem o banner do topo
          let cueDiv = targetP.previousElementSibling;
          if (!cueDiv || !cueDiv.classList.contains('soundtrack-scene-cue')) {
            const track = TRACK_CATALOG.find(t => t.id === cue.trackId) || TRACK_CATALOG[0];
            cueDiv = document.createElement('div');
            cueDiv.className = 'soundtrack-scene-cue';
            cueDiv.setAttribute('data-track-id', track.id);
            cueDiv.innerHTML = `
              <div class="scene-cue-left">
                <span class="scene-cue-icon">🎵</span>
                <span class="scene-cue-text">Cena: <strong>${escapeHtml(cue.title || track.title)}</strong></span>
              </div>
              <button type="button" class="btn-cue-play" aria-label="Sintonizar trilha desta cena">▶ Sintonizar</button>
            `;
            targetP.parentNode.insertBefore(cueDiv, targetP);
          }
        }
      });
    } else {
      // Detector dinâmico em quebras de cena (<hr class="scene-break">)
      const hrs = proseArea.querySelectorAll('hr.scene-break');
      hrs.forEach(hr => {
        let sample = '';
        let nextEl = hr.nextElementSibling;
        let count = 0;
        while (nextEl && count < 3) {
          if (nextEl.tagName === 'P') {
            sample += ' ' + nextEl.textContent;
            count++;
          }
          nextEl = nextEl.nextElementSibling;
        }

        const sampleLow = sample.toLowerCase();
        let detectedTrackId = null;
        let cueTitle = '';

        if (sampleLow.includes('sarion')) {
          detectedTrackId = 'sarion_dynasty';
          cueTitle = '🏰 Dinastia Feiticeira de Sarion';
        } else if (['clayman', 'palhaço', 'conspiração', 'traição', 'laplace'].some(k => sampleLow.includes(k))) {
          detectedTrackId = 'conspiracy_takurami';
          cueTitle = '🎭 Conspiração & Mistério';
        } else if (['reunião', 'conferência', 'conselho', 'sala de reuniões'].some(k => sampleLow.includes(k))) {
          detectedTrackId = 'tempest_meeting_dynamic';
          cueTitle = '🏛️ Reunião em Tempest';
        } else if (['batalha', 'combate', 'ataque', 'espada'].some(k => sampleLow.includes(k))) {
          detectedTrackId = 'battle_counterattack';
          cueTitle = '⚔️ Confronto & Batalha';
        } else if (['labirinto', 'dungeon', 'ramiris'].some(k => sampleLow.includes(k))) {
          detectedTrackId = 'dungeon_management';
          cueTitle = '🌀 O Labirinto de Ramiris';
        } else if (['festa', 'banquete', 'festival'].some(k => sampleLow.includes(k))) {
          detectedTrackId = 'festival_banquet';
          cueTitle = '🎊 Banquete do Festival';
        }

        if (detectedTrackId) {
          const track = TRACK_CATALOG.find(t => t.id === detectedTrackId);
          if (track) {
            let cueDiv = hr.nextElementSibling;
            if (!cueDiv || !cueDiv.classList.contains('soundtrack-scene-cue')) {
              cueDiv = document.createElement('div');
              cueDiv.className = 'soundtrack-scene-cue';
              cueDiv.setAttribute('data-track-id', track.id);
              cueDiv.innerHTML = `
                <div class="scene-cue-left">
                  <span class="scene-cue-icon">🎵</span>
                  <span class="scene-cue-text">Cena: <strong>${escapeHtml(cueTitle || track.title)}</strong></span>
                </div>
                <button type="button" class="btn-cue-play" aria-label="Sintonizar trilha desta cena">▶ Sintonizar</button>
              `;
              hr.parentNode.insertBefore(cueDiv, hr.nextSibling);
            }
          }
        }
      });
    }

    // Configura IntersectionObserver para disparar na rolagem
    const cues = proseArea.querySelectorAll('.soundtrack-scene-cue');
    if (cues.length > 0 && 'IntersectionObserver' in window) {
      sceneScrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const trackId = entry.target.getAttribute('data-track-id');
            if (trackId && trackId !== activeSceneTrackId) {
              activeSceneTrackId = trackId;
              const newTrack = TRACK_CATALOG.find(t => t.id === trackId);
              if (newTrack) {
                // Se a música está tocando e a opção de troca automática estiver ligada:
                if (isPlaying && isAutoSuggest && newTrack.id !== currentTrack.id) {
                  playTrack(newTrack, true);
                  showSceneToast(`🎵 Mudança de Cena: ${newTrack.title}`);
                }
                syncUiState();
              }
            }
          }
        });
      }, {
        root: null,
        rootMargin: '-15% 0px -65% 0px',
        threshold: 0
      });

      cues.forEach(c => sceneScrollObserver.observe(c));
    }

    // Adiciona evento de clique em todos os botões de cena inline
    proseArea.querySelectorAll('.soundtrack-scene-cue').forEach(cue => {
      const btn = cue.querySelector('.btn-cue-play');
      if (btn) {
        btn.addEventListener('click', () => {
          const trackId = cue.getAttribute('data-track-id');
          const track = TRACK_CATALOG.find(t => t.id === trackId);
          if (track) {
            if (currentTrack.id === track.id) {
              togglePlay();
            } else {
              playTrack(track, true);
              showSceneToast(`🎵 Sintonizado: ${track.title}`);
            }
          }
        });
      }
    });
  }

  /**
   * Chamado pelo leitor (app.js) quando o usuário abre ou troca de capítulo.
   */
  function handleChapterChange(volumeId, chapterIndex, chapterTitle) {
    if (!volumeId) return;

    const baseVol = String(volumeId || '').replace(/-scan$/, '');
    const key = `${baseVol}:${chapterIndex}`;
    const explicitCues = CHAPTER_SCENE_MAPPINGS[key] || [];

    // O primeiro tema do capítulo é o primeiro cue da lista ou o classificador geral
    const initialTrackId = (explicitCues.length > 0 && explicitCues[0].trackId)
      ? explicitCues[0].trackId
      : determineChapterTrack(volumeId, chapterIndex, chapterTitle);

    const initialTrack = TRACK_CATALOG.find(t => t.id === initialTrackId) || TRACK_CATALOG[0];

    renderChapterSoundtrackBadge(initialTrack);

    // Se o usuário já estava ouvindo música e tem auto-suggest ligado:
    if (isPlaying && isAutoSuggest && initialTrack && initialTrack.id !== currentTrack.id) {
      playTrack(initialTrack, true);
      showSceneToast(`🎵 Capítulo: ${initialTrack.title}`);
    }

    // Configura os observadores de cena no texto
    setTimeout(() => {
      setupSceneScrollTransitions(volumeId, chapterIndex, chapterTitle);
    }, 150);
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
          showSceneToast(`🎵 Trilha Iniciada: ${track.title}`);
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
