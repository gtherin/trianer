import datetime
import os
from google.cloud import firestore


if os.path.exists("/home/guydegnol/projects/trianer/trianer_db_credentials.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"

from . import gpx
from .races import races


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
    def __init__(self, name=None, cycling_dplus=0, running_dplus=0) -> None:

        # Init epreuve and longueur
        self.init_epreuve_and_longueur(name, cycling_dplus, running_dplus)

        self.disciplines = ["swimming", "cycling", "running"]
        self.distances = []
        self.elevations = []
        self.options = ["", "", ""]
        self.start_time = gpx.get_default_datetime()

        if name[0] == ",":
            self.init_from_string(name)
        elif name in races:
            self.init_from_race(name)

        self.init_elevations()

    def init_from_string(self, name) -> None:
        self.name = name
        self.longueur = None
        self.title = "Personalized"

        disciplines = name[1:].split(",")
        for e in disciplines:
            d = e.split(":")
            self.disciplines.append(d[0])
            self.distances.append(float(d[1]))
            self.elevations.append(float(d[2]) if len(d) > 2 else 0.0)

    @staticmethod
    def init_from_cookies(cookies_source):
        race_perso = ""

        pdisciplines = cookies_source("disciplines")
        for d in pdisciplines:
            race_perso += f",{d}:" + str(cookies_source(f"{d}_lengh"))
            if d in ["cycling", "running"]:
                dplus = cookies_source(f"p{d}_dplus")
                race_perso += f":{dplus}"
        return Race(race_perso)

    def init_from_race(self, name) -> None:
        race = races[name]
        for k in ["start_time", "distances", "elevations", "options", "dfuelings"]:
            if k in race:
                setattr(self, k, race[k])

    def init_epreuve_and_longueur(self, epreuve, cycling_dplus, running_dplus) -> None:
        if epreuve is not None and "(" in epreuve:
            self.epreuve = epreuve.split(" (")[0]
            self.longueur = epreuve[epreuve.find("(") + 1 : epreuve.find(")")]
        else:
            self.epreuve, self.longueur = epreuve, None
        self.title = epreuve
        self.ielevations = {"swimming": 0, "cycling": cycling_dplus, "running": running_dplus}

    def init_elevations(self) -> None:
        if not self.elevations:
            self.elevations = [self.ielevations[d] for d in self.disciplines]

    def get_info(self):
        info = f"{self.title} "
        for d in range(len(self.disciplines)):
            info += f"{self.disciplines[d]}: {self.distances[d]}km "
            if self.elevations[d] != 0:
                info += f" (D+={self.elevations[d]:.0f}m) "
        return info

    def get_key(self):
        race_perso = ""
        for d, di in enumerate(self.disciplines):
            race_perso += f",{di}:{self.distances[d]}"
            if self.elevations[d] != 0:
                race_perso += f":{self.elevations[d]:.0f}"
        return race_perso[1:]

    def get_start_time(self):
        return self.start_time

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
