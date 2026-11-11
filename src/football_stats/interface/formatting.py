import math
from datetime import date

NON_BREAKING_SPACE = " "
MISSING_VALUE_TEXT = "brak"
DATE_FORMAT = "%d.%m.%Y"


def format_number(value: float, decimal_places: int = 0) -> str:
    if not math.isfinite(value):
        return MISSING_VALUE_TEXT
    english_format = f"{value:z,.{decimal_places}f}"
    return english_format.replace(",", NON_BREAKING_SPACE).replace(".", ",")


def format_date(day: date) -> str:
    return day.strftime(DATE_FORMAT)


def format_percentage(value: float, decimal_places: int = 1) -> str:
    if not math.isfinite(value):
        return MISSING_VALUE_TEXT
    return f"{format_number(value, decimal_places)}%"


def whole_percentages_summing_to_hundred(percentages: list[float]) -> list[int]:
    rounded_down = [math.floor(percentage) for percentage in percentages]
    missing_points = round(100 - sum(rounded_down))
    largest_remainders_first = sorted(
        range(len(percentages)),
        key=lambda index: percentages[index] - rounded_down[index],
        reverse=True,
    )
    for index in largest_remainders_first[:missing_points]:
        rounded_down[index] += 1
    return rounded_down
