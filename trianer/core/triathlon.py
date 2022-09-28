from curses.textpad import rectangle
import datetime
import numpy as np
import pandas as pd
import logging

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib
import time
import sys


from ..race import weather
from .. import nutrition
from ..core import models
from ..core.labels import gl, gc


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
            df["speed"] = models.get_speed_vs_slope(discipline, athlete.speeds[discipline], df["slope"])

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

    def show_race_details(triathlon, xaxis="fdistance", yaxis="altitude"):

        data = triathlon.data
        # data["cspeed"] = data["duration"].cumsum()
        xaxis = triathlon.get_axis(xaxis)
        yaxis = triathlon.get_axis(yaxis)

        if xaxis in data.columns:
            data = data.set_index(xaxis)

        print(xaxis, yaxis)
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

        triathlon.plot_core(data, ax, yaxis)
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

        if xaxis == "fdistance" or 1:
            # TODO: Fix it with other axis
            cm = LinearSegmentedColormap.from_list("Custom", ["#cdcdcd", "#f08205DD"], N=30)
            ax.set_xlim([data.index[0], data.index[-1]])

            if "etime" == xaxis:
                dd = pd.DataFrame(np.arange(data.index[0], data.index[-1], 1.0 / 3600), columns=[xaxis])
            elif "time" in xaxis:
                dd = pd.date_range(start=data.index[0], end=data.index[-1], freq="s").to_frame(name=xaxis)
            else:
                dd = pd.DataFrame(np.arange(data.index[0], data.index[-1], 0.5), columns=[xaxis])
            dd = pd.merge_asof(dd, data[["slope"]].reset_index(), on=xaxis, direction="forward")

            ax.pcolorfast(
                ax.get_xlim(),
                ax.get_ylim(),
                [dd["slope"].clip(3, 60).values],
                cmap=cm,
                vmin=5,
            )
        # plot ravitos
        Triathlon.plot_ravitos(fuels, ax, xaxis, yaxis)
        ax.set_xlabel(xlabel=gl(xaxis, u=True))
        ax.set_ylabel(ylabel=gl(yaxis, u=True))

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
        ax.set_ylabel(ylabel=gl("temperature", u=True))
        ax.set_xlabel(xlabel=gl(xaxis, u=True))

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

    def plot_core(self, data, ax, variable):
        ax.set_facecolor("#cdcdcd")
        for discipline in self.race.disciplines:
            ddata = self.get_gpx(data, discipline)
            ddata[variable].plot(
                color=self.get_color(discipline),
                label=f"{discipline} D+={ddata['aelevation'].sum():0.0f} m",
                ax=ax,
            )

    @staticmethod
    def get_axis(axis):
        xaxis = gc(axis)

        if "time" in xaxis.lower() and "day" in xaxis.lower():
            return "dtime"
        elif "time" in xaxis.lower():
            return "etime"
        elif "altitude" in xaxis.lower():
            return "altitude"
        elif "speed" in xaxis.lower():
            return "speed"
        elif "slope" in xaxis.lower():
            return "slope"
        else:
            return "fdistance"

    def show_nutrition(triathlon, xaxis="fdistance"):

        data = triathlon.data
        # data["etime"] = data["duration"].cumsum()
        xaxis = triathlon.get_axis(xaxis)

        if xaxis in data.columns:
            data = data.set_index(xaxis)

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

        ax.set_xlim([data.index[0], data.index[-1]])
        xmin, xmax = ax.get_xlim()
        caloric_reserve = nutrition.get_caloric_reserve(triathlon.athlete)
        ax.hlines(-caloric_reserve, xmin=xmin, xmax=xmax, alpha=0.4, color="red")

        ax.fill_between(
            np.linspace(xmin, xmax, 50),
            [-caloric_reserve] * 50,
            [-caloric_reserve - 1000] * 50,
            color="red",
            alpha=0.8,
        )

        # xtext = xmin + 0.1 * (xmax - xmin)
        # ax.text(xtext, -caloric_reserve, gl("caloric_reserve"), fontsize=20)

        ax.grid()

        # drinks = data["drinks"].sum()
        # food = data["food"].sum()

        patches = [
            Line2D([0], [0], color="purple", label=gl("caloric_balance", u=True)),
            Line2D([0], [0], color="darkcyan", label=gl("hydric_balance", u=True)),
            Patch(facecolor="red", edgecolor="r", label=gl("caloric_balance", u=True)),
        ]
        ax.legend(handles=patches, prop={"size": 16}, framealpha=0)  # , loc=6
        ax.set_ylabel(ylabel=gl("caloric_balance", u=True))

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
        # plt.text(xtext, -500, gl("hydration_ideal"), fontsize=20)

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
        # plt.text(xtext, -triathlon.athlete.weight * 0.02 * 1000 - 500, gl("perf_loss_20"), fontsize=20)

        ax.fill_between(
            np.linspace(xmin, xmax, 50),
            [-triathlon.athlete.weight * 0.04 * 1000] * 50,
            [-triathlon.athlete.weight * 0.05 * 1000] * 50,
            color="red",
            alpha=0.8,
        )
        # plt.text(xtext, -triathlon.athlete.weight * 0.04 * 1000 - 500, gl("risk_zone"), fontsize=20)

        ax.grid()
        if xaxis == "etime":
            formatter = matplotlib.ticker.FuncFormatter(lambda ms, x: time.strftime("%H:%M", time.gmtime(ms * 3600)))
            ax.xaxis.set_major_formatter(formatter)
        if xaxis == "dtime":
            formatter = matplotlib.ticker.FuncFormatter(
                lambda ms, x: time.strftime("%H:%M", time.gmtime((ms % 1) * 24 * 3600))
            )
            ax.xaxis.set_major_formatter(formatter)

        patches = [
            Line2D([0], [0], color="green", label=gl("hydration_ideal", u=True)),
            Patch(facecolor="red", edgecolor="r", label=gl("risk_zone", u=True), alpha=0.2),
            Patch(facecolor="red", edgecolor="r", label=gl("perf_loss_20", u=True), alpha=0.8),
        ]
        ax.legend(handles=patches, prop={"size": 16}, framealpha=0)  # , loc=6
        ax.set_ylabel(ylabel=gl("hydric_balance", u=True))
        ax.set_xlabel(xlabel=gl(xaxis, u=True))
