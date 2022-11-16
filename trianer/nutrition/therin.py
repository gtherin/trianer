from io import StringIO
import pandas as pd
import datetime


def get_data():
    data = StringIO(
        """date name weight_kg height_cm
20221126 Celestine 25 134
20220727 Celestine 23.5 130
20220123 Celestine 23 128
20210522 Celestine 21.5 125
20201206 Celestine  122
20200627 Celestine  118
20181023 Celestine  108
20160327 Celestine  086
20221126 Victor 44 148
20220727 Victor 41.5 144
20220123 Victor 39 143
20210522 Victor 36 137
20201206 Victor 34 134
20200627 Victor 32 131
20191210 Victor 30 127
20181023 Victor 27 121
20170601 Victor  111
20160327 Victor  102
20150605 Victor  097"""
    )
    data = pd.read_csv(data, sep=" ", parse_dates=[0])

    birthdays = pd.DataFrame(
        {
            "name": ["Victor", "Celestine"],
            "birthday": [datetime.datetime(2011, 3, 29), datetime.datetime(2013, 12, 23)],
            "is_woman": [False, True],
        }
    )
    data = data.merge(birthdays, on="name")
    data["age"] = (data["date"] - data["birthday"]).dt.days / 365.25
    data["age"] = data["age"].astype(float)

    data["height_cm"] = data["height_cm"].astype(float)
    data["name"] = data["name"].astype(str)
    data["IMC"] = 10**4 * data["weight_kg"] / data["height_cm"] ** 2

    return data  # .sort_values("is_woman", ascending=False)
