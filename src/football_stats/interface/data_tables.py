import pandas as pd
from pandas.io.formats.style import Styler

from football_stats.data.loading import LEAGUE_FILES
from football_stats.interface.formatting import NON_BREAKING_SPACE, format_date
from football_stats.interface.labels import (
    MATCH_ATTRIBUTE_NAMES,
    MATCH_INFORMATION_NAMES,
    RESULT_NAMES,
    TEAM_ATTRIBUTE_NAMES,
    TEAM_INFORMATION_NAMES,
)

ALWAYS_VISIBLE_MATCH_COLUMNS = ["date", "league", "home_team", "away_team"]

MATCH_COLUMN_GROUPS = {
    "Wynik": [
        "result",
        "home_goals",
        "away_goals",
        "total_goals",
        "home_half_time_goals",
        "away_half_time_goals",
        "total_half_time_goals",
        "second_half_goals",
    ],
    "Strzały": [
        "home_shots",
        "away_shots",
        "total_shots",
        "home_shots_on_target",
        "away_shots_on_target",
        "total_shots_on_target",
    ],
    "Rzuty rożne i faule": [
        "home_corners",
        "away_corners",
        "total_corners",
        "home_fouls",
        "away_fouls",
        "total_fouls",
    ],
    "Kartki": [
        "home_yellow_cards",
        "away_yellow_cards",
        "total_yellow_cards",
        "home_red_cards",
        "away_red_cards",
        "total_red_cards",
        "total_cards",
    ],
    "Kursy": [
        "home_win_odds",
        "draw_odds",
        "away_win_odds",
        "home_win_probability",
        "draw_probability",
        "away_win_probability",
        "bookmaker_margin",
    ],
}

DEFAULT_MATCH_COLUMN_GROUPS = ["Wynik"]

TEAM_COLUMNS = [
    "league_position",
    "team",
    "league",
    "matches_played",
    "points",
    "wins",
    "draws",
    "losses",
    "goals_scored",
    "goals_conceded",
    "goal_difference",
    "points_per_match",
    "goals_scored_per_match",
    "goals_conceded_per_match",
    "shots_per_match",
    "shots_on_target_per_match",
    "shot_accuracy_percentage",
    "corners_per_match",
    "fouls_per_match",
    "yellow_cards_per_match",
    "red_cards_per_match",
    "home_win_percentage",
    "away_win_percentage",
    "average_win_probability_percentage",
]

DEFAULT_DECIMAL_PLACES = 2
DECIMAL_PLACES_BY_NAME_ENDING = {"_probability": 3, "bookmaker_margin": 3, "_percentage": 1}

MATCH_COLUMN_NAMES = {**MATCH_INFORMATION_NAMES, **MATCH_ATTRIBUTE_NAMES}
TEAM_COLUMN_NAMES = {**TEAM_INFORMATION_NAMES, **TEAM_ATTRIBUTE_NAMES}


def decimal_places(column: str, values: pd.Series) -> int:
    if pd.api.types.is_integer_dtype(values):
        return 0
    for name_ending, places in DECIMAL_PLACES_BY_NAME_ENDING.items():
        if column.endswith(name_ending):
            return places
    return DEFAULT_DECIMAL_PLACES


def polish_table_style(table: pd.DataFrame, polish_names: dict[str, str]) -> Styler:
    style = table.rename(columns=polish_names).style
    for column in table.columns:
        values = table[column]
        polish_name = polish_names[column]
        if pd.api.types.is_datetime64_any_dtype(values):
            style = style.format(format_date, subset=[polish_name])
        elif pd.api.types.is_numeric_dtype(values):
            style = style.format(
                precision=decimal_places(column, values),
                decimal=",",
                thousands=NON_BREAKING_SPACE,
                subset=[polish_name],
            )
    return style


def match_table(matches: pd.DataFrame, column_groups: list[str]) -> Styler:
    columns = ALWAYS_VISIBLE_MATCH_COLUMNS + [
        column for group in MATCH_COLUMN_GROUPS if group in column_groups for column in MATCH_COLUMN_GROUPS[group]
    ]
    table = matches[columns].sort_values(["date", "league", "home_team"])
    if "result" in table.columns:
        table = table.assign(result=table["result"].map(RESULT_NAMES))
    return polish_table_style(table, MATCH_COLUMN_NAMES)


def team_table(teams: pd.DataFrame) -> Styler:
    table = teams[TEAM_COLUMNS].assign(
        league=pd.Categorical(teams["league"], categories=list(LEAGUE_FILES.values()), ordered=True)
    )
    table = table.sort_values(["league", "league_position"])
    return polish_table_style(table, TEAM_COLUMN_NAMES)
