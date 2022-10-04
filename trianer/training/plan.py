import datetime
import numpy as np
import pandas as pd


from .plans import plans, Plan
from . import running_economy as re
from ..core import theme


def get_time_min(val):
    def g(n):
        return 0 if n == "" else int(n.replace("s", "").replace("m", ""))

    h, m, s = "", "", ""
    if "h" in val:
        h, m = val.split("h")
        return datetime.timedelta(hours=g(h), minutes=g(m), seconds=g(s))
    elif "m" in val:
        m, s = val.split("m")
        return datetime.timedelta(hours=g(h), minutes=g(m), seconds=g(s))
    else:
        return datetime.timedelta(hours=g(h), minutes=g(m), seconds=g(val))


def get_hr(val):
    if "-" in val:
        i, a = val.split("-")
        return 0.5 * (float(i) + float(a))
    return float(val)


def get_distance(val):
    if "km" in val:
        return float(val.replace("km", ""))
    elif "m" in val:
        return float(val.replace("m", "")) / 1000.0
    return float(val)


activities = {
    "w": "walking",
    "s": "stretching",
}

"""

Optimal intensity is between 60% and 80% of VO2 max
"""


def develop_expression(activities):
    if "(" in activities:
        activity = activities[activities.find("(") + 1 : activities.find(")")]
        times = activities.split("x")[0]
        n_activity = int(times[times.rfind("+") + 1 :])

        d_activity = ((activity + "+") * n_activity)[:-1]
        # print(f"{n_activity}x({activity}) => {d_activity}")
        activities = activities.replace(f"{n_activity}x({activity})", d_activity)
    if "(" in activities:
        return develop_expression(activities)
    return activities


def get_training_plan(name="5h"):

    vo2max = 50

    plan = Plan(name, vo2max=vo2max)

    tp = plan.plan

    t_in_days = 0
    data = []
    for n, activities in enumerate(tp):
        if "l=w" in activities:
            data.append({"atime": np.round(t_in_days), "week": int(activities[3:])})
            continue
        t_in_days += 7.0 / 3.0  # 3 trainings per week
        if activities == "a=r":
            continue

        activities = develop_expression(activities)

        a = 0
        for activity in activities.split("+"):
            comps = activity.split(",")
            idata = {"atime": np.round(t_in_days), "seq": a, "training": activity, "activity": "footing"}

            for c in comps:
                f, val = c.split("=")
                if f == "hr":
                    speed = re.get_speed_from_hr(get_hr(val))
                    pace = datetime.timedelta(seconds=int(3600 / speed))
                    idata.update({"hr": get_hr(val), "pace": pace})
                if f == "d":
                    idata.update({"distance": get_distance(val)})
                if f == "t":
                    idata.update({"duration": get_time_min(val)})
                if f == "v":
                    idata.update({"pace": get_time_min(plan.paces[val])})
                if f == "p":
                    if val == "10-20-30":
                        max_speed = re.get_relative_intensity(1) * re.get_speed_from_vo2max(vo2max)
                        steps = [(10, 0.9), (20, 0.6), (30, 0.3)]
                        if 0:
                            for _ in range(5):
                                for d, i in steps:
                                    idata2 = idata.copy()
                                    idata2.update(
                                        {"duration": get_time_min(str(d)), "distance": 1.0 * i * max_speed * d / 3600}
                                    )
                        else:
                            speed = re.get_speed_from_hr(get_hr("100"))
                            pace = datetime.timedelta(seconds=int(3600 / speed))
                            idata2 = idata.copy()
                            idata2.update({"duration": get_time_min("5m"), "hr": get_hr("100"), "pace": pace})
                            data.append(idata2)
                            a += 1
                        idata.update({"duration": get_time_min("2m"), "pace": get_time_min(plan.paces["a0"])})

                if f == "a":
                    idata.update({"activity": "other"})
                if f == "w":
                    idata.update({"activity": "walking", "duration": get_time_min(val), "hr": get_hr("50")})
            data.append(idata)
            a += 1

    data = pd.DataFrame.from_records(data)

    data["week"] = data["week"].ffill()
    data = data[~np.isnan(data["seq"])]
    data["dtime"] = data["atime"].max() - data["atime"]

    data = data[data["activity"] == "footing"]

    data["pace"] = data["pace"].fillna(
        (data["duration"].dt.seconds / data["distance"]).fillna(0.0).astype("timedelta64[s]")
    )

    data["speed"] = (3600.0 / data["pace"].dt.seconds).replace([np.inf], np.nan)  # .fillna(0.0)
    data["distance"] = data["distance"].fillna(data["speed"] * data["duration"].dt.seconds / 3600.0)

    data["duration"] = data["duration"].fillna((3600 * data["distance"] / data["speed"]).astype("timedelta64[s]"))
    data["pace"] = data["pace"].fillna(
        (data["duration"].dt.seconds / data["distance"]).fillna(0.0).astype("timedelta64[s]")
    )

    tt = datetime.datetime.strptime("2023-04-02", "%Y-%m-%d")
    # tt = datetime.datetime(2023, 1, 1)

    data["rtime"] = [tt - datetime.timedelta(days=d) for d in data["dtime"].values]
    return data
