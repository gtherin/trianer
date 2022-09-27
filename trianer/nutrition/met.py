from io import StringIO
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
    # swimming	1	180	216	252

    calories = StringIO(
        """activité_30min	speed	55 kg	70 kg	85 kg
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

    correction = 1.0  # + 0.4 * (calories["discipline"] == "running").astype(float)
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
