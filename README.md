# 🌀 Tensei Shitara Slime Datta Ken — Biblioteca & Leitor Web em Português

Uma aplicação web estática, moderna e responsiva dedicada a reunir, comparar, padronizar e ler todo o universo da novel de **Tensei Shitara Slime Datta Ken** (*That Time I Got Reincarnated as a Slime*) em Português Brasileiro (PT-BR).

Projetada para funcionar tanto localmente no seu computador quanto hospedada no **GitHub Pages**, com **salvamento automático de progresso de leitura** no navegador (`localStorage`), separação rigorosa entre **Web Novel** e **Light Novel**, galeria de ilustrações oficiais de **Mitz Vah**, guia cultural com termos originais japoneses e links diretos para apoiar as edições oficiais na **Amazon Brasil**.

---

## ✨ Principais Funcionalidades

### 1. 📘 Separação Estrita: Light Novel vs Web Novel
- **Light Novel (LN)**: A obra comercial e definitiva escrita por Fuse e ilustrada por Mitz Vah.
  - Volumes **1 a 13 (+ 8.5)** completamente compilados localmente em JSON com mais de **45.000 parágrafos**.
  - Volumes **14 a 21** mapeados com sinopses, status de publicação e links externos.
  - Galeria integrada com **171 ilustrações oficiais** em alta definição.
- **Web Novel (WN)**: O rascunho original serializado no *Shousetsuka ni Narou*.
  - **255 capítulos** categorizados e estruturados em **10 Grandes Arcos** narrativos.
  - Capítulos iniciais já baixados para leitura imediata, com scripts incluídos para sincronizar ou baixar qualquer capítulo do *Central Novel*.

### 2. 🔖 Salvamento Inteligente de Progresso (`localStorage`)
- **Auto-Save Contínuo**: Conforme você lê e rola o texto, o leitor salva automaticamente o volume, capítulo e a porcentagem exata de rolagem da tela.
- **Banner "Continuar Lendo"**: Ao reabrir o site, um banner no topo avisa onde você parou com um botão que leva diretamente à página e à posição exata de leitura.
- **Marcadores & Anotações**: Clique em qualquer parágrafo da novel para adicionar marcadores personalizados com suas próprias notas.

