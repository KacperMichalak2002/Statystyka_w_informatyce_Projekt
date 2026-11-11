from pathlib import Path

import pandas as pd

DATA_FOLDER = Path(__file__).resolve().parents[3] / "Data"

LEAGUE_FILES = {
    "E0.csv": "Premier League",
    "SP1.csv": "La Liga",
    "I1.csv": "Serie A",
    "D1.csv": "Bundesliga",
    "F1.csv": "Ligue 1",
}

COLUMN_NAMES = {
    "Date": "date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTR": "result",
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "HTHG": "home_half_time_goals",
    "HTAG": "away_half_time_goals",
    "HS": "home_shots",
    "AS": "away_shots",
    "HST": "home_shots_on_target",
    "AST": "away_shots_on_target",
    "HC": "home_corners",
    "AC": "away_corners",
    "HF": "home_fouls",
    "AF": "away_fouls",
    "HY": "home_yellow_cards",
    "AY": "away_yellow_cards",
    "HR": "home_red_cards",
    "AR": "away_red_cards",
    "AvgH": "home_win_odds",
    "AvgD": "draw_odds",
    "AvgA": "away_win_odds",
    "B365H": "bet365_home_win_odds",
    "B365D": "bet365_draw_odds",
    "B365A": "bet365_away_win_odds",
}

ODDS_COLUMNS = ["home_win_odds", "draw_odds", "away_win_odds"]
BET365_ODDS_COLUMNS = ["bet365_home_win_odds", "bet365_draw_odds", "bet365_away_win_odds"]

RESULT_NAMES = {"H": "home_win", "D": "draw", "A": "away_win"}

MATCH_STATISTICS = [
    "goals",
    "half_time_goals",
    "shots",
    "shots_on_target",
    "corners",
    "fouls",
    "yellow_cards",
    "red_cards",
]


def load_league(file_name: str, league: str) -> pd.DataFrame:
    league_matches = pd.read_csv(
        DATA_FOLDER / file_name,
        encoding="utf-8-sig",
        usecols=list(COLUMN_NAMES),
    )
    league_matches = league_matches.rename(columns=COLUMN_NAMES)
    league_matches["date"] = pd.to_datetime(league_matches["date"], format="%d/%m/%Y")
    league_matches["result"] = league_matches["result"].map(RESULT_NAMES)
    league_matches.insert(0, "league", league)
    return league_matches


def add_match_totals(matches: pd.DataFrame) -> pd.DataFrame:
    for statistic in MATCH_STATISTICS:
        matches[f"total_{statistic}"] = matches[f"home_{statistic}"] + matches[f"away_{statistic}"]
    matches["second_half_goals"] = matches["total_goals"] - matches["total_half_time_goals"]
    matches["total_cards"] = matches["total_yellow_cards"] + matches["total_red_cards"]
    return matches


def bookmaker_margin(odds: pd.DataFrame) -> pd.Series:
    return (1 / odds).sum(axis=1, min_count=3) - 1


def replace_impossible_average_odds(matches: pd.DataFrame) -> pd.DataFrame:
    impossible_odds = bookmaker_margin(matches[ODDS_COLUMNS]) <= 0
    matches.loc[impossible_odds, ODDS_COLUMNS] = matches.loc[impossible_odds, BET365_ODDS_COLUMNS].to_numpy()
    return matches.drop(columns=BET365_ODDS_COLUMNS)


def add_win_probabilities(matches: pd.DataFrame) -> pd.DataFrame:
    inverse_odds = 1 / matches[ODDS_COLUMNS]
    inverse_odds_sum = inverse_odds.sum(axis=1, min_count=3)
    matches["home_win_probability"] = inverse_odds["home_win_odds"] / inverse_odds_sum
    matches["draw_probability"] = inverse_odds["draw_odds"] / inverse_odds_sum
    matches["away_win_probability"] = inverse_odds["away_win_odds"] / inverse_odds_sum
    matches["bookmaker_margin"] = inverse_odds_sum - 1
    return matches


def load_matches() -> pd.DataFrame:
    all_leagues = [load_league(file_name, league) for file_name, league in LEAGUE_FILES.items()]
    matches = pd.concat(all_leagues, ignore_index=True)
    matches = add_match_totals(matches)
    matches = replace_impossible_average_odds(matches)
    matches = add_win_probabilities(matches)
    return matches
