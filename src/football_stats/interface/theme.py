import plotly.graph_objects as go
import plotly.io as pio

BACKGROUND_COLOR = "#121417"
PANEL_BACKGROUND_COLOR = "#1e2228"
BORDER_COLOR = "#2e343d"
TEXT_COLOR = "#f4f5f7"
MUTED_TEXT_COLOR = "#a3abb7"
ACCENT_COLOR = "#4ade80"
GRID_LINE_COLOR = "rgba(244, 245, 247, 0.12)"
YELLOW_CARD_COLOR = "#f5c518"
RED_CARD_COLOR = "#e5383b"

HOME_WIN_COLOR = ACCENT_COLOR
DRAW_COLOR = "#c9ced6"
AWAY_WIN_COLOR = "#fac775"
TICK_LABEL_DISTANCE = 12

LEAGUE_COLORS = {
    "Premier League": "#9b72d8",
    "La Liga": "#e08a4f",
    "Serie A": "#4f86d6",
    "Bundesliga": "#d0545c",
    "Ligue 1": "#c2c65c",
}

RESULT_COLORS = {
    "home_win": HOME_WIN_COLOR,
    "draw": DRAW_COLOR,
    "away_win": AWAY_WIN_COLOR,
}

NEUTRAL_COLORWAY = [TEXT_COLOR, ACCENT_COLOR, AWAY_WIN_COLOR, MUTED_TEXT_COLOR]

FONT_FAMILY = "Source Sans, Source Sans Pro, sans-serif"

PLOTLY_TEMPLATE_NAME = "application"


def build_plotly_template() -> go.layout.Template:
    axis_style = {
        "automargin": True,
        "fixedrange": True,
        "gridcolor": GRID_LINE_COLOR,
        "linecolor": GRID_LINE_COLOR,
        "zerolinecolor": GRID_LINE_COLOR,
        "tickfont": {"color": MUTED_TEXT_COLOR},
        "title": {"font": {"color": MUTED_TEXT_COLOR}},
    }
    return go.layout.Template(
        layout={
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "font": {"color": TEXT_COLOR, "family": FONT_FAMILY, "size": 14},
            "title": {"font": {"size": 18, "color": TEXT_COLOR}},
            "colorway": NEUTRAL_COLORWAY,
            "separators": ", ",
            "xaxis": axis_style,
            "yaxis": {**axis_style, "ticklabelstandoff": TICK_LABEL_DISTANCE},
            "legend": {"font": {"color": TEXT_COLOR}, "itemclick": False, "itemdoubleclick": False},
            "hoverlabel": {
                "bgcolor": PANEL_BACKGROUND_COLOR,
                "bordercolor": ACCENT_COLOR,
                "font": {"color": TEXT_COLOR, "family": FONT_FAMILY, "size": 14},
            },
            "margin": {"l": 10, "r": 10, "t": 50, "b": 10},
        }
    )


def register_plotly_template() -> None:
    pio.templates[PLOTLY_TEMPLATE_NAME] = build_plotly_template()
    pio.templates.default = PLOTLY_TEMPLATE_NAME
