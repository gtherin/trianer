import datetime
import numpy as np
import pandas as pd
import scipy as sp
import logging

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D


from .races import Race

from . import gpx
from . import weather
from . import fueling

logging.getLogger("matplotlib.font_manager").disabled = True
logging.getLogger("matplotlib").setLevel(logging.ERROR)


def get_empty_box():
    import streamlit as st

    return st.empty()


class Triathlon:
    def __init__(
        self, epreuve, longueur=None, athlete=None, temperature=None, races_configs=None, info_box=None
    ) -> None:

        self.race = Race(epreuve, longueur)

        self.info_box = get_empty_box() if info_box is None else info_box

        if self.race.epreuve not in Race.get_available_races().keys():
            raise ValueError(
                f"""Liste des epreuves documentées:

        - {list(Race.get_available_races().keys())} ou
        - {self.disciplines}

        # Definir un athlete
        athlete = triaainer.Athlete(weight=80, swimming="2min10s/100m", cycling="27.0km/h", running="5min30s/km", transitions="10min")

        # Simule une course a pieds de 20km
        course = triaainer.Triathlon(epreuve="running", longueur="20", temperature=[20, 25], athlete=athlete)

        # Simule la realisation d'un Elsassman au format L
        elsassman = triaainer.Triathlon(epreuve="Elsassman", longueur="L", athlete=athlete)

        """
            )

        self.start_time = self.race.get_start_time()
        self.gpx = self.get_adjusted_data()

        if athlete is not None:
            self.simulate_race(athlete, temperature=temperature)

    def get_adjusted_data(self):
        data = []
        self.fuelings = [0]

        info_box = get_empty_box()

        ref_dist = 0
        for d, discipline in enumerate(self.race.disciplines):

            fuelings = self.race.distances[d] if hasattr(self.race, "distances") else 0

            if "x2" in self.race.get_option(d) and discipline != "swimming":
                self.dfuelings[d] += [0.5 * +f for f in self.get_org_fueling(d)]

            if self.race.has_data(d):
                df = self.race.get_data(d, self.info_box)
            else:
                df = (
                    pd.DataFrame(np.linspace(0, fuelings, 10), columns=["distance"])
                    .assign(altitude=0.0)
                    .assign(elevation=0.0)
                    .assign(discipline=discipline)
                )

            df["distance"] *= fuelings / df.distance.iloc[-1]
            df["elevation"] *= self.race.get_elevation(d) / np.max([df.elevation.clip(0, 1000).sum(), 0.1])
            data.append(df.assign(sequence=d * 2))

            self.fuelings += [f for f in self.get_org_fueling(d)]
            ref_dist += fuelings

        self.fuelings = sorted(list(set(self.fuelings)))

        return gpx.enrich_data(pd.concat(data))

    def get_mean_coordonates(self):
        if "latitude" not in self.gpx.columns:
            return weather.get_default_coordonates()[:2]
        return self.gpx.latitude.mean(), self.gpx.longitude.mean()

    def get_temperature(self):
        return weather.get_forecasts(coordonates=self.get_mean_coordonates()[:2])

    def get_gpx(self, discipline=None, index=None):
        if discipline is None:
            data = self.gpx
        else:
            data = self.gpx.query(f"discipline=='{self.race.get_discipline(discipline)}'")
        if index is not None and index in data.columns:
            data = data.set_index(index)

        if self.race.get_discipline(discipline) != "swimming":
            d = data.distance.clip(0, 1000).diff()
            cutoff = d.mean() * 3
            data = data[d < cutoff]

        return data

    def get_org_fueling(self, d):
        if not hasattr(self, "dfuelings"):
            self.dfuelings = [[0]] * len(self.race.disciplines)
        if type(d) == int:
            return self.dfuelings[d]
        for idd, idiscipline in enumerate(self.race.get_disciplines()):
            if idiscipline == d and len(self.dfuelings) > idd:
                return self.dfuelings[idd]
        return [0]

    def get_distance(self, d):
        if type(d) == int:
            return self.distances[d]
        for idd, idiscipline in enumerate(self.get_disciplines()):
            if idiscipline == d:
                return self.distances[idd]
        return 0

    def get_colors(self):
        return ["blue", "brown", "green"]

    def get_color(self, d):
        return self.get_colors()[d]

    def simulate_race(self, athlete, temperature=None):

        data = []

        for c in ["temperature", "hr", "hydration", "kcalories", "speed", "dtime"]:
            if c in self.gpx.columns:
                del self.gpx[c]

        for d, discipline in enumerate(self.race.disciplines):
            df = self.gpx.query(f"discipline=='{discipline}'").copy()
            df = athlete.calculate_speed(df, discipline)
            df["duration"] = (df["distance"].diff().clip(0, 1000) / df["speed"]).fillna(0)

            if d < len(self.race.disciplines) - 1:
                transition = df.iloc[-1].to_dict()
                transition.update(
                    {
                        "slope": 0.0,
                        "speed": 0.0,
                        "hydration": 0.0,
                        "discipline": f"transition {d+1}",
                        "sequence": 2 * d + 1,
                        "duration": athlete.transition1 / 60.0,
                    }
                )
                df = pd.concat([df, pd.DataFrame.from_records([transition])], ignore_index=True)

            data.append(df)

        data = pd.concat(data).sort_values(["sequence", "distance", "duration"])
        data.index = range(len(data))

        data["dtime"] = self.start_time + pd.to_timedelta(data["duration"].cumsum(), unit="h")

        # Set temperature
        data = weather.merge_temperature_forecasts(
            data, coordonates=self.get_mean_coordonates()[:2], start_time=self.start_time, temperature=temperature
        )

        data["fdistance"] = data["distance"].diff().clip(0, 10000).fillna(0.0).cumsum()

        data = fueling.calculate_hydration(data, self, athlete)
        data = fueling.calculate_kcalories(data, self, athlete)
        data = fueling.calculate_fuelings(data, self, athlete)

        self.data = data
        self.athlete = athlete
        return data

    def show_weather_forecasts(self):
        return f"La temperature attendue est de {self.get_temperature()} °C"

    def show_gpx_track(triathlon):
        from branca.element import Figure
        import folium

        fig = Figure(width=900, height=300)
        trimap = folium.Map(location=triathlon.get_mean_coordonates()[:2], zoom_start=10)
        fig.add_child(trimap)

        from folium.plugins import MarkerCluster

        marker_cluster = MarkerCluster().add_to(trimap)
        for d in range(3):

            gpx = triathlon.get_gpx(d)
            gpx = gpx.dropna(subset=["latitude", "longitude"])
            if "latitude" not in gpx.columns or np.isnan(gpx["latitude"].mean()) or gpx.empty:
                continue

            folium.PolyLine(
                list(zip(gpx["latitude"], gpx["longitude"])),
                color=triathlon.get_color(d),
                weight=3,
                opacity=0.8,
            ).add_to(trimap)

        # icon = folium.Icon(color='darkblue', icon_color='white', icon='star', angle=0, prefix='fa')
        # icon = folium.DivIcon(html=f"""<div style="color: blue">1</div>""")

        for f in [10, 20, 30, 40, 50, 60, 70]:

            si = triathlon.gpx.index.searchsorted(f)
            if si == len(triathlon.gpx):
                continue
            r = triathlon.gpx.iloc[si]
            folium.Marker(
                location=[r["latitude"], r["longitude"]],
                popup="Ravito",
                icon=folium.DivIcon(html=f"""<div style="color: black; background-color:white">{f}</div>"""),
            ).add_to(marker_cluster)

        for f in triathlon.fuelings:
            si = triathlon.gpx.index.searchsorted(f)
            if si == len(triathlon.gpx):
                continue
            r = triathlon.gpx.iloc[si]
            if np.isnan(r["latitude"] * r["longitude"]):
                continue
            folium.Marker(
                location=[r["latitude"], r["longitude"]],
                popup="Ravito",
                icon=folium.Icon(color="red", icon_color="darkblue", icon="coffee", angle=0, prefix="fa"),
            ).add_to(marker_cluster)
        return trimap

    def show_race_details(triathlon, xaxis="fdistance"):

        # xaxis = st.radio("x axis", ["Total distance", "Expected time of day", "Expected time"], horizontal=True)
        if "Expected time" in xaxis:
            xaxis = "itime"
        else:
            xaxis = "fdistance"

        data = triathlon.data
        data["itime"] = data.dtime.dt.time
        if xaxis in data.columns:
            data = data.set_index(xaxis)

        fuels = data[~data["drinks"].isna()]

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 5), sharex=True, gridspec_kw={"height_ratios": [5, 2]})
        fig.subplots_adjust(hspace=0)
        fig.patch.set_facecolor("#cdcdcd")
        axes[0].set_title(
            f"Parcours fait par {triathlon.athlete.name} pour {triathlon.race.epreuve} ({triathlon.race.longueur})",
            loc="center",
            fontdict={
                "family": "serif",
                "color": "darkred",
                "weight": "normal",
                "size": 16,
            },
        )


        if xaxis == "itime":

            import matplotlib
            import time

            # formatter = matplotlib.ticker.FuncFormatter(lambda ms, x: time.strftime("%M:%S", time.gmtime(ms // 1000)))
            # axes[0].xaxis.set_major_formatter(formatter)

        def plot_ravitos(ax, x, variable):

            pd.plotting.register_matplotlib_converters()
            for i, ravito in fuels.iterrows():
                color = "purple" if "org" in ravito["fooding"] else "darkcyan"
                lw = 4 if "org" in ravito["fooding"] else 4

                ax.vlines(
                    i,
                    ymin=ax.get_ylim()[0],
                    ymax=ravito[variable] + 2,
                    alpha=0.5,
                    lw=lw,
                    color=color,
                )

            ax.grid()
            return fig

        def plot(ax, variable):
            ax.set_facecolor("#cdcdcd")
            for d in range(3):
                ddata = triathlon.get_gpx(d, index=xaxis)
                ddata[variable].plot(
                    color=triathlon.get_color(d),
                    label=f"{triathlon.race.get_discipline(d)} elevation={ddata['elevation'].clip(0, 1000).sum():0.0f} m",
                    ax=ax,
                )

        ax = axes[0]

        plot(ax, "altitude")

        patches = []
        for d in range(3):
            ddata = triathlon.get_gpx(d, index=xaxis)
            label = triathlon.race.get_discipline(d)
            if ddata["elevation"].clip(0, 1000).sum() > 3:
                label += f" (D+={ddata['elevation'].clip(0, 1000).sum():0.0f} m)"

            patches.append(
                Line2D(
                    [0],
                    [0],
                    color=triathlon.get_color(d),
                    lw=4,
                    label=label,
                )
            )

        patches.append(Line2D([0], [0], color="yellow", label=f"Temperature ({data['temperature'].max()} °C)"))
        ax.legend(handles=patches, loc=1, prop={"size": 16})

        cm = LinearSegmentedColormap.from_list("Custom", ["#cdcdcd", "#f08205DD"], N=30)

        ax.pcolorfast(
            ax.get_xlim(),
            ax.get_ylim(),
            data["slope"].clip(3, 60).apply(lambda x: int(2 * round(float(x) / 2))).values[np.newaxis],
            cmap=cm,
        )
        plot_ravitos(ax, xaxis, "altitude")

        ax = axes[1]

        ax.set_facecolor("#cdcdcd")
        data["temperature"].plot(color="yellow", ax=ax)
        ax.fill_between(data.index, data["temperature"] - 1, data["temperature"] + 2, color="yellow", alpha=0.2)
        ax.grid()

        # plot_ravitos(ax, xaxis, "temperature")

    def show_nutrition(triathlon, xaxis="fdistance"):

        """
        Des glucides : pour l’énergie
        Du sodium : quand on transpire, on évacue principalement de l’eau mais aussi du sodium qui aura pour intérêt de favoriser l’absorption intestinale des glucides).

        1% soif
        2% perte 20% perf
        4% dangereux"""

        # xaxis = st.radio("x axis", ["Total distance", "Expected time of day", "Expected time"], horizontal=True)
        if "Expected time" in xaxis:
            xaxis = "itime"
        else:
            xaxis = "fdistance"

        gperf = triathlon.data
        fuels = triathlon.data[~triathlon.data["drinks"].isna()]

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 6), sharex=True)
        fig.subplots_adjust(hspace=0)
        fig.patch.set_facecolor("#cdcdcd")
        axes[0].set_title(
            f"Nutrition fait par {triathlon.athlete.name} pour {triathlon.race.epreuve} ({triathlon.race.longueur})",
            loc="center",
            fontdict={
                "family": "serif",
                "color": "darkred",
                "weight": "normal",
                "size": 16,
            },
        )

        ax = axes[0]
        ax.set_facecolor("#cdcdcd")
        gperf.set_index("fdistance")["kcalories"].cumsum().plot(ax=ax, lw=3, color="purple")
        # ax.hlines(-6000, ymin=triathlon.gpx["altitude"].min(), ymax=triathlon.gpx["altitude"].max(), alpha=0.4, color="red")
        ax.hlines(-6000, xmin=0, xmax=gperf["fdistance"].max(), alpha=0.4, color="red")

        ax.fill_between(
            np.linspace(0, gperf["fdistance"].max(), 50),
            [-6000] * 50,
            [-7000] * 50,
            color="red",
            alpha=0.8,
        )
        ax.text(0.9, -6000 - 500, "Reservoir energetique", fontsize=20)

        ax.grid()

        patches = [
            Line2D([0], [0], color="purple", label=f"kCalories"),
            Line2D([0], [0], color="darkcyan", label=f"Hydratation"),
        ]
        ax.legend(handles=patches, loc=1, prop={"size": 16})

        # ax.legend(loc=9, prop={"size": 20})

        ax = axes[1]
        fig.patch.set_facecolor("#cdcdcd")
        ax.set_facecolor("#cdcdcd")

        ax.fill_between(
            gperf["fdistance"],
            gperf.set_index("fdistance")["ihydration"] * 0,
            gperf.set_index("fdistance")["ihydration"].cumsum(),
            color="green",
            alpha=0.2,
        )
        plt.text(0.9, -500, "Hydratation ideale", fontsize=20)

        gperf.set_index("fdistance")["ihydration"].cumsum().plot(ax=ax, color="green", label="")
        gperf.set_index("fdistance")["hydration"].cumsum().plot(ax=ax, lw=3, color="darkcyan")
        ax.hlines(
            -triathlon.athlete.weight * 0.02 * 1000, xmin=0, xmax=gperf["fdistance"].max(), alpha=0.4, color="red"
        )
        ax.hlines(
            -triathlon.athlete.weight * 0.04 * 1000, xmin=0, xmax=gperf["fdistance"].max(), alpha=0.4, color="red"
        )

        ax.fill_between(
            np.linspace(0, gperf["fdistance"].max(), 50),
            [-triathlon.athlete.weight * 0.02 * 1000] * 50,
            [-triathlon.athlete.weight * 0.04 * 1000] * 50,
            color="red",
            alpha=0.2,
        )
        plt.text(0.9, -triathlon.athlete.weight * 0.02 * 1000 - 500, "Perte de perf 20%", fontsize=20)

        ax.fill_between(
            np.linspace(0, gperf["fdistance"].max(), 50),
            [-triathlon.athlete.weight * 0.04 * 1000] * 50,
            [-triathlon.athlete.weight * 0.05 * 1000] * 50,
            color="red",
            alpha=0.8,
        )
        plt.text(0.9, -triathlon.athlete.weight * 0.04 * 1000 - 500, "Zone de risque", fontsize=20)

        ax.grid()

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
                "food",
            ]
        ].copy()
        ff["Temps de passage"] = ff["dtime"].dt.strftime("%H:%M")
        ff["Bilan hydrique"] = ff["hydration"].fillna(0).cumsum()
        ff["Bilan kcalorique"] = ff["kcalories"].fillna(0).cumsum()
        ff["Depuis depart"] = (60 * ff["duration"].fillna(0)).cumsum().round()

        ff = ff.rename(
            columns={
                "drinks": "Boisson",
                "fooding": "Consommation",
                "food": "Alimentation",
                "temperature": "Temperature",
            }
        )

        # ff["Durée totale"] = pd.to_timedelta(ff["duration"].cumsum(), unit="h")  # .dt.strftime("%H:%M")
        ff["Durée totale"] = (
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            + pd.to_timedelta(ff["duration"].cumsum(), unit="h")
        ).dt.strftime("%H:%M")

        ff = ff[(~ff["Boisson"].isna()) | (ff.index[-1] == ff.index)]

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
            else:
                return ["background-color: white"] * len(s)

        return (
            ff[
                [
                    "Depuis depart",
                    "discipline",
                    "distance",
                    "Consommation",
                    "Boisson",
                    "Alimentation",
                    "Temps de passage",
                    "Bilan hydrique",
                    "Bilan kcalorique",
                    "Durée totale",
                    "Temperature",
                ]
            ]
            .style.hide_index()
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
                    "Bilan hydrique": "{0:.0f} ml",
                    "Bilan kcalorique": "{0:.0f} kcal",
                    "Boisson": "{0:.0f} ml",
                    "Alimentation": "{0:.0f} kcal",
                    "Minutes depuis depart": "{0:.0f} min",
                }
            )
            .bar(color=["Red", "Green"], subset=["Depuis depart"], align="left")
        )
