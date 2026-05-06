# Dashboard — Campeonato Brasileiro Série A 2017

Dashboard interativo em **Python + Pandas + Dash + Plotly** que analisa o desempenho dos clubes do Brasileirão 2017, mais uma versão equivalente em **Excel** gerada programaticamente.

Projeto da disciplina *Dashboard em Python* — Insper.

![Stack](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-4.x-119DFF)
![Plotly](https://img.shields.io/badge/Plotly-6.x-3F4F75)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![Excel](https://img.shields.io/badge/Excel-XlsxWriter-217346?logo=microsoft-excel&logoColor=white)

---

## Sumário

- [Visão geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como executar](#como-executar)
- [Versão Excel](#versão-excel)
- [Decisões de design](#decisões-de-design)
- [Fonte dos dados](#fonte-dos-dados)
- [Próximos passos](#próximos-passos)

---

## Visão geral

Duas entregas a partir do mesmo dataset:

1. **Dashboard web interativo** (`app.py`) — tema escuro estilo painel esportivo, hero section com logo do clube, identidade visual reagindo ao time selecionado, gráficos Plotly e tabela clicável.
2. **Dashboard Excel** (`dashboard_brasileirao_2017.xlsx`) — gerado por `src/excel_dashboard.py` com 6 abas, KPIs, tabela formatada e 3 gráficos embutidos.

A camada de dados é compartilhada entre as duas: `src/data_loader.py` e `src/data_processing.py` calculam tudo uma única vez e ambas as saídas consomem os mesmos DataFrames.

## Funcionalidades

### Dashboard web (Dash)

- **Tema escuro** com identidade visual sincronizada à cor oficial de cada clube.
- **Hero section** rica: logo do clube, posição, pontos, aproveitamento (com comparação vs média da liga), saldo, **maior vitória**, **maior derrota** e **forma recente** (últimos 5 jogos como pílulas V/E/D coloridas).
- **8 KPI cards reativos**:
  - Modo time: jogos, V/E/D, gols pró/sofridos, **finalizações** (com chutes/jogo + escanteios) e **conversão** (% gols/chutes, com progress bar).
  - Modo liga: % mandante/empate/visitante, total de gols, maior goleada, líder em gols, campeão e vice.
- **Tabela de classificação** ordenável (clique nos cabeçalhos), com **tooltips** explicando cada coluna (P, J, V, E, D, GP, GC, SG, %), faixas G4/Z4 destacadas e clicável (clicar numa linha seleciona o clube em todo o dashboard).
- **4 gráficos** reativos ao clube:
  - Pontos acumulados por rodada (com linha tracejada do campeão como referência).
  - Casa vs Fora (V/E/D do clube ou distribuição da liga).
  - Gols marcados — Top 10 (com clube destacado, mesmo se fora do Top 10).
  - Gols pró × sofridos — Top 10.
- **Top 10 jogos com mais gols** em tabela HTML estilizada, com placares destacados em pílula e linhas do clube tingidas em accent.
- **Display names** com tildes/abreviações corretas (Grêmio, São Paulo, Athletico-PR, Atlético-MG, etc.).
- **Footer com link do GitHub**, fonte do dataset e crédito.
- Responsivo: 3 breakpoints (1180 px, 980 px, 760 px).

### Dashboard Excel

- **6 abas**, com a aba `Dashboard` como primeira:
  - `Dashboard` — visão visual com header escuro, 6 KPI cards, tabela de classificação formatada, 3 gráficos embutidos e tabela de top jogos.
  - `Desempenho_Times` — uma linha por clube, com filtros, freeze pane e autofilter.
  - `Jogos_Top_Gols` — top 10 jogos de mais gols.
  - `Casa_Fora` — métricas por clube divididas entre mando e visitante.
  - `Base_Tratada` — 380 jogos da Série A 2017, limpos e padronizados.
  - `Base_Raw` — dataset original do Kaggle (10.296 linhas) preservado.

- **6 KPIs no topo**: total de jogos, total de gols, média/jogo, campeão, maior ataque, melhor defesa.
- **Tabela de classificação** com posições G4/Z4 destacadas em verde/vermelho e cores zebradas.
- **Gráficos** embutidos com tema escuro:
  - Pontos por time (barra horizontal de 20 clubes).
  - Gols pró × sofridos · Top 10 (colunas agrupadas).
  - Pontos como mandante × visitante · Top 10.

## Estrutura do projeto

```
dashboard-brasileirao/
├── app.py                              # Dashboard web (Dash)
├── data/
│   ├── raw/
│   │   └── BR-Football-Dataset.csv     # dataset original do Kaggle
│   └── processed/                      # reservado
├── src/
│   ├── __init__.py
│   ├── data_loader.py                  # leitura e filtro do CSV
│   ├── data_processing.py              # tabela, métricas, casa/fora, liga
│   ├── teams.py                        # cor accent, slug do logo, display name
│   ├── charts.py                       # figuras Plotly (tema escuro reativo)
│   └── excel_dashboard.py              # gerador do .xlsx
├── assets/
│   ├── style.css                       # CSS escuro do dashboard web
│   └── logos/                          # PNGs dos clubes (slug = src/teams.py)
├── dashboard_brasileirao_2017.xlsx     # arquivo Excel gerado
├── requirements.txt
└── README.md
```

## Como executar

### Pré-requisitos

- Python 3.10+
- pip

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# ou: source .venv/bin/activate # Linux/macOS

pip install -r requirements.txt
```

### Dashboard web

```bash
python app.py
```

Abre em [http://127.0.0.1:8050](http://127.0.0.1:8050).

### Gerar o Excel

```bash
python -m src.excel_dashboard
```

Saída: `dashboard_brasileirao_2017.xlsx` na raiz.

## Versão Excel

O gerador (`src/excel_dashboard.py`) reaproveita 100% da camada de dados do app web. A paleta de cores é a mesma do dashboard Dash, adaptada às limitações dos gráficos nativos do Excel.

### Decisões práticas no Excel

| Decisão | Motivo |
|---------|--------|
| `xlsxwriter` em vez de `openpyxl` | Controle muito superior dos charts (cores, bg, plot area, legend), suporte a tema escuro nativo. |
| Aba `Dashboard` como primeira | Garante que ela é a primeira coisa que o avaliador vê ao abrir. |
| `set_tab_color` por aba | Dashboard em accent (azul), data sheets em cinza. |
| `hide_gridlines(2)` no Dashboard | Aparência de painel, não de planilha. |
| `freeze_panes` + `autofilter` nas data sheets | Navegação prática nos dados brutos. |
| Tabela de classificação com cores zebradas + bordas G4/Z4 | Replica o highlight da versão web. |
| Top 10 jogos como tabela formatada (não chart) | Chart de placares ficaria ruim — tabela com placar destacado funciona melhor. |
| Placar em texto `"3 x 6"` em vez de duas colunas | Igual à versão web; legibilidade. |
| Casa × Fora como column chart com `pontos_casa` vs `pontos_fora` (top 10) | Consistente com a métrica que importa (pontos). |

## Decisões de design

### Tema escuro reativo

A versão web usa CSS variable `--accent` que é sobrescrito no inline style do hero conforme o clube selecionado. Os gráficos Plotly recebem o accent como argumento e tingem barras/linhas. Times fora do destaque ficam em accent com alpha 0.4 para criar hierarquia.

### Display names em camada

`src/teams.py` mantém o nome cru do CSV como chave (`"Vasco Da Gama RJ"`, `"Sao Paulo"`) e o display em campo separado (`"Vasco da Gama"`, `"São Paulo"`). Toda lógica de filtro e agregação usa o nome cru; só a UI converte. Isso permitiu adicionar tildes/abreviações sem reprocessar dados.

### Tabela clicável

Um callback separado escuta `active_cell` da DataTable e atualiza o `value` do dropdown. O callback principal já reage a mudanças do dropdown, então o efeito é cascata sem código duplicado.

### Logo com fallback

`src/teams.py:logo_url()` detecta automaticamente arquivos em `assets/logos/{slug}.png|svg|jpg|webp`. Se não existir, o hero renderiza um badge circular com a abreviação do clube na cor oficial — o dashboard funciona com ou sem logos.

### Top 10 com clube garantido

`src/charts.py:_top_n_com_destaque` substitui o 10º colocado pelo clube selecionado quando ele está fora do Top 10, garantindo que ele apareça sempre destacado.

## Fonte dos dados

Dataset público **Brazilian Football Matches** disponível no Kaggle. O arquivo `BR-Football-Dataset.csv` contém 10.296 partidas de Copa do Brasil e Séries A, B e C entre 2014 e 2023; o dashboard filtra **apenas Série A 2017** (380 jogos, 20 clubes).

### Validações

- 380 jogos ✓
- 20 clubes ✓
- Corinthians campeão com 72 pontos ✓
- Atlético-GO rebaixado em último (36 pts) ✓
- Maior goleada: Chapecoense 3×6 Grêmio (9 gols) ✓
- Líder em gols pró: Palmeiras (61) ✓
- Melhor defesa: Corinthians (30 sofridos) ✓
- Total de finalizações: 8.183 (~21,5/jogo) ✓
- Conversão Corinthians: 12,5% (50 gols / 401 chutes) ✓

### Dados utilizados do CSV

Do dataset original são consumidas:

| Coluna   | Uso |
|----------|-----|
| `tournament` | Filtro: `Serie A` |
| `date`   | Filtro de ano (2017), ordenação cronológica, eixo do gráfico de pontos acumulados |
| `home`, `away` | Identificação dos clubes |
| `home_goal`, `away_goal` | Gols pró/contra, saldo, maior vitória/derrota, total de gols |
| `home_shots`, `away_shots` | Finalizações totais, chutes/jogo, % conversão |
| `home_corner`, `away_corner` | Escanteios pró por clube, escanteios/jogo |

As demais colunas do CSV (`home_attack`, `away_attack`, `ht_diff`, `at_diff`, `ht_result`, `at_result`, `total_corners`, `time`) **não são usadas** por não agregarem clareza ou serem redundantes com o que já é calculado.

## Próximos passos

- [ ] Filtros adicionais (range de rodadas, casa/fora) na versão web.
- [ ] Heatmap de confronto direto.
- [ ] Multi-select de clubes para comparação no gráfico de pontos acumulados.
- [ ] Deploy (Render / Fly.io) com link público.
- [ ] Adicionar métricas avançadas: xG, posse, escanteios (já no CSV mas não usadas).

---

**Autor:** Douglas Celestino · Insper · 2026
**Stack:** Python · Pandas · Dash · Plotly · XlsxWriter
