from scipy.optimize import curve_fit
import json
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


from ..core import tools

hermann = """85,07:21,12:39,26:27,40:46,55:25,1:25:32,2:03:17
84,07:27,12:50,26:51,41:23,56:18,1:26:54,2:05:18
83,07:34,13:02,27:16,42:02,57:11,1:28:19,2:07:23
82,07:41,13:13,27:41,42:43,58:07,1:29:46,2:09:31
81,07:47,13:25,28:07,43:24,59:03,1:31:16,2:11:43
80,07:54,13:38,28:34,44:06,1:00:02,1:32:48,2:13:59
79,08:02,13:50,29:01,44:49,1:01:02,1:34:23,2:16:20
78,08:09,14:03,29:30,45:34,1:02:03,1:36:01,2:18:44
77,08:16,14:17,29:59,46:20,1:03:07,1:37:42,2:21:13
76,08:24,14:30,30:29,47:07,1:04:12,1:39:26,2:23:46
75,08:32,14:44,30:59,47:55,1:05:20,1:41:13,2:26:24
74,08:40,14:59,31:31,48:45,1:06:29,1:43:03,2:29:07
73,08:49,15:13,32:03,49:37,1:07:41,1:44:57,2:31:56
72,08:57,15:29,32:37,50:30,1:08:54,1:46:54,2:34:50
71,09:06,15:44,33:11,51:25,1:10:11,1:48:56,2:37:50
70,09:15,16:01,33:47,52:21,1:11:29,1:51:01,2:40:56
69,09:25,16:17,34:23,53:19,1:12:50,1:53:11,2:44:09
68,09:34,16:34,35:01,54:19,1:14:14,1:55:25,2:47:29
67,09:44,16:52,35:40,55:21,1:15:41,1:57:43,2:50:55
66,09:54,17:10,36:20,56:25,1:17:10,2:00:07,2:54:30
65,10:05,17:29,37:02,57:32,1:18:43,2:02:35,2:58:12
64,10:15,17:48,37:44,58:41,1:20:19,2:05:10,3:02:02
63,10:26,18:08,38:29,59:52,1:21:58,2:07:50,3:06:01
62,10:38,18:29,39:15,1:01:05,1:23:41,2:10:36,3:10:10
61,10:50,18:50,40:02,1:02:21,1:25:28,2:13:28,3:14:29
60,11:02,19:12,40:51,1:03:40,1:27:18,2:16:27,3:18:58
59,11:15,19:35,41:42,1:05:02,1:29:13,2:19:33,3:23:38
58,11:28,19:58,42:35,1:06:27,1:31:13,2:22:47,3:28:30
57,11:41,20:22,43:30,1:07:55,1:33:17,2:26:09,3:33:35
56,11:55,20:48,44:26,1:09:27,1:35:26,2:29:40,3:38:53
55,12:10,21:14,45:25,1:11:02,1:37:41,2:33:19,3:44:25
54,12:24,21:41,46:27,1:12:42,1:40:01,2:37:08,3:50:13
53,12:40,22:09,47:31,1:14:25,1:42:28,2:41:08,3:56:17
52,12:56,22:38,48:36,1:16:13,1:45:00,2:45:18,4:02:39
51,13:13,23:09,49:46,1:18:05,1:47:40,2:49:40,4:09:19
50,13:30,23:40,50:58,1:20:03,1:50:27,2:54:15,4:16:20
49,13:48,24:13,52:13,1:22:06,1:53:22,2:59:04,4:23:42
48,14:06,24:47,53:32,1:24:14,1:56:25,3:04:06,4:31:27
47,14:26,25:22,54:53,1:26:29,1:59:37,3:09:25,4:39:38
46,14:46,25:59,56:19,1:28:50,2:02:58,3:15:01,4:48:16
45,15:07,26:38,57:49,1:31:18,2:06:30,3:20:54,4:57:25
44,15:29,27:18,59:23,1:33:54,2:10:13,3:27:08,5:07:04
43,15:51,28:01,1:01:01,1:36:37,2:14:08,3:33:42,5:17:20
42,16:15,28:45,1:02:45,1:39:29,2:18:16,3:40:41,5:28:14
41,16:40,29:31,1:04:34,1:42:30,2:22:38,3:48:05,5:39:51
40,17:06,30:19,1:06:28,1:45:42,2:27:15,3:55:55,5:52:13
39,17:33,31:10,1:08:29,1:49:05,2:32:10,4:04:17,6:05:27
38,18:01,32:03,1:10:37,1:52:39,2:37:21,4:13:11,6:19:38
37,18:31,33:00,1:12:51,1:56:26,2:42:54,4:22:43,6:34:51
36,19:03,33:59,1:15:14,2:00:28,2:48:47,4:32:56,6:51:14"""
# ,VO2,3,5,10,15,20,30,42.5

