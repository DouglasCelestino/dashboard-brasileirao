"""Cálculo das métricas e da tabela de classificação."""

import pandas as pd

from .teams import display


def tabela_classificacao(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela de classificação no formato Brasileirão (3-1-0).
    Mantém a coluna `time` com o nome cru do CSV e adiciona `time_display`
    pra UI (com til, abreviações, etc.).
    """
    times = sorted(set(df["home"]).union(df["away"]))
    linhas = [_estatisticas_time(df, time) for time in times]
    tabela = pd.DataFrame(linhas)
    tabela = tabela.sort_values(
        by=["pontos", "vitorias", "saldo", "gols_pro"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    tabela.insert(0, "posicao", tabela.index + 1)
    tabela["time_display"] = tabela["time"].map(display)
    return tabela


def liga_metricas(df: pd.DataFrame, tabela: pd.DataFrame) -> dict:
    """Métricas no nível da liga, usadas no modo 'Todos os times'."""
    total = len(df)
    h = int((df["result"] == "H").sum())
    e = int((df["result"] == "D").sum())
    a = int((df["result"] == "A").sum())
    total_gols = int(df["home_goal"].sum() + df["away_goal"].sum())

    idx_max = df["total_goals"].idxmax()
    jogo = df.loc[idx_max]
    maior_goleada = (
        f"{display(jogo['home'])} {int(jogo['home_goal'])} × {int(jogo['away_goal'])} {display(jogo['away'])}"
    )

    lider = tabela.loc[tabela["gols_pro"].idxmax()]
    campeao = tabela.iloc[0]

    return {
        "jogos": total,
        "vitoria_mandante": h,
        "empates": e,
        "vitoria_visitante": a,
        "pct_mandante": round(h / total * 100, 1),
        "pct_empate":   round(e / total * 100, 1),
        "pct_visitante": round(a / total * 100, 1),
        "total_gols": total_gols,
        "media_gols": round(df["total_goals"].mean(), 2),
        "maior_goleada": maior_goleada,
        "maior_goleada_total": int(jogo["total_goals"]),
        "lider_gols_time": display(lider["time"]),
        "lider_gols_n": int(lider["gols_pro"]),
        "campeao_time": display(campeao["time"]),
        "campeao_pontos": int(campeao["pontos"]),
        "vice_time": display(tabela.iloc[1]["time"]),
        "aproveitamento_medio": round(tabela["aproveitamento"].mean(), 1),
    }


def metricas_time(df: pd.DataFrame, time: str | None) -> dict:
    """Métricas resumidas para os KPI cards. Se time=None, devolve total da liga."""
    if time is None or time == "Todos os times":
        jogos = len(df)
        gols_pro = int(df["home_goal"].sum() + df["away_goal"].sum())
        return {
            "jogos": jogos,
            "vitorias": int((df["result"] != "D").sum()),
            "empates": int((df["result"] == "D").sum()),
            "derrotas": 0,
            "gols_pro": gols_pro,
            "gols_contra": gols_pro,
            "saldo": 0,
            "pontos": 0,
            "aproveitamento": 0.0,
        }
    base = _estatisticas_time(df, time)
    base.update(_estatisticas_chutes(df, time))
    return base


def forma_recente(df: pd.DataFrame, time: str, n: int = 5) -> list[str]:
    """Últimos n jogos do time. Retorna lista de 'V', 'E', 'D' em ordem cronológica."""
    casa = df[df["home"] == time].assign(_mando="H")
    fora = df[df["away"] == time].assign(_mando="A")
    jogos = pd.concat([casa, fora]).sort_values("date").tail(n)
    forma = []
    for _, j in jogos.iterrows():
        if j["result"] == "D":
            forma.append("E")
        elif (j["_mando"] == "H" and j["result"] == "H") or (j["_mando"] == "A" and j["result"] == "A"):
            forma.append("V")
        else:
            forma.append("D")
    return forma


def maior_vitoria_e_derrota(df: pd.DataFrame, time: str) -> tuple[dict | None, dict | None]:
    """Maior vitória e maior derrota do time, com placar e adversário."""
    casa = df[df["home"] == time].copy()
    fora = df[df["away"] == time].copy()

    casa["diff"] = casa["home_goal"] - casa["away_goal"]
    casa["adversario"] = casa["away"]
    casa["mando"] = "Casa"
    casa["placar"] = casa["home_goal"].astype(int).astype(str) + " × " + casa["away_goal"].astype(int).astype(str)

    fora["diff"] = fora["away_goal"] - fora["home_goal"]
    fora["adversario"] = fora["home"]
    fora["mando"] = "Fora"
    fora["placar"] = fora["away_goal"].astype(int).astype(str) + " × " + fora["home_goal"].astype(int).astype(str)

    cols = ["date", "adversario", "mando", "placar", "diff"]
    todos = pd.concat([casa[cols], fora[cols]])
    if not len(todos):
        return None, None

    melhor = todos.loc[todos["diff"].idxmax()]
    pior = todos.loc[todos["diff"].idxmin()]
    return _row_to_dict(melhor), _row_to_dict(pior)


def _row_to_dict(row) -> dict:
    return {
        "data": row["date"].strftime("%d/%m/%Y") if hasattr(row["date"], "strftime") else str(row["date"]),
        "adversario": row["adversario"],
        "mando": row["mando"],
        "placar": row["placar"],
        "diff": int(row["diff"]),
    }


def _estatisticas_chutes(df: pd.DataFrame, time: str) -> dict:
    casa = df[df["home"] == time]
    fora = df[df["away"] == time]
    chutes_pro = casa["home_shots"].fillna(0).sum() + fora["away_shots"].fillna(0).sum()
    chutes_contra = casa["away_shots"].fillna(0).sum() + fora["home_shots"].fillna(0).sum()
    escanteios_pro = casa["home_corner"].fillna(0).sum() + fora["away_corner"].fillna(0).sum()
    n = len(casa) + len(fora)
    gols_pro = int(casa["home_goal"].sum() + fora["away_goal"].sum())
    return {
        "chutes_pro": int(chutes_pro),
        "chutes_contra": int(chutes_contra),
        "chutes_por_jogo": round(chutes_pro / n, 1) if n else 0.0,
        "conversao": round(gols_pro / chutes_pro * 100, 1) if chutes_pro else 0.0,
        "escanteios_pro": int(escanteios_pro),
        "escanteios_por_jogo": round(escanteios_pro / n, 1) if n else 0.0,
    }


def pontos_por_rodada(df: pd.DataFrame, time: str) -> pd.DataFrame:
    """Sequência de pontos acumulados por rodada para um time, ordenado por data."""
    casa = df[df["home"] == time].copy()
    fora = df[df["away"] == time].copy()
    casa["adversario"] = casa["away"]
    casa["gols_pro"] = casa["home_goal"]
    casa["gols_contra"] = casa["away_goal"]
    casa["mando"] = "Casa"
    casa["pontos"] = casa["result"].map({"H": 3, "D": 1, "A": 0})

    fora["adversario"] = fora["home"]
    fora["gols_pro"] = fora["away_goal"]
    fora["gols_contra"] = fora["home_goal"]
    fora["mando"] = "Fora"
    fora["pontos"] = fora["result"].map({"A": 3, "D": 1, "H": 0})

    cols = ["date", "adversario", "gols_pro", "gols_contra", "mando", "pontos"]
    jogos = pd.concat([casa[cols], fora[cols]]).sort_values("date").reset_index(drop=True)
    jogos["rodada"] = jogos.index + 1
    jogos["pontos_acum"] = jogos["pontos"].cumsum()
    return jogos


def desempenho_casa_fora(df: pd.DataFrame, time: str) -> pd.DataFrame:
    """Tabela longa com V/E/D divididos por mando para o time."""
    casa = df[df["home"] == time]
    fora = df[df["away"] == time]
    return pd.DataFrame(
        [
            {"mando": "Casa", "tipo": "Vitórias", "valor": int((casa["result"] == "H").sum())},
            {"mando": "Casa", "tipo": "Empates",  "valor": int((casa["result"] == "D").sum())},
            {"mando": "Casa", "tipo": "Derrotas", "valor": int((casa["result"] == "A").sum())},
            {"mando": "Fora", "tipo": "Vitórias", "valor": int((fora["result"] == "A").sum())},
            {"mando": "Fora", "tipo": "Empates",  "valor": int((fora["result"] == "D").sum())},
            {"mando": "Fora", "tipo": "Derrotas", "valor": int((fora["result"] == "H").sum())},
        ]
    )


def top_jogos_mais_gols(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Retorna os n jogos com mais gols, formatados para exibição."""
    top = df.sort_values("total_goals", ascending=False).head(n).copy()
    top["data"] = top["date"].dt.strftime("%d/%m/%Y")
    top["placar"] = top["home_goal"].astype(str) + " x " + top["away_goal"].astype(str)
    return top[["data", "home", "placar", "away", "total_goals"]].rename(
        columns={"home": "mandante", "away": "visitante", "total_goals": "total"}
    )


def _estatisticas_time(df: pd.DataFrame, time: str) -> dict:
    casa = df[df["home"] == time]
    fora = df[df["away"] == time]

    v_casa = int((casa["result"] == "H").sum())
    e_casa = int((casa["result"] == "D").sum())
    d_casa = int((casa["result"] == "A").sum())

    v_fora = int((fora["result"] == "A").sum())
    e_fora = int((fora["result"] == "D").sum())
    d_fora = int((fora["result"] == "H").sum())

    vitorias = v_casa + v_fora
    empates = e_casa + e_fora
    derrotas = d_casa + d_fora
    jogos = vitorias + empates + derrotas

    gols_pro = int(casa["home_goal"].sum() + fora["away_goal"].sum())
    gols_contra = int(casa["away_goal"].sum() + fora["home_goal"].sum())
    saldo = gols_pro - gols_contra
    pontos = vitorias * 3 + empates
    aproveitamento = round(pontos / (jogos * 3) * 100, 1) if jogos else 0.0

    return {
        "time": time,
        "jogos": jogos,
        "vitorias": vitorias,
        "empates": empates,
        "derrotas": derrotas,
        "gols_pro": gols_pro,
        "gols_contra": gols_contra,
        "saldo": saldo,
        "pontos": pontos,
        "aproveitamento": aproveitamento,
    }
