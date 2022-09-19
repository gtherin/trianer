import datetime
import os
from google.cloud import firestore


if os.path.exists("/home/guydegnol/projects/trianer/trianer_db_credentials.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"

from . import gpx


"""

Through a unique systematic approach scientific perspective, the main goal of my job was to extract values from data analyses, to create added value (as research manager). 
The main goal of my job was to extract values from data analyses, to create added value (as research manager). 
Make sure that these systems have the right impact in production.
Leading projects making sure they reach their purpose by adding value to the company.


Why are you interested in designing for subscription growth at Strava? *

Strava has built the biggest sport's community in the world by offering well designed products.
Designing new products are the key to garantee a future subscription growth.

In particular, strava's athletes database built over the years, can play a key role to build new products to improve the custormer experience.
I'll be glad to help strava developing new products and services, and make them available to athletes around the world.
"""


class Race:
    def __init__(self, epreuve=None, longueur=None, cycling_dplus=0, running_dplus=0, disciplines=None) -> None:
        """ """

        self.disciplines = self.get_disciplines()
        if epreuve is not None and "(" in epreuve:
            self.epreuve = epreuve.split(" (")[0]
            self.longueur = epreuve[epreuve.find("(") + 1 : epreuve.find(")")]
        else:
            self.epreuve, self.longueur = epreuve, longueur

        self.elevations = [0, cycling_dplus, running_dplus]

        # Should come with the epreuve
        if disciplines is not None:
            self.distances = longueur
            self.disciplines = disciplines
            self.elevations = []
            for d in disciplines:
                if d == "cycling":
                    self.elevations.append(cycling_dplus)
                elif d == "running":
                    self.elevations.append(running_dplus)
                else:
                    self.elevations.append(0)

        elif self.epreuve in ["swimming", "cycling", "running"]:
            self.distances = [float(self.longueur)]
            self.disciplines = [self.epreuve]
            if self.epreuve == "cycling":
                self.elevations = [cycling_dplus]
            elif self.epreuve == "running":
                self.elevations = [running_dplus]
            else:
                self.elevations = [0]

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

        elif self.longueur == "L":
            self.distances = [1.9, 90, 21.195]
        elif self.longueur == "M":
            self.distances = [1.5, 40, 10]
        elif self.longueur == "S":
            self.distances = [0.65, 20, 5]

    def get_info(self):
        info = ""
        for d in range(len(self.disciplines)):
            info += f"{self.disciplines[d]}: {self.distances[d]}km "
            if self.elevations[d] != 0:
                info += f" (D+={self.elevations[d]}m) "
        return info

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
