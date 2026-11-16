import math

import numpy as np
import pandas as pd


def most_frequent_values(values: pd.Series) -> tuple[list[float], int]:
    value_counts = values.value_counts()
    highest_count = int(value_counts.max())
    if highest_count == 1:
        return [], highest_count
    return sorted(value_counts[value_counts == highest_count].index.tolist()), highest_count


def class_count_by_sturges_rule(observation_count: int) -> int:
    return math.ceil(1 + math.log2(observation_count))


def modes_interpolated_from_classes(values: pd.Series) -> tuple[list[float], int]:
    class_counts, class_edges = np.histogram(values, bins=class_count_by_sturges_rule(len(values)))
    highest_count = int(class_counts.max())
    if highest_count == 1:
        return [], highest_count
    counts_with_empty_neighbours = np.concatenate([[0], class_counts, [0]])
    modes = []
    for class_index in np.flatnonzero(class_counts == highest_count):
        lower_edge = class_edges[class_index]
        class_width = class_edges[class_index + 1] - lower_edge
        surplus_over_previous_class = highest_count - counts_with_empty_neighbours[class_index]
        surplus_over_next_class = highest_count - counts_with_empty_neighbours[class_index + 2]
        surplus_sum = surplus_over_previous_class + surplus_over_next_class
        position_in_class = surplus_over_previous_class / surplus_sum if surplus_sum > 0 else 0.5
        modes.append(float(lower_edge + position_in_class * class_width))
    return modes, highest_count


def central_tendency_measures(values: pd.Series, is_continuous: bool) -> dict:
    values = values.dropna()
    find_modes = modes_interpolated_from_classes if is_continuous else most_frequent_values
    modes, mode_count = find_modes(values)
    return {
        "count": len(values),
        "mean": values.mean(),
        "median": values.median(),
        "modes": modes,
        "mode_count": mode_count,
    }
