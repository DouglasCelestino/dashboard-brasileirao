"""Identidade visual e display dos clubes do Brasileirão 2017.

`color`   — accent escolhido pra alto contraste em fundo escuro.
`slug`    — nome de arquivo do logo em assets/logos/{slug}.png
`abbr`    — fallback quando o logo não existe.
`display` — nome formatado pra UI (com til, hífens, abreviações).

Os dados crus do CSV (chave do dict) são preservados em todo o pipeline;
display só é usado na camada visual.
"""

from pathlib import Path

DEFAULT = {"slug": "default", "color": "#3DA5D9", "abbr": "—", "display": "—"}

TEAM_INFO: dict[str, dict] = {
    "Corinthians":         {"slug": "corinthians",         "color": "#F5F5F5", "abbr": "COR", "display": "Corinthians"},
    "Palmeiras":           {"slug": "palmeiras",           "color": "#1B9E4A", "abbr": "PAL", "display": "Palmeiras"},
    "Santos":              {"slug": "santos",              "color": "#F4D43A", "abbr": "SAN", "display": "Santos"},
    "Gremio":              {"slug": "gremio",              "color": "#1E8FE0", "abbr": "GRE", "display": "Grêmio"},
    "Cruzeiro":            {"slug": "cruzeiro",            "color": "#3656C7", "abbr": "CRU", "display": "Cruzeiro"},
    "Flamengo":            {"slug": "flamengo",            "color": "#E8202A", "abbr": "FLA", "display": "Flamengo"},
    "Vasco Da Gama RJ":    {"slug": "vasco",               "color": "#EAEAEA", "abbr": "VAS", "display": "Vasco da Gama"},
    "Chapecoense":         {"slug": "chapecoense",         "color": "#1FA85B", "abbr": "CHA", "display": "Chapecoense"},
    "Atletico Mineiro":    {"slug": "atletico-mineiro",    "color": "#E5E5E5", "abbr": "CAM", "display": "Atlético-MG"},
    "Botafogo RJ":         {"slug": "botafogo",            "color": "#E5E5E5", "abbr": "BOT", "display": "Botafogo"},
    "Atletico Paranaense": {"slug": "atletico-paranaense", "color": "#E8202A", "abbr": "CAP", "display": "Athletico-PR"},
    "EC Bahia":            {"slug": "bahia",               "color": "#3656C7", "abbr": "BAH", "display": "Bahia"},
    "Sao Paulo":           {"slug": "sao-paulo",           "color": "#E8202A", "abbr": "SAO", "display": "São Paulo"},
    "Fluminense":          {"slug": "fluminense",          "color": "#8A1538", "abbr": "FLU", "display": "Fluminense"},
    "Sport Recife":        {"slug": "sport",               "color": "#E8202A", "abbr": "SPT", "display": "Sport"},
    "Vitoria":             {"slug": "vitoria",             "color": "#E8202A", "abbr": "VIT", "display": "Vitória"},
    "Coritiba":            {"slug": "coritiba",            "color": "#1B9E4A", "abbr": "CFC", "display": "Coritiba"},
    "Avai":                {"slug": "avai",                "color": "#3656C7", "abbr": "AVA", "display": "Avaí"},
    "Ponte Preta":         {"slug": "ponte-preta",         "color": "#E5E5E5", "abbr": "PON", "display": "Ponte Preta"},
    "Atletico Goianiense": {"slug": "atletico-goianiense", "color": "#E8202A", "abbr": "ACG", "display": "Atlético-GO"},
}

LEAGUE_ACCENT = "#3DA5D9"
LOGOS_DIR = Path(__file__).resolve().parent.parent / "assets" / "logos"


def info(time: str | None) -> dict:
    if not time or time == "Todos os times":
        return {"slug": "league", "color": LEAGUE_ACCENT, "abbr": "BR", "display": "Brasileirão 2017"}
    return TEAM_INFO.get(time, DEFAULT)


def display(time: str | None) -> str:
    """Nome formatado pra UI; retorna o próprio nome se não estiver mapeado."""
    if not time or time == "Todos os times":
        return "Todos os times"
    return TEAM_INFO.get(time, {}).get("display", time)


def logo_url(time: str | None) -> str | None:
    """Retorna a URL do logo se o arquivo existir; senão None."""
    if not time:
        return None
    slug = info(time)["slug"]
    for ext in ("png", "svg", "jpg", "webp"):
        p = LOGOS_DIR / f"{slug}.{ext}"
        if p.exists():
            return f"/assets/logos/{p.name}"
    return None
