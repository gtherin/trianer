import datetime
import os
from google.cloud import firestore


if os.path.exists("/home/guydegnol/projects/trianer/trianer_db_credentials.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"

from . import gpx


class Race:
    def __init__(self, epreuve, longueur=None) -> None:

        self.disciplines = self.get_disciplines()
        if "(" in epreuve:
            self.epreuve = epreuve.split(" (")[0]
            self.longueur = epreuve[epreuve.find("(") + 1 : epreuve.find(")")]
        else:
            self.epreuve, self.longueur = epreuve, longueur

        if self.longueur == "L":
            self.distances = [1.9, 90, 21.195]
        elif self.longueur == "M":
            self.distances = [1.5, 40, 10]
        elif self.longueur == "S":
            self.distances = [0.65, 20, 5]

        # Should come with the epreuve
        if self.epreuve in ["swimming", "cycling", "running"]:
            self.distances = [float(self.longueur)]
            self.disciplines = [self.epreuve]

        elif self.epreuve == "Elsassman" and self.longueur == "L":
            self.start_time = datetime.datetime.strptime("2022-07-10 08:00", "%Y-%m-%d %H:%M")
            self.distances = [1.9, 80.3, 20]
            self.elevations = [0, 1366, 306]
            self.options = ["x2", "", "Mx2"]
            self.dfuelings = [[0], [0, 39], [0, 3.25, 6.75]]

        elif self.epreuve == "Deauville" and self.longueur == "L":
            self.start_time = datetime.datetime.strptime("2022-07-10 08:00", "%Y-%m-%d %H:%M")
            self.options = ["x2", "", "Mx2"]
            self.dfuelings = [[0], [0, 43], [0, 3, 7]]

        elif self.epreuve == "Elsassman" and self.longueur == "M":
            self.start_time = datetime.datetime.strptime("2022-07-10 11:15", "%Y-%m-%d %H:%M")
            self.distances = [1.5, 39.6, 10]
            self.elevations = [0, 338, 153]
            self.options = ["x2", "", ""]
            self.dfuelings = [[0], [0, 20.5], [0, 3.25, 6.75]]
        elif self.epreuve == "Elsassman" and self.longueur == "S":
            self.start_time = datetime.datetime.strptime("2022-07-09 10:30", "%Y-%m-%d %H:%M")
            self.distances = [0.65, 23.9, 5.2]
            self.elevations = [0, 9, 0]

    def get_start_time(self):
        return gpx.get_default_datetime()

    def get_discipline(self, d):
        return self.get_disciplines()[d] if type(d) == int else d

    def get_disciplines(self):
        return ["swimming", "cycling", "running"]

    def has_data(self, d):
        return gpx.has_data(self.epreuve, self.longueur, self.get_discipline(d), options=self.get_option(d))

    def get_data(self, d, info_box):
        return gpx.get_data(
            self.epreuve,
            self.longueur,
            self.get_discipline(d),
            options=self.get_option(d),
            info_box=info_box,
        )

    def get_option(self, d):
        if not hasattr(self, "options"):
            return ""
        return self.options[d]

    def get_elevation(self, d):
        if not hasattr(self, "elevation"):
            return 0.0
        return self.elevations[d]

    @staticmethod
    def get_available_races():
        return {
            "Elsassman": {},
            "Deauville": {},
            "Paris": {},
            "Bois-le-Roi": {},
        }

    @staticmethod
    def load_races_configs():
        # info_box.info("Load races from db")
        races_db = firestore.Client().collection("races")
        races_stream = races_db.stream()
        races_configs = {doc.id: doc.to_dict() for doc in races_stream}
        return races_configs
