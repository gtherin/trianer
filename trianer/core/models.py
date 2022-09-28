import numpy as np
import pandas as pd

empirical_factor = 0.7


def get_maximum_ideal_hydration(discipline, athlete):
    # Max hydration 700ml man, 600ml woman
    max_hydration = 600 if athlete.is_woman() else 700
    return 0 if discipline == "swimming" else max_hydration


def get_corehydration_vs_temp(temp):
    # -np.clip(temp * 100 - 600, 400, 2500)
    # -np.clip(temp * 70 - 800, 400, 2000)
    return -empirical_factor * np.clip(temp * 100 - 600, 400, 2000)


def get_hydration_vs_temp(discipline, temp):
    if discipline == "cycling":
        return 0.8 * get_corehydration_vs_temp(temp)
    elif discipline == "running":
        return 0.9 * get_corehydration_vs_temp(temp)
    else:
        return -empirical_factor * 500


def get_model_hydration_vs_temp():
    temp = np.arange(0, 40)
    return pd.DataFrame({d: get_hydration_vs_temp(d, temp) for d in ["swimming", "cycling", "running"]})


# Speed models
def get_speed_vs_slope(discipline, flat_speed, slope):
    if discipline == "cycling":
        return np.clip(flat_speed - 2.6 * slope, 5, 50)
    elif discipline == "running":
        return np.clip(flat_speed - 0.2 * slope, 0.6 * flat_speed, 1.3 * flat_speed)
    else:
        return flat_speed


def get_model_speed_vs_slope(cycling=30, running=10, swimming=3.0):
    flat_speeds = {"swimming": swimming, "cycling": cycling, "running": running}
    slopes = np.arange(-30, 30)
    return pd.DataFrame({d: get_speed_vs_slope(d, flat_speeds[d], slopes) for d in ["swimming", "cycling", "running"]})
