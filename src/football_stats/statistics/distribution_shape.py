import math

import numpy as np
import pandas as pd

from football_stats.statistics.central_tendency import modes_interpolated_from_classes, most_frequent_values

NORMAL_DISTRIBUTION_KURTOSIS = 3
SYMMETRY_LIMIT = 0.1
SKEWNESS_STRENGTH_NAMES = {0.5: "słaba", 1: "umiarkowana"}
HIGHEST_SKEWNESS_STRENGTH_NAME = "silna"
NORMAL_PEAK_LIMIT = 0.1
CONCENTRATION_LEVEL_NAMES = {0.2: "niska", 0.4: "umiarkowana"}
HIGHEST_CONCENTRATION_LEVEL_NAME = "wysoka"


def central_moment(values: pd.Series, order: int) -> float:
    return float(((values - values.mean()) ** order).mean())


def gini_coefficient(values: pd.Series) -> float:
    sorted_values = np.sort(values.to_numpy(dtype=float))
    total = sorted_values.sum()
    if len(sorted_values) == 0 or (sorted_values < 0).any() or total == 0:
        return math.nan
    observation_count = len(sorted_values)
    positions = np.arange(1, observation_count + 1)
    return float(
        2 * (positions * sorted_values).sum() / (observation_count * total)
        - (observation_count + 1) / observation_count
    )


def lorenz_curve(values: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    sorted_values = np.sort(values.dropna().to_numpy(dtype=float))
    shares_of_observations = np.arange(len(sorted_values) + 1) / len(sorted_values)
    shares_of_total = np.concatenate([[0], np.cumsum(sorted_values) / sorted_values.sum()])
    return shares_of_observations, shares_of_total


def single_mode(values: pd.Series, is_continuous: bool) -> float:
    find_modes = modes_interpolated_from_classes if is_continuous else most_frequent_values
    modes, _ = find_modes(values)
    return modes[0] if len(modes) == 1 else math.nan


def positional_skewness(values: pd.Series) -> float:
    first_quartile = values.quantile(0.25)
    third_quartile = values.quantile(0.75)
    if first_quartile == third_quartile:
        return math.nan
    return (third_quartile + first_quartile - 2 * values.median()) / (third_quartile - first_quartile)


def distribution_shape_measures(values: pd.Series, is_continuous: bool) -> dict:
    values = values.dropna()
    mean = values.mean()
    second_moment = central_moment(values, 2)
    standard_deviation = math.sqrt(second_moment)
    has_spread = values.nunique() > 1
    skewness = central_moment(values, 3) / second_moment**1.5 if has_spread else math.nan
    kurtosis = central_moment(values, 4) / second_moment**2 if has_spread else math.nan
    pearson_skewness = (mean - single_mode(values, is_continuous)) / standard_deviation if has_spread else math.nan
    return {
        "count": len(values),
        "mean": mean,
        "standard_deviation": standard_deviation,
        "skewness": skewness,
        "pearson_skewness": pearson_skewness,
        "positional_skewness": positional_skewness(values),
        "kurtosis": kurtosis,
        "excess_kurtosis": kurtosis - NORMAL_DISTRIBUTION_KURTOSIS,
        "gini": gini_coefficient(values),
    }


def skewness_description(skewness: float) -> str:
    if abs(skewness) < SYMMETRY_LIMIT:
        return "rozkład niemal symetryczny"
    side = "prawostronna" if skewness > 0 else "lewostronna"
    for upper_limit, strength in SKEWNESS_STRENGTH_NAMES.items():
        if abs(skewness) < upper_limit:
            return f"{strength} {side} asymetria"
    return f"{HIGHEST_SKEWNESS_STRENGTH_NAME} {side} asymetria"


def peak_description(excess_kurtosis: float) -> str:
    if abs(excess_kurtosis) < NORMAL_PEAK_LIMIT:
        return "spłaszczenie zbliżone do rozkładu normalnego"
    if excess_kurtosis > 0:
        return "kształt wysmukły"
    return "kształt spłaszczony"


def shape_description(skewness: float, excess_kurtosis: float) -> str:
    if not (math.isfinite(skewness) and math.isfinite(excess_kurtosis)):
        return "brak (wszystkie wartości są równe)"
    return f"{skewness_description(skewness)}, {peak_description(excess_kurtosis)}"


def concentration_level(gini: float) -> str:
    for upper_limit, level in CONCENTRATION_LEVEL_NAMES.items():
        if gini < upper_limit:
            return level
    return HIGHEST_CONCENTRATION_LEVEL_NAME
