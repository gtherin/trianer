import streamlit as st

from . import fueling


class Athlete:
    def __init__(
        self,
        # poids=80,
        # natation="2min10s/100m",
        # course="5min0s/km",
        # transitions="5min",
        name="Athlete",
        sudation="normal",
        config=None,
    ) -> None:

        print("AAAAAAAAAAAA", name, config)
        self.config = config
        self.name = name

        self.poids = self.config["weight"]  # masse en kilogramme

        # Extract natation perf
        natation = self.config["natation"].replace(" ", "").replace("min", ":").replace("s", ":").split(":")
        natation_pace = float(natation[0]) * 60 + float(natation[1]) / 60
        self.natation_speed = 3600 / (10 * natation_pace)

        # Extract natation perf
        self.cyclisme_speed = float(self.config["cyclisme"].replace(" ", "").replace("k", ":").split(":")[0])

        # Extract natation perf
        course = self.config["course"].replace(" ", "").replace("min", ":").replace("s", ":").split(":")
        course_pace = float(course[0]) * 60 + float(course[1]) / 60
        self.course_speed = 3600 / course_pace
        self.speeds = {"natation": self.natation_speed, "cyclisme": self.cyclisme_speed, "course": self.course_speed}
        self.dspeeds_slope = {"natation": 0.0, "cyclisme": 2.6, "course": 0.1}

        self.transition1 = float(self.config["transition1"].replace(" ", "").replace("min", ":").split(":")[0])
        self.transition2 = float(self.config["transition2"].replace(" ", "").replace("min", ":").split(":")[0])

        self.sudation = sudation

    def calculate_speed(self, df, discipline) -> float:
        df["speed"] = df.apply(lambda x: self.speeds[discipline] - self.dspeeds_slope[discipline] * x["slope"], axis=1)
        return df

    def get_nat_pace(self, empirical) -> float:
        return st.metric("Natation, minutes par 100m", self.natation_speed, empirical)
