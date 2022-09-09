from lib2to3.pgen2.pgen import DFAState
from locale import D_FMT
import numpy as np
import pandas as pd

from .diver import Diver


r_nfoam = 170  # kg/m3


def get_data(surname=None, raw=False):
    df = pd.read_csv("freediving_data.csv")

    df.columns = [
        "timestamp",
        "username",
        "name",
        "surname",
        "depth_max",
        "time_descent",
        "time_ascent",
        "depth_gliding_descent",
        "depth_gliding_descent_error",
        "depth_gliding_ascent",
        "depth_gliding_ascent_error",
        "volume_lungs",
        "weight_body",
        "weight_ballast",
        "thickness_suit",
        "weight_suit",
        "model_suit",
        "rights",
    ]

    df = df[
        [
            "surname",
            "depth_max",
            "time_descent",
            "time_ascent",
            "depth_gliding_descent",
            "depth_gliding_descent_error",
            "depth_gliding_ascent",
            "depth_gliding_ascent_error",
            "volume_lungs",
            "weight_body",
            "weight_ballast",
            "thickness_suit",
            "weight_suit",
        ]
    ]

    df = pd.concat(
        [
            df,
            pd.DataFrame.from_records(
                [
                    {
                        "surname": "Guillaume Néry",
                        "depth_max": 125,  # in m
                        "time_descent": 120,  # in sec
                        "time_ascent": 94,  # in sec
                        "depth_gliding_descent": 27.5,  # in m
                        "depth_gliding_descent_error": 2.5,  # in m
                        "depth_gliding_ascent": 7.5,  # in m
                        "depth_gliding_ascent_error": 2.5,  # in m
                        "volume_lungs": 9,  # in l
                        "weight_body": 78,  # in kg
                        "weight_ballast": 1,  # in kg
                        "thickness_suit": 1.5,  # in mm
                    },
                    {  # Is it the same person as Stephane T ?
                        "surname": "Stephane Tourreau",
                        "depth_max": 103,  # in m
                        "time_descent": 165,  # TO BE CHECKED with TINO
                        "time_ascent": 165,  # TO BE CHECKED with TINO
                        "depth_gliding_descent": 55,  # in m
                        "depth_gliding_descent_error": 5,  # in m
                        "depth_gliding_ascent": 10,  # in m
                        "depth_gliding_ascent_error": 2.5,  # in m
                        "volume_lungs": 8,  # in l
                        "weight_body": 71,  # in kg
                        "weight_ballast": 1.5,  # in kg
                        "thickness_suit": 3,  # in mm
                    },
                ]
            ),
        ]
    )

    if not raw:
        df["volume_lungs"] = df["volume_lungs"].clip(0, 10.0)
        df["depth_gliding_descent_error"].fillna(3.0, inplace=True)
        df["depth_gliding_ascent_error"].fillna(3.0, inplace=True)
        df["thickness_suit"].fillna(r_nfoam * df["thickness_suit"] / 1000.0, inplace=True)

        # Get suite volume in m3
        df["volume_suit"] = (surface_suit := 2) * df["thickness_suit"] / 1000.0
        df["speed_descent"] = df["depth_max"] / df["time_descent"]
        df["speed_ascent"] = df["depth_max"] / df["time_ascent"]
        df["volume_lungs"] = df["volume_lungs"] / 1000.0

    if surname is None:
        return df

    return Diver(dict(df.query(f"surname == '{surname}'").iloc[0]))


def show_foam_density():

    df = get_data(raw=True)

    ts = r_nfoam * df["thickness_suit"] / 1000.0
    df["weight_suit_exp"] = ts

    # df["thickness_suit_estimation"] = r_nfoam * df["thickness_suit"] / 1000.0
    r_nfoam_corr = (df["weight_suit"].replace([0.0], [np.nan]) / ts).mean()
    print(f"Neoprene foam density is underestimated by a factor of {r_nfoam_corr:.2f}")
    print(f"{r_nfoam} kg/m3 => {r_nfoam_corr*r_nfoam:.0f} kg/m3. Calculation is done with {r_nfoam} kg/m3")

    df = df.sort_values("weight_suit_exp")

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(15, 5))

    ax.set_title(f"Suit weight estimation from density (default is {r_nfoam:.0f} kg/m3)", fontsize=16)
    ax.plot(np.arange(2), np.arange(2), label=f"Weight estimation with density={r_nfoam:.0f} kg/m3", lw=6)
    ax.plot(
        np.arange(4),
        np.arange(4) / r_nfoam_corr,
        lw=6,
        label=f"Using {r_nfoam_corr*r_nfoam:.0f} kg/m3 instead of {r_nfoam} kg/m3",
    )
    ax.scatter(df["weight_suit"], df["weight_suit_exp"], s=60, label=f"Comparison with given data")

    fig.legend(loc=4, fontsize=16)
