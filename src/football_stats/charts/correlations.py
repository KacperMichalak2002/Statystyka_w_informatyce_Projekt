import numpy as np
import pandas as pd
import plotly.graph_objects as go

from football_stats.data.loading import LEAGUE_FILES
from football_stats.interface.formatting import format_number
from football_stats.interface.theme import (
    ACCENT_COLOR,
    LEAGUE_COLORS,
    NEGATIVE_CORRELATION_COLOR,
    PANEL_BACKGROUND_COLOR,
    POSITIVE_CORRELATION_COLOR,
    TEXT_COLOR,
)

CORRELATION_COLOR_SCALE = [
    [0, NEGATIVE_CORRELATION_COLOR],
    [0.5, PANEL_BACKGROUND_COLOR],
    [1, POSITIVE_CORRELATION_COLOR],
]
COEFFICIENT_DECIMAL_PLACES = 2
MINIMUM_HEATMAP_HEIGHT = 460
HEATMAP_ROW_HEIGHT = 24
HEATMAP_LABELS_HEIGHT = 240
LARGEST_ATTRIBUTE_COUNT_WITH_CELL_VALUES = 16
SCATTER_CHART_HEIGHT = 520
SCATTER_MARKER = {"size": 9, "opacity": 0.75}
LARGEST_SHARE_OF_DISTINCT_POINTS_FOR_BUBBLES = 0.5
LARGEST_BUBBLE_DIAMETER = 34
SMALLEST_BUBBLE_DIAMETER = 3
BUBBLE_OPACITY = 0.6
TREND_LINE_WIDTH = 3


def correlation_heatmap(matrix: pd.DataFrame, attribute_names: dict[str, str], title: str) -> go.Figure:
    names = [attribute_names[column] for column in matrix.columns]
    show_cell_values = len(names) <= LARGEST_ATTRIBUTE_COUNT_WITH_CELL_VALUES
    cell_texts = [
        [format_number(value, COEFFICIENT_DECIMAL_PLACES) if np.isfinite(value) else "" for value in row]
        for row in matrix.to_numpy()
    ]
    figure = go.Figure(
        go.Heatmap(
            z=matrix.to_numpy(),
            x=names,
            y=names,
            zmin=-1,
            zmax=1,
            colorscale=CORRELATION_COLOR_SCALE,
            text=cell_texts,
            texttemplate="%{text}" if show_cell_values else None,
            xgap=1,
            ygap=1,
            hoverongaps=False,
            colorbar={"title": "Współczynnik", "tickvals": [-1, -0.5, 0, 0.5, 1]},
            hovertemplate="<b>%{y}</b><br><b>%{x}</b><br>Współczynnik: %{text}<extra></extra>",
        )
    )
    figure.update_layout(
        title=title,
        xaxis={"tickangle": -45, "showgrid": False, "dtick": 1},
        yaxis={"autorange": "reversed", "showgrid": False, "dtick": 1},
        height=max(MINIMUM_HEATMAP_HEIGHT, HEATMAP_ROW_HEIGHT * len(names) + HEATMAP_LABELS_HEIGHT),
    )
    return figure


def points_overlap(table: pd.DataFrame, first_column: str, second_column: str) -> bool:
    distinct_points = len(table[[first_column, second_column]].drop_duplicates())
    return distinct_points < LARGEST_SHARE_OF_DISTINCT_POINTS_FOR_BUBBLES * len(table)


def add_observation_count_bubbles(
    figure: go.Figure, table: pd.DataFrame, first_column: str, second_column: str, count_name: str
) -> None:
    point_counts = table.groupby([first_column, second_column]).size().rename("count").reset_index()
    largest_bubble_area = LARGEST_BUBBLE_DIAMETER**2
    figure.add_scatter(
        x=point_counts[first_column],
        y=point_counts[second_column],
        mode="markers",
        name=count_name,
        marker={
            "size": point_counts["count"],
            "sizemode": "area",
            "sizeref": point_counts["count"].max() / largest_bubble_area,
            "sizemin": SMALLEST_BUBBLE_DIAMETER,
            "color": ACCENT_COLOR,
            "opacity": BUBBLE_OPACITY,
        },
        hovertemplate="%{x} i %{y}<br>" + count_name + ": %{marker.size}<extra></extra>",
    )


def add_league_points(
    figure: go.Figure,
    table: pd.DataFrame,
    first_column: str,
    second_column: str,
    point_labels: pd.Series,
    first_axis_title: str,
    second_axis_title: str,
) -> None:
    for league in LEAGUE_FILES.values():
        league_rows = table.index[table["league"] == league]
        if league_rows.empty:
            continue
        figure.add_scatter(
            x=table.loc[league_rows, first_column],
            y=table.loc[league_rows, second_column],
            text=point_labels.loc[league_rows],
            mode="markers",
            name=league,
            marker={**SCATTER_MARKER, "color": LEAGUE_COLORS[league]},
            hovertemplate="<b>%{text}</b><br>"
            + first_axis_title
            + ": %{x}<br>"
            + second_axis_title
            + ": %{y}<extra></extra>",
        )


def pair_scatter_chart(
    table: pd.DataFrame,
    first_column: str,
    second_column: str,
    point_labels: pd.Series,
    trend_line: tuple[float, float] | None,
    count_name: str,
    title: str,
    first_axis_title: str,
    second_axis_title: str,
) -> go.Figure:
    figure = go.Figure()
    if points_overlap(table, first_column, second_column):
        add_observation_count_bubbles(figure, table, first_column, second_column, count_name)
    else:
        add_league_points(figure, table, first_column, second_column, point_labels, first_axis_title, second_axis_title)
    if trend_line is not None:
        slope, intercept = trend_line
        line_ends = np.array([table[first_column].min(), table[first_column].max()])
        figure.add_scatter(
            x=line_ends,
            y=slope * line_ends + intercept,
            mode="lines",
            name="Prosta regresji",
            line={"color": TEXT_COLOR, "width": TREND_LINE_WIDTH},
            hoverinfo="skip",
        )
    figure.update_layout(
        title=title,
        xaxis={"title": first_axis_title},
        yaxis={"title": second_axis_title},
        legend={"orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.2, "yanchor": "top"},
        margin={"t": 50, "b": 110},
        height=SCATTER_CHART_HEIGHT,
    )
    return figure
