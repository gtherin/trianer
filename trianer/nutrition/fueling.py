import numpy as np
import pandas as pd
import streamlit as st

from . import met
from ..core import models
from ..core.theme import background_color


def calculate_kcalories(df, race, athlete) -> pd.DataFrame:
    """

    Contrairement aux sports terrestres, en natation, la puissance mécanique est utilisée pour surpasser
    la résistance de l’eau et des vagues. Cette puissance dépend du cube de la vitesse de déplacement.
    ette relation implique qu’une petite augmentation de vitesse, nécessite une très forte augmentation de la puissance mécanique.
    Par exemple, pour augmenter sa vitesse de 2%, il faudra générer une augmentation de 8% de sa puissance.
    Un autre aspect important de la relation entre l’énergie et la propulsion est le coût énergétique. Cela correspond à la somme totale d’énergie
    dépensée par le corps du nageur sur une distance donnée. Différentes équations permettent d’estimer la production d’énergie de chaque système énergétique.
    Sur de très hautes intensités, tous les systèmes contribuent à la production d’énergie (à des niveaux différents selon la durée de l’effort).
    Sur des intensités sous-maximales, toute la puissance mécanique est générée par le métabolisme aérobie.
    En résumé, la natation est un sport où la dépense d’énergie est forte.
    Cela est principalement dû aux contraintes qui sont imposées par son environnement.

    2min de mieux au km avec combinaison
    """

    if "kcalories" in df.columns:
        del df["kcalories"]

    kcalories = pd.Series(
        [met.get_kcalories(athlete.weight, discipline=d, speed=athlete.speeds[d]) for d in race.disciplines],
        index=[d for d in race.disciplines],
    ).to_frame(name="kcalories")
    df = df.merge(kcalories, how="left", left_on=df["discipline"], right_index=True)
    df["kcalories"] = -df["kcalories"] * df["duration"]
    df.loc[df["discipline"].str.find("transition") == 0, "kcalories"] = 200

    return df


def get_basal_metabolic_rate(athlete):
    # Basal_metabolic_rate: The Mifflin St Jeor equation
    # 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age_year
    s = -161 if athlete.is_woman() else 5
    return 10.0 * athlete.weight + 6.25 * athlete.height - 5.0 * athlete.age + s


def get_caloric_reserve(athlete):
    # Assume it is 3 times the one of the BMR
    return 3.5 * get_basal_metabolic_rate(athlete)


