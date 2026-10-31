# 🌀 Tensei Shitara Slime Datta Ken — Biblioteca & Leitor Completo em Português

Uma aplicação web estática, moderna, rápida e 100% em **Português Brasileiro (PT-BR)** criada para reunir, revisar, comparar e ler todo o universo de **Tensei Shitara Slime Datta Ken** (*That Time I Got Reincarnated as a Slime*), escrita por **Fuse** e ilustrada por **Mitz Vah**.

Pronta tanto para leitura local offline no seu PC (`Iniciar_Leitor.bat`) quanto publicada online no **GitHub Pages** (**https://cdiangell-dei.github.io/tensei-shitara-slime-novel/**), com **salvamento automático de progresso** (`localStorage` + backup `.json`), separação estrita entre **Light Novel** e **Web Novel**, centenas de ilustrações oficiais locais em WebP, notas culturais interativas e links diretos para a **Amazon Brasil**.

---

## ✨ O Que Foi Compilado, Comparado e Revisado

### 1. 📘 Light Novel Completa & Ilustrada (Separada da Web Novel)
- **21 Volumes Disponíveis Offline (`Volumes 1 a 20 + Volume 8.5`)**:
  - **Volumes 1 a 5 + 8.5**: Compilados a partir da tradução de fã da *TSSDK Scan PT-BR*, higienizados e padronizados com todas as ilustrações oficiais posicionadas dentro dos capítulos.
  - **Volumes 6 a 20 (incluindo Edições Coloridas 11–17 e 20)**: Extraídos e reparados a partir dos EPUBs da sua pasta `drive_files/`, preservando capas, ilustrações duplas coloridas, páginas de mangá bônus, os **13 Gráficos Oficiais de Poder do Volume 16**, posfácios de Fuse e **570 notas culturais e de tradução interativas** (`[Nota N]`).
- **Alternância Dupla de Tradução (`Volumes 6 a 13`)**:
  - Nos volumes em que ambas as fontes se sobrepõem, há um botão no topo do leitor para alternar instantaneamente entre a **✨ Edição Ilustrada Revisada (Drive)** e a **👥 Tradução de Fã (TSSDK Scan)** mantendo o mesmo capítulo e ponto de leitura!
- **EPUBs Revisados para Kindle / Celular (`drive_files_corrigidos/`)**:
  - Além do leitor web, o pipeline também gerou versões `.epub` corrigidas dos seus 15 volumes do Drive na pasta local `drive_files_corrigidos/` (ignorada pelo `.gitignore` para manter o repositório Git leve).

### 2. 📜 Web Novel Original 100% Completa (Separada da Light Novel)
- **303 de 303 Capítulos Offline**:
  - **255 Capítulos Principais** (`Capítulo 0` a `Capítulo 249`, incluindo as intermissões `.5`: `18.5`, `161.5` e `185.5`) organizados em **10 Grandes Arcos**.
  - **48 Capítulos Extras Pós-Final** (`Extra 01` a `Extra 48`), abrangendo *O Jogo de Fuga Elegante de Rimuru*, *Visita ao Desconhecido* e *Histórias Especiais de Tempest*, organizados em **3 Arcos Extras**.

### 3. 🛠️ Revisão de Tradução & Padronização Canônica (`scripts/fix_translation.py`)
Os arquivos públicos da pasta `drive_files/` possuíam tradução rápida/automática com erros graves de nomes, gênero e termos em inglês. Mais de **2.380 blocos** foram corrigidos automaticamente usando nossa base comparativa:
- **Nomes Próprios Restaurados**: `Fusível` → `Fuse`, `Campo de golfe` → `Feldway`, `Cara` / `Cara Carmesim` → `Guy` / `Guy Crimson`, `Carreira` → `Carrera`, `Lacaio` → `Footman`, `Rasgue a 'Lágrima'` → `Tear`, `Musgo` → `Moss`, `Espírito` → `Esprit`, `Nome: Diabo` → `Nome: Diablo`, `Zegião` → `Zegion`.
- **Fichas de Status & Concordância**: `Corrida:` (*Race*) → `Raça:`, `Classificação de Contagem` (*Count Rank*) → `Classe Conde`, `Nove Caldas` → `Nove Caudas`, `Primordial Branco/Amarelo/Violeta` → `Primordial Branca/Amarela/Violeta` (Testarossa, Carrera e Ultima).
- **100% em Português**: Tradução de mais de 60 *Ultimate Skills*, títulos e patentes deixados em inglês (*Void God Azathoth* → *Deus do Vazio Azathoth*, *Gluttonous King Beelzebuth* → *Rei da Gula Beelzebuth*, *Soul Corridor* → *Corredor da Alma*), além de falsos cognatos (*"O gol de um santo"* → *"O Objetivo de um Santo"*, *"fotografar"* → *"atirar"*).

### 4. 🌸 Guia Cultural Japonês & Notas Interativas no Texto
- Aba dedicada explicando honoríficos japoneses (`-sama`, `-san`, `-kun`, `-chan`, `-dono`, `-sensei`, `Senpai/Kouhai`, `Danna/Aniki`), conceitos originais (`Majin`, `Kijin`, `Naming`, `Dragões Verdadeiros`, `Primordiais`, `Manas: Ciel`, `EP`) e aspectos culturais (`Onsen`, culinária diplomática, `Wa`, `Matsuri` e sincretismo mitológico).
- Durante a leitura, clique em qualquer selo **`[Nota N]`** ou termo cultural pontilhado para abrir a explicação sem perder seu lugar no capítulo!

### 5. 🔖 Progresso de Leitura Persistente & Portável
- **Memória Independente LN & WN**: Salva separadamente onde você parou na Light Novel e na Web Novel, além da porcentagem lida em cada volume/capítulo.
- **Marcadores com Anotações**: Clique no ícone `🔖` ao lado de qualquer parágrafo para guardar trechos favoritos com notas pessoais.
- **Exportar / Importar JSON**: Em `⚙️ Configurações`, você pode exportar seu progresso em `.json` e importar no celular ou no GitHub Pages.

### 6. 🛒 Links Diretos da Amazon Brasil
- Aba dedicada e botões rápidos em cada card de volume levando diretamente às edições oficiais da Light Novel (Kindle / físico) e do Mangá (Editora JBC) na **Amazon.com.br**.

---

## 📂 Estrutura do Repositório

```text
Tensei Shitara Slime Novel/
├── index.html                        # Aplicação Web Semântica (Catálogo, Leitor e Modais <dialog>)
├── Iniciar_Leitor.bat                # Atalho Windows para abrir o leitor localmente com 1 clique
├── assets/
│   ├── css/style.css                 # Temas (Sistema, Dia, Noite, Sépia, OLED) e tipografia literária
│   ├── js/app.js                     # Motor do leitor, galerias, notas culturais e LocalStorage
│   ├── images/slime.svg              # Ícone vetorial do Rimuru
│   └── illustrations/ln/             # +420 ilustrações oficiais otimizadas localmente em WebP
├── data/
│   ├── catalog.json                  # Catálogo mestre (LN, WN, Comparador, Guia Cultural e Amazon BR)
│   ├── illustrations.json            # Índice consolidado de ilustrações locais por volume
│   ├── translation_comparison.json   # Relatório real de auditoria Antes vs. Depois dos EPUBs
│   ├── light_novel/                  # 29 arquivos JSON (Vols. 1–20 + 8.5 + alternativas Scan 6–13)
│   └── web_novel/                    # 303 capítulos completos em JSON (0–249 + 48 Extras)
├── scripts/
│   ├── fix_translation.py            # Motor corretor PT-BR (.epub, .json e .txt)
│   ├── build_light_novel.py          # Pipeline completo da Light Novel (TSSDK + Drive EPUBs + WebP)
│   ├── compile_wn.py                 # Compilador completo da Web Novel (Central Novel + fallback)
│   ├── polish_all_data.py            # Higienização em lote de todos os JSONs
│   └── generate_master_catalog.py    # Gerador do data/catalog.json
├── drive_files/                      # Seus arquivos .epub originais (ignorados no Git)
└── drive_files_corrigidos/           # Seus 15 arquivos .epub já revisados em PT-BR (ignorados no Git)
```

---

## 🚀 Como Abrir e Ler no Seu Computador

Como navegadores modernos bloqueiam requisições `fetch()` em arquivos abertos via `file://`, basta iniciar um servidor local leve:

### Opção 1: Com 2 Cliques no Windows (Mais Fácil)
Dê dois cliques no arquivo **`Iniciar_Leitor.bat`** na raiz do projeto. Ele iniciará o servidor Python e abrirá `http://localhost:8080` automaticamente no seu navegador!

### Opção 2: Via Terminal
```powershell
python -m http.server 8080
```
Depois acesse **`http://localhost:8080`** no navegador.

---

## 🌐 Como Publicar no GitHub Pages

O `.gitignore` já está configurado para ignorar os arquivos `.epub` pesados (`drive_files/` e `drive_files_corrigidos/`), mantendo apenas os JSONs otimizados e as ilustrações WebP para o site carregar rápido no GitHub Pages:

- **Repositório GitHub**: https://github.com/CDiangell-dei/tensei-shitara-slime-novel
- **Leitor Online (GitHub Pages)**: https://cdiangell-dei.github.io/tensei-shitara-slime-novel/

Caso precise ativar/verificar nas configurações do repositório:
1. Acesse https://github.com/CDiangell-dei/tensei-shitara-slime-novel/settings/pages
2. Em **Build and deployment → Branch**, selecione **`main`** e a pasta **`/ (root)`**, e clique em **Save**.

---

## 📜 Créditos & Fontes

- **Autor Original**: Fuse (伏瀬) • **Ilustrações Oficiais**: Mitz Vah (みっつばー)
- **Light Novel (Fã Scan Vols. 1–13 + 8.5)**: [TSSDK Scan PT-BR](https://sites.google.com/view/tssdklscanptbr/p%C3%A1gina-inicial)
- **Arquivos EPUB Revisados (Vols. 6–20)**: [Pasta Google Drive](https://drive.google.com/drive/u/0/folders/1GM_wQEc6KIp5F3GmqUOLY8XGN8dkUv45)
- **Web Novel em Português**: [Central Novel](https://centralnovel.com/series/tensei-shitara-slime-datta-ken/)
- **Edições Oficiais**: [Amazon Brasil](https://www.amazon.com.br/s?k=tensei+shitara+slime+datta+ken+light+novel)
