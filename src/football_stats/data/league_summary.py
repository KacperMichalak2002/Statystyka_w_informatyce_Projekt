import pandas as pd

from football_stats.data.loading import LEAGUE_FILES


def build_league_summary(matches: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    grouped = matches.groupby("league")
    summary = pd.DataFrame(
        {
            "matches": grouped.size(),
            "teams": teams.groupby("league").size(),
            "goals_per_match": grouped["total_goals"].mean(),
            "cards_per_match": grouped["total_cards"].mean(),
            "home_win_percentage": 100 * grouped["result"].apply(lambda results: (results == "home_win").mean()),
            "draw_percentage": 100 * grouped["result"].apply(lambda results: (results == "draw").mean()),
            "away_win_percentage": 100 * grouped["result"].apply(lambda results: (results == "away_win").mean()),
        }
    )
    champions = teams[teams["league_position"] == 1].set_index("league")
    summary["champion"] = champions["team"]
    summary["champion_points"] = champions["points"]
    return summary.reindex(list(LEAGUE_FILES.values()))
