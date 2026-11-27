from dataclasses import dataclass

import pandas as pd
import streamlit as st

from football_stats.interface.attribute_catalog import (
    ALL_NAMES,
    CONTINUOUS,
    DISCRETE,
    MATCH_LEVEL,
    TEAM_LEVEL,
    AttributeDescription,
    all_descriptions,
)
from football_stats.interface.cached_data import get_matches, get_teams
from football_stats.interface.data_tables import decimal_places

LEVEL_NAMES = {MATCH_LEVEL: "Mecze", TEAM_LEVEL: "Drużyny"}
OBSERVATION_NAMES = {MATCH_LEVEL: "meczów", TEAM_LEVEL: "drużyn"}
DEFAULT_COLUMNS = {MATCH_LEVEL: "total_goals", TEAM_LEVEL: "points"}
NUMERIC_VARIABLE_TYPES = {DISCRETE, CONTINUOUS}
MINIMUM_MEASURE_DECIMAL_PLACES = 2


@dataclass(frozen=True)
class SelectedAttribute:
    table: pd.DataFrame
    level: str
    column: str
    name: str
    unit: str
    is_continuous: bool

    @property
    def values(self) -> pd.Series:
        return self.table[self.column]

    @property
    def observation_labels(self) -> pd.Series:
        if self.level == MATCH_LEVEL:
            return self.table["home_team"] + " - " + self.table["away_team"]
        return self.table["team"]

    @property
    def observation_name(self) -> str:
        return OBSERVATION_NAMES[self.level]

    @property
    def value_decimal_places(self) -> int:
        return decimal_places(self.column, self.values)

    @property
    def measure_decimal_places(self) -> int:
        return max(self.value_decimal_places, MINIMUM_MEASURE_DECIMAL_PLACES)


def numeric_attributes(level: str) -> list[AttributeDescription]:
    return [
        description
        for description in all_descriptions()
        if description.level == level and description.variable_type in NUMERIC_VARIABLE_TYPES
    ]


def select_level() -> str:
    return st.segmented_control(
        "Poziom danych",
        list(LEVEL_NAMES),
        format_func=LEVEL_NAMES.get,
        default=MATCH_LEVEL,
        required=True,
    )


def table_for_level(level: str) -> pd.DataFrame:
    return get_matches() if level == MATCH_LEVEL else get_teams()


def select_numeric_attribute() -> SelectedAttribute:
    selection_columns = st.columns([2, 3], vertical_alignment="bottom")
    with selection_columns[0]:
        level = select_level()
    attributes = numeric_attributes(level)
    default_index = [attribute.column for attribute in attributes].index(DEFAULT_COLUMNS[level])
    with selection_columns[1]:
        attribute = st.selectbox(
            "Atrybut",
            attributes,
            index=default_index,
            format_func=lambda description: ALL_NAMES[level][description.column],
            key=f"numeric_attribute_{level}",
        )
    return SelectedAttribute(
        table=table_for_level(level),
        level=level,
        column=attribute.column,
        name=ALL_NAMES[level][attribute.column],
        unit=attribute.unit,
        is_continuous=attribute.variable_type == CONTINUOUS,
    )
