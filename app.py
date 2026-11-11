import streamlit as st

from football_stats.interface.navigation import build_navigation
from football_stats.interface.page_elements import apply_application_styles
from football_stats.interface.theme import register_plotly_template

st.set_page_config(
    page_title="Statystyki piłkarskie 2025/26",
    page_icon=":material/sports_soccer:",
    layout="wide",
)
register_plotly_template()
apply_application_styles()
st.navigation(build_navigation()).run()
