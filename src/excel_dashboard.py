"""Gera o arquivo `dashboard_brasileirao_2017.xlsx` a partir do CSV.

Reaproveita as funções de carregamento e processamento já existentes no projeto.
Saída: 1 aba Dashboard formatada + 5 abas de dados.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import xlsxwriter

from src.data_loader import load_raw, load_serie_a_2017
from src.data_processing import (
    liga_metricas,
    tabela_classificacao,
    top_jogos_mais_gols,
)
from src.teams import display

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dashboard_brasileirao_2017.xlsx"

# ============= Paleta (sincronizada com a versão Dash) =============
HEADER_BG  = "#0B0E14"
CARD_BG    = "#1C2230"
ROW_DARK   = "#171B25"
ROW_LIGHT  = "#1C2230"
ACCENT     = "#3DA5D9"
GREEN      = "#48C78E"
RED        = "#F25C5C"
YELLOW     = "#F4D43A"
TEXT       = "#E6E9F2"
MUTED      = "#8B92A8"
GRID       = "#252B3A"
WHITE      = "#FFFFFF"
G4_BG      = "#142a1f"
Z4_BG      = "#2a1818"


# ============================ entry point ============================

def gerar(path: Path | str = OUTPUT) -> Path:
    df_raw = load_raw()
    df = load_serie_a_2017()
    tabela = tabela_classificacao(df)
    top10 = top_jogos_mais_gols(df, n=10).reset_index(drop=True)
    liga = liga_metricas(df, tabela)
    casa_fora = _build_casa_fora(df, tabela)

    melhor_defesa_idx = tabela["gols_contra"].idxmin()
    melhor_defesa_time = display(tabela.loc[melhor_defesa_idx, "time"])
    melhor_defesa_n = int(tabela.loc[melhor_defesa_idx, "gols_contra"])

    wb = xlsxwriter.Workbook(str(path))
    fmt = _build_formats(wb)

    ws_dash      = wb.add_worksheet("Dashboard")
    ws_desemp    = wb.add_worksheet("Desempenho_Times")
    ws_top       = wb.add_worksheet("Jogos_Top_Gols")
    ws_casa_fora = wb.add_worksheet("Casa_Fora")
    ws_tratada   = wb.add_worksheet("Base_Tratada")
    ws_raw       = wb.add_worksheet("Base_Raw")

    _write_desempenho(ws_desemp, tabela, fmt)
    _write_top(ws_top, top10, fmt)
    _write_casa_fora(ws_casa_fora, casa_fora, fmt)
    _write_base_tratada(ws_tratada, df, fmt)
    _write_base_raw(ws_raw, df_raw, fmt)
    _write_dashboard(
        wb, ws_dash, tabela, top10, casa_fora, liga,
        melhor_defesa_time, melhor_defesa_n, fmt,
    )

    wb.close()
    return Path(path)


# ============================ helpers ============================

def _build_casa_fora(df: pd.DataFrame, tabela: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for time in tabela["time"]:
        casa = df[df["home"] == time]
        fora = df[df["away"] == time]
        v_casa = int((casa["result"] == "H").sum())
        e_casa = int((casa["result"] == "D").sum())
        d_casa = int((casa["result"] == "A").sum())
        v_fora = int((fora["result"] == "A").sum())
        e_fora = int((fora["result"] == "D").sum())
        d_fora = int((fora["result"] == "H").sum())
        rows.append({
            "time": time,
            "time_display": display(time),
            "jogos_casa": int(len(casa)),
            "vitorias_casa": v_casa,
            "empates_casa": e_casa,
            "derrotas_casa": d_casa,
            "pontos_casa": v_casa * 3 + e_casa,
            "jogos_fora": int(len(fora)),
            "vitorias_fora": v_fora,
            "empates_fora": e_fora,
            "derrotas_fora": d_fora,
            "pontos_fora": v_fora * 3 + e_fora,
        })
    cf = pd.DataFrame(rows)
    cf["pontos_total"] = cf["pontos_casa"] + cf["pontos_fora"]
    return cf


def _build_formats(wb: xlsxwriter.Workbook) -> dict:
    """Coleção de formats reutilizáveis."""
    F = {}

    F["title"] = wb.add_format({
        "font_name": "Calibri", "font_size": 24, "bold": True,
        "font_color": TEXT, "bg_color": HEADER_BG,
        "valign": "vcenter", "indent": 2,
    })
    F["subtitle"] = wb.add_format({
        "font_name": "Calibri", "font_size": 12, "italic": True,
        "font_color": MUTED, "bg_color": HEADER_BG,
        "valign": "vcenter", "indent": 2,
    })
    F["section"] = wb.add_format({
        "font_name": "Calibri", "font_size": 13, "bold": True,
        "font_color": TEXT, "bg_color": HEADER_BG,
        "valign": "vcenter", "indent": 1,
        "top": 2, "top_color": ACCENT,
    })

    F["kpi_label"] = wb.add_format({
        "font_name": "Calibri", "font_size": 9, "bold": True,
        "font_color": MUTED, "bg_color": CARD_BG,
        "valign": "vcenter", "align": "left", "indent": 1,
        "top": 2, "top_color": ACCENT,
        "left": 1, "left_color": GRID,
        "right": 1, "right_color": GRID,
    })
    F["kpi_value"] = wb.add_format({
        "font_name": "Calibri", "font_size": 22, "bold": True,
        "font_color": TEXT, "bg_color": CARD_BG,
        "valign": "vcenter", "align": "left", "indent": 1,
        "left": 1, "left_color": GRID,
        "right": 1, "right_color": GRID,
        "bottom": 1, "bottom_color": GRID,
    })
    F["kpi_value_text"] = wb.add_format({
        "font_name": "Calibri", "font_size": 16, "bold": True,
        "font_color": TEXT, "bg_color": CARD_BG,
        "valign": "vcenter", "align": "left", "indent": 1,
        "left": 1, "left_color": GRID,
        "right": 1, "right_color": GRID,
        "bottom": 1, "bottom_color": GRID,
    })

    F["table_header"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "font_color": MUTED, "bg_color": HEADER_BG,
        "align": "center", "valign": "vcenter",
        "bottom": 2, "bottom_color": ACCENT,
    })
    F["table_header_left"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "font_color": MUTED, "bg_color": HEADER_BG,
        "align": "left", "valign": "vcenter", "indent": 1,
        "bottom": 2, "bottom_color": ACCENT,
    })

    # row alternates × posição (G4 verde / Z4 vermelho / normal)
    for variant, bg in [("dark", ROW_DARK), ("light", ROW_LIGHT), ("g4", G4_BG), ("z4", Z4_BG)]:
        F[f"row_{variant}_pos"] = wb.add_format({
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": TEXT, "bg_color": bg,
            "align": "center", "valign": "vcenter",
        })
        F[f"row_{variant}_team"] = wb.add_format({
            "font_name": "Calibri", "font_size": 10,
            "font_color": TEXT, "bg_color": bg,
            "align": "left", "valign": "vcenter", "indent": 1,
        })
        F[f"row_{variant}_num"] = wb.add_format({
            "font_name": "Calibri", "font_size": 10,
            "font_color": TEXT, "bg_color": bg,
            "align": "center", "valign": "vcenter",
        })
        F[f"row_{variant}_pts"] = wb.add_format({
            "font_name": "Calibri", "font_size": 10, "bold": True,
            "font_color": TEXT, "bg_color": bg,
            "align": "center", "valign": "vcenter",
        })
        F[f"row_{variant}_pct"] = wb.add_format({
            "font_name": "Calibri", "font_size": 10,
            "font_color": MUTED, "bg_color": bg,
            "align": "center", "valign": "vcenter",
            "num_format": '0.0"%"',
        })

    F["top_row_dark"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10,
        "font_color": TEXT, "bg_color": ROW_DARK,
        "align": "left", "valign": "vcenter", "indent": 1,
    })
    F["top_row_light"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10,
        "font_color": TEXT, "bg_color": ROW_LIGHT,
        "align": "left", "valign": "vcenter", "indent": 1,
    })
    F["top_placar_dark"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "font_color": ACCENT, "bg_color": ROW_DARK,
        "align": "center", "valign": "vcenter",
    })
    F["top_placar_light"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "font_color": ACCENT, "bg_color": ROW_LIGHT,
        "align": "center", "valign": "vcenter",
    })
    F["top_total_dark"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "font_color": TEXT, "bg_color": ROW_DARK,
        "align": "center", "valign": "vcenter",
    })
    F["top_total_light"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "font_color": TEXT, "bg_color": ROW_LIGHT,
        "align": "center", "valign": "vcenter",
    })

    F["data_header"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10, "bold": True,
        "font_color": WHITE, "bg_color": "#1F4E78",
        "align": "center", "valign": "vcenter", "border": 1,
    })
    F["data_cell"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10,
        "align": "left", "valign": "vcenter", "border": 1, "border_color": "#D4D4D4",
    })
    F["data_cell_num"] = wb.add_format({
        "font_name": "Calibri", "font_size": 10,
        "align": "center", "valign": "vcenter", "border": 1, "border_color": "#D4D4D4",
    })

    F["filler_dark"] = wb.add_format({"bg_color": HEADER_BG})

    return F


# ============================ Dashboard sheet ============================

def _write_dashboard(wb, ws, tabela, top10, casa_fora, liga,
                     melhor_defesa_time, melhor_defesa_n, F):
    ws.hide_gridlines(2)
    ws.set_tab_color(ACCENT)
    ws.set_zoom(100)

    # Larguras
    ws.set_column("A:A", 5)
    ws.set_column("B:B", 18)
    ws.set_column("C:K", 6.6)
    ws.set_column("L:L", 1.6)
    ws.set_column("M:R", 11.5)

    # Pinta o fundo escuro estendido (até col R)
    for r in range(0, 90):
        ws.set_row(r, None, F["filler_dark"])

    # ===== Header =====
    ws.set_row(0, 44)
    ws.merge_range("A1:R1", "Campeonato Brasileiro Série A 2017", F["title"])
    ws.set_row(1, 22)
    ws.merge_range("A2:R2", "Dashboard de desempenho dos clubes · Análise da temporada", F["subtitle"])
    ws.set_row(2, 8)

    # ===== KPI cards =====
    ws.set_row(3, 22)
    ws.set_row(4, 44)

    kpis = [
        ("TOTAL DE JOGOS",  liga["jogos"],          "num"),
        ("TOTAL DE GOLS",   liga["total_gols"],     "num"),
        ("MÉDIA POR JOGO",  liga["media_gols"],     "num"),
        ("CAMPEÃO",         liga["campeao_time"],   "text"),
        ("MAIOR ATAQUE",    f"{liga['lider_gols_time']} ({liga['lider_gols_n']})", "text"),
        ("MELHOR DEFESA",   f"{melhor_defesa_time} ({melhor_defesa_n})", "text"),
    ]
    spans = [("A4:C4", "A5:C5"), ("D4:F4", "D5:F5"), ("G4:I4", "G5:I5"),
             ("J4:L4", "J5:L5"), ("M4:O4", "M5:O5"), ("P4:R4", "P5:R5")]

    for (label_range, value_range), (label, value, kind) in zip(spans, kpis):
        ws.merge_range(label_range, label, F["kpi_label"])
        fmt = F["kpi_value"] if kind == "num" else F["kpi_value_text"]
        ws.merge_range(value_range, value, fmt)

    ws.set_row(5, 14)

    # ===== Section: Tabela de classificação =====
    ws.set_row(6, 26)
    ws.merge_range("A7:K7", "  TABELA DE CLASSIFICAÇÃO", F["section"])
    ws.merge_range("M7:R7", "  PONTOS POR TIME", F["section"])

    headers = ["Pos", "Clube", "P", "J", "V", "E", "D", "GP", "GC", "SG", "%"]
    ws.set_row(7, 22)
    ws.write("A8", headers[0], F["table_header"])
    ws.write("B8", headers[1], F["table_header_left"])
    for i, h in enumerate(headers[2:], start=2):
        ws.write(0, i, "")  # placeholder, overwritten below
        ws.write_string(7, i, h, F["table_header"])

    # Escreve as 20 linhas
    for i, row in tabela.iterrows():
        excel_row = 8 + i
        ws.set_row(excel_row, 19)
        if row["posicao"] <= 4:
            variant = "g4"
        elif row["posicao"] >= 17:
            variant = "z4"
        else:
            variant = "dark" if (i % 2 == 0) else "light"
        ws.write_number(excel_row, 0, int(row["posicao"]),    F[f"row_{variant}_pos"])
        ws.write_string(excel_row, 1, row["time_display"],     F[f"row_{variant}_team"])
        ws.write_number(excel_row, 2, int(row["pontos"]),      F[f"row_{variant}_pts"])
        ws.write_number(excel_row, 3, int(row["jogos"]),       F[f"row_{variant}_num"])
        ws.write_number(excel_row, 4, int(row["vitorias"]),    F[f"row_{variant}_num"])
        ws.write_number(excel_row, 5, int(row["empates"]),     F[f"row_{variant}_num"])
        ws.write_number(excel_row, 6, int(row["derrotas"]),    F[f"row_{variant}_num"])
        ws.write_number(excel_row, 7, int(row["gols_pro"]),    F[f"row_{variant}_num"])
        ws.write_number(excel_row, 8, int(row["gols_contra"]), F[f"row_{variant}_num"])
        sg = int(row["saldo"])
        ws.write_string(excel_row, 9, f"{sg:+d}",              F[f"row_{variant}_num"])
        ws.write_number(excel_row, 10, float(row["aproveitamento"]) / 100, F[f"row_{variant}_pct"])

    ws.freeze_panes(8, 0)

    # ===== Chart: Pontos por time =====
    chart_pontos = wb.add_chart({"type": "bar"})
    n_times = len(tabela)
    chart_pontos.add_series({
        "name":       "Pontos",
        "categories": ["Desempenho_Times", 1, 1, n_times, 1],   # time_display
        "values":     ["Desempenho_Times", 1, 4, n_times, 4],   # pontos
        "fill":       {"color": ACCENT},
        "border":     {"color": ACCENT},
        "data_labels": {"value": True, "font": {"color": TEXT, "size": 8, "bold": True}},
    })
    _style_chart(chart_pontos, title="Pontos por time (P)", show_legend=False, reverse_y=True)
    chart_pontos.set_size({"width": 460, "height": 560})
    ws.insert_chart("M8", chart_pontos, {"x_offset": 4, "y_offset": 0})

    # ===== Section: Análise de gols =====
    next_row = 30
    ws.set_row(next_row - 1, 14)
    ws.set_row(next_row, 26)
    ws.merge_range(next_row, 0, next_row, 17, "  ANÁLISE DE GOLS", F["section"])

    chart_gols = wb.add_chart({"type": "column"})
    n10 = 10
    chart_gols.add_series({
        "name": "Gols pró",
        "categories": ["Desempenho_Times", 1, 1, n10, 1],
        "values":     ["Desempenho_Times", 1, 7, n10, 7],
        "fill":       {"color": ACCENT},
        "border":     {"color": ACCENT},
    })
    chart_gols.add_series({
        "name": "Gols sofridos",
        "categories": ["Desempenho_Times", 1, 1, n10, 1],
        "values":     ["Desempenho_Times", 1, 8, n10, 8],
        "fill":       {"color": RED},
        "border":     {"color": RED},
    })
    _style_chart(chart_gols, title="Gols pró × sofridos · Top 10", show_legend=True)
    chart_gols.set_size({"width": 580, "height": 360})
    ws.insert_chart(next_row + 1, 0, chart_gols, {"x_offset": 4, "y_offset": 4})

    # ===== Top 10 jogos · tabela ao lado =====
    ws.merge_range(next_row + 1, 11, next_row + 1, 17, "  TOP 10 JOGOS COM MAIS GOLS", F["section"])
    top_header_row = next_row + 2
    ws.set_row(top_header_row, 22)
    ws.write_string(top_header_row, 11, "Data",      F["table_header_left"])
    ws.merge_range(top_header_row, 12, top_header_row, 13, "Mandante", F["table_header_left"])
    ws.write_string(top_header_row, 14, "Placar",    F["table_header"])
    ws.merge_range(top_header_row, 15, top_header_row, 16, "Visitante", F["table_header_left"])
    ws.write_string(top_header_row, 17, "Total",     F["table_header"])

    for i, row in top10.iterrows():
        rr = top_header_row + 1 + i
        ws.set_row(rr, 19)
        is_dark = (i % 2 == 0)
        f_row = F["top_row_dark"] if is_dark else F["top_row_light"]
        f_pl  = F["top_placar_dark"] if is_dark else F["top_placar_light"]
        f_tot = F["top_total_dark"] if is_dark else F["top_total_light"]
        ws.write_string(rr, 11, row["data"], f_row)
        ws.merge_range(rr, 12, rr, 13, display(row["mandante"]), f_row)
        ws.write_string(rr, 14, row["placar"], f_pl)
        ws.merge_range(rr, 15, rr, 16, display(row["visitante"]), f_row)
        ws.write_number(rr, 17, int(row["total"]), f_tot)

    # ===== Section: Casa × Fora (Top 10) =====
    casa_fora_section_row = next_row + 1 + 22
    ws.set_row(casa_fora_section_row - 1, 12)
    ws.set_row(casa_fora_section_row, 26)
    ws.merge_range(casa_fora_section_row, 0, casa_fora_section_row, 17,
                   "  PONTOS COMO MANDANTE × VISITANTE · TOP 10", F["section"])

    chart_cf = wb.add_chart({"type": "column"})
    chart_cf.add_series({
        "name": "Pontos casa",
        "categories": ["Casa_Fora", 1, 1, 10, 1],
        "values":     ["Casa_Fora", 1, 6, 10, 6],
        "fill":       {"color": GREEN},
        "border":     {"color": GREEN},
    })
    chart_cf.add_series({
        "name": "Pontos fora",
        "categories": ["Casa_Fora", 1, 1, 10, 1],
        "values":     ["Casa_Fora", 1, 11, 10, 11],
        "fill":       {"color": YELLOW},
        "border":     {"color": YELLOW},
    })
    _style_chart(chart_cf, title="Pontos como mandante × visitante", show_legend=True)
    chart_cf.set_size({"width": 1120, "height": 380})
    ws.insert_chart(casa_fora_section_row + 1, 0, chart_cf, {"x_offset": 4, "y_offset": 4})

    # ===== Footer =====
    footer_row = casa_fora_section_row + 23
    ws.set_row(footer_row, 26)
    ws.merge_range(footer_row, 0, footer_row, 17,
                   "Fonte: Brazilian Football Matches (Kaggle) · Projeto acadêmico Insper · 2026",
                   F["subtitle"])


def _style_chart(chart, title: str, show_legend: bool, reverse_y: bool = False):
    chart.set_title({
        "name": title,
        "name_font": {"name": "Calibri", "color": TEXT, "size": 12, "bold": True},
    })
    axis_font = {"name": "Calibri", "color": MUTED, "size": 9}
    line_color = GRID
    chart.set_x_axis({
        "num_font": axis_font, "name_font": axis_font,
        "line": {"color": line_color}, "major_gridlines": {"visible": True, "line": {"color": GRID, "dash_type": "dash"}},
        "minor_gridlines": {"visible": False},
    })
    y_axis_args = {
        "num_font": axis_font, "name_font": axis_font,
        "line": {"color": line_color},
        "major_gridlines": {"visible": False},
        "minor_gridlines": {"visible": False},
    }
    if reverse_y:
        y_axis_args["reverse"] = True
    chart.set_y_axis(y_axis_args)
    chart.set_chartarea({"border": {"none": True}, "fill": {"color": CARD_BG}})
    chart.set_plotarea({"border": {"none": True}, "fill": {"color": CARD_BG}})
    if show_legend:
        chart.set_legend({
            "position": "top",
            "font": {"name": "Calibri", "color": TEXT, "size": 10},
            "border": {"none": True}, "fill": {"color": CARD_BG},
        })
    else:
        chart.set_legend({"none": True})


# ============================ Data sheets ============================

def _write_desempenho(ws, tabela, F):
    ws.set_tab_color(MUTED)
    headers = [
        "Posição", "Clube", "Time (raw)", "Jogos", "Pontos",
        "Vitórias", "Empates", "Derrotas",
        "Gols pró", "Gols sofridos", "Saldo", "Aproveitamento (%)",
    ]
    for i, h in enumerate(headers):
        ws.write(0, i, h, F["data_header"])
    for i, row in tabela.iterrows():
        ws.write_number(i + 1, 0, int(row["posicao"]),       F["data_cell_num"])
        ws.write_string(i + 1, 1, row["time_display"],         F["data_cell"])
        ws.write_string(i + 1, 2, row["time"],                 F["data_cell"])
        ws.write_number(i + 1, 3, int(row["jogos"]),           F["data_cell_num"])
        ws.write_number(i + 1, 4, int(row["pontos"]),          F["data_cell_num"])
        ws.write_number(i + 1, 5, int(row["vitorias"]),        F["data_cell_num"])
        ws.write_number(i + 1, 6, int(row["empates"]),         F["data_cell_num"])
        ws.write_number(i + 1, 7, int(row["derrotas"]),        F["data_cell_num"])
        ws.write_number(i + 1, 8, int(row["gols_pro"]),        F["data_cell_num"])
        ws.write_number(i + 1, 9, int(row["gols_contra"]),     F["data_cell_num"])
        ws.write_number(i + 1, 10, int(row["saldo"]),          F["data_cell_num"])
        ws.write_number(i + 1, 11, float(row["aproveitamento"]), F["data_cell_num"])

    ws.set_column("A:A", 9)
    ws.set_column("B:C", 22)
    ws.set_column("D:L", 14)
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(tabela), len(headers) - 1)


def _write_top(ws, top10, F):
    ws.set_tab_color(MUTED)
    headers = ["Data", "Mandante", "Placar", "Visitante", "Total de gols"]
    for i, h in enumerate(headers):
        ws.write(0, i, h, F["data_header"])
    for i, row in top10.iterrows():
        ws.write_string(i + 1, 0, row["data"],               F["data_cell"])
        ws.write_string(i + 1, 1, display(row["mandante"]),  F["data_cell"])
        ws.write_string(i + 1, 2, row["placar"],             F["data_cell_num"])
        ws.write_string(i + 1, 3, display(row["visitante"]), F["data_cell"])
        ws.write_number(i + 1, 4, int(row["total"]),         F["data_cell_num"])
    ws.set_column("A:A", 12)
    ws.set_column("B:D", 22)
    ws.set_column("E:E", 16)
    ws.freeze_panes(1, 0)


def _write_casa_fora(ws, casa_fora, F):
    ws.set_tab_color(MUTED)
    headers = [
        "Time (raw)", "Clube",
        "Jogos casa", "Vitórias casa", "Empates casa", "Derrotas casa",
        "Pontos casa",
        "Jogos fora", "Vitórias fora", "Empates fora", "Derrotas fora",
        "Pontos fora", "Pontos total",
    ]
    for i, h in enumerate(headers):
        ws.write(0, i, h, F["data_header"])

    cols = [
        ("time", "data_cell"),
        ("time_display", "data_cell"),
        ("jogos_casa", "data_cell_num"),
        ("vitorias_casa", "data_cell_num"),
        ("empates_casa", "data_cell_num"),
        ("derrotas_casa", "data_cell_num"),
        ("pontos_casa", "data_cell_num"),
        ("jogos_fora", "data_cell_num"),
        ("vitorias_fora", "data_cell_num"),
        ("empates_fora", "data_cell_num"),
        ("derrotas_fora", "data_cell_num"),
        ("pontos_fora", "data_cell_num"),
        ("pontos_total", "data_cell_num"),
    ]
    for i, row in casa_fora.iterrows():
        for j, (col, fmt_key) in enumerate(cols):
            value = row[col]
            if isinstance(value, str):
                ws.write_string(i + 1, j, value, F[fmt_key])
            else:
                ws.write_number(i + 1, j, int(value), F[fmt_key])

    ws.set_column("A:B", 22)
    ws.set_column("C:M", 14)
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(casa_fora), len(headers) - 1)


def _write_base_tratada(ws, df, F):
    ws.set_tab_color(MUTED)
    headers = ["Data", "Mandante", "Gols mandante", "Gols visitante", "Visitante", "Total de gols", "Resultado"]
    for i, h in enumerate(headers):
        ws.write(0, i, h, F["data_header"])
    for i, row in df.iterrows():
        ws.write_string(i + 1, 0, row["date"].strftime("%d/%m/%Y"), F["data_cell"])
        ws.write_string(i + 1, 1, display(row["home"]),             F["data_cell"])
        ws.write_number(i + 1, 2, int(row["home_goal"]),            F["data_cell_num"])
        ws.write_number(i + 1, 3, int(row["away_goal"]),            F["data_cell_num"])
        ws.write_string(i + 1, 4, display(row["away"]),             F["data_cell"])
        ws.write_number(i + 1, 5, int(row["total_goals"]),          F["data_cell_num"])
        resultado = {"H": "Mandante", "A": "Visitante", "D": "Empate"}[row["result"]]
        ws.write_string(i + 1, 6, resultado,                        F["data_cell"])
    ws.set_column("A:A", 12)
    ws.set_column("B:B", 22)
    ws.set_column("C:D", 14)
    ws.set_column("E:E", 22)
    ws.set_column("F:G", 14)
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(df), len(headers) - 1)


def _write_base_raw(ws, df_raw, F):
    ws.set_tab_color(MUTED)
    cols = list(df_raw.columns)
    for i, h in enumerate(cols):
        ws.write(0, i, h, F["data_header"])
    # write_row é mais rápido que cell-a-cell pra dataset grande
    for i, row in enumerate(df_raw.itertuples(index=False), start=1):
        for j, value in enumerate(row):
            if pd.isna(value):
                continue
            if isinstance(value, (int,)):
                ws.write_number(i, j, value, F["data_cell_num"])
            elif isinstance(value, float):
                if value.is_integer():
                    ws.write_number(i, j, value, F["data_cell_num"])
                else:
                    ws.write_number(i, j, value, F["data_cell_num"])
            elif isinstance(value, pd.Timestamp):
                ws.write_string(i, j, value.strftime("%Y-%m-%d"), F["data_cell"])
            else:
                ws.write_string(i, j, str(value), F["data_cell"])
    ws.set_column(0, len(cols) - 1, 14)
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(df_raw), len(cols) - 1)


# ============================ CLI ============================

if __name__ == "__main__":
    saida = gerar()
    print(f"OK — arquivo gerado em: {saida}")
