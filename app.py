"""Dashboard interativo — Campeonato Brasileiro Série A 2017."""

from dash import Dash, dcc, html, Input, Output, State, dash_table, no_update

from src.data_loader import load_serie_a_2017
from src.data_processing import (
    desempenho_casa_fora,
    liga_metricas,
    metricas_time,
    pontos_por_rodada,
    tabela_classificacao,
    top_jogos_mais_gols,
)
from src.charts import (
    MODEBAR_CONFIG,
    grafico_casa_fora,
    grafico_casa_fora_liga,
    grafico_gols_marcados,
    grafico_gols_pro_contra,
    grafico_pontos_acumulados,
    grafico_pontos_top_times,
)
from src.teams import LEAGUE_ACCENT, display, info as team_info, logo_url

TODOS = "Todos os times"
CHAMPION_RAW = "Corinthians"

df = load_serie_a_2017()
tabela = tabela_classificacao(df)
top_jogos = top_jogos_mais_gols(df, n=10)
liga = liga_metricas(df, tabela)
times = sorted(set(df["home"]).union(df["away"]))
opcoes_time = [{"label": TODOS, "value": TODOS}] + [
    {"label": display(t), "value": t} for t in times
]
TOP6_LIGA = [
    (row["time"], display(row["time"]), team_info(row["time"])["color"])
    for _, row in tabela.head(6).iterrows()
]
JOGOS_CAMPEAO = pontos_por_rodada(df, CHAMPION_RAW)

app = Dash(__name__)
app.title = "Brasileirão 2017 — Dashboard"


# ---------- helpers de UI ----------

def kpi_card(label: str, value, *, sub: str | None = None, progress: float | None = None,
             accent: str | None = None) -> html.Div:
    children = [html.Div(label, className="kpi-title"), html.Div(value, className="kpi-value")]
    if sub:
        children.append(html.Div(sub, className="kpi-sub"))
    if progress is not None:
        children.append(
            html.Div(
                html.Div(
                    style={"width": f"{min(progress, 100)}%", "background": accent or "var(--accent)"},
                    className="kpi-bar-fill",
                ),
                className="kpi-bar",
            )
        )
    style = {"--card-accent": accent} if accent else {}
    return html.Div(children, className="kpi-card", style=style)


def hero_logo(time: str | None) -> html.Div:
    info = team_info(time)
    src = logo_url(time) if time and time != TODOS else None
    if src:
        return html.Div(html.Img(src=src, className="hero-logo-img", alt=display(time)), className="hero-logo")
    return html.Div(
        info["abbr"],
        className="hero-logo hero-logo-fallback",
        style={
            "background": info["color"],
            "color": "#11141C" if info["color"] in ("#F5F5F5", "#EAEAEA", "#E5E5E5", "#F4D43A") else "#FFFFFF",
        },
    )


def hero_stat(label: str, valor) -> html.Div:
    return html.Div(
        className="hero-stat",
        children=[html.Div(label, className="hero-stat-label"), html.Div(str(valor), className="hero-stat-value")],
    )


