import math

import pandas as pd
import streamlit as st

from football_stats.charts.distribution_shape import histogram_with_normal_curve, lorenz_curve_chart
from football_stats.data.loading import LEAGUE_FILES
from football_stats.interface.attribute_catalog import TEAM_LEVEL
from football_stats.interface.attribute_selection import select_numeric_attribute
from football_stats.interface.formatting import format_number
from football_stats.interface.labels import ALL_LEAGUES_NAME
from football_stats.interface.navigation import find_page
from football_stats.interface.page_elements import show_chart
from football_stats.interface.statistics_tables import measure_table
from football_stats.statistics.distribution_shape import (
    concentration_level,
    distribution_shape_measures,
    lorenz_curve,
    shape_description,
    skewness_description,
)
from football_stats.statistics.league_groups import measures_by_league

LEAGUES = list(LEAGUE_FILES.values())
MEASURE_DECIMAL_PLACES = 3
MEASURE_COLUMNS = [
    "skewness",
    "pearson_skewness",
    "positional_skewness",
    "kurtosis",
    "excess_kurtosis",
    "gini",
]
TABLE_COLUMN_NAMES = {
    "count": "Liczba obserwacji",
    "skewness": "Skośność",
    "pearson_skewness": "Współczynnik asymetrii Pearsona",
    "positional_skewness": "Pozycyjny współczynnik asymetrii",
    "kurtosis": "Kurtoza",
    "excess_kurtosis": "Eksces",
    "gini": "Współczynnik Giniego",
    "description": "Opis kształtu",
}


def format_measure(value: float) -> str:
    return format_number(value, MEASURE_DECIMAL_PLACES)


def gini_missing_reason(values: pd.Series) -> str:
    if (values < 0).any():
        return "Atrybut ma wartości ujemne, więc nie da się policzyć udziałów w sumie ani współczynnika Giniego."
    return "Suma wartości jest zerowa, więc nie da się policzyć udziałów w sumie ani współczynnika Giniego."


page = find_page(__file__)
st.title(f"{page.icon} {page.title}")
st.markdown(
    "Miary kształtu opisują, czym rozkład różni się od symetrycznego rozkładu normalnego. **Skośność** "
    "mówi, w którą stronę rozkład jest przechylony: dodatnia oznacza długi prawy ogon (kilka bardzo dużych "
    "wartości), ujemna długi lewy ogon. **Kurtoza** i **eksces** (kurtoza minus 3) to miary koncentracji "
    "wokół średniej: mówią, czy wartości skupiają się mocniej wokół średniej niż w rozkładzie normalnym. "
    "**Współczynnik Giniego** mierzy koncentrację sumy wartości: 0 oznacza równy podział sumy między obserwacje, a wartości bliskie 1 skupienie sumy "
    "w nielicznych obserwacjach."
)

attribute = select_numeric_attribute(per_match_team_attributes_only=True)
if attribute.level == TEAM_LEVEL:
    st.caption(
        "Na poziomie drużyny są tylko wartości na mecz i procenty, bo Bundesliga i Ligue 1 grają 34 mecze, "
        "a pozostałe ligi 38, więc sumy z sezonu nie są porównywalne."
    )

measures = measures_by_league(
    attribute.table,
    attribute.column,
    lambda values: distribution_shape_measures(values, attribute.is_continuous),
    ALL_LEAGUES_NAME,
)
measures["description"] = [
    shape_description(skewness, excess_kurtosis)
    for skewness, excess_kurtosis in zip(measures["skewness"], measures["excess_kurtosis"])
]
all_leagues = measures.loc[ALL_LEAGUES_NAME]
league_measures = measures.loc[LEAGUES]

metric_columns = st.columns(4)
metric_columns[0].metric("Skośność", format_measure(all_leagues["skewness"]), border=True)
metric_columns[1].metric("Eksces", format_measure(all_leagues["excess_kurtosis"]), border=True)
metric_columns[2].metric(
    "Asymetria Pearsona",
    format_measure(all_leagues["pearson_skewness"]),
    border=True,
    help="Współczynnik asymetrii Pearsona: (średnia - dominanta) / odchylenie standardowe.",
)
metric_columns[3].metric("Współczynnik Giniego", format_measure(all_leagues["gini"]), border=True)
st.caption(
    f"Wartości dla wszystkich lig razem. Atrybut: {attribute.name}, jednostka: {attribute.unit}. "
    f"Opis rozkładu: {all_leagues['description']}."
)

