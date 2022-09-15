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


def get_kcalories(weight, discipline="all", speed=None):

    en2fr = {
        "swimming": "natation",
        "cycling": "cyclisme",
        "running": "course",
        "walking": "marche",
        "rower": "rameur",
        "climbing": "escalade",
        "hiking": "randonnée",
        "golfing": "golf",
        "jumping_rope": "corde_a_sauter",
    }

    """Get calories per hour"""

    # Calories for 30 minutes
    # source https://www.health.harvard.edu/diet-and-weight-loss/calories-burned-in-30-minutes-for-people-of-three-different-weights
    # https://www.urmc.rochester.edu/encyclopedia/content.aspx?ContentTypeID=41&ContentID=CalorieBurnCalc&CalorieBurnCalc_Parameters=80
    calories = StringIO(
        """activité_30min	speed	55 kg	70 kg	85 kg
swimming	1	180	216	252
swimming	3	300	360	420

cycling	19	210	252	290
cycling	23.5	300	360	420
cycling	27.5	360	432	504
cycling	35	495	594	693
VTT		255	306	357
Vélo elliptique	0	270	324	378

walking	5.5	107	133	159
walking	6.5	135	175	189
hiking	0	170	216	252
golfing	1	105	126	147
golfing	3	165	198	231

running	5.5	107	133	159
running	6.5	135	175	189
running	8	240	288	336
running	9.5	300	360	420
running	12	375	450	525
running	16	453	562	671

weight_lifting	1	90	108	126
weight_lifting	3	180	216	252

yoga		120	144	168

cardio	1	135	162	189
cardio	3	240	306	336

Aérobic_à_faible_impact		165	198	231
Bowling	0	90	108	125
Frisbee	0	85	105	125
Volleyball		90	108	126
Équitation		57	70	84

kayaking	0	150	180	210

dancing	0	165	198	231
skiing	0	180	216	252
catch	0	180	216	252
stepper	0	180	216	252
basket-fauteuil	0	195	234	273

skating	1	210	252	294
skating	2	311	386	461
climbing	0	227	282	336
Ski_de_fond	0	198	246	293
jumping_rope	3	340	421	503
jumping_rope	2	226	281	335
handball	0	360	432	504

basket	0	240	288	336
football	0	210	252	294

judo	0	300	360	420

sleeping		19	22	26
reading		34	40	47
queuing		28	35	41
cooking		57	70	84
playing_with_kids		114	141	168
car_wash		135	162	189
painting		142	176	210
moving_furniture		170	211	252
moving_boxes		210	252	294"""
    )

    more_sports = {
        "handball": ["dodgeball"],
        "judo": ["boxing", "karaté"],
        "football": ["tennis", "rower", "racquetball", "squash", "diving"],
        "kayaking": ["rafting", "Skateboard"],
        "yoga": ["aquagym", "tai_chi"],
        "basket": ["rugby", "hockey", "beach-volley", "Marche_en_raquettes"],
    }

    calories = pd.read_csv(calories, sep="	").rename(columns={"activité_30min": "discipline"})

    for r, ss in more_sports.items():
        for s in ss:
            calories = pd.concat(
                [calories, calories.query(f"discipline=='{r}'").assign(discipline=s)], axis=0
            ).reset_index(drop=True)

    for w in ["speed", "55 kg", "70 kg", "85 kg"]:
        calories[w] = calories[w].astype("float")

    calories["MET 55 kg"] = calories["55 kg"] / 107
    calories["MET 70 kg"] = calories["70 kg"] / 133
    calories["MET 85 kg"] = calories["85 kg"] / 159

    correction = 1.0  # + 0.4 * (calories["discipline"] == "course").astype(float)
    calories["X kg"] = 0.0
    for w in ["55 kg", "70 kg", "85 kg"]:
        calories[w] *= 2.0 * correction
        calories["X kg"] += 0.33 * calories[w]

    if weight is None:
        return calories

    weights = get_calweights(weight)
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
        [get_kcalories(athlete.weight, discipline=d, speed=athlete.speeds[d]) for d in triathlon.disciplines],
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

    return fig
