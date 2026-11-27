import pandas as pd
from pandas.io.formats.style import Styler

from football_stats.interface.formatting import MISSING_VALUE_TEXT, NON_BREAKING_SPACE, format_number

LEAGUE_COLUMN_NAME = "Liga"


def measure_table(measures: pd.DataFrame, column_names: dict[str, str], decimal_places: dict[str, int]) -> Styler:
    table = measures[list(column_names)].rename(columns=column_names)
    table.insert(0, LEAGUE_COLUMN_NAME, table.index)
    for column, polish_name in column_names.items():
        if pd.api.types.is_numeric_dtype(measures[column]) and measures[column].isna().any():
            table[polish_name] = measures[column].apply(format_number, args=(decimal_places.get(column, 0),))
    style = table.style
    for column, polish_name in column_names.items():
        if pd.api.types.is_numeric_dtype(table[polish_name]):
            style = style.format(
                precision=decimal_places.get(column, 0),
                decimal=",",
                thousands=NON_BREAKING_SPACE,
                na_rep=MISSING_VALUE_TEXT,
                subset=[polish_name],
            )
    return style
