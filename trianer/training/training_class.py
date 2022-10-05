import numpy as np
import matplotlib.pyplot as plt

from . import running_economy as re
from ..core import theme
from .hermann import Hermann


class Training:
    def __init__(self, athlete, race, target) -> None:
        self.athlete, self.race, self.target = athlete, race, target

    def show_speed_vs_duration(self, tmax=300):
        """
        3 5 10 15 20 30 42.195
        13:30 23:40 50:58 1:20:03 1:50:27 2:54:15 4:16:20
        """
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 6))
        running_time = np.linspace(1, tmax, 100)
        sherm = [Hermann.smooth_clip(self.athlete.vo2max, t) for t in running_time]
        vma = sherm[0]

        plt.hlines(vma, 1, tmax, label=f"VMA: {vma:.1f} km/h", color=theme.get_color("cycling"))

        ax.plot(running_time, sherm, label="Max Speed (Hermann)", color=theme.get_color("swimming"))
        # Hermann value is the aerobic limit
        # relative_intensity = np.clip(relative_intensity, 0, herm.max())

        plt.hlines(
            vma * 0.85,
            1,
            tmax,
            label=f"85%VMA: {.85*vma:.1f} km/h (Elite effic.)",
            color=theme.get_color("running"),
            ls="dashed",
        )
        plt.fill_between(
            np.linspace(1, tmax, 100),
            [vma] * 100,
            [vma * 0.9] * 100,
            color=theme.danger_color,
            alpha=0.2,
        )
        plt.fill_between(
            np.linspace(1, tmax, 100),
            [vma * 0.75] * 100,
            [vma * 0.7] * 100,
            color=theme.danger_color,
            alpha=0.2,
        )

        plt.hlines(
            vma * 0.725,
            1,
            tmax,
            label=f"60%-VMA: {.6*vma:.1f} km/h",
            color=theme.get_color("swimming"),
            ls="dotted",
        )
        plt.title("Average speed estimation versus duration of the race")
        plt.ylabel("Estimated speed (km/h)")
        plt.xlabel("Running time in minutes")
        plt.legend()

        plt.show()

    def show_pace_vs_percentage(self):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 6))
        per = np.linspace(0.5, 1.0, 100)
        vma = Hermann.smooth_clip(self.athlete.vo2max, 0)

        speed = per * vma

        ax.plot(per, speed, label="% of VO2 max")
        perhr = re.get_hr_from_vo2max(per)

        ax.plot(perhr, speed, label="% of hr max")
        plt.title("Speed versus %hrmax and %vo2max")
        plt.xlabel("Percentage")
        plt.ylabel("Speed (km/h)")
        plt.legend()
        plt.show()
