import datetime
import pandas as pd
import logging


from ..core.labels import gl

pd.plotting.register_matplotlib_converters()


def show_roadmap(triathlon):

    ff = triathlon.data[
        [
            "discipline",
            "dtime",
            "distance",
            "cduration",
            "duration",
            "temperature",
            "hydration",
            "kcalories",
            "fooding",
            "drinks",
            "aelevation",
            "food",
        ]
    ].copy()
    ff[gl("dtime_str")] = ff["dtime"].dt.strftime("%H:%M")
    ff[gl("hydric_balance")] = ff["hydration"].fillna(0).cumsum()
    ff[gl("caloric_balance")] = ff["kcalories"].fillna(0).cumsum()
    ff[gl("cduration_min")] = (60 * ff["duration"].fillna(0)).cumsum().round()
    # ff["aelevation"] = ff["elevation"].fillna(0).clip(0, 1000)
    ff["D+"] = ff.groupby("discipline")["aelevation"].cumsum().round()

    ff = ff.rename(
        columns={
            "drinks": "Drinks",
            "fooding": "Comments",
            "food": "Food supply",
            "temperature": "Temperature",
        }
    )

    ff[gl("time_total")] = (
        datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        + pd.to_timedelta(ff["duration"].cumsum(), unit="h")
    ).dt.strftime("%H:%M")

    ff = ff[(~ff["Drinks"].isna()) | (ff.index[-1] == ff.index)]
    ff["discipline"].iloc[-1] = "The end"

    for c in ["dtime", "hydration", "kcalories", "duration"]:
        if c in ff.columns:
            del ff[c]

    def highlight(s):
        if s.discipline == "cycling":
            return ["background-color: rgba(196, 77, 86, 0.2);"] * len(s)
        elif "transition" in s.discipline:
            return ["background-color: rgba(204, 204, 204, 0.5);"] * len(s)
        elif s.discipline == "running":
            return ["background-color: rgba(0, 255, 0, 0.3);"] * len(s)
        elif s.discipline == "swimming":
            return ["background-color: rgba(0, 0, 255, 0.2);"] * len(s)
        elif s.discipline == "The end":
            return ["background-color: rgba(0, 6, 57, 112);color: red; font-weight: bolder"] * len(s)
        else:
            return ["background-color: white"] * len(s)

    return (
        ff[
            [
                gl("cduration_min"),
                "discipline",
                "distance",
                "Comments",
                "Drinks",
                "Food supply",
                gl("dtime_str"),
                gl("hydric_balance"),
                gl("caloric_balance"),
                "D+",
                gl("time_total"),
                "Temperature",
            ]
        ]
        .style.hide(axis="index")
        .apply(highlight, axis=1)
        .set_table_styles(
            [
                {"selector": "th", "props": "background-color: #cdcdcd; color: white;"},
            ],
            overwrite=False,
        )
        .format(
            {
                "distance": "{0:,.0f} km",
                "Temperature": "{0:,.0f} °C",
                gl("hydric_balance"): "{0:.0f} ml",
                gl("caloric_balance"): "{0:.0f} kcal",
                "Drinks": "{0:.0f} ml",
                "Food supply": "{0:.0f} kcal",
                gl("cduration_min"): "{0:.0f} min",
                "D+": "{0:.0f} m",
            }
        )
        .bar(color=["Red", "Green"], subset=[gl("cduration_min")], align="left")
    )