# ,vo2max,=,3.5,vma


def get_hermann(format="default", vo2max=None):
    import pandas as pd
    import datetime

    data = hermann.replace(",", ",")
    data = pd.DataFrame(
        [row.split(",") for row in hermann.split("\n")], columns=["vo2max", 3, 5, 10, 15, 20, 30, 42.5]
    ).set_index("vo2max")

    data.columns = [float(c) for c in data.columns]
    data.index = [float(i) for i in data.index]

    def get_duration(x):
        dt = x.split(":")
        h = int(dt[0]) if len(dt) == 3 else 0
        return datetime.timedelta(hours=h, minutes=int(dt[-2]), seconds=int(dt[-1]))

    if format == "default":
        return data

    data = data.applymap(get_duration)

    if format == "duration_speed":
        if vo2max is not None:
            data = get_hermann(format="duration_speed").query(f"vo2max == {vo2max}")
            return data.set_index("duration")["speed"]
        else:
            # duration in (min)
            data = get_hermann(format="seconds")
            data = data.stack().reset_index()
            data.columns = ["vo2max", "distance", "duration"]
            data["duration"] /= 60
            data["speed"] = 60 * data["distance"] / data["duration"]

            # Add speed for 100m as equal to the VMA, neglecting anaerobic contributions
            mdf = data[data["distance"] == data["distance"].min()].copy()
            mdf["distance"] = 0.1
            mdf["speed"] = mdf["speed"] * 1.0

            mdf["duration"] = 60 * mdf["distance"] / mdf["speed"]

            vma = mdf[["vo2max", "speed"]].copy().rename(columns={"speed": "vma"})

            data = pd.concat([mdf, data]).sort_values(["vo2max", "distance"])

            data = data.merge(vma, on="vo2max")

            return data

    if format == "minutes":
        for c in data.columns:
            data[c] = (data[c].dt.seconds / 60.0).astype(int)
    elif format == "speed":
        for c in data.columns:
            data[c] = 3600 * c / data[c].dt.seconds
    elif format == "seconds":
        for c in data.columns:
            data[c] = data[c].dt.seconds

    if vo2max is not None:
        return data.loc[vo2max]

    return data


def smooth(x, a, b, c):
    return a / (x + 0.001) ** b + c


def generate_hermann_parameters():

    dparameters = {}
    print(tools.get_file("hermann.json"))
    # os.system(f"rm " + tools.get_file("hermann.json"))

    for vo2max in range(30, 90):
        df = get_hermann("duration_speed")
        df = df[(df["distance"] > 1.0) & (df["vo2max"] == vo2max)]
        if df.empty:
            continue

        popt, pcov = curve_fit(smooth, df["duration"], df["speed"], bounds=([7.0, 0.1, 1.2], [26.0, 1.8, 10.0]))
        params = list(popt) + [df["speed"].max()]

        dparameters[vo2max] = params
    print(tools.get_file("hermann.json"))
    with open(tools.get_file("hermann.json"), "w") as f:
        json.dump(dparameters, f)


class Hermann:
    hparameters = None

    @staticmethod
    def get_hparameters(reload=False, vo2max=None):
        if Hermann.hparameters is None or reload:
            print(tools.get_file("hermann.json"))
            with open(tools.get_file("hermann.json")) as f:
                Hermann.hparameters = json.load(f)
                print(Hermann.hparameters)
        if vo2max is None:
            return Hermann.hparameters
        else:
            return Hermann.hparameters[str(vo2max)]

    @staticmethod
    def plot():
        # trianer.training.generate_hermann_parameters()

        vo2max = np.arange(40, 80, 1)
        duration = np.arange(0, 300)

        xx, yy = np.meshgrid(vo2max, duration)
        vo2max = np.reshape(xx, np.product(xx.shape))
        duration = np.reshape(yy, np.product(yy.shape))

        sdata = pd.DataFrame(
            {
                "vo2max": vo2max,
                "duration": duration,
                "speed": [Hermann.smooth_clip(vo2max[i], duration[i]) for i in range(len(vo2max))],
            }
        )

        palette = sns.color_palette("rocket_r", as_cmap=True)

        # Plot the lines on two facets
        sns.relplot(
            data=sdata, x="duration", y="speed", hue="vo2max", kind="line", palette=palette, lw=3, height=6, aspect=1
        )

        filename = tools.get_file("hermann.png", read=False, write=False)
        print(f"Write in {filename}")
        plt.savefig(filename)

        plt.show()

    @staticmethod
    def smooth_clip(vo2max, duration):
        a, b, c, clip = Hermann.get_hparameters(vo2max=vo2max)
        return np.clip(smooth(duration, a, b, c), 0, clip)
