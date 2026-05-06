"""Carregamento e limpeza dos dados do Campeonato Brasileiro."""

from pathlib import Path
import pandas as pd

DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "raw" / "BR-Football-Dataset.csv"


def load_raw(path: Path | str = DEFAULT_CSV) -> pd.DataFrame:
    """Lê o CSV bruto. Usa engine='python' para evitar problema de memória do engine C."""
    return pd.read_csv(path, engine="python", parse_dates=["date"])


def load_serie_a_2017(path: Path | str = DEFAULT_CSV) -> pd.DataFrame:
    """Filtra apenas jogos da Série A de 2017 e enriquece com colunas auxiliares."""
    df = load_raw(path)

    df = df[(df["tournament"] == "Serie A") & (df["date"].dt.year == 2017)].copy()
    df = df.dropna(subset=["home_goal", "away_goal"])
    df["home_goal"] = df["home_goal"].astype(int)
    df["away_goal"] = df["away_goal"].astype(int)

    df["total_goals"] = df["home_goal"] + df["away_goal"]
    df["result"] = df.apply(_resultado, axis=1)

    df = df.sort_values("date").reset_index(drop=True)
    return df[[
        "date", "home", "home_goal", "away_goal", "away",
        "total_goals", "result",
        "home_shots", "away_shots",
        "home_corner", "away_corner",
    ]]


def _resultado(row) -> str:
    if row["home_goal"] > row["away_goal"]:
        return "H"
    if row["home_goal"] < row["away_goal"]:
        return "A"
    return "D"
