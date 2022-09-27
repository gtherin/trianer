from io import StringIO
import numpy as np
import pandas as pd


def calculate_hydration(df, race, athlete) -> pd.DataFrame:
    """
    Max hydration 700ml homme, 600ml femme

    """

    if "hydration" in df.columns:
        del df["hydration"]

    temp = np.arange(0, 40)
    # hydr = pd.Series(np.clip(temp * 70 - 800, 400, 2000), index=temp).to_frame(name="hydration")
    # hydr = pd.Series(-np.clip(temp * 100 - 600, 400, 2500), index=temp).to_frame(name="hydration")
    hydr = pd.Series(-np.clip(temp * 100 - 600, 400, 2000), index=temp).to_frame(name="hydration")
    hydr_nat = 500

    if type(athlete.sudation) == float:
        hydr *= athlete.sudation
        hydr_nat *= athlete.sudation
    hydr = df.merge(hydr, how="left", left_on=df["temperature"].round(), right_index=True)

    # Dehydration
    df.loc[df["discipline"] == "swimming", "hydration"] = (
        -hydr_nat * df.loc[df["discipline"] == "swimming", "duration"]
    )
    df.loc[df["discipline"] == "cycling", "hydration"] = (
        df.loc[df["discipline"] == "cycling", "duration"] * hydr.loc[hydr["discipline"] == "cycling", "hydration"]
    )
    df.loc[df["discipline"] == "running", "hydration"] = (
        df.loc[df["discipline"] == "running", "duration"] * hydr.loc[hydr["discipline"] == "running", "hydration"]
    )

    # Ideal hydration
    df["ihydration"] = 0.0
    df.loc[df["discipline"] == "cycling", "ihydration"] = 700 * df.loc[df["discipline"] == "cycling", "duration"]
    df.loc[df["discipline"] == "running", "ihydration"] = 700 * df.loc[df["discipline"] == "running", "duration"]

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
