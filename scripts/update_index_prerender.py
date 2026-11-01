import json
import re

with open('data/catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

sr = cat['story_recap']
bp = sr['beginner_pitch']
pt = sr['progression_timeline']

def escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

synopsis_html = escape_html(bp['synopsis']).replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
synopsis_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', synopsis_html)

recom_html = escape_html(bp['recommendation']).replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
recom_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', recom_html)

pillars_html = '\n'.join([f'''              <div class="pillar-card">
                <div class="pillar-icon">{escape_html(p["icon"])}</div>
                <h4 class="pillar-title">{escape_html(p["title"])}</h4>
                <p class="pillar-desc">{escape_html(p["desc"])}</p>
              </div>''' for p in bp['pillars']])

cards_html = []
for item in pt:
    lines = [l for l in item['summary_two_lines'].split('\n') if l]
    line1 = escape_html(lines[0]) if len(lines) > 0 else ''
    line2 = escape_html(lines[1]) if len(lines) > 1 else ''

    card = f'''          <article class="progression-card" data-vol-id="{escape_html(item['vol_id'])}">
            <div class="progression-card-top">
              <span class="progression-vol-badge">{escape_html(item['vol_num'])}</span>
              <span class="progression-scale-badge">{escape_html(item['scale'])}</span>
            </div>
            <h4 class="progression-title">{escape_html(item['title'])}</h4>
            <p class="progression-theme"><span class="progression-theme-label">Escopo &amp; Foco:</span> {escape_html(item['theme_scope'])}</p>
            <div class="progression-spoiler-box" aria-label="Resumo em 2 Linhas com spoiler leve">
              <div class="progression-spoiler-header">
                <span aria-hidden="true">👁️</span> <strong>Resumo em 2 Linhas:</strong>
              </div>
              <p class="progression-two-lines">
                <span class="p2-line"><span class="p2-bullet">•</span> {line1}</span>
                <span class="p2-line"><span class="p2-bullet">•</span> {line2}</span>
              </p>
            </div>
            <div class="progression-card-footer">
              <button type="button" class="btn-secondary-pill btn-progression-read" data-action="open-ln" data-vol="{escape_html(item['vol_id'])}">
                📖 Ler {escape_html(item['vol_num'])} →
              </button>
            </div>
          </article>'''
    cards_html.append(card)

grid_cards_html = '\n'.join(cards_html)

new_beginner_panel = f'''      <!-- PAINEL 1: NOVO POR AQUI? (GUIA SEM SPOILER & PROGRESSÃO EM 2 LINHAS) -->
      <div id="recap-panel-beginner" class="recap-panel active" role="tabpanel" aria-labelledby="btn-recap-audience-beginner">
        <!-- Hero Pitch para Iniciantes -->
        <div class="section-hero hero-recap hero-beginner">
          <div class="hero-badges">
            <span class="hero-tag">Guia Oficial para Iniciantes</span>
            <span class="hero-stat">24 Volumes • Da Caverna ao Fim do Universo</span>
          </div>
          <h2 id="heading-recap-beginner">Novo no Universo de Tensura? Comece por Aqui!</h2>
          <p id="recap-beginner-tagline" class="recap-tagline-text">
            {escape_html(bp['tagline'])}
          </p>
        </div>

        <!-- Card de Sinopse & 4 Pilares -->
        <article class="beginner-pitch-card">
          <div class="beginner-pitch-body">
            <h3 class="beginner-pitch-title">📖 O que é Tensei Shitara Slime Datta Ken?</h3>
            <p id="beginner-synopsis-text" class="beginner-synopsis">
              {synopsis_html}
            </p>

            <div class="beginner-pillars-grid" id="beginner-pillars-grid">
{pillars_html}
            </div>

            <div class="beginner-recommendation-box">
              <div class="recom-icon">💡</div>
              <div class="recom-content">
                <strong>Por que ler a Light Novel no Volume 1?</strong>
                <p id="beginner-recom-text">
                  {recom_html}
                </p>
                <div class="beginner-cta-row">
                  <button type="button" class="btn-primary-glow btn-recap-start" data-action="open-ln" data-vol="vol-01">
                    📖 Começar Leitura pelo Volume 1 →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </article>

        <!-- Seção: Como a Trama Vai Crescendo (Vols 1 a 23 + 8.5) -->
        <section class="recap-block progression-timeline-section" aria-labelledby="progression-heading">
          <div class="progression-header-wrap">
            <div>
              <h3 id="progression-heading" class="subsection-heading">📈 Como a Trama Vai Crescendo (Volumes 1 a 23 + 8.5)</h3>
              <p class="section-subtext">Veja a evolução da escala de poder, política e nações ao longo de cada livro.</p>
            </div>

            <!-- Controle Toggle: Sem Spoiler vs Com Spoiler Leve (2 Linhas) -->
            <div class="progression-toggle-bar">
              <span class="toggle-bar-label">Modo de Exibição:</span>
              <div class="segmented-control" role="radiogroup" aria-label="Modo de spoiler da linha de progressão">
                <button type="button" class="segmented-btn active" id="btn-progression-spoiler-free" role="radio" aria-checked="true" data-mode="free">
                  🛡️ Sem Spoilers (Apenas Escopo &amp; Temas)
                </button>
                <button type="button" class="segmented-btn" id="btn-progression-spoiler-two-lines" role="radio" aria-checked="false" data-mode="two-lines">
                  👁️ Com Spoiler Leve (Resumo em 2 Linhas)
                </button>
              </div>
            </div>
          </div>

          <div id="progression-timeline-grid" class="progression-grid mode-spoiler-free">
{grid_cards_html}
          </div>
        </section>
      </div>'''

with open('index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

# Replace the old panel
pattern = r'<!-- PAINEL 1: NOVO POR AQUI\?.*?<!-- PAINEL 2: JÁ VI O ANIME'
match = re.search(pattern, index_html, re.DOTALL)
if match:
    index_html = index_html[:match.start()] + new_beginner_panel + '\n\n      <!-- PAINEL 2: JÁ VI O ANIME' + index_html[match.end():]
    print('Replaced beginner panel in index.html!')
else:
    print('ERROR: Pattern not found!')

# Update cache busters in index.html
index_html = re.sub(r'href="assets/css/style\.css(?:\?[^"]*)?"', 'href="assets/css/style.css?v=20261101_v6"', index_html)
index_html = re.sub(r'src="assets/js/app\.js(?:\?[^"]*)?"', 'src="assets/js/app.js?v=20261101_v6"', index_html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

print('Updated index.html successfully with pre-rendered content and cache buster v6!')
