import datetime
import numpy as np
import pandas as pd
import logging

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import matplotlib
import time
import sys


from ..race import weather
from .. import nutrition
from ..core.labels import gl

logging.getLogger("matplotlib.font_manager").disabled = True
logging.getLogger("matplotlib").setLevel(logging.ERROR)
pd.plotting.register_matplotlib_converters()


def is_kernel():
    if "IPython" not in sys.modules:
        # IPython hasn't been imported, definitely not
        return False
    from IPython import get_ipython

    # check for `kernel` attribute on the IPython instance
    return getattr(get_ipython(), "kernel", None) is not None


class Triathlon:
    def __init__(self, race=None, athlete=None, temperature=None) -> None:
        self.race, self.athlete = race, athlete
        self.gpx = self.race.get_gpx_data()

        self.data = self.simulate_race(self.race, self.athlete, temperature=temperature)

    def get_mean_coordonates(self, use_map=False):
        coordonates = self.race.get_param("weather_coordonates")
        if coordonates and not use_map:
            return coordonates
        if "latitude" not in self.gpx.columns and not use_map:
            return weather.get_default_coordonates()[:2]
        return self.gpx.latitude.mean(), self.gpx.longitude.mean()

    def get_temperature(self):
        return weather.get_forecasts(coordonates=self.get_mean_coordonates())

    def get_gpx(self, data, discipline):
        if discipline is None:
            return data

        data = data.query(f"discipline=='{discipline}'")

        # No cleaning for swimming data (points might be too far)
        if discipline == "swimming":
            return data

        # Try to clean gpx tracks
        d = data.distance.clip(0, 1000).diff()
        cutoff = d.mean() * 3
        data = data[d < cutoff]

        return data

    def get_color(self, discipline):
        colors = {"swimming": "blue", "cycling": "brown", "running": "green"}
        return colors[discipline]

    def simulate_race(self, race, athlete, temperature=None):

        data = []

        for c in ["temperature", "hr", "hydration", "kcalories", "speed", "dtime"]:
            if c in self.gpx.columns:
                del self.gpx[c]

        for d, discipline in enumerate(race.disciplines):
            df = self.gpx.query(f"discipline=='{discipline}'").copy()
            # Speed km/h
            df = athlete.calculate_speed(df, discipline)
            # Duration between 2 points in hour
            df["duration"] = (df["distance"].diff().clip(0, 1000) / df["speed"]).fillna(0)

            if d < len(race.disciplines) - 1:
                transition = df.iloc[-1].to_dict()

                transition.update(
                    {
                        "slope": 0.0,
                        "speed": 0.0,
                        "hydration": 0.0,
                        "discipline": f"transition {d+1}",
                        "sequence": 2 * d + 1,
                        "duration": athlete.transitions[d] / 3600.0,
                    }
                )
                df = pd.concat([df, pd.DataFrame.from_records([transition])], ignore_index=True)

            data.append(df)

        data = pd.concat(data).sort_values(["sequence", "distance", "duration"])
        data.index = range(len(data))

        data["dtime"] = race.start_time + pd.to_timedelta(data["duration"].cumsum(), unit="h")

        # Set temperature
        data = weather.merge_temperature_forecasts(
            data, coordonates=self.get_mean_coordonates(), start_time=race.start_time, temperature=temperature
        )

        data["fdistance"] = data["distance"].diff().clip(0, 10000).fillna(0.0).cumsum()
        for f in [nutrition.calculate_hydration, nutrition.calculate_kcalories, nutrition.calculate_fuelings]:
            data = f(data, race, athlete)

        return data

    def show_weather_forecasts(self):
        return f"The expected temperature is {self.get_temperature()} °C"

    def show_race_details(triathlon, xaxis="fdistance", fields="altitude,temperature"):

        data = triathlon.data
        data["etime"] = data["duration"].cumsum()
        xaxis = triathlon.get_axis(xaxis)

        if xaxis in data.columns:
            data = data.set_index(xaxis)

        fuels = data[~data["drinks"].isna()]

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 5), sharex=True, gridspec_kw={"height_ratios": [5, 2]})
        fig.subplots_adjust(hspace=0)
        fig.patch.set_facecolor("#cdcdcd")
        axes[0].set_title(
            triathlon.race.get_info(),
            loc="center",
            fontdict={"family": "serif", "color": "darkred", "weight": "normal", "size": 16},
        )

        ax = axes[0]

        triathlon.plot_core(data, ax, "altitude", xaxis)

        if 1:
            patches = []
            for discipline in triathlon.race.disciplines:
                ddata = triathlon.get_gpx(data, discipline)
                label = discipline
                duration = ddata["duration"].sum()
                duration = ", t=%.0fmin." % (duration * 60)
                label += duration
                if ddata["aelevation"].sum() > 3:
                    label += f", D+={ddata['aelevation'].sum():0.0f}m"

                patches.append(Line2D([0], [0], color=triathlon.get_color(discipline), lw=4, label=label))
            patches.append(Line2D([0], [0], color="yellow", label=f"temperature, max={data['temperature'].max()}°C"))
            ax.legend(handles=patches, prop={"size": 16}, framealpha=0)  # , loc=2

        if xaxis == "fdistance":
            # TODO: Fix it with other axis
            cm = LinearSegmentedColormap.from_list("Custom", ["#cdcdcd", "#f08205DD"], N=30)

            ax.pcolorfast(
                ax.get_xlim(),
                ax.get_ylim(),
                data["slope"].clip(3, 60).apply(lambda x: int(2 * round(float(x) / 2))).values[np.newaxis],
                cmap=cm,
            )
        Triathlon.plot_ravitos(fuels, ax, xaxis, "altitude")
        ax.set_xlabel(xlabel=gl(xaxis))
        ax.set_ylabel(ylabel="Elevation (m)")

        ax = axes[1]

        ax.set_facecolor("#cdcdcd")
        data["temperature"].plot(color="yellow", ax=ax)
        ax.fill_between(data.index, data["temperature"] - 1, data["temperature"] + 2, color="yellow", alpha=0.2)
        ax.grid()
        if xaxis == "etime":
            formatter = matplotlib.ticker.FuncFormatter(lambda ms, x: time.strftime("%H:%M", time.gmtime(ms * 3600)))
            ax.xaxis.set_major_formatter(formatter)
        if xaxis == "dtime":
            formatter = matplotlib.ticker.FuncFormatter(
                lambda ms, x: time.strftime("%H:%M", time.gmtime((ms % 1) * 24 * 3600))
            )
            ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel(ylabel="Temperature (°C)")
        ax.set_xlabel(xlabel=gl(xaxis))

    @staticmethod
    def plot_ravitos(fuels, ax, x, variable):

        ymin = ax.get_ylim()[0]

        for i, ravito in fuels.iterrows():
            color = "purple" if "org" in ravito["fooding"] else "darkcyan"
            lw = 4 if "org" in ravito["fooding"] else 4

            ax.vlines(
                i,
                ymin=ymin,
                ymax=ravito[variable] + 2,
                alpha=0.5,
                lw=lw,
                color=color,
            )

        ax.grid()

    def plot_core(self, data, ax, variable, xaxis):
        ax.set_facecolor("#cdcdcd")
        for discipline in self.race.disciplines:
            ddata = self.get_gpx(data, discipline)
            ddata[variable].plot(
                color=self.get_color(discipline),
                label=f"{discipline} D+={ddata['aelevation'].sum():0.0f} m",
                ax=ax,
            )

    @staticmethod
    def get_axis(xaxis):
        if "time" in xaxis.lower() and "day" in xaxis.lower():
            return "dtime"
        elif "ime" in xaxis.lower():
            return "etime"
        else:
            return "fdistance"

    def show_nutrition(triathlon, xaxis="fdistance"):

        data = triathlon.data
        data["etime"] = data["duration"].cumsum()
        xaxis = triathlon.get_axis(xaxis)

        if xaxis in data.columns:
            data = data.set_index(xaxis)

        fuels = data[~data["drinks"].isna()]

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 6), sharex=True)
        fig.subplots_adjust(hspace=0)
        fig.patch.set_facecolor("#cdcdcd")
        axes[0].set_title(
            triathlon.race.get_info(),
            loc="center",
            fontdict={"family": "serif", "color": "darkred", "weight": "normal", "size": 16},
        )

        ax = axes[0]
        ax.set_facecolor("#cdcdcd")
        data["kcalories"].cumsum().plot(ax=ax, lw=3, color="purple")

        xmin, xmax = ax.get_xlim()
        ax.hlines(-6000, xmin=xmin, xmax=xmax, alpha=0.4, color="red")

        ax.fill_between(
            np.linspace(xmin, xmax, 50),
            [-6000] * 50,
            [-7000] * 50,
            color="red",
            alpha=0.8,
        )

        xtext = xmin + 0.1 * (xmax - xmin)
        ax.text(xtext, -nutrition.get_caloric_reserve(triathlon.athlete), gl("caloric_reserve"), fontsize=20)

        ax.grid()

        patches = [
            Line2D([0], [0], color="purple", label=gl("caloric_balance")),
            Line2D([0], [0], color="darkcyan", label=gl("hydric_balance")),
        ]
        ax.legend(handles=patches, prop={"size": 16}, framealpha=0)  # , loc=6
        ax.set_ylabel(ylabel=gl("caloric_balance") + " (kcal)")

        ax = axes[1]
        fig.patch.set_facecolor("#cdcdcd")
        ax.set_facecolor("#cdcdcd")

        ax.fill_between(
            data.index,
            data["ihydration"] * 0,
            data["ihydration"].cumsum(),
            color="green",
            alpha=0.2,
        )
        plt.text(xtext, -500, gl("hydration_ideal"), fontsize=20)

        data["ihydration"].cumsum().plot(ax=ax, color="green", label="")
        data["hydration"].cumsum().plot(ax=ax, lw=3, color="darkcyan")

        ax.hlines(
            -nutrition.get_hydric_reserve(triathlon.athlete),
            xmin=xmin,
            xmax=xmax,
            alpha=0.4,
            color="red",
        )
        ax.hlines(
            -nutrition.get_hydric_reserve(triathlon.athlete, danger=True),
            xmin=xmin,
            xmax=xmax,
            alpha=0.4,
            color="red",
        )

        ax.fill_between(
            np.linspace(xmin, xmax, 50),
            [-triathlon.athlete.weight * 0.02 * 1000] * 50,
            [-triathlon.athlete.weight * 0.04 * 1000] * 50,
            color="red",
            alpha=0.2,
        )
        plt.text(xtext, -triathlon.athlete.weight * 0.02 * 1000 - 500, gl("perf_loss_20"), fontsize=20)

        ax.fill_between(
            np.linspace(xmin, xmax, 50),
            [-triathlon.athlete.weight * 0.04 * 1000] * 50,
            [-triathlon.athlete.weight * 0.05 * 1000] * 50,
            color="red",
            alpha=0.8,
        )
        plt.text(xtext, -triathlon.athlete.weight * 0.04 * 1000 - 500, gl("risk_zone"), fontsize=20)

        ax.grid()
        if xaxis == "etime":
            formatter = matplotlib.ticker.FuncFormatter(lambda ms, x: time.strftime("%H:%M", time.gmtime(ms * 3600)))
            ax.xaxis.set_major_formatter(formatter)
        if xaxis == "dtime":
            formatter = matplotlib.ticker.FuncFormatter(
                lambda ms, x: time.strftime("%H:%M", time.gmtime((ms % 1) * 24 * 3600))
            )
            ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel(ylabel=gl("hydric_balance") + " (ml)")
        ax.set_xlabel(xlabel=gl(xaxis))

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
