import pandas as pd
import plotly.graph_objects as go

from football_stats.interface.formatting import format_number, whole_percentages_summing_to_hundred
from football_stats.interface.labels import RESULT_NAMES
from football_stats.interface.theme import LEAGUE_COLORS, BACKGROUND_COLOR, RESULT_COLORS

CHART_HEIGHT = 460
CHART_MARGIN = {"t": 50, "b": 140}
PLOT_AREA_HEIGHT = CHART_HEIGHT - CHART_MARGIN["t"] - CHART_MARGIN["b"]
LEGEND_DISTANCE_BELOW_PLOT = 74


def goals_per_match_chart(league_summary: pd.DataFrame) -> go.Figure:
    goals_per_match = league_summary["goals_per_match"]
    figure = go.Figure(
        go.Bar(
            x=goals_per_match,
            y=league_summary.index,
            orientation="h",
            marker_color=[LEAGUE_COLORS[league] for league in league_summary.index],
            text=[format_number(value, 2) for value in goals_per_match],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Średnio %{x:.2f} gola na mecz<extra></extra>",
        )
    )
    figure.update_layout(
        title="Średnia liczba goli na mecz",
        xaxis={"title": "Gole na mecz", "range": [0, 1.15 * goals_per_match.max()]},
        yaxis={"autorange": "reversed"},
        margin=CHART_MARGIN,
        height=CHART_HEIGHT,
    )
    return figure


def match_results_chart(league_summary: pd.DataFrame) -> go.Figure:
    result_columns = [f"{result}_percentage" for result in RESULT_NAMES]
    whole_percentages = league_summary[result_columns].apply(
        lambda row: pd.Series(whole_percentages_summing_to_hundred(row.tolist()), index=result_columns),
        axis=1,
    )
    figure = go.Figure()
    for result, result_name in RESULT_NAMES.items():
        column = f"{result}_percentage"
        figure.add_bar(
            name=result_name,
            x=league_summary[column],
            y=league_summary.index,
            orientation="h",
            marker_color=RESULT_COLORS[result],
            text=[f"{value}%" for value in whole_percentages[column]],
            textposition="inside",
            insidetextanchor="middle",
            textfont={"color": BACKGROUND_COLOR},
            hoverlabel={"bordercolor": RESULT_COLORS[result]},
            hovertemplate="<b>%{y}</b><br>" + result_name + ": %{x:.1f}%<extra></extra>",
        )
    figure.update_layout(
        title="Jak kończą się mecze",
        barmode="stack",
        xaxis={"title": "Udział meczów (%)", "range": [0, 100], "tickvals": [0, 20, 40, 60, 80, 100]},
        yaxis={"autorange": "reversed"},
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -LEGEND_DISTANCE_BELOW_PLOT / PLOT_AREA_HEIGHT,
            "yanchor": "top",
            "traceorder": "normal",
            "font": {"size": 13},
        },
        margin=CHART_MARGIN,
        height=CHART_HEIGHT,
    )
    return figure
