import datetime
import pandas as pd

from ..core.labels import gl, Labels
from ..core import theme

pd.plotting.register_matplotlib_converters()


def show_roadmap(triathlon):

    ff = (
        triathlon.data[
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
        ]
        .copy()
        .rename(
            columns={
                "drinks": Labels.add_label("drinks", en="Drinks", fr="Boissons"),
                "fooding": Labels.add_label("comments", en="Comments", fr="Commentaires"),
                "food": Labels.add_label("food_supply", en="Food supply", fr="Alimentation"),
                "temperature": gl("temperature"),
                "distance": Labels.add_label("distance", en="Distance"),
                "discipline": Labels.add_label("discipline", en="Discipline"),
            }
        )
    )
    Labels.add_label("dtime_str", en="Transit time", fr="Temps de passage")
    ff[gl("dtime_str")] = ff["dtime"].dt.strftime("%H:%M")
    ff[gl("hydric_balance")] = ff["hydration"].fillna(0).cumsum()
    ff[gl("caloric_balance")] = ff["kcalories"].fillna(0).cumsum()
    Labels.add_label("cduration_min", en="Since start", fr="Depuis depart")
    ff[gl("cduration_min")] = (60 * ff["duration"].fillna(0)).cumsum().round()
    ff[gl("D+")] = ff.groupby(gl("discipline"))["aelevation"].cumsum().round()

    ff[gl("time_total")] = (
        datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        + pd.to_timedelta(ff["duration"].cumsum(), unit="h")
    ).dt.strftime("%H:%M")

    ff = ff[(~ff[gl("drinks")].isna()) | (ff.index[-1] == ff.index)].copy()
    for i in ff.index:
        if i == ff.index[-1]:
            ff.loc[i, gl("discipline")] = Labels.add_label(en="The end", fr="The end")
            ff.loc[i, gl("comments")] = Labels.add_label(en="Who's up for a beer ?", fr="Une petite bière ?")
        else:
            discipline = ff.loc[i, gl("discipline")]
            comment = ff.loc[i, gl("comments")].replace(discipline, gl(discipline))
            comment_fr = (
                comment.replace("Start", "Début").replace("End of", "Fin de").replace("FruitPaste", "Pate de fruits")
            )
            ff.loc[i, gl("discipline")] = gl(discipline)
            ff.loc[i, gl("comments")] = Labels.add_label(en=comment, fr=comment_fr)

    for c in ["dtime", "hydration", "kcalories", "duration"]:
        if c in ff.columns:
            del ff[c]

    return (
        ff[
            [
                gl("cduration_min"),
                gl("discipline"),
                gl("distance"),
                gl("comments"),
                gl("drinks"),
                gl("food_supply"),
                gl("dtime_str"),
                gl("hydric_balance"),
                gl("caloric_balance"),
                gl("D+"),
                gl("time_total"),
                gl("temperature"),
            ]
        ]
        .style.hide(axis="index")
        .apply(theme.roadmap_highlight, axis=1)
        .set_table_styles(
            [
                {"selector": "th", "props": f"background-color: {theme.background_color}; color: white;"},
            ],
            overwrite=False,
        )
        .format(
            {
                gl("distance"): "{0:,.1f} km",
                gl("temperature"): "{0:,.0f} °C",
                gl("hydric_balance"): "{0:.0f} ml",
                gl("caloric_balance"): "{0:.0f} kcal",
                gl("drinks"): "{0:.0f} ml",
                gl("food_supply"): "{0:.0f} kcal",
                gl("cduration_min"): "{0:.0f} min",
                gl("D+"): "{0:.0f} m",
            }
        )
        .bar(color=theme.roadmap_progress_bar, subset=[gl("cduration_min")], align="left")
    )
