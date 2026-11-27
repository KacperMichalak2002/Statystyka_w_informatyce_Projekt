import math

import numpy as np
import pandas as pd
from scipy import stats

PEARSON = "pearson"
SPEARMAN = "spearman"

PAIR_CORRELATION_FUNCTIONS = {PEARSON: stats.pearsonr, SPEARMAN: stats.spearmanr}


def correlation_matrix(table: pd.DataFrame, columns: list[str], method: str) -> pd.DataFrame:
    return table[columns].corr(method=method)


def correlation_pairs(matrix: pd.DataFrame) -> pd.DataFrame:
    above_diagonal = np.triu(np.ones(matrix.shape, dtype=bool), k=1)
    pairs = matrix.where(above_diagonal).stack().dropna().rename("coefficient").reset_index()
    pairs.columns = ["first_column", "second_column", "coefficient"]
    strongest_first = pairs["coefficient"].abs().sort_values(ascending=False).index
    return pairs.loc[strongest_first].reset_index(drop=True)


def pair_correlation(first_values: pd.Series, second_values: pd.Series, method: str) -> dict:
    complete_pairs = pd.concat([first_values, second_values], axis=1).dropna()
    first_values = complete_pairs.iloc[:, 0]
    second_values = complete_pairs.iloc[:, 1]
    if first_values.nunique() < 2 or second_values.nunique() < 2:
        return {"count": len(complete_pairs), "coefficient": math.nan, "p_value": math.nan}
    result = PAIR_CORRELATION_FUNCTIONS[method](first_values, second_values)
    return {"count": len(complete_pairs), "coefficient": float(result.statistic), "p_value": float(result.pvalue)}


def least_squares_line(first_values: pd.Series, second_values: pd.Series) -> tuple[float, float]:
    slope, intercept = np.polyfit(first_values, second_values, deg=1)
    return float(slope), float(intercept)
