from dataclasses import dataclass

import pandas as pd

from football_stats.data.loading import COLUMN_NAMES
from football_stats.interface.labels import (
    MATCH_ATTRIBUTE_NAMES,
    MATCH_INFORMATION_NAMES,
    TEAM_ATTRIBUTE_NAMES,
    TEAM_INFORMATION_NAMES,
)

MATCH_LEVEL = "mecz"
TEAM_LEVEL = "drużyna"

NOMINAL = "jakościowa nominalna"
ORDINAL = "porządkowa"
TIME = "czas (data)"
DISCRETE = "ilościowa dyskretna"
CONTINUOUS = "ilościowa ciągła"

COMPUTED_FROM_TEAM_MATCHES = "obliczone z meczów drużyny"

SOURCE_CODES = {column: code for code, column in COLUMN_NAMES.items()}

TEAMS_IN_DESCRIPTION = {"home": "gospodarzy", "away": "gości", "total": "obu drużyn"}

COUNTED_MATCH_STATISTICS = {
    "goals": ("Liczba goli {teams}.", "gole"),
    "half_time_goals": ("Liczba goli {teams} do przerwy.", "gole"),
    "shots": ("Liczba strzałów {teams}, celnych i niecelnych.", "strzały"),
    "shots_on_target": ("Liczba strzałów celnych {teams}.", "strzały"),
    "corners": ("Liczba rzutów rożnych {teams}.", "rzuty rożne"),
    "fouls": ("Liczba fauli {teams}.", "faule"),
    "yellow_cards": ("Liczba żółtych kartek {teams}.", "kartki"),
    "red_cards": ("Liczba czerwonych kartek {teams}.", "kartki"),
}

OUTCOMES = {
    "home_win": ("H", "zwycięstwo gospodarzy"),
    "draw": ("D", "remis"),
    "away_win": ("A", "zwycięstwo gości"),
}


@dataclass(frozen=True)
class AttributeDescription:
    column: str
    level: str
    variable_type: str
    unit: str
    source: str
    description: str


def counted_statistic_descriptions() -> list[AttributeDescription]:
    descriptions = []
    for statistic, (description_template, unit) in COUNTED_MATCH_STATISTICS.items():
        home_source = SOURCE_CODES[f"home_{statistic}"]
        away_source = SOURCE_CODES[f"away_{statistic}"]
        sources = {"home": home_source, "away": away_source, "total": f"{home_source} + {away_source}"}
        for side, teams_in_description in TEAMS_IN_DESCRIPTION.items():
            descriptions.append(
                AttributeDescription(
                    f"{side}_{statistic}",
                    MATCH_LEVEL,
                    DISCRETE,
                    unit,
                    sources[side],
                    description_template.format(teams=teams_in_description),
                )
            )
    return descriptions


def odds_descriptions() -> list[AttributeDescription]:
    descriptions = []
    for outcome, (code_letter, outcome_name) in OUTCOMES.items():
        descriptions.append(
            AttributeDescription(
                f"{outcome}_odds",
                MATCH_LEVEL,
                CONTINUOUS,
                "kurs dziesiętny",
                f"Avg{code_letter} (B365{code_letter}, gdy marża <= 0)",
                f"Średni kurs bukmacherów na {outcome_name}.",
            )
        )
    for outcome, (code_letter, outcome_name) in OUTCOMES.items():
        descriptions.append(
            AttributeDescription(
                f"{outcome}_probability",
                MATCH_LEVEL,
                CONTINUOUS,
                "prawdopodobieństwo (0-1)",
                f"(1/Avg{code_letter}) / (1/AvgH + 1/AvgD + 1/AvgA)",
                f"Szansa na {outcome_name} wynikająca z kursów, po usunięciu marży bukmachera.",
            )
        )
    descriptions.append(
        AttributeDescription(
            "bookmaker_margin",
            MATCH_LEVEL,
            CONTINUOUS,
            "ułamek (0-1)",
            "1/AvgH + 1/AvgD + 1/AvgA - 1",
            "Marża bukmachera, czyli nadwyżka sumy odwrotności kursów ponad 1.",
        )
    )
    return descriptions


def match_descriptions() -> list[AttributeDescription]:
    return [
        AttributeDescription("date", MATCH_LEVEL, TIME, "dzień", "Date", "Dzień rozegrania meczu."),
        AttributeDescription("league", MATCH_LEVEL, NOMINAL, "-", "nazwa pliku CSV", "Liga, w której rozegrano mecz."),
        AttributeDescription("home_team", MATCH_LEVEL, NOMINAL, "-", "HomeTeam", "Drużyna grająca u siebie."),
        AttributeDescription("away_team", MATCH_LEVEL, NOMINAL, "-", "AwayTeam", "Drużyna grająca na wyjeździe."),
        AttributeDescription(
            "result",
            MATCH_LEVEL,
            NOMINAL,
            "-",
            "FTR",
            "Wynik meczu: wygrana gospodarzy, remis albo wygrana gości.",
        ),
        *counted_statistic_descriptions(),
        AttributeDescription(
            "second_half_goals",
            MATCH_LEVEL,
            DISCRETE,
            "gole",
            "FTHG + FTAG - HTHG - HTAG",
            "Liczba goli strzelonych po przerwie przez obie drużyny.",
        ),
        AttributeDescription(
            "total_cards",
            MATCH_LEVEL,
            DISCRETE,
            "kartki",
            "HY + AY + HR + AR",
            "Wszystkie kartki w meczu, żółte i czerwone razem.",
        ),
        *odds_descriptions(),
    ]


