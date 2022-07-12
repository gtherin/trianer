from . import fueling


class Athlete:
    def __init__(
        self,
        poids,
        natation="2min10s/100m",
        cyclisme="30.0km/h",
        course="5min0s/km",
        transitions="5min",
        name="Athlete",
        sudation="normal",
    ) -> None:
        self.poids = poids  # masse en kilogramme

        self.name = name
        # Extract natation perf
        natation = natation.replace(" ", "").replace("min", ":").replace("s", ":").split(":")
        natation_pace = float(natation[0]) * 60 + float(natation[1]) / 60
        self.natation_speed = 3600 / (10 * natation_pace)

        # Extract natation perf
        self.cyclisme_speed = float(cyclisme.replace(" ", "").replace("k", ":").split(":")[0])

        # Extract natation perf
        course = course.replace(" ", "").replace("min", ":").replace("s", ":").split(":")
        course_pace = float(course[0]) * 60 + float(course[1]) / 60
        self.course_speed = 3600 / course_pace
        self.speeds = {"natation": self.natation_speed, "cyclisme": self.cyclisme_speed, "course": self.course_speed}
        self.dspeeds_slope = {"natation": 0.0, "cyclisme": 2.6, "course": 0.1}

        transitions = float(transitions.replace(" ", "").replace("min", ":").split(":")[0])
        self.transitions = transitions
        self.sudation = sudation

    def calculate_speed(self, df, discipline) -> float:
        df["speed"] = df.apply(lambda x: self.speeds[discipline] - self.dspeeds_slope[discipline] * x["slope"], axis=1)
        return df
