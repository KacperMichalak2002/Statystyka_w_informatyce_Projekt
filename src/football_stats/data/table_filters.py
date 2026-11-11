import pandas as pd


def name_contains(names: pd.Series, name_fragment: str) -> pd.Series:
    return names.str.contains(name_fragment.strip(), case=False, regex=False)


def filter_matches(matches: pd.DataFrame, leagues: list[str], team_name_fragment: str) -> pd.DataFrame:
    selected = matches["league"].isin(leagues)
    if team_name_fragment.strip():
        selected &= name_contains(matches["home_team"], team_name_fragment) | name_contains(
            matches["away_team"], team_name_fragment
        )
    return matches[selected]


def filter_teams(teams: pd.DataFrame, leagues: list[str], team_name_fragment: str) -> pd.DataFrame:
    selected = teams["league"].isin(leagues)
    if team_name_fragment.strip():
        selected &= name_contains(teams["team"], team_name_fragment)
    return teams[selected]
