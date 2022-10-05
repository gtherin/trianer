import datetime


class Athlete:
    def __init__(
        self,
        name="John Doe",
        weight_kg=None,
        swimming_sX100m=None,
        cycling_kmXh=None,
        running_sXkm=None,
        transition_swi2cyc_s=None,
        transition_cyc2run_s=None,
        sudation=None,
        sex=None,
        year_of_birth=None,
        height_cm=None,
        vo2max=None,
    ) -> None:

        self.name = name

        # Masse en kilogramme
        self.weight = weight_kg
        self.speeds, self.paces = {}, {}

        # Extract natation_speed
        self.paces["swimming"] = Athlete.get_pace(swimming_sX100m)
        self.speeds["swimming"] = 3600 / (10 * self.paces["swimming"])

        # Extract cycling_speed
        self.speeds["cycling"] = float(cycling_kmXh)
        self.paces["cycling"] = 3600.0 / self.speeds["cycling"]

        # Extract running_speed
        self.paces["running"] = Athlete.get_pace(running_sXkm)
        self.speeds["running"] = 3600 / self.paces["running"]

        # Global speeds
        self.transitions = [Athlete.get_pace(transition_swi2cyc_s), Athlete.get_pace(transition_cyc2run_s)]

        self.sudation = 1 + 0.1 * (sudation - 5.0)
        self.sex = "F" if sex in ["F", "Female", "Fille", "Femme"] else "M"
        self.height = float(height_cm)
        self.age = datetime.datetime.now().year - float(year_of_birth)
        self.vo2max = vo2max
        self.hrmax = self.get_max_heart_rate()

    @staticmethod
    def get_pace(pace):
        if type(pace) == str:
            swimming_pace = pace.split(":")
            return float(swimming_pace[0]) * 60 + float(swimming_pace[1]) / 60
        else:
            return float(pace.hour) * 60 + float(pace.minute) / 60

    def get_dinfo(self, discispline):
        return self.speeds[discispline.lower()], self.paces[discispline.lower()]

    def is_woman(self):
        return self.sex == "F"

    def get_max_heart_rate(self, model=""):
        """
        Calculate your maximum heart rate. The most common way to calculate your maximum heart rate is to subtract your age from 220.[4] If you’re 25 years old, your HRmax = 220 -25 = 195 beats per minute (bpm).
        There is some research that suggests this formula oversimplifies the calculation. You can also estimate your max heart rate with the formula HRmax = 205.8 – (0.685 x age).[5]"""

        if model == "basic":
            return 220 - self.age
        else:
            return 205.8 - 0.685 * self.age
