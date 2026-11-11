from dataclasses import dataclass
from pathlib import Path

import streamlit as st

MAIN_SECTION = ""


@dataclass(frozen=True)
class ApplicationPage:
    file_path: str
    title: str
    icon: str
    section: str
    description: str


HOME_PAGE = ApplicationPage(
    "pages/home.py",
    "Strona główna",
    ":material/home:",
    MAIN_SECTION,
    "Przegląd danych i najważniejsze liczby sezonu.",
)

ANALYSIS_PAGES = [
    ApplicationPage(
        "pages/data_overview.py",
        "Dane",
        ":material/table_chart:",
        MAIN_SECTION,
        "Źródło danych, opis atrybutów i tabela meczów oraz drużyn.",
    ),
    ApplicationPage(
        "pages/descriptive_statistics/central_tendency.py",
        "Średnie",
        ":material/bar_chart:",
        "Statystyka opisowa",
        "Średnia, mediana i dominanta pokazane jako piktogramy dla każdej ligi.",
    ),
    ApplicationPage(
        "pages/descriptive_statistics/dispersion.py",
        "Rozrzut",
        ":material/query_stats:",
        "Statystyka opisowa",
        "Rozstęp, odchylenie standardowe i współczynnik zmienności na wykresach pudełkowych lig.",
    ),
    ApplicationPage(
        "pages/descriptive_statistics/distribution_shape.py",
        "Kształt rozkładu",
        ":material/insights:",
        "Statystyka opisowa",
        "Skośność, kurtoza i współczynnik Giniego na tle rozkładu normalnego.",
    ),
    ApplicationPage(
        "pages/descriptive_statistics/correlations.py",
        "Korelacje",
        ":material/scatter_plot:",
        "Statystyka opisowa",
        "Współczynniki korelacji każdej pary atrybutów na mapie ciepła.",
    ),
    ApplicationPage(
        "pages/analyses/league_comparison.py",
        "Porównanie lig",
        ":material/stadium:",
        "Analizy",
        "Która liga jest najbardziej ofensywna, a która najbardziej brutalna.",
    ),
    ApplicationPage(
        "pages/analyses/team_profile.py",
        "Profil drużyny",
        ":material/groups:",
        "Analizy",
        "Statystyki wybranej drużyny na tle jej ligi.",
    ),
    ApplicationPage(
        "pages/analyses/bookmakers.py",
        "Bukmacherzy",
        ":material/casino:",
        "Analizy",
        "Czy faworyci wygrywają tak często, jak wynika z kursów.",
    ),
]

PAGES_BY_FILE_NAME = {Path(page.file_path).name: page for page in [HOME_PAGE, *ANALYSIS_PAGES]}


def build_navigation() -> dict[str, list[st.Page]]:
    sections: dict[str, list[st.Page]] = {
        HOME_PAGE.section: [st.Page(HOME_PAGE.file_path, title=HOME_PAGE.title, icon=HOME_PAGE.icon, default=True)]
    }
    for page in ANALYSIS_PAGES:
        sections.setdefault(page.section, []).append(st.Page(page.file_path, title=page.title, icon=page.icon))
    return sections


def find_page(file_path: str) -> ApplicationPage:
    file_name = Path(file_path).name
    if file_name not in PAGES_BY_FILE_NAME:
        raise KeyError(f"Strona {file_name} nie jest zarejestrowana w navigation.py")
    return PAGES_BY_FILE_NAME[file_name]


def show_planned_page(file_path: str) -> None:
    page = find_page(file_path)
    st.title(f"{page.icon} {page.title}")
    st.write(page.description)
    st.info("Ta sekcja jest w przygotowaniu.", icon=":material/construction:")
