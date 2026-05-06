"""Figuras Plotly do dashboard — tema escuro com accent reativo ao time."""

import pandas as pd
import plotly.graph_objects as go

BG = "#11141C"
CARD = "#171B25"
GRID = "#252B3A"
TEXT = "#E6E9F2"
MUTED = "#8B92A8"
NEUTRAL = "#3A4255"
RED = "#F25C5C"
GREEN = "#48C78E"
YELLOW = "#F4D43A"

FONT_FAMILY = "Inter, 'Segoe UI', Roboto, sans-serif"
MODEBAR_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}


def _layout_base(title: str = "", height: int = 360, has_legend: bool = False) -> dict:
    """Base layout. Legenda fica abaixo do plot pra não competir com o título."""
    return dict(
        title=dict(
            text=f"<span style='color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px'>{title}</span>" if title else "",
            x=0.02, y=0.97, xanchor="left", yanchor="top",
        ),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(color=TEXT, family=FONT_FAMILY, size=11),
        margin=dict(l=20, r=24, t=48, b=70 if has_legend else 36),
        height=height,
        xaxis=dict(
            gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID, tickcolor=GRID,
            tickfont=dict(size=11, color=MUTED), title_font=dict(size=11, color=MUTED),
        ),
        yaxis=dict(
            gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID, tickcolor=GRID,
            tickfont=dict(size=11, color=MUTED), title_font=dict(size=11, color=MUTED),
        ),
        legend=dict(
            orientation="h", yanchor="top", y=-0.16, xanchor="left", x=0,
            font=dict(color=TEXT, size=11), bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=BG, bordercolor=GRID,
            font=dict(color=TEXT, family=FONT_FAMILY, size=12),
        ),
    )


def grafico_pontos_acumulados(
    jogos_time: pd.DataFrame,
    time: str,
    accent: str,
    jogos_referencia: pd.DataFrame | None = None,
    nome_referencia: str | None = None,
) -> go.Figure:
    """Pontos acumulados do time. Se `jogos_referencia` for passado, plota
    uma linha tracejada de referência (ex.: campeão da temporada)."""
    fig = go.Figure()

    # Referência (campeão) — fica atrás, em cinza tracejado
    if jogos_referencia is not None and len(jogos_referencia):
        fig.add_trace(
            go.Scatter(
                x=jogos_referencia["rodada"], y=jogos_referencia["pontos_acum"],
                mode="lines",
                line=dict(color=MUTED, width=1.8, dash="dot"),
                name=f"{nome_referencia} (referência)" if nome_referencia else "Referência",
                hovertemplate="<b>%{fullData.name}</b><br>Rodada %{x}: %{y} pts<extra></extra>",
            )
        )

    if jogos_time is not None and len(jogos_time):
        placares = jogos_time["gols_pro"].astype(str) + " x " + jogos_time["gols_contra"].astype(str)
        custom = pd.DataFrame({
            "adversario": jogos_time["adversario"],
            "placar": placares,
            "mando": jogos_time["mando"],
        }).values
        fig.add_trace(
            go.Scatter(
                x=jogos_time["rodada"],
                y=jogos_time["pontos_acum"],
                mode="lines+markers",
                line=dict(color=accent, width=3, shape="spline", smoothing=0.6),
                marker=dict(size=5, color=accent, line=dict(color=BG, width=1.5)),
                fill="tozeroy",
                fillcolor=_with_alpha(accent, 0.12),
                customdata=custom,
                hovertemplate=(
                    "<b>Rodada %{x}</b><br>"
                    "Pontos: %{y}<br>"
                    "vs %{customdata[0]} (%{customdata[2]})<br>"
                    "Placar: %{customdata[1]}<extra></extra>"
                ),
                name=time,
            )
        )

    has_legend = jogos_referencia is not None and len(jogos_referencia) > 0
    layout = _layout_base("Pontos acumulados por rodada", height=420, has_legend=has_legend)
    layout["xaxis"]["title"] = dict(text="Rodada", font=dict(size=11, color=MUTED))
    layout["yaxis"]["title"] = dict(text="Pontos", font=dict(size=11, color=MUTED))
    fig.update_layout(**layout)
    return fig


