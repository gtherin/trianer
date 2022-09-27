import pandas as pd
from . import met

"""

    https://www.ericfavre.com/lifestyle/tableau-depenses-des-calories/#:~:text=Par%20exemple%2C%20pour%20un%20homme,1%2C8%20%3D%203006%20kcal.
    https://www.lepape-info.com/entrainement/les-systemes-energetiques-en-natation/#:~:text=En%20natation%2C%20comme%20dans%20les,a%C3%A9robie%20qui%20utilise%20l'oxyg%C3%A8ne
    https://britishswimschool.com/seattle/the-burn-how-many-calories-do-you-burn-swimming/#:~:text=Because%20most%20people%20are%20unable,and%20750%20calories%20per%20hour.

# Do it in a navigator
https://www.strava.com/oauth/authorize?client_id=93746&redirect_uri=http://localhost&response_type=code&approval_prompt=force&scope=activity:read_all
=> GET: code=3f5b0c1958bc3b5271771322048289377bf5580d

# Use new received code
https://www.strava.com/oauth/token?client_id=93746&client_secret=310f65abdda89164047e3881c3f3ec674f968665&code=3f5b0c1958bc3b5271771322048289377bf5580d&grant_type=authorization_code
=> POST: access_token=8e7ba78aef1a1f5f867a14c9d577be274c3b1ef3

https://www.strava.com/api/v3/athlete/activities?access_token=8e7ba78aef1a1f5f867a14c9d577be274c3b1ef3



https://www.strava.com/oauth/token?client_id=93746&client_secret=310f65abdda89164047e3881c3f3ec674f968665&code=8e7ba78aef1a1f5f867a14c9d577be274c3b1ef3&grant_type=refresh_token


https://www.strava.com/oauth/authorize?client_id=93746&redirect_uri=http://developers.strava.com&response_type=code&approval_prompt=force&scope=profile:read_all,activity:read_all

https://www.strava.com/oauth/authorize?client_id=93746&redirect_uri=http://localhost&response_type=code&approval_prompt=force&scope=read_all


=>
http://localhost/?state=&code=04eaa98832882031a3808f68fe0f906e5cac1b41&scope=read,read_all
http://localhost/?state=&code=ee79113371c136533bfe6d80347dcb4665996817&scope=read_all,activity:read_all,profile:read_all
=>

https://www.strava.com/api/v3/athlete/activities?client_id=93746&access_token=9f4a54258fffb124953127fe1bf8680abeaf8e9d


    """


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


def get_caloric_reserve(athlete, level=None):
    return 6000 - 500


def calculate_fuelings(df, race, athlete) -> pd.DataFrame:

    df["cduration"] = df.groupby("discipline")["duration"].cumsum()
    df["ddistance"] = df["distance"].diff().clip(0, 1000).fillna(0.0)
    fuelings = []
    fuels = race.get_fuels()
    needed_calories = df["kcalories"].sum() + get_caloric_reserve(athlete)

    durations = df.groupby("discipline")["duration"].sum()

    print("needed_calories=", needed_calories)
    print(durations)
    print(durations["cycling"] / 0.5)
    print(fuels)

    factor = 1
    if needed_calories < 6000:
        factor = 2
    foods_stuffs = {
        "running": [300, factor * 100],
        "cycling": [300, factor * 100],
        "transition 1": [300, factor * 100],
        "transition 2": [300, factor * 100],
    }

    tot_distance, tot_duration, pdiscipline, pindex = 0, 0, race.disciplines[0], df.index[0]
    for d in df.index:

        if pdiscipline != df["discipline"][d]:
            add_fuelings(pindex, f"End of {pdiscipline}", 0, 0)

        pindex, pdiscipline = d, df["discipline"][d]

        tot_duration += df["duration"][d]
        tot_distance += df["ddistance"][d]

        discipline = df["discipline"][d]

        def add_fuelings(i, source, drinks, food, pop=False):
            fuelings.append(
                [i, df["sequence"][i], df["discipline"][i], tot_distance, source, tot_duration, drinks, food]
            )
            if pop:
                fuels[df["discipline"][i]].pop(0)

        if d == df.index[0]:
            add_fuelings(d, "Start", 0, 0)
        if discipline in ["transition 1"]:
            add_fuelings(d, "Isotonic+fruit paste+compote", foods_stuffs[discipline][0], foods_stuffs[discipline][1])
        if discipline in ["transition 2"]:
            add_fuelings(d, "Isotonic+fruit paste+gel", foods_stuffs[discipline][0], foods_stuffs[discipline][1])
        if discipline in ["cycling"]:
            if len(fuels[discipline]) > 0 and df["distance"][d] >= fuels[discipline][0]:
                add_fuelings(
                    d, "org: fill up water", foods_stuffs[discipline][0], foods_stuffs[discipline][1], pop=True
                )
        if discipline in ["running"]:
            if len(fuels[discipline]) > 0 and df["distance"][d] >= fuels[discipline][0]:
                add_fuelings(d, "org: water+fruit", foods_stuffs[discipline][0], foods_stuffs[discipline][1], pop=True)
        if discipline in ["cycling"]:
            if tot_duration - fuelings[-1][5] > 0.5:
                add_fuelings(d, "Food (30 min)", foods_stuffs[discipline][0], foods_stuffs[discipline][1])
        if discipline in ["running"]:
            if tot_duration - fuelings[-1][5] > 0.5:
                add_fuelings(d, "Gel (30 min)", foods_stuffs[discipline][0], foods_stuffs[discipline][1])
        if d == df.index[-1]:
            add_fuelings(d, "Who's up for a beer ?", 0, 0)

    fuelings = pd.DataFrame(
        fuelings, columns=["index", "sequence", "discipline", "fdistance", "fooding", "cduration", "drinks", "food"]
    )

    # Get rid of double fuelings during transitions
    fuelings = fuelings.groupby("index", as_index=False).first().sort_values("index")
    fuelings = fuelings.groupby("cduration", as_index=False).first().sort_values("index")

    df = df.join(fuelings.set_index("index")[["fooding", "drinks", "food"]])
    print(df["food"].fillna(0.0).sum())

    df["kcalories"] += df["food"].fillna(0.0)
    df["ihydration"] = df["ihydration"].fillna(0.0) + df["hydration"].fillna(0.0)
    df["hydration"] += df["drinks"].fillna(0.0)

    return df


def show_kcalories():

    kcalories = met.get_kcalories(None)

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 4))
    fig.patch.set_facecolor("#cdcdcd")

    ax = axes[0]
    ax.set_facecolor("#cdcdcd")
    kcalories.query("discipline == 'running'").set_index("speed").plot(ax=ax)

    ax.grid()
    ax.legend(loc=1, prop={"size": 16})

    ax = axes[1]
    fig.patch.set_facecolor("#cdcdcd")
    ax.set_facecolor("#cdcdcd")
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
