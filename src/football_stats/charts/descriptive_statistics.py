from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from football_stats.data.loading import LEAGUE_FILES
from football_stats.interface.formatting import format_number
from football_stats.interface.theme import LEAGUE_COLORS, MUTED_TEXT_COLOR
from football_stats.statistics.central_tendency import class_count_by_sturges_rule

CHART_HEIGHT = 460
LEGEND_BELOW_CHART = {"orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.22, "yanchor": "top"}
MEASURE_LINE_WIDTH = 3
BAR_OPACITY_UNDER_MEASURE_LINES = 0.55
SPACE_ABOVE_HIGHEST_BAR = 1.08
SPACE_FOR_BAR_LABELS = 1.15


@dataclass(frozen=True)
class MeasureLine:
    name: str
    value: float
    color: str
    dash: str


def league_color(league: str) -> str:
    return LEAGUE_COLORS.get(league, MUTED_TEXT_COLOR)


def frequency_bars(values: pd.Series, is_continuous: bool) -> tuple[pd.Series, float | None]:
    if is_continuous:
        class_counts, class_edges = np.histogram(values, bins=class_count_by_sturges_rule(len(values)))
        class_middles = (class_edges[:-1] + class_edges[1:]) / 2
        return pd.Series(class_counts, index=class_middles), class_edges[1] - class_edges[0]
    return values.value_counts().sort_index(), None


def distribution_chart(
    values: pd.Series,
    is_continuous: bool,
    measure_lines: list[MeasureLine],
    league: str,
    title: str,
    value_axis_title: str,
    count_axis_title: str,
) -> go.Figure:
    counts, bar_width = frequency_bars(values.dropna(), is_continuous)
    line_top = SPACE_ABOVE_HIGHEST_BAR * counts.max()
    figure = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts,
            width=bar_width,
            marker_color=league_color(league),
            opacity=BAR_OPACITY_UNDER_MEASURE_LINES,
            showlegend=False,
            hovertemplate="Wartość: %{x}<br>" + count_axis_title + ": %{y}<extra></extra>",
        )
    )
    for measure_line in measure_lines:
        figure.add_scatter(
            x=[measure_line.value, measure_line.value],
            y=[0, line_top],
            mode="lines",
            name=measure_line.name,
            line={"color": measure_line.color, "width": MEASURE_LINE_WIDTH, "dash": measure_line.dash},
            hoverinfo="skip",
        )
    figure.update_layout(
        title=title,
        xaxis={"title": value_axis_title},
        yaxis={"title": count_axis_title, "range": [0, line_top]},
        legend=LEGEND_BELOW_CHART,
        bargap=0.08,
        margin={"t": 50, "b": 110},
        height=CHART_HEIGHT,
    )
    return figure


def league_box_plot(
    table: pd.DataFrame,
    column: str,
    point_labels: pd.Series,
    all_leagues_name: str,
    title: str,
    value_axis_title: str,
    show_all_points: bool,
) -> go.Figure:
    groups = {all_leagues_name: table.index}
    for league in LEAGUE_FILES.values():
        groups[league] = table.index[table["league"] == league]
    figure = go.Figure()
    for group_name, group_rows in groups.items():
        figure.add_box(
            y=table.loc[group_rows, column],
            text=point_labels.loc[group_rows],
            name=group_name,
            marker_color=league_color(group_name),
            boxmean="sd",
            boxpoints="all" if show_all_points else "outliers",
            jitter=0.5,
            pointpos=0,
            hoveron="points",
            hovertemplate="<b>%{text}</b><br>" + value_axis_title + ": %{y}<extra></extra>",
        )
    figure.update_layout(
        title=title,
        yaxis={"title": value_axis_title},
        showlegend=False,
        height=CHART_HEIGHT,
    )
    return figure


def league_measure_chart(
    measure_values: pd.Series,
    title: str,
    value_axis_title: str,
    decimal_places: int,
    value_suffix: str = "",
) -> go.Figure:
    figure = go.Figure(
        go.Bar(
            x=measure_values,
            y=measure_values.index,
            orientation="h",
            marker_color=[league_color(league) for league in measure_values.index],
            text=[f"{format_number(value, decimal_places)}{value_suffix}" for value in measure_values],
            textposition="outside",
            cliponaxis=False,
            hoverinfo="skip",
        )
    )
    figure.update_layout(
        title=title,
        xaxis={"title": value_axis_title, "range": [0, SPACE_FOR_BAR_LABELS * measure_values.max()]},
        yaxis={"autorange": "reversed"},
        height=CHART_HEIGHT,
    )
    return figure
