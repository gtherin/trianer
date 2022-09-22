class Athlete:
    def __init__(
        self,
        name="John Doe",
        sudation=1.0,
        config=None,
    ) -> None:

        self.config = config
        self.name = name

        # Masse en kilogramme
        self.weight = self.config["weight_kg"]

        # Extract natation_speed
        self.swimming_pace = Athlete.get_pace(self.config["swimming_sX100m"])
        self.swimming_speed = 3600 / (10 * self.swimming_pace)

        # Extract cycling_speed
        self.cycling_speed = float(self.config["cycling_kmXh"])
        self.cycling_pace = 3600.0 / self.cycling_speed

        # Extract running_speed
        self.running_pace = Athlete.get_pace(self.config["running_sXkm"])
        self.running_speed = 3600 / self.running_pace

        # Global speeds
        self.speeds = {"swimming": self.swimming_speed, "cycling": self.cycling_speed, "running": self.running_speed}
        self.dspeeds_slope = {"swimming": 0.0, "cycling": 2.6, "running": 0.1}

        self.transitions = [Athlete.get_pace(self.config[k]) for k in ["transition_swi2cyc_s", "transition_cyc2run_s"]]

        self.sudation = sudation

    def calculate_speed(self, df, discipline) -> float:
        df["speed"] = df.apply(lambda x: self.speeds[discipline] - self.dspeeds_slope[discipline] * x["slope"], axis=1)
        return df

    @staticmethod
    def get_pace(pace):
        if type(pace) == str:
            swimming_pace = pace.split(":")
            return float(swimming_pace[0]) * 60 + float(swimming_pace[1]) / 60
        else:
            return float(pace.hour) * 60 + float(pace.minute) / 60
