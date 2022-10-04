import numpy as np
import matplotlib.pyplot as plt


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


def get_max_heart_rate(age, model=""):
    """
    Calculate your maximum heart rate. The most common way to calculate your maximum heart rate is to subtract your age from 220.[4] If you’re 25 years old, your HRmax = 220 -25 = 195 beats per minute (bpm).
    There is some research that suggests this formula oversimplifies the calculation. You can also estimate your max heart rate with the formula HRmax = 205.8 – (0.685 x age).[5]"""

    if model == "basic":
        return 220 - age
    else:
        return 205.8 - 0.685 * age


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
    plt.scatter([0.4, 0.6, 0.8, 0.85], [0.55, 0.7, 0.85, 0.9], marker="P", s=100.0, label="From webpage")

    hrm = np.linspace(0.4, 1.0, 100)
    vo2m = get_vo2max_from_hr(hrm)

    plt.plot(vo2m, hrm, label="Estimation")
    plt.title("Link between working with % of hr or % of vo2max")
    plt.xlabel("% of HR max")
    plt.ylabel("Relative intensity (%VO2max)")
    plt.legend()
    plt.show()


def show_relative_intensity_vs_running_time():
    running_time = np.linspace(1, 180, 100)
    plt.plot(running_time, 100.0 * get_relative_intensity(running_time), label="% of VO2max")
    plt.hlines(85, 1, 180, label="85% of VO2max")
    plt.title("The percentage of VO2max you can reach depending of the time of the race")
    plt.ylabel("Relative intensity (%VO2max)")
    plt.xlabel("Running time in minutes")
    plt.legend()
    plt.show()


def show_vo2max_vs_speed():

    vo2max = np.linspace(40, 65, 100)

    speed = get_speed_from_vo2max(vo2max)

    plt.plot(speed, vo2max)
    plt.title("The speed you can reach for a given vo2max")
    plt.xlabel("Speed (km/h)")
    plt.ylabel("VO2max (ml/kg/min)")
    plt.show()
