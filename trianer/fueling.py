from io import StringIO
import numpy as np
import pandas as pd


def get_calweights(masse):
    """Get calories for swimming"""
    if masse <= 55:
        return {"55 kg": 1, "70 kg": 0, "85 kg": 0}
    elif masse < 70:
        w = (masse - 55) / (70 - 55)
        return {"55 kg": 1 - w, "70 kg": w, "85 kg": 0}
    elif masse < 85:
        w = (masse - 70) / (85 - 70)
        return {"55 kg": 0, "70 kg": 1 - w, "85 kg": w}
    else:
        return {"55 kg": 0, "70 kg": 0, "85 kg": 1}


def get_kcalories(poids, discipline="all", speed=None):
    """Get calories per hour"""

    # Calories for 30 minutes
    calories = StringIO(
        """activité_30min	speed	55 kg	70 kg	85 kg
natation		300	360	420

cyclisme	19	210	252	290
cyclisme	23.5	300	360	420
cyclisme	27.5	360	432	504
cyclisme	35	495	594	693

course	5.5	107	133	159
course	6.5	135	175	189
course	8	240	288	336
course	9.5	300	360	420
course	12	375	450	525
course	16	453	562	671
        """
    )

    calories = pd.read_csv(calories, sep="	").rename(columns={"activité_30min": "discipline"})
    correction = 1.0 + 0.4 * (calories["discipline"] == "course").astype(float)
    for w in ["55 kg", "70 kg", "85 kg"]:
        calories[w] *= 2.0 * correction

    if poids is None:
        return calories

    weights = get_calweights(poids)
    calories["atl"] = 0
    for w in ["55 kg", "70 kg", "85 kg"]:
        calories["atl"] += weights[w] * calories[w]

    calories = calories[["discipline", "speed", "atl"]]

    if discipline != "all":
        calories = calories.query(f"discipline=='{discipline}'")

    if speed is None:
        return calories

    x = calories["speed"].searchsorted(speed)
    # print(discipline, speed, calories["atl"].iloc[x])

    return calories["atl"].iloc[x]


def calculate_hydration(df, triathlon, athlete) -> pd.DataFrame:
    """
    Max hydration 700ml homme, 600ml femme

    """

    if "hydration" in df.columns:
        del df["hydration"]

    temp = np.arange(0, 40)
    hydr = pd.Series(-np.clip(temp * 100 - 600, 400, 2500), index=temp).to_frame(name="hydration")

    if type(athlete.sudation) == float:
        hydr *= athlete.sudation
    elif athlete.sudation == "intense":
        hydr *= 1.2
    elif athlete.sudation == "faible":
        hydr *= 0.8
    hydr = df.merge(hydr, how="left", left_on=df["temperature"].round(), right_index=True)

    df.loc[df["discipline"] == "natation", "hydration"] = -900 * df.loc[df["discipline"] == "natation", "duration"]
    df.loc[df["discipline"] == "cyclisme", "hydration"] = (
        df.loc[df["discipline"] == "cyclisme", "duration"] * hydr.loc[hydr["discipline"] == "cyclisme", "hydration"]
    )
    df.loc[df["discipline"] == "course", "hydration"] = (
        df.loc[df["discipline"] == "course", "duration"] * hydr.loc[hydr["discipline"] == "course", "hydration"]
    )

    df["ihydration"] = 0.0
    df.loc[df["discipline"] == "cyclisme", "ihydration"] = 700 * df.loc[df["discipline"] == "cyclisme", "duration"]
    df.loc[df["discipline"] == "course", "ihydration"] = 700 * df.loc[df["discipline"] == "course", "duration"]

    return df


def calculate_kcalories(df, triathlon, athlete) -> pd.DataFrame:

    if "kcalories" in df.columns:
        del df["kcalories"]

    kcalories = pd.Series(
        [get_kcalories(athlete.poids, discipline=d, speed=athlete.speeds[d]) for d in triathlon.disciplines],
        index=[d for d in triathlon.disciplines],
    ).to_frame(name="kcalories")
    df = df.merge(kcalories, how="left", left_on=df["discipline"], right_index=True)
    df["kcalories"] = -df["kcalories"] * df["duration"]
    df.loc[df["discipline"].str.find("transition") == 0, "kcalories"] = 200

    return df


def calculate_fuelings(df, triathlon, athlete) -> pd.DataFrame:

    df["cduration"] = df.groupby("discipline")["duration"].cumsum()
    df["ddistance"] = df["distance"].diff().clip(0, 1000).fillna(0.0)

    fuelings = []

    fuels = {
        "natation": [0],
        "cyclisme": triathlon.get_org_fueling("cyclisme")[1:],
        "course": triathlon.get_org_fueling("course")[1:],
    }

    tot_distance, tot_duration = 0, 0
    for d in df.index:
        tot_duration += df["duration"][d]
        tot_distance += df["ddistance"][d]

        def add_fuelings(d, source, drinks, food):
            fuelings.append(
                [d, df["sequence"][d], df["discipline"][d], tot_distance, source, tot_duration, drinks, food]
            )

        if df["discipline"][d] in ["transition 1"]:
            add_fuelings(d, "Isotonic+pate de fruits + compote", 300, 200)
        if df["discipline"][d] in ["transition 2"]:
            add_fuelings(d, "Isotonic+pate de fruits + gel", 300, 200)
        if df["discipline"][d] in ["natation"]:
            if len(fuels[df["discipline"][d]]) > 0 and df["distance"][d] >= fuels[df["discipline"][d]][0]:
                add_fuelings(d, "transition", 100, 0)
                fuels[df["discipline"][d]].pop(0)
        if df["discipline"][d] in ["cyclisme"]:
            if len(fuels[df["discipline"][d]]) > 0 and df["distance"][d] >= fuels[df["discipline"][d]][0]:
                add_fuelings(d, "org: remplir eau", 300, 100)
                fuels[df["discipline"][d]].pop(0)

        if df["discipline"][d] in ["course"]:
            if len(fuels[df["discipline"][d]]) > 0 and df["distance"][d] >= fuels[df["discipline"][d]][0]:
                add_fuelings(d, "org: eau + fruit", 300, 100)
                fuels[df["discipline"][d]].pop(0)
        if df["discipline"][d] in ["cyclisme"]:
            if tot_duration - fuelings[-1][5] > 0.5:
                add_fuelings(d, "30 min", 300, 100)

    fuelings = pd.DataFrame(
        fuelings, columns=["index", "sequence", "discipline", "fdistance", "fooding", "cduration", "drinks", "food"]
    ).set_index("index")

    # print(fuelings)
    df = df.merge(fuelings[["fooding", "drinks", "food"]], how="left", left_index=True, right_index=True)

    df["kcalories"] += df["food"].fillna(0.0)
    df["ihydration"] = df["ihydration"].fillna(0.0) + df["hydration"].fillna(0.0)
    df["hydration"] += df["drinks"].fillna(0.0)

    return df


def show_kcalories():

    kcalories = get_kcalories(None)

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 4))
    fig.patch.set_facecolor("#cdcdcd")

    ax = axes[0]
    ax.set_facecolor("#cdcdcd")
    kcalories.query("discipline == 'course'").set_index("speed").plot(ax=ax)

    ax.grid()
    ax.legend(loc=1, prop={"size": 16})

    ax = axes[1]
    fig.patch.set_facecolor("#cdcdcd")
    ax.set_facecolor("#cdcdcd")
    kcalories.query("discipline == 'cyclisme'").set_index("speed").plot(ax=ax)

    ax.grid()
    ax.legend(loc=1, prop={"size": 16})
