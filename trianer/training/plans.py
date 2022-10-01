import datetime
import numpy as np
import pandas as pd

"""
80: course rapide
70-75: course normale
65-70: aisance respiratoire, peux parler pendant la course
sl is slow run, trotinant


10-20-30
1 km d’échauffement en course lente + 3-4 séries de 5 min d’entraînement 10-20-30 avec 2 minutes de récupération entre les séries.
Les 10 secondes sont courues à plus de 90% de la vitesse maximale (vitesse déterminée par une épreuve de sprint de 100 m), 
les 20 secondes à 60% de la vitesse maximale 
et les 30 secondes à 30% de la vitesse maximale.


f : footing
a: fractionné
+: footing montée
-: footing descente
e: echauffement
s: stretching

4h30
a1 : 8min05 à 6min50 au km
a2 : 6min50 à 5min55 au km

4h00
a1 : 7min31 à 6min22 au km
a2 : 6min22 à 5min20 au km
am : allure marathon
    """

plans = {
    # https://www.kalenji.fr/terminer-mon-premier-marathon-en-12-semaines
    "Marathon (Decathlon, 5h, 12w)": (
        ["l:w1", "f:1h,hr:70-75", "f:1h,hr:70-75", "f:1h30,hr:70-75"]
        + ["l:w2", "f:1h,hr:70-75", "f:1h,hr:65-70+f:0h05,hr:80+f:0h10,hr:60", "f:1h45,hr:65-70"]
        + ["l:w3", "f:1h,hr:70-75", "f:0h55,hr:65-70+f:0h10,hr:80+f:0h10,hr:60", "f:2h,hr:65-70"]
        + ["l:w4", "f:0h45,hr:70-75", "rest", "f:1h,hr:70-75"]  # Rest week
        + ["l:w5", "f:1h30,hr:70-75", "f:h42,hr:65-70+f:0h08,hr:80+f:0h10,hr:60", "f:1h30,hr:65-70"]
        + ["l:w6", "f:1h30,hr:70-75", "f:h30,hr:65-70+f:h8,hr:80+sl:h5+f:h8,hr:80+f:h9,hr:60", "f:1h30,hr:65-70"]
        + ["l:w7", "f:1h30,hr:70-75", "f:h25,hr:65-70+f:h10,hr:80+sl:h5+f:h10,hr:80+f:h10,hr:60", "f:2h,hr:65-70"]
        + ["l:w8", "f:1h,hr:70-75", "rest", "f:1h,hr:65-70"]  # Rest week
        + ["l:w9", "f:1h30,hr:70-75", "f:h40,hr:65-70+f:h12,hr:80+f:h8,hr:60", "f:2h15,hr:65-70"]
        + [
            "l:w10",
            "f:h25,hr:65-70+f:h10,hr:80+sl:h5+f:h10,hr:80+f:h10,hr:60",
            "f:1h15,hr:65-70+f:h5,hr:80+f:h10,hr:60",
            "f:1h30,hr:70-75",
        ]
        + [
            "l:w11",
            "f:1h,hr:70-75",
            "f:h26,hr:65-70+f:h5,hr:100+sl:h3+f:h5,hr:100+sl:h3+f:h5,hr:100+sl:h3+f:h10,hr:60",
            "f:1h30,hr:70-75",
        ]
        + ["l:w12", "f:1h,hr:70-75", "rest", "w:h10"]  # Rest week
    ),  # https://www.timeto.com/Assets/TimeTo/plans/marathon_4h30
    "Marathon (Schneider, 4h30)": (
        [
            "l:w1",
            "e:h5+4x(f:h8,d:1.5km+sl:h2)+f:h15,a:a1",
            # Should prepare for the D+, check D+ of race
            "e:h5+15x(f:s20,hr:100+f:s20,hr:50)+f:h15,a:a1",  # Cote moderé
            "f:1h30,a:a2",
        ]
        + [
            "l:w2",
            "e:h5+f:h18,d:3km+2x(f:h10s42,d:2km+sl:h2)+f:h15,a:a1",
            # Should prepare for the D+, check D+ of race
            "e:h5+6x(f:s30,hr:100+f:s10,hr:50)+f:h3,hr:50+6x(f:s30,hr:100+f:s10,hr:50)+f:h15,a:a1",  # Cote moderé
            "f:1h45,a:a2",
        ]
        + [
            "l:w3",
            "e:h5+7x(f:h5s40,d:1km+sl:h1s45)+f:1h,a:a1",
            # Should prepare for the D+, check D+ of race
            "e:h5+10x(f:s40,hr:100+f:s10,hr:50)+f:h15,a:a1",  # Cote moderé
            "f:2h,a:a2",
        ]
        + [
            "l:w4",
            "e:h5+3x(f:h12,d:2km+sl:h3)+f:h15,a:a1",
            "e:h5+4x(10-20-30)+f:h15,a:a1",  # Cote moderé
            "f:1h45,a:a2",
        ]
        + [
            "l:w5",
            "e:h5+f:h30,d:5km+sl:h2+f:h11s40,d:2km+sl:h5+f:h5s25,d:1km+f:h15,a:a1",
            "f:h30,a:a2",
            "e:h12+f:2h08,d=21km,a:a2",
        ]
        + [
            "l:w6",
            "f:1h15,a=a2",
            "e:h5+7x(f:h4s30,d:0.8km+sl:h2)+f:h15,a:a1",
            "f:2h10,a:a2",
        ]
        + [
            "l:w7",
            "e:h5+2x(f:h17s45,d:3km+sl:d=0.4)+f:h15,a:a1",
            "e:h5+8x(f:h2s25,d:0.5km+sl:h=h1s15)+f:h15,a:a1",
            "f:2h20,a:a2",
        ]
        + [
            "l:w8",
            "e:h5+2x(f:h23,d:4km+sl:d=0.4)+f:h15,a:a1",
            "e:h5+8x(f:h3s18,d:0.6km+sl:d=0.2)+f:h15,a:a1",
            "f:2h,a:a2",
        ]
        + [
            "l:w9",
            "f:h30,a=a2+f:30s50,d=5km+f:h10,a:a2",
            "e:h5+6x(f:h2s28,d:0.5km+sl:h=h1s10)",
            "f:1h20,a:a2",
        ]
        + ["l:w10", "f:h20,a:a2+f:h12s20,d:2km+f:h10,a:a1", "f:h20,s:h10", "rest"]
    ),
}

