from base64 import b64encode
from functools import cache
from pathlib import Path

LEAGUE_LOGOS_FOLDER = Path(__file__).resolve().parents[3] / "assets" / "leagues"

LEAGUE_LOGO_FILES = {
    "Premier League": "england_english-premier-league.svg",
    "La Liga": "spain_la-liga.svg",
    "Serie A": "italy_serie-a.svg",
    "Bundesliga": "germany_bundesliga.svg",
    "Ligue 1": "france_ligue-1.svg",
}


@cache
def league_logo_data_address(league: str) -> str:
    logo_bytes = (LEAGUE_LOGOS_FOLDER / LEAGUE_LOGO_FILES[league]).read_bytes()
    return f"data:image/svg+xml;base64,{b64encode(logo_bytes).decode('ascii')}"