def grafico_pontos_top_times(df: pd.DataFrame, top_times: list[tuple[str, str, str]]) -> go.Figure:
    """Linhas de pontos acumulados pros top N times.
    `top_times` é uma lista de (nome_raw, nome_display, cor)."""
    from .data_processing import pontos_por_rodada

    fig = go.Figure()
    for nome_raw, nome_display, cor in top_times:
        jogos = pontos_por_rodada(df, nome_raw)
        if not len(jogos):
            continue
        fig.add_trace(
            go.Scatter(
                x=jogos["rodada"], y=jogos["pontos_acum"],
                mode="lines",
                line=dict(color=cor, width=2.4, shape="spline", smoothing=0.6),
                name=nome_display,
                hovertemplate="<b>%{fullData.name}</b><br>Rodada %{x}: %{y} pts<extra></extra>",
            )
        )
    layout = _layout_base("Pontos acumulados — Top 6 da temporada", height=420, has_legend=True)
    layout["xaxis"]["title"] = dict(text="Rodada", font=dict(size=11, color=MUTED))
    layout["yaxis"]["title"] = dict(text="Pontos", font=dict(size=11, color=MUTED))
    fig.update_layout(**layout)
    return fig


def grafico_gols_pro_contra(tabela: pd.DataFrame, time_destaque: str | None = None, accent: str = "#3DA5D9") -> go.Figure:
    top = _top_n_com_destaque(tabela, n=10, sort_by="gols_pro", destaque=time_destaque)
    dados = top.sort_values("gols_pro", ascending=True)
    cor_pro = [accent if t == time_destaque else _with_alpha(accent, 0.45) for t in dados["time"]]
    cor_contra = [RED if t == time_destaque else _with_alpha(RED, 0.45) for t in dados["time"]]

    fig = go.Figure()
    fig.add_bar(
        y=dados["time_display"], x=dados["gols_pro"], name="Gols pró",
        orientation="h", marker_color=cor_pro,
        hovertemplate="<b>%{y}</b><br>Pró: %{x}<extra></extra>",
    )
    fig.add_bar(
        y=dados["time_display"], x=dados["gols_contra"], name="Sofridos",
        orientation="h", marker_color=cor_contra,
        hovertemplate="<b>%{y}</b><br>Sofridos: %{x}<extra></extra>",
    )
    layout = _layout_base("Gols pró × sofridos · Top 10", height=420, has_legend=True)
    layout["barmode"] = "group"
    layout["bargap"] = 0.35
    layout["bargroupgap"] = 0.1
    layout["margin"] = dict(l=130, r=20, t=48, b=70)
    fig.update_layout(**layout)
    return fig


def grafico_gols_marcados(tabela: pd.DataFrame, time_destaque: str | None = None, accent: str = "#3DA5D9") -> go.Figure:
    top = _top_n_com_destaque(tabela, n=10, sort_by="gols_pro", destaque=time_destaque)
    dados = top.sort_values("gols_pro", ascending=True)
    cores = [accent if t == time_destaque else _with_alpha(accent, 0.4) for t in dados["time"]]
    fig = go.Figure(
        go.Bar(
            x=dados["gols_pro"], y=dados["time_display"],
            orientation="h",
            marker=dict(color=cores, line=dict(color=BG, width=0)),
            text=dados["gols_pro"], textposition="outside",
            textfont=dict(color=TEXT, family=FONT_FAMILY, size=11),
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Gols marcados: %{x}<extra></extra>",
        )
    )
    layout = _layout_base("Gols marcados · Top 10", height=420)
    layout["margin"] = dict(l=130, r=44, t=48, b=36)
    layout["bargap"] = 0.35
    fig.update_layout(**layout)
    return fig


