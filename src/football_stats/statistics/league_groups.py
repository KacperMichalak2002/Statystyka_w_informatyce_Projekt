from collections.abc import Callable

import pandas as pd

from football_stats.data.loading import LEAGUE_FILES


def measures_by_league(
    table: pd.DataFrame,
    column: str,
    calculate_measures: Callable[[pd.Series], dict],
    all_leagues_name: str,
) -> pd.DataFrame:
    measures = {all_leagues_name: calculate_measures(table[column])}
    for league in LEAGUE_FILES.values():
        measures[league] = calculate_measures(table.loc[table["league"] == league, column])
    return pd.DataFrame.from_dict(measures, orient="index")
