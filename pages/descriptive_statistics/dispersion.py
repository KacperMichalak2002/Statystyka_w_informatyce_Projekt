import streamlit as st

from football_stats.charts.descriptive_statistics import league_box_plot, league_measure_chart
from football_stats.data.loading import LEAGUE_FILES
from football_stats.interface.attribute_catalog import TEAM_LEVEL
from football_stats.interface.attribute_selection import select_numeric_attribute
from football_stats.interface.formatting import format_number, format_percentage
from football_stats.interface.labels import ALL_LEAGUES_NAME
from football_stats.interface.navigation import find_page
from football_stats.interface.page_elements import show_chart
from football_stats.interface.statistics_tables import measure_table
from football_stats.statistics.dispersion import dispersion_measures
from football_stats.statistics.league_groups import measures_by_league

LEAGUES = list(LEAGUE_FILES.values())
TABLE_COLUMN_NAMES = {
    "count": "Liczba obserwacji",
    "minimum": "Minimum",
    "maximum": "Maksimum",
    "value_range": "Rozstęp",
    "variance": "Wariancja",
    "standard_deviation": "Odchylenie standardowe",
    "coefficient_of_variation_percentage": "Współczynnik zmienności (%)",
    "first_quartile": "Kwartyl 1",
    "third_quartile": "Kwartyl 3",
    "interquartile_range": "Rozstęp międzykwartylowy",
}
VALUE_COLUMNS = ["minimum", "maximum", "value_range"]
MEASURE_COLUMNS = ["variance", "standard_deviation", "first_quartile", "third_quartile", "interquartile_range"]
COEFFICIENT_OF_VARIATION_DECIMAL_PLACES = 1


page = find_page(__file__)
st.title(f"{page.icon} {page.title}")
st.markdown(
    "Miary zróżnicowania pokazują, jak bardzo obserwacje różnią się między sobą. **Rozstęp** to różnica "
    "między największą i najmniejszą wartością, **odchylenie standardowe** to przeciętne odchylenie od "
    "średniej, a **współczynnik zmienności** wyraża je w procentach średniej, więc pozwala porównywać "
    "atrybuty o różnych jednostkach."
)

attribute = select_numeric_attribute()


def format_measure(value: float) -> str:
    return format_number(value, attribute.measure_decimal_places)


measures = measures_by_league(attribute.table, attribute.column, dispersion_measures, ALL_LEAGUES_NAME)
all_leagues = measures.loc[ALL_LEAGUES_NAME]
league_measures = measures.loc[LEAGUES]
coefficient_of_variation = all_leagues["coefficient_of_variation_percentage"]
has_coefficient_of_variation = league_measures["coefficient_of_variation_percentage"].notna().all()

metric_columns = st.columns(4)
metric_columns[0].metric(
    "Rozstęp", format_number(all_leagues["value_range"], attribute.value_decimal_places), border=True
)
metric_columns[1].metric("Odchylenie standardowe", format_measure(all_leagues["standard_deviation"]), border=True)
metric_columns[2].metric(
    "Współczynnik zmienności",
    format_percentage(coefficient_of_variation, COEFFICIENT_OF_VARIATION_DECIMAL_PLACES),
    border=True,
)
metric_columns[3].metric(
    "Rozstęp międzykwartylowy", format_measure(all_leagues["interquartile_range"]), border=True
)

st.subheader(":material/candlestick_chart: Rozrzut w ligach")
show_chart(
    league_box_plot(
        attribute.table,
        attribute.column,
        attribute.observation_labels,
        ALL_LEAGUES_NAME,
        f"{attribute.name}: wykresy pudełkowe",
        f"{attribute.name} ({attribute.unit})",
        show_all_points=attribute.level == TEAM_LEVEL,
    )
)

st.subheader(":material/percent: Zmienność względna")
if has_coefficient_of_variation:
    show_chart(
        league_measure_chart(
            league_measures["coefficient_of_variation_percentage"],
            f"{attribute.name}: współczynnik zmienności",
            "Współczynnik zmienności (%)",
            COEFFICIENT_OF_VARIATION_DECIMAL_PLACES,
            "%",
        )
    )
else:
    st.info(
        "Współczynnik zmienności ma sens tylko przy dodatniej średniej, a średnia tego atrybutu "
        "jest zerowa lub ujemna.",
        icon=":material/block:",
    )

st.subheader(":material/table_chart: Miary w liczbach")
table_decimal_places = {
    **{column: attribute.value_decimal_places for column in VALUE_COLUMNS},
    **{column: attribute.measure_decimal_places for column in MEASURE_COLUMNS},
    "coefficient_of_variation_percentage": COEFFICIENT_OF_VARIATION_DECIMAL_PLACES,
}
st.dataframe(measure_table(measures, TABLE_COLUMN_NAMES, table_decimal_places), hide_index=True)