### 3. ⚙️ Experiência de Leitura Customizável
- **4 Temas Visuais**:
  - 🌙 **Noite (Dark)**: Fundo ardósia profundo (#0b1120) para leitura noturna suave.
  - ☀️ **Dia (Claro)**: Tons quentes de pergaminho (#fdfbf7) para alta legibilidade.
  - 📜 **Sépia**: Estilo clássico de livro vintage (#f4ecd8).
  - 🖤 **OLED**: Preto absoluto (#000000) para economia de bateria e telas OLED.
- **Tipografia Adaptativa**:
  - **Moderna**: Inter (sem serifa).
  - **Livro**: Merriweather / Georgia (serifada para romances literários).
  - **Dislexia**: OpenDyslexic (desenhada para facilitar leitura).
  - **Mono**: Fira Code / Consolas.
- **Ajustes de Escala**: Controle de tamanho de texto (14px a 28px), espaçamento de linha e barra de progresso em tempo real no topo da tela.

### 4. ⚖️ Comparador Aprofundado (WN x LN)
- Guia detalhado explicando por que Fuse reescreveu mais de 50% da história na Light Novel.
- Cards comparativos analisando divergências em arcos fundamentais:
  - *Charybdis* e o Reino de Eurazania (Lorde Carrion);
  - A convocação de *Diablo* no massacre de Farmas (*Megiddo*);
  - A conspiração política do *Walpurgis* e o papel de Guy Crimson;
  - A diplomacia com *Hinata Sakaguchi* e a Santa Igreja;
  - A *Família Rosso e Mariabell* (exclusivos da LN);
  - O paradoxo dos ciclos temporais do *Herói do Tempo (Chloe Aubert & Chronoa)*;
  - As *Três Progenitoras Demônios* (Testarossa, Ultima, Carrera);
  - A invasão militar do *Império Oriental* no Labirinto;
  - O verdadeiro vilão final e o clímax da história.

### 5. 🌸 Guia Cultural & Nomenclatura Original
- **Honoríficos Japoneses**: Explicações contextuais para `-sama`, `-san`, `-kun`, `-chan`, `senpai/kouhai` e `danna`.
- **Sistemas de Poder Canônicos**: A importância de nomear monstros (*Naming*), *Majin*, *Kijin*, *Dragões Verdadeiros*, as Habilidades Definitivas (*Ultimate Skills*) e a evolução da consciência de Rimuru (*Grande Sábio → Raphael → Ciel*).
- **Cultura e Culinária**: Como a gastronomia japonesa (ramen, gyoza, shoyu) e as águas termais (*onsen*) foram utilizadas por Rimuru como instrumentos diplomáticos de paz (*Wa*).

### 6. 🛒 Catálogo Oficial Amazon Brasil
- Seção com links diretos de pesquisa e compra na **Amazon.com.br** para todos os Volumes 1 a 21.
- Informações sobre edições digitais para **Kindle** e livros físicos importados (**Yen Press**).

### 7. 🛠️ Corretor e Padronizador de Tradução (`scripts/fix_translation.py`)
- Ferramenta em Python criada especificamente para revisar traduções rápidas/automáticas de arquivos do Google Drive.
- Corrige nomes próprios, substitui termos em inglês ou transliterações errôneas por nomes canônicos e melhora a pontuação e gramática em Português do Brasil.

---

## 📂 Estrutura de Diretórios

```
Tensei Shitara Slime Novel/
├── index.html                   # Interface do Leitor e Catálogo (SPA)
├── assets/
│   ├── css/
│   │   └── style.css            # Estilos modernos, responsivos e temas
│   ├── js/
│   │   └── app.js               # Motor do leitor, roteamento e LocalStorage
│   └── images/
│       └── slime.svg            # Ícone vetorial do Rimuru Slime
├── data/
│   ├── catalog.json             # Catálogo mestre estruturado
│   ├── illustrations.json       # 171 ilustrações oficiais catalogadas
│   ├── light_novel/             # Volumes 1 a 13 (+ 8.5) completos em JSON
│   └── web_novel/               # Capítulos da Web Novel em JSON
├── scripts/
│   ├── fix_translation.py       # Módulo corretor e revisor de traduções
│   ├── polish_all_data.py       # Script de revisão em lote dos dados
│   ├── compile_ln.py            # Extrator/compilador da Light Novel
│   └── compile_wn.py            # Extrator/compilador da Web Novel
├── drive_files/                 # Pasta para colocar arquivos do seu Google Drive
└── README.md                    # Documentação do projeto
```

---

## 🚀 Como Executar Localmente

### Opção 1: Abrir Diretamente no Navegador
Basta dar dois cliques no arquivo `index.html` ou arrastá-lo para qualquer navegador moderno (Chrome, Edge, Firefox, Brave, Safari).

### Opção 2: Servidor Local Leve (Recomendado)
Para evitar restrições de CORS locais em alguns navegadores ao carregar arquivos JSON locais:
```bash
# Na pasta do projeto, execute:
python -m http.server 8000
```
Em seguida, abra seu navegador em: `http://localhost:8000`

---

## 🌐 Como Publicar no GitHub e Ativar o GitHub Pages

1. Crie um novo repositório vazio na sua conta do **GitHub** (ex: `tensei-shitara-slime-novel`).
2. No terminal da pasta do projeto, execute:
   ```bash
   git remote add origin https://github.com/SEU_USUARIO/tensei-shitara-slime-novel.git
   git branch -M main
   git push -u origin main
   ```
3. No GitHub:
   - Acesse **Settings** (Configurações) do repositório.
   - Na barra lateral esquerda, clique em **Pages**.
   - Em **Build and deployment** > **Branch**, selecione `main` e a pasta `/ (root)`.
   - Clique em **Save**.
4. Em poucos segundos, seu site de leitura estará disponível publicamente no link fornecido pelo GitHub!

---

## 🔧 Como Revisar Arquivos do seu Google Drive

Caso você tenha baixado arquivos da sua pasta do Google Drive (`1GM_wQEc6KIp5F3GmqUOLY8XGN8dkUv45`) que possuam erros ou tradução rápida:

1. Coloque o arquivo `.txt` ou `.json` dentro da pasta `drive_files/`.
2. Execute o corretor:
   ```bash
   python scripts/fix_translation.py drive_files/meu_arquivo.txt drive_files/meu_arquivo_revisado.txt
   ```
3. O script aplicará automaticamente todo o glossário canônico de nomes, habilidades e concordância gramatical em Português Brasileiro.

---

## 📜 Fontes & Créditos

- **Autor Original**: Fuse (伏瀬)
- **Ilustrador Oficial**: Mitz Vah (みっつばー)
- **Editoras Oficiais**: Micro Magazine (Japão) / Yen Press (EUA)
- **Tradução da Light Novel**: [TSSDK Scan PT-BR](https://sites.google.com/view/tssdklscanptbr/p%C3%A1gina-inicial)
- **Tradução da Web Novel**: [Central Novel](https://centralnovel.com/series/tensei-shitara-slime-datta-ken/)
- **Pasta de Origem no Drive**: [Google Drive TSSDK](https://drive.google.com/drive/u/0/folders/1GM_wQEc6KIp5F3GmqUOLY8XGN8dkUv45)
- **Loja Oficial**: [Amazon Brasil](https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+light+novel)