st.subheader(":material/insights: Histogram na tle rozkładu normalnego")
selected_league = st.segmented_control(
    "Liga na wykresie",
    [ALL_LEAGUES_NAME, *LEAGUES],
    default=ALL_LEAGUES_NAME,
    required=True,
)
league_values = (
    attribute.values
    if selected_league == ALL_LEAGUES_NAME
    else attribute.values[attribute.table["league"] == selected_league]
)
selected_measures = measures.loc[selected_league]
show_chart(
    histogram_with_normal_curve(
        league_values,
        attribute.is_continuous,
        selected_measures["mean"],
        selected_measures["standard_deviation"],
        selected_league,
        f"{attribute.name}: {selected_league}",
        f"{attribute.name} ({attribute.unit})",
        f"Liczba {attribute.observation_name}",
    )
)
st.caption(
    f"Opis rozkładu ({selected_league}): {selected_measures['description']}. Biała krzywa to rozkład "
    "normalny o tej samej średniej i tym samym odchyleniu standardowym, przeliczony na liczebności. Słupki "
    "wychodzące ponad krzywą po jednej stronie oznaczają asymetrię, a wyższy i węższy szczyt niż krzywa "
    "oznacza rozkład wysmukły."
    + (
        " Dla atrybutu ciągłego liczbę przedziałów wyznacza reguła Sturgesa."
        if attribute.is_continuous
        else ""
    )
)

defined_skewness = league_measures["skewness"].dropna()
if not defined_skewness.empty:
    highest_skewness_league = defined_skewness.idxmax()
    lowest_skewness_league = defined_skewness.idxmin()
    st.info(
        f"Największą skośność ma {highest_skewness_league} ({format_measure(defined_skewness.max())}: "
        f"{skewness_description(defined_skewness.max())}), a najmniejszą {lowest_skewness_league} "
        f"({format_measure(defined_skewness.min())}: {skewness_description(defined_skewness.min())}).",
        icon=":material/lightbulb:",
    )

st.subheader(":material/donut_large: Koncentracja: krzywa Lorenza")
gini = selected_measures["gini"]
if math.isfinite(gini):
    shares_of_observations, shares_of_total = lorenz_curve(league_values)
    show_chart(
        lorenz_curve_chart(
            shares_of_observations,
            shares_of_total,
            selected_league,
            f"{attribute.name}: {selected_league}, współczynnik Giniego {format_measure(gini)}",
        )
    )
    st.caption(
        "Krzywa Lorenza pokazuje, jaką część sumy wartości ma dany odsetek obserwacji z najmniejszymi "
        "wartościami. Im bardziej krzywa odchyla się od przekątnej równego podziału, tym większa "
        "koncentracja. Współczynnik Giniego to podwojone pole między przekątną a krzywą."
    )
    st.info(
        f"Współczynnik Giniego ({selected_league}) wynosi {format_measure(gini)}, "
        f"co oznacza koncentrację: {concentration_level(gini)}.",
        icon=":material/lightbulb:",
    )
else:
    st.info(gini_missing_reason(league_values.dropna()), icon=":material/block:")

st.subheader(":material/table_chart: Miary w liczbach")
st.dataframe(
    measure_table(
        measures,
        TABLE_COLUMN_NAMES,
        {column: MEASURE_DECIMAL_PLACES for column in MEASURE_COLUMNS},
    ),
    hide_index=True,
)
st.caption(
    "Skośność A = m3 / m2^1,5, kurtoza K = m4 / m2^2, eksces = K - 3, gdzie m2, m3, m4 to momenty "
    "centralne z dzielnikiem n (tak samo jak odchylenie standardowe na stronie Rozrzut). Współczynnik "
    "asymetrii Pearsona = (średnia - dominanta) / odchylenie standardowe; „brak”, gdy dominant jest kilka "
    "albo żadna wartość się nie powtarza. Pozycyjny współczynnik asymetrii = (Q3 + Q1 - 2 Me) / (Q3 - Q1); "
    "„brak”, gdy kwartyle są równe. Współczynnik Giniego ma „brak” dla atrybutów z wartościami ujemnymi "
    "albo zerową sumą. Progi opisu: skośność poniżej 0,1 co do wartości bezwzględnej to rozkład niemal "
    "symetryczny, do 0,5 słaba, do 1 umiarkowana, wyżej silna asymetria; eksces poniżej 0,1 co do wartości "
    "bezwzględnej to spłaszczenie zbliżone do normalnego, większy kształt wysmukły, mniejszy spłaszczony. "
    "Koncentracja: Gini poniżej 0,2 niska, "
    "do 0,4 umiarkowana, wyżej wysoka."
)
