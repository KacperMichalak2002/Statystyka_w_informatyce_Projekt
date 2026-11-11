import pandas as pd
import streamlit as st

from football_stats.data.loading import load_matches
from football_stats.data.team_table import build_team_table


@st.cache_data
def get_matches() -> pd.DataFrame:
    return load_matches()


@st.cache_data
def get_teams() -> pd.DataFrame:
    return build_team_table(get_matches())
