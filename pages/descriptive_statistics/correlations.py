import math

import pandas as pd
import streamlit as st

from football_stats.charts.correlations import correlation_heatmap, pair_scatter_chart
from football_stats.data.loading import LEAGUE_FILES
from football_stats.interface.attribute_catalog import ALL_NAMES, MATCH_LEVEL, TEAM_LEVEL
from football_stats.interface.attribute_selection import (
    LEVEL_NAMES,
    OBSERVATION_NAMES,
    numeric_attributes,
    select_level,
    table_for_level,
)
from football_stats.interface.data_tables import MATCH_COLUMN_GROUPS
from football_stats.interface.formatting import MISSING_VALUE_TEXT, format_number
from football_stats.interface.labels import ALL_LEAGUES_NAME
from football_stats.interface.navigation import find_page
from football_stats.interface.page_elements import show_chart
from football_stats.statistics.correlation import (
    PEARSON,
    SPEARMAN,
    correlation_matrix,
    correlation_pairs,
    least_squares_line,
    pair_correlation,
)

LEAGUES = list(LEAGUE_FILES.values())
METHOD_NAMES = {PEARSON: "Pearsona", SPEARMAN: "Spearmana"}
DEFAULT_PAIRS = {
    MATCH_LEVEL: ("total_shots_on_target", "total_goals"),
    TEAM_LEVEL: ("shots_on_target_per_match", "points"),
}
STRENGTH_NAMES = {0.2: "bardzo słaba", 0.4: "słaba", 0.7: "umiarkowana", 0.9: "silna"}
HIGHEST_STRENGTH_NAME = "bardzo silna"
COEFFICIENT_DECIMAL_PLACES = 3
STRONGEST_PAIRS_IN_TABLE = 15
SMALLEST_SHOWN_P_VALUE = 0.001
MINIMUM_ATTRIBUTE_COUNT = 2


def strength_name(coefficient: float) -> str:
    if not math.isfinite(coefficient):
        return MISSING_VALUE_TEXT
    for upper_limit, name in STRENGTH_NAMES.items():
        if abs(coefficient) < upper_limit:
            return name
    return HIGHEST_STRENGTH_NAME


def direction_name(coefficient: float) -> str:
    return "dodatnia" if coefficient > 0 else "ujemna"


def format_coefficient(coefficient: float) -> str:
    return format_number(coefficient, COEFFICIENT_DECIMAL_PLACES)


def format_p_value(p_value: float) -> str:
    if not math.isfinite(p_value):
        return MISSING_VALUE_TEXT
    if p_value < SMALLEST_SHOWN_P_VALUE:
        return f"< {format_number(SMALLEST_SHOWN_P_VALUE, 3)}"
    return format_number(p_value, 3)


page = find_page(__file__)
st.title(f"{page.icon} {page.title}")
st.markdown(
    "Współczynnik korelacji mierzy siłę i kierunek zależności dwóch atrybutów w skali od -1 do 1. "
    "Wartość bliska 1 oznacza, że atrybuty rosną razem, bliska -1, że jeden rośnie, gdy drugi maleje, "
    "a bliska 0 brak zależności. Korelacja nie oznacza związku przyczynowego."
)

selection_columns = st.columns([2, 3, 2], vertical_alignment="bottom")
with selection_columns[0]:
    level = select_level()
with selection_columns[1]:
    method = st.segmented_control(
        "Współczynnik korelacji",
        list(METHOD_NAMES),
        format_func=METHOD_NAMES.get,
        default=PEARSON,
        required=True,
        help="Współczynnik Pearsona mierzy zależność liniową, a Spearmana zależność monotoniczną "
        "liczoną na rangach, więc jest odporny na wartości odstające.",
    )
with selection_columns[2]:
    league = st.selectbox("Liga", [ALL_LEAGUES_NAME, *LEAGUES])

attribute_names = ALL_NAMES[level]
observation_name = OBSERVATION_NAMES[level]
numeric_columns = [attribute.column for attribute in numeric_attributes(level)]
table = table_for_level(level)
if league != ALL_LEAGUES_NAME:
    table = table[table["league"] == league]

columns = numeric_columns
if level == MATCH_LEVEL:
    column_groups = st.segmented_control(
        "Grupy atrybutów",
        list(MATCH_COLUMN_GROUPS),
        selection_mode="multi",
        default=list(MATCH_COLUMN_GROUPS),
    )
    columns_in_groups = {column for group in column_groups for column in MATCH_COLUMN_GROUPS[group]}
    columns = [column for column in numeric_columns if column in columns_in_groups]
if len(columns) < MINIMUM_ATTRIBUTE_COUNT:
    st.warning("Wybierz przynajmniej jedną grupę atrybutów.", icon=":material/filter_alt:")
    st.stop()

matrix = correlation_matrix(table, columns, method)
pairs = correlation_pairs(matrix)
if pairs.empty:
    st.warning("Wybrane atrybuty mają w tej lidze stałe wartości, więc nie da się policzyć korelacji.")
    st.stop()


def pair_name(pair: pd.Series) -> str:
    return f"{attribute_names[pair['first_column']]} i {attribute_names[pair['second_column']]}"


strongest_positive_pair = pairs.loc[pairs["coefficient"].idxmax()]
strongest_negative_pair = pairs.loc[pairs["coefficient"].idxmin()]

