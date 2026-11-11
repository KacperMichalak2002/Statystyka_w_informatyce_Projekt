from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from football_stats.interface.formatting import format_number
from football_stats.interface.labels import LEAGUE_COUNTRIES
from football_stats.interface.league_logos import league_logo_data_address
from football_stats.interface.theme import (
    BORDER_COLOR,
    LEAGUE_COLORS,
    MUTED_TEXT_COLOR,
    PANEL_BACKGROUND_COLOR,
    TEXT_COLOR,
)

CHART_CONFIGURATION = {"displayModeBar": False, "scrollZoom": False, "doubleClick": False}

APPLICATION_STYLES = f"""
<style>
.league-cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
    gap: 1rem;
}}
.league-card {{
    background: {PANEL_BACKGROUND_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-top: 4px solid var(--league-color);
    border-radius: 0.6rem;
    padding: 0.9rem 1rem;
}}
.league-card-header {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 0.4rem;
}}
.league-logo {{
    flex: none;
    width: 2.8rem;
    height: 2.8rem;
    padding: 0.3rem;
    background: {TEXT_COLOR};
    border-radius: 0.5rem;
    object-fit: contain;
}}
.league-card-name {{
    font-size: 1.15rem;
    font-weight: 600;
    line-height: 1.2;
}}
.league-card-details {{
    color: {MUTED_TEXT_COLOR};
    font-size: 0.85rem;
    margin-bottom: 0.6rem;
}}
.league-card-label {{
    color: {MUTED_TEXT_COLOR};
    font-size: 0.85rem;
}}
.league-card-value {{
    font-weight: 600;
    margin-bottom: 0.5rem;
}}
</style>
"""


def apply_application_styles() -> None:
    st.html(APPLICATION_STYLES)


def show_chart(figure: go.Figure) -> None:
    st.plotly_chart(figure, theme=None, width="stretch", config=CHART_CONFIGURATION)


def league_card_html(league: str, league_row: pd.Series) -> str:
    champion = f"{escape(league_row['champion'])} ({format_number(league_row['champion_points'])} pkt)"
    details = (
        f"{escape(LEAGUE_COUNTRIES[league])}, {format_number(league_row['teams'])} drużyn, "
        f"{format_number(league_row['matches'])} meczów"
    )
    values = [
        ("Mistrz", champion),
        ("Gole na mecz", format_number(league_row["goals_per_match"], 2)),
        ("Kartki na mecz", format_number(league_row["cards_per_match"], 2)),
    ]
    value_rows = "".join(
        f'<div class="league-card-label">{label}</div><div class="league-card-value">{value}</div>'
        for label, value in values
    )
    return (
        f'<div class="league-card" style="--league-color: {LEAGUE_COLORS[league]};">'
        f'<div class="league-card-header">'
        f'<img class="league-logo" src="{league_logo_data_address(league)}" alt="Logo {escape(league)}">'
        f'<div class="league-card-name">{escape(league)}</div>'
        f"</div>"
        f'<div class="league-card-details">{details}</div>'
        f"{value_rows}</div>"
    )


def league_cards_html(league_summary: pd.DataFrame) -> str:
    cards = "".join(league_card_html(league, league_row) for league, league_row in league_summary.iterrows())
    return f'<div class="league-cards">{cards}</div>'
