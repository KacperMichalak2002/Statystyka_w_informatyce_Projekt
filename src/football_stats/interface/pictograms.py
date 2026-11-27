import math
from html import escape

import pandas as pd

from football_stats.interface.formatting import MISSING_VALUE_TEXT, format_number
from football_stats.interface.theme import LEAGUE_COLORS, MUTED_TEXT_COLOR

DEFAULT_ICON = "⚽"
ICONS_BY_COLUMN_NAME_FRAGMENT = {
    "red_cards": "🟥",
    "cards": "🟨",
    "shots_on_target": "🎯",
    "shot": "👟",
    "corners": "🚩",
    "fouls": "✋",
    "odds": "💰",
    "margin": "💰",
    "probability": "🎲",
    "points": "⭐",
    "wins": "🏆",
    "win_percentage": "🏆",
    "draws": "🤝",
    "losses": "❌",
    "matches_played": "🏟️",
}

MAXIMUM_ICONS_IN_ROW = 20
SMALLEST_ICON_VALUE_FOR_LARGE_NUMBERS = 1
ICON_VALUE_MULTIPLIERS = [1, 2, 5]
ICON_WIDTH_IN_EM = 1.3


def icon_for_column(column: str) -> str:
    for name_fragment, icon in ICONS_BY_COLUMN_NAME_FRAGMENT.items():
        if name_fragment in column:
            return icon
    return DEFAULT_ICON


def icon_value_for(largest_value: float) -> float:
    if not math.isfinite(largest_value) or largest_value <= 0:
        return SMALLEST_ICON_VALUE_FOR_LARGE_NUMBERS
    power_of_ten = -2 if largest_value < 1 else 0
    while True:
        for multiplier in ICON_VALUE_MULTIPLIERS:
            icon_value = multiplier * 10**power_of_ten
            if largest_value / icon_value <= MAXIMUM_ICONS_IN_ROW:
                return icon_value
        power_of_ten += 1


def icons_html(value: float, icon_value: float, icon: str) -> str:
    icon_count = value / icon_value
    whole_icons = math.floor(icon_count)
    icon_fraction = icon_count - whole_icons
    icon_html = f'<span class="pictogram-icon">{icon}</span>'
    partial_icon_html = (
        f'<span class="pictogram-icon-part" style="width: {icon_fraction * ICON_WIDTH_IN_EM:.3f}em;">{icon_html}</span>'
        if icon_fraction > 0
        else ""
    )
    return icon_html * whole_icons + partial_icon_html


def pictogram_row_html(label: str, value: float, value_text: str, icon_value: float, icon: str) -> str:
    color = LEAGUE_COLORS.get(label, MUTED_TEXT_COLOR)
    if math.isfinite(value) and value > 0:
        icons = icons_html(value, icon_value, icon)
    else:
        icons = ""
    return (
        f'<div class="pictogram-row" style="--league-color: {color};">'
        f'<div class="pictogram-label">{escape(label)}</div>'
        f'<div class="pictogram-icons">{icons}</div>'
        f'<div class="pictogram-value">{escape(value_text)}</div>'
        f"</div>"
    )


def pictogram_html(values: pd.Series, value_texts: pd.Series, icon: str) -> tuple[str, float]:
    icon_value = icon_value_for(values.max())
    rows = "".join(
        pictogram_row_html(label, value, value_texts[label], icon_value, icon) for label, value in values.items()
    )
    return f'<div class="pictogram">{rows}</div>', icon_value


def pictogram_legend(icon: str, icon_value: float, unit: str) -> str:
    decimal_places = max(0, -math.floor(math.log10(icon_value)))
    unit_text = "" if unit in {"-", MISSING_VALUE_TEXT} else f" (jednostka: {unit})"
    return f"Jedna ikona {icon} odpowiada wartości {format_number(icon_value, decimal_places)}{unit_text}."
