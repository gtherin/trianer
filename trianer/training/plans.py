import datetime
import numpy as np
import pandas as pd

"""
80: course rapide
70-75: course normale
65-70: aisance respiratoire, peux parler pendant la course
sl is slow run, trotinant

f : footing
a: fractionné
+: footing montée
-: footing descente

4h30
Allures endurance > Allure 1 : 8min05 à 6min50 au km / Allure 2 : 6min50 à 5min55 au km

4h00
Allures endurance > Allure 1 : 7min31 à 6min22 au km / Allure 2 : 6min22 à 5min20 au km
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


def get_training_plan():
    tp = training_plan_marathon

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
