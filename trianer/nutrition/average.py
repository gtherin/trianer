from io import StringIO
import pandas as pd
import datetime


def get_data():
    norm = StringIO(
        """age name weight_kg height_cm
0. Boy 3.3 55
1. Boy 10 75
2 Boy 12.5 86
3 Boy 14 95
4 Boy 16 102
5 Boy 17.5 108
6 Boy 19.5 114
7 Boy 22 119
8 Boy 24 125
9 Boy 27 130
10 Boy 29.5 135
11 Boy 32.5 141
12 Boy 36 147
13 Boy 40 153
14 Boy 42 160
15 Boy 53 167
16 Boy 58 171
17 Boy 62 174
18 Boy 63 175
0 Girl 3.3 55
1 Girl 9.5 73
2 Girl 12 84
3 Girl 14 93
4 Girl 15.5 100
5 Girl 17 106
6 Girl 19 112
7 Girl 21.5 118
8 Girl 23.5 124
9 Girl 25.5 129
10 Girl 29 135
11 Girl 32.5 141
12 Girl 37 147
13 Girl 42 153
14 Girl 45.5 158
15 Girl 48.5 162
16 Girl 61.5 162
17 Girl 62 163
18 Girl 62 163"""
    )

    data = pd.read_csv(norm, sep=" ", parse_dates=[0])
    data["age"] = data["age"].astype(float)
    data["height_cm"] = data["height_cm"].astype(float)
    data["weight_kg"] = data["weight_kg"].astype(float)
    data["name"] = data["name"].astype(str)
    data["IMC"] = 10**4 * data["weight_kg"] / data["height_cm"] ** 2

    birthdays = pd.DataFrame(
        {
            "name": ["Boy", "Girl"],
            "is_woman": [False, True],
        }
    )
    data = data.merge(birthdays, on="name")

    return data