def calculate_fuelings(df, race, athlete) -> pd.DataFrame:
    df["cduration"] = df.groupby("discipline")["duration"].cumsum()
    df["etime"] = df["duration"].cumsum()
    df["ddistance"] = df["distance"].diff().clip(0, 1000).fillna(0.0)
    fuelings = []
    fuels = race.get_fuels()
    needed_calories = df["kcalories"].sum() + get_caloric_reserve(athlete)
    # needed_calories = df["hydration"].sum() + get_caloric_reserve(athlete)

    ravitos = {}
    for discipline, ddf in df.groupby("discipline"):
        if discipline == "swimming":
            ravitos[discipline] = np.array([])
        elif "transition" in discipline:
            # r.append(ddf["etime"].iloc[0])
            ravitos[discipline] = np.array([0.0])
        else:
            dduration = ddf["duration"].sum()
            nor = np.round(2 * dduration)
            # for a in (np.linspace(0.0, 1.0, int(nor) + 2) * dduration)[1:-1]:
            #    r.append(ddf.iloc[(ddf["duration"] - a).abs().argsort()[:1]]["etime"].iloc[0])

            ravitos[discipline] = (np.linspace(0.0, 1.0, int(nor) + 2) * dduration)[1:-1]

    nor = np.sum([len(r) for r in ravitos.values()])
    calories_per_stop = np.clip(np.round(-needed_calories / nor / 100), 1, 3)

    max_hydration = df["duration"].sum() * models.get_maximum_ideal_hydration("mean", athlete)
    ratio = np.min([df["hydration"].abs().sum() / max_hydration, 1])

    hydr = 10 * np.floor(ratio * 33)

    dfood, rfood = f"Iso+{calories_per_stop:.0f}xFP/B", f"Iso+{calories_per_stop:.0f}xGel"
    dfood, rfood = f"Iso+FP/B", f"Iso+FP/B/Gel"
    foods_stuffs = {
        "swimming": [0, 0, f"Start"],
        "running": [hydr, calories_per_stop * 100, rfood],  # "org: water+fruit"
        "cycling": [hydr, calories_per_stop * 100, dfood],  # org: fill up water
        "transition 1": [hydr, calories_per_stop * 100, dfood],
        "transition 2": [hydr, calories_per_stop * 100, dfood],
    }

    tot_distance, tot_duration, pdiscipline, pindex = 0, 0, race.disciplines[0], df.index[0]
    for d in df.index:

        def add_fuelings(i, foods_stuffss):
            fuelings.append(
                {
                    "index": i,
                    "sequence": df["sequence"][i],
                    "discipline": df["discipline"][i],
                    "fdistance": tot_distance,
                    "drinks": foods_stuffss[0],
                    "food": foods_stuffss[1],
                    "fooding": foods_stuffss[2],
                    "cduration": tot_duration,
                }
            )
            ravitos[discipline] = ravitos[discipline][1:]

        if pdiscipline != df["discipline"][d]:
            add_fuelings(pindex, [0, 0, f"End of {pdiscipline}"])

        pindex, pdiscipline = d, df["discipline"][d]

        tot_duration += df["duration"][d]
        tot_distance += df["ddistance"][d]

        discipline = df["discipline"][d]

        dduration = df["cduration"][d] - df["duration"][d]

        if d == df.index[0]:
            add_fuelings(d, [0, 0, f"Start"])
        if d == df.index[-1]:
            add_fuelings(d, [0, 0, "Who's up for a beer ?"])
        if len(ravitos[discipline]) > 0 and dduration >= ravitos[discipline][0]:
            add_fuelings(d, foods_stuffs[discipline])

    # Get rid of double fuelings during transitions
    fuelings = pd.DataFrame.from_records(fuelings)
    fuelings = fuelings.groupby("index", as_index=False).first().sort_values("index")
    fuelings = fuelings.groupby("cduration", as_index=False).first().sort_values("index")

    df = df.join(fuelings.set_index("index")[["fooding", "drinks", "food"]])

    df["kcalories"] += df["food"].fillna(0.0)
    df["ihydration"] = df["ihydration"].fillna(0.0) + df["hydration"].fillna(0.0)
    df["hydration"] += df["drinks"].fillna(0.0)

    return df


def show_kcalories():
    kcalories = met.get_kcalories(None)

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 4))
    fig.patch.set_facecolor(background_color)

    ax = axes[0]
    ax.set_facecolor(background_color)
    kcalories.query("discipline == 'running'").set_index("speed").plot(ax=ax)

    ax.grid()
    ax.legend(loc=1, prop={"size": 16})

    ax = axes[1]
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)
    kcalories.query("discipline == 'cycling'").set_index("speed").plot(ax=ax)

    ax.grid()
    ax.legend(loc=1, prop={"size": 16})

    return fig


def configure_physiology():
    import matplotlib.pyplot as plt
    import numpy as np

    show_kcalories()

    fig, ax = plt.subplots(figsize=(15, 4))
    for w in [80 * 0.9, 80, 80 * 1.1]:
        kcalories = met.get_kcalories(w, discipline="swimming").set_index("speed")["atl"]
        kcalories.plot(ax=ax)

    fig, ax = plt.subplots(figsize=(15, 4))
    for w in [80 * 0.9, 80, 80 * 1.1]:
        kcalories = met.nutrition.get_kcalories(w, discipline="running").set_index("speed")["atl"]
        kcalories.plot(ax=ax)

    # 1000/1100 kcal pour les hommes et 800/900 kcal par repas

    fig, ax = plt.subplots(figsize=(15, 4))

    temp = np.arange(0, 40)
    hydr = pd.Series(-np.clip(temp * 100 - 600, 400, 2500), index=temp).to_frame(name="hydration")
    hydr *= 1.5
    hydr.plot(ax=ax)

    return fig