TEAM_DESCRIPTIONS = {
    "team": (NOMINAL, "-", "Nazwa drużyny."),
    "league": (NOMINAL, "-", "Liga, w której gra drużyna."),
    "league_position": (ORDINAL, "miejsce", "Miejsce w końcowej tabeli ligi."),
    "matches_played": (DISCRETE, "mecze", "Liczba rozegranych meczów (34 albo 38, zależnie od ligi)."),
    "points": (DISCRETE, "punkty", "Punkty zdobyte w sezonie: 3 za zwycięstwo, 1 za remis."),
    "points_per_match": (CONTINUOUS, "punkty na mecz", "Średnia liczba punktów na mecz."),
    "wins": (DISCRETE, "mecze", "Liczba zwycięstw."),
    "draws": (DISCRETE, "mecze", "Liczba remisów."),
    "losses": (DISCRETE, "mecze", "Liczba porażek."),
    "goals_scored": (DISCRETE, "gole", "Gole strzelone w sezonie."),
    "goals_conceded": (DISCRETE, "gole", "Gole stracone w sezonie."),
    "goal_difference": (DISCRETE, "gole", "Różnica goli strzelonych i straconych (może być ujemna)."),
    "goals_scored_per_match": (CONTINUOUS, "gole na mecz", "Średnia liczba goli strzelonych na mecz."),
    "goals_conceded_per_match": (CONTINUOUS, "gole na mecz", "Średnia liczba goli straconych na mecz."),
    "shots_per_match": (CONTINUOUS, "strzały na mecz", "Średnia liczba strzałów na mecz."),
    "shots_on_target_per_match": (CONTINUOUS, "strzały na mecz", "Średnia liczba strzałów celnych na mecz."),
    "shot_accuracy_percentage": (CONTINUOUS, "%", "Udział strzałów celnych we wszystkich strzałach drużyny."),
    "corners_per_match": (CONTINUOUS, "rzuty rożne na mecz", "Średnia liczba rzutów rożnych na mecz."),
    "fouls_per_match": (CONTINUOUS, "faule na mecz", "Średnia liczba fauli popełnionych na mecz."),
    "yellow_cards_per_match": (CONTINUOUS, "kartki na mecz", "Średnia liczba żółtych kartek na mecz."),
    "red_cards_per_match": (CONTINUOUS, "kartki na mecz", "Średnia liczba czerwonych kartek na mecz."),
    "home_win_percentage": (CONTINUOUS, "%", "Odsetek meczów u siebie zakończonych zwycięstwem."),
    "away_win_percentage": (CONTINUOUS, "%", "Odsetek meczów na wyjeździe zakończonych zwycięstwem."),
    "average_win_probability_percentage": (
        CONTINUOUS,
        "%",
        "Średnia szansa drużyny na zwycięstwo wynikająca z kursów przed meczami.",
    ),
}


def team_descriptions() -> list[AttributeDescription]:
    return [
        AttributeDescription(column, TEAM_LEVEL, variable_type, unit, COMPUTED_FROM_TEAM_MATCHES, description)
        for column, (variable_type, unit, description) in TEAM_DESCRIPTIONS.items()
    ]


ALL_NAMES = {
    MATCH_LEVEL: {**MATCH_INFORMATION_NAMES, **MATCH_ATTRIBUTE_NAMES},
    TEAM_LEVEL: {**TEAM_INFORMATION_NAMES, **TEAM_ATTRIBUTE_NAMES},
}


def all_descriptions() -> list[AttributeDescription]:
    return [*match_descriptions(), *team_descriptions()]


def attribute_count(level: str) -> int:
    return sum(1 for item in all_descriptions() if item.level == level)


def attribute_catalog() -> pd.DataFrame:
    descriptions = all_descriptions()
    return pd.DataFrame(
        {
            "Atrybut": [ALL_NAMES[item.level][item.column] for item in descriptions],
            "Poziom": [item.level for item in descriptions],
            "Typ zmiennej": [item.variable_type for item in descriptions],
            "Jednostka": [item.unit for item in descriptions],
            "Źródło w CSV": [item.source for item in descriptions],
            "Opis": [item.description for item in descriptions],
        }
    )
