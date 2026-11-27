import math

import streamlit as st

from football_stats.charts.descriptive_statistics import MeasureLine, distribution_chart
from football_stats.data.loading import LEAGUE_FILES
from football_stats.interface.attribute_selection import select_numeric_attribute
from football_stats.interface.formatting import MISSING_VALUE_TEXT, format_number
from football_stats.interface.labels import ALL_LEAGUES_NAME
from football_stats.interface.navigation import find_page
from football_stats.interface.page_elements import show_chart
from football_stats.interface.pictograms import icon_for_column, pictogram_html, pictogram_legend
from football_stats.interface.statistics_tables import measure_table
from football_stats.interface.theme import ACCENT_COLOR, AWAY_WIN_COLOR, TEXT_COLOR
from football_stats.statistics.central_tendency import central_tendency_measures
from football_stats.statistics.league_groups import measures_by_league

LEAGUES = list(LEAGUE_FILES.values())
MEASURE_NAMES = {"mean": "Średnia", "median": "Mediana", "mode": "Dominanta"}
TABLE_COLUMN_NAMES = {
    "count": "Liczba obserwacji",
    "mean": "Średnia",
    "median": "Mediana",
    "mode_text": "Dominanta",
    "mode_count": "Liczebność dominanty",
}

page = find_page(__file__)
st.title(f"{page.icon} {page.title}")
st.markdown(
    "Miary tendencji centralnej wskazują wartość typową dla atrybutu: **średnia** to suma wartości "
    "podzielona przez ich liczbę, **mediana** dzieli uporządkowane obserwacje na dwie równe połowy, "
    "a **dominanta** to wartość występująca najczęściej."
)

attribute = select_numeric_attribute()
mode_decimal_places = attribute.measure_decimal_places if attribute.is_continuous else attribute.value_decimal_places


def format_measure(value: float) -> str:
    return format_number(value, attribute.measure_decimal_places)


def format_modes(modes: list[float]) -> str:
    if not modes:
        return MISSING_VALUE_TEXT
    return " i ".join(format_number(mode, mode_decimal_places) for mode in modes)


measures = measures_by_league(
    attribute.table,
    attribute.column,
    lambda values: central_tendency_measures(values, attribute.is_continuous),
    ALL_LEAGUES_NAME,
)
measures["mode"] = measures["modes"].apply(lambda modes: modes[0] if modes else math.nan)
measures["mode_text"] = measures["modes"].apply(format_modes)
all_leagues = measures.loc[ALL_LEAGUES_NAME]

metric_columns = st.columns(4)
metric_columns[0].metric(f"Liczba {attribute.observation_name}", format_number(all_leagues["count"]), border=True)
metric_columns[1].metric("Średnia", format_measure(all_leagues["mean"]), border=True)
metric_columns[2].metric("Mediana", format_measure(all_leagues["median"]), border=True)
metric_columns[3].metric("Dominanta", all_leagues["mode_text"], border=True)
st.caption(f"Wartości dla wszystkich lig razem. Atrybut: {attribute.name}, jednostka: {attribute.unit}.")

st.subheader(":material/apps: Ligi na piktogramie")
pictogram_measure = st.segmented_control(
    "Miara na piktogramie",
    list(MEASURE_NAMES),
    format_func=MEASURE_NAMES.get,
    default="mean",
    required=True,
)
league_measures = measures.loc[LEAGUES]
pictogram_value_texts = (
    league_measures["mode_text"] if pictogram_measure == "mode" else league_measures[pictogram_measure].apply(format_measure)
)
icon = icon_for_column(attribute.column)
pictogram, icon_value = pictogram_html(league_measures[pictogram_measure], pictogram_value_texts, icon)
st.html(pictogram)
pictogram_notes = [pictogram_legend(icon, icon_value, attribute.unit)]
if pictogram_measure == "mode":
    pictogram_notes.append("Gdy liga ma kilka dominant, ikony pokazują najmniejszą z nich.")
if (league_measures[pictogram_measure] <= 0).any():
    pictogram_notes.append("Wartości zerowe i ujemne nie mają ikon.")
st.caption(" ".join(pictogram_notes))

highest_mean_league = league_measures["mean"].idxmax()
lowest_mean_league = league_measures["mean"].idxmin()
st.info(
    f"Najwyższą średnią ma {highest_mean_league} ({format_measure(league_measures['mean'].max())}), "
    f"a najniższą {lowest_mean_league} ({format_measure(league_measures['mean'].min())}). "
    f"Połowa obserwacji ze wszystkich lig nie przekracza mediany {format_measure(all_leagues['median'])}.",
    icon=":material/lightbulb:",
)

st.subheader(":material/bar_chart: Miary na tle rozkładu")
distribution_league = st.segmented_control(
    "Liga na wykresie",
    [ALL_LEAGUES_NAME, *LEAGUES],
    default=ALL_LEAGUES_NAME,
    required=True,
)
league_values = (
    attribute.values
    if distribution_league == ALL_LEAGUES_NAME
    else attribute.values[attribute.table["league"] == distribution_league]
)
selected_measures = measures.loc[distribution_league]
measure_lines = [
    MeasureLine(f"Średnia: {format_measure(selected_measures['mean'])}", selected_measures["mean"], ACCENT_COLOR, "solid"),
    MeasureLine(
        f"Mediana: {format_measure(selected_measures['median'])}", selected_measures["median"], AWAY_WIN_COLOR, "dash"
    ),
    *[
        MeasureLine(f"Dominanta: {format_number(mode, mode_decimal_places)}", mode, TEXT_COLOR, "dot")
        for mode in selected_measures["modes"]
    ],
]
show_chart(
    distribution_chart(
        league_values,
        attribute.is_continuous,
        measure_lines,
        distribution_league,
        f"{attribute.name}: {distribution_league}",
        f"{attribute.name} ({attribute.unit})",
        f"Liczba {attribute.observation_name}",
    )
)
if attribute.is_continuous:
    st.caption(
        "Atrybut ciągły rzadko powtarza dokładnie tę samą wartość, dlatego jego dominanta jest interpolowana "
        "z najliczniejszego przedziału szeregu rozdzielczego. Liczbę przedziałów wyznacza reguła Sturgesa."
    )
else:
    st.caption("Słupki pokazują, ile razy wystąpiła każda wartość. Dominanta to wartość z najwyższym słupkiem.")

st.subheader(":material/table_chart: Miary w liczbach")
st.dataframe(
    measure_table(
        measures,
        TABLE_COLUMN_NAMES,
        {"mean": attribute.measure_decimal_places, "median": attribute.measure_decimal_places},
    ),
    hide_index=True,
)
st.caption(
    "Liczebność dominanty to liczba obserwacji z wartością dominanty, a dla atrybutów ciągłych "
    "liczba obserwacji w przedziale dominanty. Słowo „brak” oznacza, że żadna wartość się nie powtarza."
)
