import pandas as pd

TEAM_STATISTICS = ["shots", "shots_on_target", "corners", "fouls", "yellow_cards", "red_cards"]

LEAGUES_RANKED_BY_HEAD_TO_HEAD = {"La Liga", "Serie A"}


def team_matches_from_one_side(matches: pd.DataFrame, side: str) -> pd.DataFrame:
    opponent_side = "away" if side == "home" else "home"
    team_matches = pd.DataFrame(
        {
            "league": matches["league"],
            "team": matches[f"{side}_team"],
            "is_home_match": side == "home",
            "goals_scored": matches[f"{side}_goals"],
            "goals_conceded": matches[f"{opponent_side}_goals"],
            "win_probability": matches[f"{side}_win_probability"],
            "won": matches["result"] == f"{side}_win",
            "drawn": matches["result"] == "draw",
            "lost": matches["result"] == f"{opponent_side}_win",
        }
    )
    for statistic in TEAM_STATISTICS:
        team_matches[statistic] = matches[f"{side}_{statistic}"]
    return team_matches


def team_matches_from_both_sides(matches: pd.DataFrame) -> pd.DataFrame:
    home_matches = team_matches_from_one_side(matches, "home")
    away_matches = team_matches_from_one_side(matches, "away")
    return pd.concat([home_matches, away_matches], ignore_index=True)


def head_to_head_records(matches: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    records = []
    teams_in_head_to_head_leagues = teams[teams["league"].isin(LEAGUES_RANKED_BY_HEAD_TO_HEAD)]
    for (league, _), teams_level_on_points in teams_in_head_to_head_leagues.groupby(["league", "points"]):
        if len(teams_level_on_points) < 2:
            continue
        team_names = teams_level_on_points["team"]
        matches_between_them = matches[
            (matches["league"] == league)
            & matches["home_team"].isin(team_names)
            & matches["away_team"].isin(team_names)
        ]
        mini_table = team_matches_from_both_sides(matches_between_them).groupby(["league", "team"]).agg(
            wins=("won", "sum"),
            draws=("drawn", "sum"),
            goals_scored=("goals_scored", "sum"),
            goals_conceded=("goals_conceded", "sum"),
        )
        records.append(
            pd.DataFrame(
                {
                    "head_to_head_points": 3 * mini_table["wins"] + mini_table["draws"],
                    "head_to_head_goal_difference": mini_table["goals_scored"] - mini_table["goals_conceded"],
                }
            )
        )
    if not records:
        return pd.DataFrame(columns=["head_to_head_points", "head_to_head_goal_difference"])
    return pd.concat(records)


def add_league_positions(teams: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    tie_breaks = head_to_head_records(matches, teams.reset_index())
    teams = teams.join(tie_breaks).fillna({"head_to_head_points": 0, "head_to_head_goal_difference": 0})
    teams = teams.reset_index().sort_values(
        ["league", "points", "head_to_head_points", "head_to_head_goal_difference", "goal_difference", "goals_scored", "team"],
        ascending=[True, False, False, False, False, False, True],
    )
    teams = teams.drop(columns=["head_to_head_points", "head_to_head_goal_difference"])
    teams.insert(2, "league_position", teams.groupby("league").cumcount() + 1)
    return teams.reset_index(drop=True)


def build_team_table(matches: pd.DataFrame) -> pd.DataFrame:
    team_matches = team_matches_from_both_sides(matches)
    home_only = team_matches[team_matches["is_home_match"]]
    away_only = team_matches[~team_matches["is_home_match"]]
    grouped = team_matches.groupby(["league", "team"])

    teams = grouped.agg(
        matches_played=("won", "size"),
        wins=("won", "sum"),
        draws=("drawn", "sum"),
        losses=("lost", "sum"),
        goals_scored=("goals_scored", "sum"),
        goals_conceded=("goals_conceded", "sum"),
    )
    teams["points"] = 3 * teams["wins"] + teams["draws"]
    teams["goal_difference"] = teams["goals_scored"] - teams["goals_conceded"]
    teams["points_per_match"] = teams["points"] / teams["matches_played"]
    teams["goals_scored_per_match"] = teams["goals_scored"] / teams["matches_played"]
    teams["goals_conceded_per_match"] = teams["goals_conceded"] / teams["matches_played"]
    for statistic in TEAM_STATISTICS:
        teams[f"{statistic}_per_match"] = grouped[statistic].mean()
    teams["shot_accuracy_percentage"] = 100 * grouped["shots_on_target"].sum() / grouped["shots"].sum()
    teams["home_win_percentage"] = 100 * home_only.groupby(["league", "team"])["won"].mean()
    teams["away_win_percentage"] = 100 * away_only.groupby(["league", "team"])["won"].mean()
    teams["average_win_probability_percentage"] = 100 * grouped["win_probability"].mean()

    return add_league_positions(teams, matches)