# https://www.schneiderelectricparismarathon.com/fr/se-preparer/plan-guides

# https://www.timeto.com/Assets/TimeTo/plans/marathon_3h00

# https://www.timeto.com/Assets/TimeTo/plans/marathon_4h00


def get_time_min(val):
    h, m = val.split("h")
    if h == "":
        return int(m)
    elif m == "":
        return 60 * int(h)
    return int(h) * 60 + int(m)


def get_hr(val):
    if "-" in val:
        i, a = val.split("-")
        return 0.5 * (float(i) + float(a))

    return float(val)


def get_training_plan(name="Marathon (Decathlon, 5h, 12w)"):

    tp = plans[name]

    t_in_days = 0
    data = []
    for n, p in enumerate(tp):
        if "l:w" in p:
            data.append({"atime": np.round(t_in_days), "week": int(p[3:])})
            continue
        t_in_days += 7.0 / 3.0  # 3 trainings per week
        if p == "rest":
            continue

        for a, i in enumerate(p.split("+")):
            comps = i.split(",")
            idata = {"atime": np.round(t_in_days), "seq": a, "training": i}
            for c in comps:
                f, val = c.split(":")
                if f == "hr":
                    idata.update({"hr": get_hr(val)})
                if f == "f":
                    idata.update({"activity": "footing", "duration": get_time_min(val)})
                if f == "w":
                    idata.update({"activity": "walking", "duration": get_time_min(val), "hr": get_hr("50")})
                if f == "sl":
                    idata.update({"activity": "footing", "duration": get_time_min(val), "hr": get_hr("50")})
            data.append(idata)

    data = pd.DataFrame.from_records(data)
    data["week"] = data["week"].ffill()
    data = data[~np.isnan(data["seq"])]
    data["dtime"] = data["atime"].max() - data["atime"]

    tt = datetime.datetime(2023, 1, 1)

    data["rtime"] = [tt - datetime.timedelta(days=d) for d in data["dtime"].values]
    return data
