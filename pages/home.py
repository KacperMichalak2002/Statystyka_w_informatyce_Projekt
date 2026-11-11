import streamlit as st

from football_stats.charts.league_overview import goals_per_match_chart, match_results_chart
from football_stats.data.league_summary import build_league_summary
from football_stats.interface.cached_data import get_matches, get_teams
from football_stats.interface.formatting import format_number
from football_stats.interface.navigation import ANALYSIS_PAGES
from football_stats.interface.page_elements import league_cards_html, show_chart

PAGE_TILES_PER_ROW = 4

matches = get_matches()
teams = get_teams()
league_summary = build_league_summary(matches, teams)

st.title(":material/sports_soccer: Statystyki piłkarskie 2025/26")

metric_columns = st.columns(5)
metric_columns[0].metric("Mecze", format_number(len(matches)), border=True)
metric_columns[1].metric("Drużyny", format_number(len(teams)), border=True)
metric_columns[2].metric("Ligi", format_number(matches["league"].nunique()), border=True)
metric_columns[3].metric("Gole", format_number(matches["total_goals"].sum()), border=True)
metric_columns[4].metric("Gole na mecz", format_number(matches["total_goals"].mean(), 2), border=True)

st.subheader(":material/stadium: Ligi w skrócie")
st.html(league_cards_html(league_summary))

chart_columns = st.columns(2)
with chart_columns[0]:
    show_chart(goals_per_match_chart(league_summary))
with chart_columns[1]:
    show_chart(match_results_chart(league_summary))

st.subheader(":material/explore: Co znajdziesz w aplikacji")
for first_page_index in range(0, len(ANALYSIS_PAGES), PAGE_TILES_PER_ROW):
    row_pages = ANALYSIS_PAGES[first_page_index : first_page_index + PAGE_TILES_PER_ROW]
    for column, page in zip(st.columns(PAGE_TILES_PER_ROW), row_pages):
        with column.container(border=True, height="stretch"):
            st.page_link(page.file_path, label=page.title, icon=page.icon)
            st.caption(page.description)
