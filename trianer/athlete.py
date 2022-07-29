import streamlit as st

from . import fueling


class Athlete:
    def __init__(
        self,
        name="Athlete",
        sudation="normal",
        config=None,
    ) -> None:

        self.config = config
        self.name = name

        # Masse en kilogramme
        self.weight = self.config["weight_kg"]

        # Extract natation_speed
        swimming_pace = (
            float(self.config["swimming_sX100m"].hour) * 60 + float(self.config["swimming_sX100m"].minute) / 60
        )
        self.swimming_speed = 3600 / (10 * swimming_pace)

        # Extract cycling_speed
        self.cycling_speed = float(self.config["cycling_kmXh"])

        # Extract running_speed
        running_pace = float(self.config["running_sXkm"].hour) * 60 + float(self.config["running_sXkm"].minute) / 60
        self.running_speed = 3600 / running_pace

        # Global speeds
        self.speeds = {
            "natation": self.swimming_speed,
            "cyclisme": self.cycling_speed,
            "course": self.running_speed,
        }
        self.dspeeds_slope = {"natation": 0.0, "cyclisme": 2.6, "course": 0.1}

        self.transition1 = (
            float(self.config["transition_cyc2run_s"].hour) * 60
            + float(self.config["transition_cyc2run_s"].minute) / 60
        )
        self.transition2 = (
            float(self.config["transition_swi2cyc_s"].hour) * 60
            + float(self.config["transition_swi2cyc_s"].minute) / 60
        )

        self.sudation = sudation

    def calculate_speed(self, df, discipline) -> float:
        df["speed"] = df.apply(lambda x: self.speeds[discipline] - self.dspeeds_slope[discipline] * x["slope"], axis=1)
        return df

    def get_nat_pace(self, empirical) -> float:
        return st.metric("Natation, minutes par 100m", self.natation_speed, empirical)
