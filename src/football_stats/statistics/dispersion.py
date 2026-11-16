import math

import pandas as pd

WHOLE_POPULATION_DEGREES_OF_FREEDOM = 0


def coefficient_of_variation_percentage(mean: float, standard_deviation: float) -> float:
    if mean <= 0:
        return math.nan
    return 100 * standard_deviation / mean


def dispersion_measures(values: pd.Series) -> dict:
    values = values.dropna()
    mean = values.mean()
    standard_deviation = values.std(ddof=WHOLE_POPULATION_DEGREES_OF_FREEDOM)
    first_quartile = values.quantile(0.25)
    third_quartile = values.quantile(0.75)
    return {
        "count": len(values),
        "minimum": values.min(),
        "maximum": values.max(),
        "value_range": values.max() - values.min(),
        "variance": values.var(ddof=WHOLE_POPULATION_DEGREES_OF_FREEDOM),
        "standard_deviation": standard_deviation,
        "coefficient_of_variation_percentage": coefficient_of_variation_percentage(mean, standard_deviation),
        "first_quartile": first_quartile,
        "third_quartile": third_quartile,
        "interquartile_range": third_quartile - first_quartile,
    }
