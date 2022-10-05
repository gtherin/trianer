import numpy as np
import matplotlib.pyplot as plt

from ..core import theme
from ..core import tools
from ..core.labels import gl

from .hermann import get_hermann, Hermann


def get_speed_from_vo2max(vo2max):
    # from https://www.cairn.info/revue-staps-2001-1-page-45.htm figure 1
    # TODO: Find better alternative
    return (vo2max - 43) * 0.27 + 14


def get_speed_from_hr(hr_frac):
    vo2max = get_vo2max()
    vo2_frac = get_vo2max_from_hr(0.01 * hr_frac)
    return get_speed_from_vo2max(vo2max * vo2_frac)


def get_vo2max_from_hr(hr):
    """
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4555089/

    ACSM suggest that
    40% VO2 max corresponds to 55% HR max,
    60% VO2 max corresponds to 70% HR max,
    80% VO2 max corresponds to 85% HR max
    85% VO2 max corresponds to 90% HR max
    """
    # from
    # TODO: Find better alternative
    return (hr - 0.23) / 0.78


def get_hr_from_vo2max(vo2m):
    return 0.78 * vo2m + 0.23


def get_maxspeed_for_duration(vo2max, duration):
    return get_relative_intensity(duration) * get_speed_from_vo2max(vo2max)


def get_relative_intensity(running_time_in_minutes):
    # Doit etre utilisé comme reference pour la vitesse maximale accessible pour un certain temps
    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4555089/ figure 3
    # The 130 clip value is a reasonable guess
    # TODO: It probably can be measured looking at data
    """
    Running time should be in minutes
    # 15: 98, 30: 93, 45: 90, 60: 88
    """
    return 0.01 * np.clip(200 / running_time_in_minutes + 85, 50, 110)


def get_vo2max():
    # TODO: Extract it from athlete's data
    return 50


def show_perhrmax_vs_pervo2max():
    plt.scatter(
        [0.4, 0.6, 0.8, 0.85],
        [0.55, 0.7, 0.85, 0.9],
        marker="P",
        s=100.0,
        label="From observation",
        color=theme.get_color("running"),
        zorder=10,
    )

    hrm = np.linspace(0.4, 1.0, 100)
    vo2m = get_vo2max_from_hr(hrm)

    plt.plot(vo2m, hrm, label="Estimation")
    plt.title("Link between %hr or %vo2max")
    plt.xlabel("% of HR max")
    plt.ylabel("Relative intensity (%VO2max)")
    plt.legend()

    filename = tools.get_file("perhrmax_vs_pervo2max.png", read=False, write=False)
    print(f"Write in {filename}")
    plt.savefig(filename)

    plt.show()


def show_relative_intensity_vs_running_time(tmax=300):
    """
    3 5 10 15 20 30 42.195
    13:30 23:40 50:58 1:20:03 1:50:27 2:54:15 4:16:20
    """

    running_time = np.linspace(1, tmax, 100)
    relative_intensity = 100.0 * get_relative_intensity(running_time)

    plt.plot(running_time, relative_intensity, label="% of VO2max")
    plt.hlines(100.0 * 0.85, 1, tmax, label="85% of VO2max", color=theme.get_color("running"))
    plt.title("%VO2max you can reach versus duration of the race")
    plt.ylabel("Relative intensity (%VO2max)")

    plt.xlabel("Running time in minutes")
    plt.legend()

    filename = tools.get_file("relative_intensity_vs_running_time.png", read=False, write=False)
    print(f"Write in {filename}")
    plt.savefig(filename)
    plt.show()


def show_vo2max_vs_speed():

    vo2max = np.linspace(40, 65, 100)
    speed = get_speed_from_vo2max(vo2max)

    plt.plot(speed, vo2max)
    plt.title(gl(en="Reachable speed for a given vo2max"))
    plt.xlabel("Speed (km/h)")
    plt.ylabel("VO2max (ml/kg/min)")

    filename = tools.get_file("vo2max_vs_speed.png", read=False, write=False)
    print(f"Write in {filename}")
    plt.savefig(filename)
    plt.show()
