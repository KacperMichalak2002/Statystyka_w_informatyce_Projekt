import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats

from football_stats.charts.descriptive_statistics import (
    CHART_HEIGHT,
    LEGEND_BELOW_CHART,
    MEASURE_LINE_WIDTH,
    frequency_bars,
    league_color,
)
from football_stats.interface.theme import ACCENT_COLOR, MUTED_TEXT_COLOR, TEXT_COLOR

DISCRETE_CLASS_WIDTH = 1
NORMAL_CURVE_POINT_COUNT = 200
BAR_OPACITY = 0.6
SPACE_ABOVE_HIGHEST_POINT = 1.08
LORENZ_AREA_OPACITY = 0.25
LORENZ_CHART_HEIGHT = 480


def normal_curve_points(
    values: pd.Series, mean: float, standard_deviation: float, class_width: float
) -> tuple[np.ndarray, np.ndarray]:
    half_class = class_width / 2
    curve_x = np.linspace(values.min() - half_class, values.max() + half_class, NORMAL_CURVE_POINT_COUNT)
    expected_counts = len(values) * class_width * stats.norm.pdf(curve_x, mean, standard_deviation)
    return curve_x, expected_counts


def histogram_with_normal_curve(
    values: pd.Series,
    is_continuous: bool,
    mean: float,
    standard_deviation: float,
    league: str,
    title: str,
    value_axis_title: str,
    count_axis_title: str,
) -> go.Figure:
    values = values.dropna()
    counts, bar_width = frequency_bars(values, is_continuous)
    figure = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts,
            width=bar_width,
            name="Liczebność",
            marker_color=league_color(league),
            opacity=BAR_OPACITY,
            hovertemplate="Wartość: %{x}<br>" + count_axis_title + ": %{y}<extra></extra>",
        )
    )
    highest_point = counts.max()
    if values.nunique() > 1:
        class_width = bar_width if is_continuous else DISCRETE_CLASS_WIDTH
        curve_x, expected_counts = normal_curve_points(values, mean, standard_deviation, class_width)
        highest_point = max(highest_point, expected_counts.max())
        figure.add_scatter(
            x=curve_x,
            y=expected_counts,
            mode="lines",
            name="Rozkład normalny o tej samej średniej i odchyleniu",
            line={"color": TEXT_COLOR, "width": MEASURE_LINE_WIDTH},
            hoverinfo="skip",
        )
    line_top = SPACE_ABOVE_HIGHEST_POINT * highest_point
    figure.add_scatter(
        x=[mean, mean],
        y=[0, line_top],
        mode="lines",
        name="Średnia",
        line={"color": ACCENT_COLOR, "width": MEASURE_LINE_WIDTH, "dash": "dash"},
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


def lorenz_curve_chart(
    shares_of_observations: np.ndarray, shares_of_total: np.ndarray, league: str, title: str
) -> go.Figure:
    observation_percentages = 100 * shares_of_observations
    total_percentages = 100 * shares_of_total
    color = league_color(league)
    figure = go.Figure()
    figure.add_scatter(
        x=[0, 100],
        y=[0, 100],
        mode="lines",
        name="Równy podział",
        line={"color": MUTED_TEXT_COLOR, "width": 2, "dash": "dash"},
        hoverinfo="skip",
    )
    figure.add_scatter(
        x=observation_percentages,
        y=total_percentages,
        mode="lines",
        name="Krzywa Lorenza",
        line={"color": color, "width": MEASURE_LINE_WIDTH},
        fill="tonexty",
        fillcolor=transparent_color(color, LORENZ_AREA_OPACITY),
        hovertemplate="%{x:.1f}% obserwacji z najmniejszymi wartościami<br>"
        "ma %{y:.1f}% sumy wartości<extra></extra>",
    )
    figure.update_layout(
        title=title,
        xaxis={"title": "Skumulowany udział obserwacji (%)", "range": [0, 100], "ticksuffix": "%"},
        yaxis={"title": "Skumulowany udział sumy wartości (%)", "range": [0, 100], "ticksuffix": "%"},
        legend=LEGEND_BELOW_CHART,
        margin={"t": 50, "b": 110},
        height=LORENZ_CHART_HEIGHT,
    )
    return figure


def transparent_color(hex_color: str, opacity: float) -> str:
    red, green, blue = (int(hex_color[position : position + 2], 16) for position in (1, 3, 5))
    return f"rgba({red}, {green}, {blue}, {opacity})"