metric_columns = st.columns(4)
metric_columns[0].metric(f"Liczba {observation_name}", format_number(len(table)), border=True)
metric_columns[1].metric("Pary atrybutów", format_number(len(pairs)), border=True)
metric_columns[2].metric(
    "Najsilniejsza dodatnia", format_coefficient(strongest_positive_pair["coefficient"]), border=True
)
metric_columns[3].metric(
    "Najsilniejsza ujemna", format_coefficient(strongest_negative_pair["coefficient"]), border=True
)
st.caption(
    f"Najsilniejsza korelacja dodatnia: {pair_name(strongest_positive_pair)}. "
    f"Najsilniejsza ujemna: {pair_name(strongest_negative_pair)}."
)

st.subheader(":material/grid_on: Mapa ciepła")
show_chart(
    correlation_heatmap(
        matrix,
        attribute_names,
        f"Korelacja {METHOD_NAMES[method]}: {LEVEL_NAMES[level].lower()}, {league}",
    )
)
st.caption(
    "Każde pole to współczynnik korelacji jednej pary atrybutów: niebieskie oznacza zależność dodatnią, "
    "pomarańczowe ujemną, a ciemne brak zależności. Dokładną wartość pokazuje najechanie kursorem. "
    "Puste pole oznacza atrybut o stałej wartości w wybranej lidze."
)

st.subheader(":material/leaderboard: Najsilniejsze zależności")
strongest_pairs = pairs.head(STRONGEST_PAIRS_IN_TABLE)
st.dataframe(
    pd.DataFrame(
        {
            "Atrybut 1": strongest_pairs["first_column"].map(attribute_names),
            "Atrybut 2": strongest_pairs["second_column"].map(attribute_names),
            "Współczynnik": strongest_pairs["coefficient"],
            "Kierunek": strongest_pairs["coefficient"].apply(direction_name),
            "Siła": strongest_pairs["coefficient"].apply(strength_name),
        }
    ).style.format(precision=COEFFICIENT_DECIMAL_PLACES, decimal=",", subset=["Współczynnik"]),
    hide_index=True,
)
st.caption(
    "Część najsilniejszych korelacji wynika z budowy atrybutów, na przykład suma meczu zależy od wartości "
    "gospodarzy i gości, a szanse z kursów sumują się do 1. Przyjęte progi siły dla wartości bezwzględnej: "
    "poniżej 0,2 bardzo słaba, 0,2-0,4 słaba, 0,4-0,7 umiarkowana, 0,7-0,9 silna, od 0,9 bardzo silna."
)

st.subheader(":material/scatter_plot: Wybrana para atrybutów")
default_first_column, default_second_column = DEFAULT_PAIRS[level]
pair_columns = st.columns(2)
with pair_columns[0]:
    first_column = st.selectbox(
        "Atrybut na osi poziomej",
        numeric_columns,
        index=numeric_columns.index(default_first_column),
        format_func=attribute_names.get,
        key=f"first_correlation_attribute_{level}",
    )
with pair_columns[1]:
    second_column = st.selectbox(
        "Atrybut na osi pionowej",
        numeric_columns,
        index=numeric_columns.index(default_second_column),
        format_func=attribute_names.get,
        key=f"second_correlation_attribute_{level}",
    )

selected_pair = pair_correlation(table[first_column], table[second_column], method)
coefficient = selected_pair["coefficient"]
has_coefficient = math.isfinite(coefficient)

pair_metric_columns = st.columns(4)
pair_metric_columns[0].metric(
    f"Współczynnik {METHOD_NAMES[method]}", format_coefficient(coefficient), border=True
)
pair_metric_columns[1].metric(f"Liczba {observation_name}", format_number(selected_pair["count"]), border=True)
pair_metric_columns[2].metric(
    "Współczynnik determinacji",
    format_coefficient(coefficient**2) if method == PEARSON else MISSING_VALUE_TEXT,
    border=True,
    help="Kwadrat współczynnika Pearsona: część zmienności jednego atrybutu wyjaśniana liniowo przez drugi.",
)
pair_metric_columns[3].metric(
    "Wartość p",
    format_p_value(selected_pair["p_value"]),
    border=True,
    help="Prawdopodobieństwo uzyskania tak silnej korelacji, gdyby atrybuty były niezależne.",
)

if has_coefficient:
    st.info(
        f"Zależność jest {strength_name(coefficient)} i {direction_name(coefficient)}: "
        f"{attribute_names[first_column]} i {attribute_names[second_column]}.",
        icon=":material/lightbulb:",
    )
else:
    st.info("Jeden z atrybutów ma stałą wartość, więc współczynnika nie da się policzyć.", icon=":material/block:")

point_labels = table["home_team"] + " - " + table["away_team"] if level == MATCH_LEVEL else table["team"]
trend_line = least_squares_line(table[first_column], table[second_column]) if has_coefficient else None
show_chart(
    pair_scatter_chart(
        table,
        first_column,
        second_column,
        point_labels,
        trend_line,
        f"Liczba {observation_name}",
        f"{attribute_names[second_column]} a {attribute_names[first_column].lower()}",
        attribute_names[first_column],
        attribute_names[second_column],
    )
)
st.caption(
    "Biała linia to prosta regresji wyznaczona metodą najmniejszych kwadratów. Gdy obserwacje się nie "
    "powtarzają, każdy punkt to jedna obserwacja w kolorze ligi. Gdy wiele obserwacji ma te same wartości, "
    "wykres pokazuje koła o polu proporcjonalnym do liczby obserwacji."
)