def grafico_casa_fora(dados: pd.DataFrame, time: str, accent: str) -> go.Figure:
    """Barras V/E/D casa vs fora (vertical, narrow). Compacto."""
    pivot = dados.pivot(index="tipo", columns="mando", values="valor").reindex(["Vitórias", "Empates", "Derrotas"])
    fig = go.Figure()
    fig.add_bar(
        x=pivot.index, y=pivot["Casa"], name="Casa",
        marker_color=accent,
        text=pivot["Casa"], textposition="outside",
        textfont=dict(color=TEXT, size=11), cliponaxis=False,
        hovertemplate="<b>Casa</b><br>%{x}: %{y}<extra></extra>",
    )
    fig.add_bar(
        x=pivot.index, y=pivot["Fora"], name="Fora",
        marker_color=_with_alpha(accent, 0.4),
        text=pivot["Fora"], textposition="outside",
        textfont=dict(color=TEXT, size=11), cliponaxis=False,
        hovertemplate="<b>Fora</b><br>%{x}: %{y}<extra></extra>",
    )
    layout = _layout_base("Casa vs Fora", height=420, has_legend=True)
    layout["barmode"] = "group"
    layout["bargap"] = 0.4
    layout["bargroupgap"] = 0.15
    fig.update_layout(**layout)
    return fig


def grafico_casa_fora_liga(df: pd.DataFrame) -> go.Figure:
    """Distribuição de resultados na temporada (modo Todos os times)."""
    counts = df["result"].value_counts().reindex(["H", "D", "A"]).fillna(0).astype(int)
    labels = ["Mandante", "Empate", "Visitante"]
    cores = [GREEN, YELLOW, RED]
    fig = go.Figure(
        go.Bar(
            x=labels, y=counts.values, marker_color=cores,
            text=counts.values, textposition="outside",
            textfont=dict(color=TEXT, size=12), cliponaxis=False,
            width=[0.55, 0.55, 0.55],
            hovertemplate="<b>%{x} venceu</b><br>%{y} jogos<extra></extra>",
        )
    )
    layout = _layout_base("Distribuição de resultados", height=420)
    fig.update_layout(**layout)
    return fig


def tabela_top_jogos(top_df: pd.DataFrame, time_destaque: str | None = None, accent: str = "#3DA5D9") -> go.Figure:
    fill = []
    for _, row in top_df.iterrows():
        if time_destaque and time_destaque in (row["mandante"], row["visitante"]):
            fill.append(_with_alpha(accent, 0.18))
        else:
            fill.append(CARD)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["<b>Data</b>", "<b>Mandante</b>", "<b>Placar</b>", "<b>Visitante</b>", "<b>Total</b>"],
                    fill_color=BG,
                    line_color=GRID,
                    font=dict(color=MUTED, size=11, family=FONT_FAMILY),
                    align="left",
                    height=36,
                ),
                cells=dict(
                    values=[
                        top_df["data"], top_df["mandante"], top_df["placar"],
                        top_df["visitante"], top_df["total"],
                    ],
                    fill_color=[fill],
                    line_color=GRID,
                    font=dict(color=TEXT, size=12, family=FONT_FAMILY),
                    align="left",
                    height=34,
                ),
                columnwidth=[80, 160, 80, 160, 70],
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text=f"<span style='color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px'>Top 10 jogos com mais gols</span>",
            x=0.02, y=0.97, xanchor="left", yanchor="top",
        ),
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        margin=dict(l=12, r=12, t=44, b=10),
        height=460,
    )
    return fig


# --------- helpers ---------

def _top_n_com_destaque(tabela: pd.DataFrame, n: int, sort_by: str, destaque: str | None) -> pd.DataFrame:
    """Top N por sort_by. Se o time destacado não está no top, substitui o último por ele."""
    top = tabela.nlargest(n, sort_by)
    if destaque and destaque not in top["time"].values:
        time_row = tabela[tabela["time"] == destaque]
        if len(time_row):
            top = pd.concat([top.iloc[:-1], time_row], ignore_index=True)
    return top


def _with_alpha(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
