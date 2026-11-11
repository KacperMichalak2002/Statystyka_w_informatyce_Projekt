import streamlit as st

from football_stats.data.loading import LEAGUE_FILES
from football_stats.data.table_filters import filter_matches, filter_teams
from football_stats.interface.attribute_catalog import MATCH_LEVEL, TEAM_LEVEL, attribute_catalog, attribute_count
from football_stats.interface.cached_data import get_matches, get_teams
from football_stats.interface.data_tables import (
    DEFAULT_MATCH_COLUMN_GROUPS,
    MATCH_COLUMN_GROUPS,
    match_table,
    team_table,
)
from football_stats.interface.formatting import format_date, format_number
from football_stats.interface.navigation import find_page

LEAGUES = list(LEAGUE_FILES.values())

page = find_page(__file__)
matches = get_matches()
teams = get_teams()

st.title(f"{page.icon} {page.title}")
st.markdown(
    f"Wyniki, statystyki meczowe i kursy bukmacherskie sezonu 2025/26 z serwisu "
    f"[football-data.co.uk](https://www.football-data.co.uk/), jeden plik CSV na ligę: "
    f"{', '.join(f'`{file_name}` ({league})' for file_name, league in LEAGUE_FILES.items())}. "
    f"Mecze od {format_date(matches['date'].min())} do {format_date(matches['date'].max())}."
)

metric_columns = st.columns(5)
metric_columns[0].metric("Mecze", format_number(len(matches)), border=True)
metric_columns[1].metric("Drużyny", format_number(len(teams)), border=True)
metric_columns[2].metric("Ligi", format_number(len(LEAGUES)), border=True)
metric_columns[3].metric("Atrybuty meczu", format_number(attribute_count(MATCH_LEVEL)), border=True)
metric_columns[4].metric("Atrybuty drużyny", format_number(attribute_count(TEAM_LEVEL)), border=True)

filter_columns = st.columns([3, 2], vertical_alignment="bottom")
with filter_columns[0]:
    selected_leagues = st.pills("Ligi", LEAGUES, selection_mode="multi", default=LEAGUES)
with filter_columns[1]:
    team_name_fragment = st.text_input(
        "Szukaj drużyny",
        placeholder="np. Inter",
        icon=":material/search:",
    )
st.caption("Filtry działają w zakładkach Mecze i Drużyny.")

matches_tab, teams_tab, attributes_tab = st.tabs(
    [
        ":material/sports_soccer: Mecze",
        ":material/groups: Drużyny",
        ":material/list_alt: Atrybuty",
    ]
)

with matches_tab:
    column_groups = st.segmented_control(
        "Grupy kolumn",
        list(MATCH_COLUMN_GROUPS),
        selection_mode="multi",
        default=DEFAULT_MATCH_COLUMN_GROUPS,
    )
    filtered_matches = filter_matches(matches, selected_leagues, team_name_fragment)
    if filtered_matches.empty:
        st.info("Żaden mecz nie pasuje do wybranych filtrów.", icon=":material/filter_alt:")
    else:
        st.caption(f"Mecze w tabeli: {format_number(len(filtered_matches))} z {format_number(len(matches))}.")
        st.dataframe(match_table(filtered_matches, column_groups), hide_index=True)

with teams_tab:
    filtered_teams = filter_teams(teams, selected_leagues, team_name_fragment)
    if filtered_teams.empty:
        st.info("Żadna drużyna nie pasuje do wybranych filtrów.", icon=":material/filter_alt:")
    else:
        st.caption(
            f"Drużyny w tabeli: {format_number(len(filtered_teams))} z {format_number(len(teams))}. "
            "Wartości na mecz i procenty pozwalają porównywać ligi, w których drużyny grają "
            f"{' albo '.join(format_number(count) for count in sorted(teams['matches_played'].unique()))} meczów."
        )
        st.dataframe(team_table(filtered_teams), hide_index=True)

with attributes_tab:
    st.caption(
        "Atrybuty meczu to kolumny tabeli meczów, atrybuty drużyny to kolumny tabeli drużyn. "
        "Typ zmiennej decyduje o tym, które miary statystyczne mają sens."
    )
    st.dataframe(attribute_catalog(), hide_index=True)
