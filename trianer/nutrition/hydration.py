from io import StringIO
import numpy as np
import pandas as pd

from ..core import models


def calculate_hydration(df, race, athlete) -> pd.DataFrame:

    # Dehydration
    for discipline in ["swimming", "cycling", "running"]:
        df.loc[df["discipline"] == discipline, "hydration"] = models.get_hydration_vs_temp(
            discipline, df.loc[df["discipline"] == discipline, "temperature"]
        )
        df.loc[df["discipline"] == discipline, "ihydration"] = models.get_maximum_ideal_hydration(discipline, athlete)

    # Make it proportional to duration
    sudation = athlete.sudation if type(athlete.sudation) == float else 1.0
    df["hydration"] *= sudation * df["duration"]
    df["ihydration"] *= df["duration"]

    return df


def get_hydric_reserve(athlete, danger=False):
    """
            Des glucides : pour l’énergie
            Du sodium : quand on transpire, on évacue principalement de l’eau mais aussi du sodium qui aura pour intérêt de favoriser l’absorption intestinale des glucides).

            1% soif
            2% perte 20% perf
            4% dangereux

    Return in ml"""
    if not danger:
        return athlete.weight * 0.02 * 1000
    else:
        return athlete.weight * 0.04 * 1000
