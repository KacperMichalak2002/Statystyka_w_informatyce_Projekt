import plotly.graph_objects as go
import plotly.io as pio

PITCH_BACKGROUND_COLOR = "#0f2a12"
PANEL_BACKGROUND_COLOR = "#173404"
TEXT_COLOR = "#f1efe8"
MUTED_TEXT_COLOR = "#b8c7a8"
ACCENT_COLOR = "#fac775"
PITCH_LINE_COLOR = "rgba(241, 239, 232, 0.18)"
YELLOW_CARD_COLOR = "#f5c518"
RED_CARD_COLOR = "#e5383b"

HOME_WIN_COLOR = "#9be15d"
DRAW_COLOR = "#d8dde0"
AWAY_WIN_COLOR = ACCENT_COLOR
TICK_LABEL_DISTANCE = 12

LEAGUE_COLORS = {
    "Premier League": "#9b72d8",
    "La Liga": "#e08a4f",
    "Serie A": "#4f86d6",
    "Bundesliga": "#c0444c",
    "Ligue 1": "#c2c65c",
}

RESULT_COLORS = {
    "home_win": HOME_WIN_COLOR,
    "draw": DRAW_COLOR,
    "away_win": AWAY_WIN_COLOR,
}

NEUTRAL_COLORWAY = [TEXT_COLOR, ACCENT_COLOR, HOME_WIN_COLOR, MUTED_TEXT_COLOR]

FONT_FAMILY = "Source Sans, Source Sans Pro, sans-serif"

PLOTLY_TEMPLATE_NAME = "pitch"


def build_plotly_template() -> go.layout.Template:
    axis_style = {
        "automargin": True,
        "gridcolor": PITCH_LINE_COLOR,
        "linecolor": PITCH_LINE_COLOR,
        "zerolinecolor": PITCH_LINE_COLOR,
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
            "legend": {"font": {"color": TEXT_COLOR}},
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