def render_top_jogos(top_df, time_destaque: str | None):
    rows = []
    for _, r in top_df.iterrows():
        is_destaque = bool(time_destaque) and time_destaque in (r["mandante"], r["visitante"])
        rows.append(
            html.Tr(
                className="top-row destaque" if is_destaque else "top-row",
                children=[
                    html.Td(r["data"], className="cell-data"),
                    html.Td(display(r["mandante"]), className="cell-team"),
                    html.Td(r["placar"], className="cell-placar"),
                    html.Td(display(r["visitante"]), className="cell-team cell-team-right"),
                    html.Td(r["total"], className="cell-total"),
                ],
            )
        )
    return html.Table(
        className="top-jogos-table",
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th("Data"),
                        html.Th("Mandante"),
                        html.Th("Placar"),
                        html.Th("Visitante"),
                        html.Th("Total"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
    )


# ---------- layout ----------

app.layout = html.Div(
    className="app-shell",
    children=[
        html.Header(
            className="topbar",
            children=[
                html.Div(
                    className="brand",
                    children=[
                        html.Div("BR", className="brand-mark"),
                        html.Div(
                            children=[
                                html.Div("Brasileirão Série A", className="brand-title"),
                                html.Div("Temporada 2017 · Dashboard interativo", className="brand-subtitle"),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    className="topbar-meta",
                    children=[
                        html.Span(f"{liga['jogos']} jogos", className="chip"),
                        html.Span("20 clubes", className="chip"),
                        html.Span("Fonte: Kaggle", className="chip chip-muted"),
                    ],
                ),
            ],
        ),

        html.Div(
            className="container",
            children=[
                html.Section(
                    className="filter-row",
                    children=[
                        html.Div(
                            className="filter-control",
                            children=[
                                html.Label("Selecione um clube", className="filter-label"),
                                dcc.Dropdown(
                                    id="dropdown-time",
                                    options=opcoes_time,
                                    value=TODOS,
                                    clearable=False,
                                    className="dark-dropdown",
                                ),
                            ],
                        ),
                        html.Div(
                            "Dica: clique em qualquer linha da tabela de classificação para selecionar o clube.",
                            className="filter-hint",
                        ),
                    ],
                ),

                html.Section(id="hero", className="hero"),
                html.Section(id="kpi-grid", className="kpi-grid"),

                dcc.Loading(
                    id="loading-charts",
                    type="circle",
                    color=LEAGUE_ACCENT,
                    children=[
                        html.Section(
                            className="chart-grid hero-side",
                            children=[
                                html.Div(className="chart-card", children=[dcc.Graph(id="grafico-pontos", config=MODEBAR_CONFIG)]),
                                html.Div(className="chart-card", children=[dcc.Graph(id="grafico-casa-fora", config=MODEBAR_CONFIG)]),
                            ],
                        ),
                        html.Section(
                            className="chart-grid two-col",
                            children=[
                                html.Div(className="chart-card", children=[dcc.Graph(id="grafico-gols-marcados", config=MODEBAR_CONFIG)]),
                                html.Div(className="chart-card", children=[dcc.Graph(id="grafico-gols-pro-contra", config=MODEBAR_CONFIG)]),
                            ],
                        ),
                    ],
                ),

                html.Section(
                    className="section",
                    children=[
                        html.H2("Tabela de classificação", className="section-title"),
                        html.Div(
                            className="table-card",
                            children=[
                                dash_table.DataTable(
                                    id="tabela-classificacao",
                                    columns=[
                                        {"name": "Pos", "id": "posicao"},
                                        {"name": "Clube", "id": "time_display"},
                                        {"name": "P", "id": "pontos"},
                                        {"name": "J", "id": "jogos"},
                                        {"name": "V", "id": "vitorias"},
                                        {"name": "E", "id": "empates"},
                                        {"name": "D", "id": "derrotas"},
                                        {"name": "GP", "id": "gols_pro"},
                                        {"name": "GC", "id": "gols_contra"},
                                        {"name": "SG", "id": "saldo"},
                                        {"name": "%", "id": "aproveitamento"},
                                    ],
                                    data=tabela.to_dict("records"),
                                    style_as_list_view=True,
                                    style_header={
                                        "backgroundColor": "transparent",
                                        "color": "#8B92A8",
                                        "fontWeight": "600",
                                        "border": "none",
                                        "borderBottom": "1px solid #252B3A",
                                        "textTransform": "uppercase",
                                        "fontSize": "11px",
                                        "letterSpacing": "0.5px",
                                        "padding": "12px 10px",
                                    },
                                    style_cell={
                                        "backgroundColor": "transparent",
                                        "color": "#E6E9F2",
                                        "fontFamily": "Inter, 'Segoe UI', Roboto, sans-serif",
                                        "fontSize": "13px",
                                        "padding": "10px",
                                        "border": "none",
                                        "borderBottom": "1px solid rgba(37, 43, 58, 0.6)",
                                        "textAlign": "left",
                                        "cursor": "pointer",
                                    },
                                    style_data_conditional=[
                                        {"if": {"filter_query": "{posicao} <= 4"}, "borderLeft": "3px solid #48C78E"},
                                        {"if": {"filter_query": "{posicao} >= 17"}, "borderLeft": "3px solid #F25C5C"},
                                    ],
                                    page_size=20,
                                )
                            ],
                        ),
                    ],
                ),

                html.Section(
                    className="section",
                    children=[
                        html.H2("Top 10 jogos com mais gols", className="section-title"),
                        html.Div(id="top-jogos-table", className="table-card"),
                    ],
                ),

                html.Footer(
                    "Fonte: Brazilian Football Matches · Kaggle · Projeto acadêmico Insper, 2026",
                    className="footer",
                ),
            ],
        ),
    ],
)


# ============== Callbacks ==============

@app.callback(
    Output("dropdown-time", "value"),
    Input("tabela-classificacao", "active_cell"),
    State("tabela-classificacao", "data"),
    prevent_initial_call=True,
)
def click_para_selecionar(active_cell, data):
    if not active_cell or not data:
        return no_update
    return data[active_cell["row"]]["time"]


@app.callback(
    Output("hero", "children"),
    Output("kpi-grid", "children"),
    Output("grafico-pontos", "figure"),
    Output("grafico-gols-pro-contra", "figure"),
    Output("grafico-casa-fora", "figure"),
    Output("grafico-gols-marcados", "figure"),
    Output("top-jogos-table", "children"),
    Output("tabela-classificacao", "style_data_conditional"),
    Input("dropdown-time", "value"),
)
def atualizar_dashboard(time_selecionado):
    base_style = [
        {"if": {"filter_query": "{posicao} <= 4"},  "borderLeft": "3px solid #48C78E"},
        {"if": {"filter_query": "{posicao} >= 17"}, "borderLeft": "3px solid #F25C5C"},
    ]

    if time_selecionado == TODOS:
        accent = LEAGUE_ACCENT

        hero = html.Div(
            className="hero-inner",
            children=[
                html.Div(
                    className="hero-logo hero-logo-fallback",
                    style={"background": LEAGUE_ACCENT, "color": "#FFFFFF"},
                    children="BR",
                ),
                html.Div(
                    className="hero-info",
                    children=[
                        html.Div("Temporada", className="hero-eyebrow"),
                        html.H2("Brasileirão Série A 2017", className="hero-name"),
                        html.Div(
                            className="hero-stats",
                            children=[
                                hero_stat("Jogos", liga["jogos"]),
                                hero_stat("Total de gols", liga["total_gols"]),
                                hero_stat("Média/jogo", liga["media_gols"]),
                                hero_stat("Campeão", liga["campeao_time"]),
                            ],
                        ),
                    ],
                ),
            ],
        )

        kpis = [
            kpi_card("Vitórias do mandante", liga["vitoria_mandante"],
                     sub=f"{liga['pct_mandante']}% dos jogos",
                     progress=liga["pct_mandante"], accent="#48C78E"),
            kpi_card("Empates", liga["empates"],
                     sub=f"{liga['pct_empate']}% dos jogos",
                     progress=liga["pct_empate"], accent="#F4D43A"),
            kpi_card("Vitórias do visitante", liga["vitoria_visitante"],
                     sub=f"{liga['pct_visitante']}% dos jogos",
                     progress=liga["pct_visitante"], accent="#F25C5C"),
            kpi_card("Total de gols", liga["total_gols"], sub=f"{liga['media_gols']} gols/jogo"),
            kpi_card("Maior goleada", f"{liga['maior_goleada_total']} gols", sub=liga["maior_goleada"]),
            kpi_card("Líder em gols", liga["lider_gols_time"], sub=f"{liga['lider_gols_n']} gols marcados"),
            kpi_card("Campeão", liga["campeao_time"], sub=f"{liga['campeao_pontos']} pontos"),
            kpi_card("Vice", liga["vice_time"], sub=f"{int(tabela.iloc[1]['pontos'])} pontos"),
        ]

        fig_pontos = grafico_pontos_top_times(df, TOP6_LIGA)
        fig_gols_pc = grafico_gols_pro_contra(tabela, time_destaque=None, accent=accent)
        fig_casa_fora = grafico_casa_fora_liga(df)
        fig_gols_marcados = grafico_gols_marcados(tabela, time_destaque=None, accent=accent)
        top_jogos_html = render_top_jogos(top_jogos, time_destaque=None)
        return hero, kpis, fig_pontos, fig_gols_pc, fig_casa_fora, fig_gols_marcados, top_jogos_html, base_style

    # ---------- Modo time selecionado ----------
    info = team_info(time_selecionado)
    accent = info["color"]
    nome_display = display(time_selecionado)
    m = metricas_time(df, time_selecionado)
    posicao = int(tabela.loc[tabela["time"] == time_selecionado, "posicao"].iloc[0])

    hero = html.Div(
        className="hero-inner",
        style={"--accent": accent},
        children=[
            hero_logo(time_selecionado),
            html.Div(
                className="hero-info",
                children=[
                    html.Div("Clube em destaque", className="hero-eyebrow"),
                    html.H2(nome_display, className="hero-name"),
                    html.Div(
                        className="hero-stats",
                        children=[
                            hero_stat("Posição", f"{posicao}º"),
                            hero_stat("Pontos", m["pontos"]),
                            hero_stat("Aproveitamento", f"{m['aproveitamento']}%"),
                            hero_stat("Saldo de gols", f"{m['saldo']:+d}"),
                        ],
                    ),
                ],
            ),
        ],
    )

    kpis = [
        kpi_card("Jogos", m["jogos"]),
        kpi_card("Vitórias", m["vitorias"], accent="#48C78E"),
        kpi_card("Empates", m["empates"], accent="#F4D43A"),
        kpi_card("Derrotas", m["derrotas"], accent="#F25C5C"),
        kpi_card("Gols pró", m["gols_pro"], accent=accent),
        kpi_card("Gols sofridos", m["gols_contra"]),
        kpi_card("Saldo", f"{m['saldo']:+d}", accent=accent),
        kpi_card("Aproveitamento", f"{m['aproveitamento']}%",
                 progress=m["aproveitamento"], accent=accent),
    ]

    jogos_time = pontos_por_rodada(df, time_selecionado)
    casa_fora = desempenho_casa_fora(df, time_selecionado)

    referencia = JOGOS_CAMPEAO if time_selecionado != CHAMPION_RAW else None
    nome_referencia = display(CHAMPION_RAW) if referencia is not None else None

    fig_pontos = grafico_pontos_acumulados(
        jogos_time, nome_display, accent,
        jogos_referencia=referencia, nome_referencia=nome_referencia,
    )
    fig_gols_pc = grafico_gols_pro_contra(tabela, time_destaque=time_selecionado, accent=accent)
    fig_casa_fora = grafico_casa_fora(casa_fora, nome_display, accent)
    fig_gols_marcados = grafico_gols_marcados(tabela, time_destaque=time_selecionado, accent=accent)
    top_jogos_html = render_top_jogos(top_jogos, time_destaque=time_selecionado)

    style = base_style + [
        {
            "if": {"filter_query": f'{{time}} = "{time_selecionado}"'},
            "backgroundColor": "rgba(61, 165, 217, 0.08)",
            "borderLeft": f"3px solid {accent}",
            "fontWeight": "600",
        }
    ]

    return hero, kpis, fig_pontos, fig_gols_pc, fig_casa_fora, fig_gols_marcados, top_jogos_html, style


if __name__ == "__main__":
    app.run(debug=True)
