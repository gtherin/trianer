import numpy as np
import pandas as pd
import os
from google.cloud import firestore


if os.path.exists("/home/guydegnol/projects/trianer/trianer_db_credentials.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"

from . import gpx
from .races import available_races
from ..core.labels import gl


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
        self.init_basic(name, cycling_dplus, running_dplus)

        if name in available_races.keys():
            self.init_from_race(name)
        else:
            self.init_from_string(name)

        self.init_elevations()
        self.init_fuelings(name)

    def init_from_string(self, name) -> None:
        self.longueur = None
        self.title = "Personalized"

        disciplines = name.split(",")
        for e in disciplines:
            d = e.split(":")
            self.disciplines.append(d[0])
            self.distances.append(float(d[1]))
            self.elevations.append(float(d[2]) if len(d) > 2 else 0.0)

    @staticmethod
    def init_from_cookies(cookies_source):
        race_perso = ""
        disciplines = cookies_source("disciplines")
        for d in disciplines:
            race_perso += f",{d}:" + str(cookies_source(f"{d}_lengh"))
            if d in ["cycling", "running"]:
                dplus = cookies_source(f"p{d}_dplus")
                race_perso += f":{dplus}"
        return Race(race_perso[1:])

    def get_key(self):
        race_perso = ""
        for d, di in enumerate(self.disciplines):
            race_perso += f",{di}:{self.distances[d]}"
            if self.elevations[d] != 0:
                race_perso += f":{self.elevations[d]:.0f}"
        return race_perso[1:]

    def init_from_race(self, name) -> None:
        self.disciplines = ["swimming", "cycling", "running"]
        for k in ["disciplines", "start_time", "distances", "elevations", "gpx_data", "comments"]:
            if k in available_races[name]:
                setattr(self, k, available_races[name][k])
        if not getattr(self, "distances"):
            self.distances = available_races["Triathlon (M)"]["distances"]

    def get_param(self, k):
        if self.name in available_races and k in available_races[self.name]:
            return available_races[self.name][k]
        return None

    def init_fuelings(self, name) -> None:
        if (
            name not in available_races
            or "dfuelings" not in available_races[name]
            or "gpx_data" not in available_races[name]
        ):
            self.dfuelings = [[0.0] for _ in self.disciplines]
        else:
            self.dfuelings = [[] for _ in self.disciplines]
            immutable_fuelings = available_races[name]["dfuelings"].copy()
            for d, discipline in enumerate(self.disciplines):

                gpx_info = self.gpx_data[d].split(",x")
                nlaps = 1 if len(gpx_info) == 1 or discipline == "swimming" else int(gpx_info[1])

                for l in range(nlaps):
                    self.dfuelings[d] += [self.distances[d] * float(l) / nlaps + f for f in immutable_fuelings[d]]

    def init_basic(self, epreuve, cycling_dplus, running_dplus) -> None:
        self.name = epreuve
        if epreuve is not None and "(" in epreuve:
            self.epreuve = epreuve.split(" (")[0]
            self.longueur = epreuve[epreuve.find("(") + 1 : epreuve.find(")")]
        else:
            self.epreuve, self.longueur = epreuve, None
        self.title = epreuve

        self.disciplines, self.distances, self.elevations = [], [], []
        self.ielevations = {"swimming": 0, "cycling": cycling_dplus, "running": running_dplus}
        self.gpx_data = ["", "", ""]
        self.start_time = gpx.get_default_datetime()

    def init_elevations(self) -> None:
        if not self.elevations:
            self.elevations = [self.ielevations[d] for d in self.disciplines]

    def get_info(self):
        info = f"{self.title} "
        for d in range(len(self.disciplines)):
            info += f"{gl(self.disciplines[d])}: {self.distances[d]}km "
            if self.elevations[d] != 0:
                info += f" (D+={self.elevations[d]:.0f}m) "
        return info

    def get_dinfo(self, discipline):
        dist, deniv = 0.0, 0.0
        for d in range(len(self.disciplines)):
            if discipline.lower() == self.disciplines[d] or discipline.lower() == "total":
                dist += self.distances[d]
                deniv += self.elevations[d]
        return dist, deniv

    def get_fuels(self):
        return {discipline: self.dfuelings[d] for d, discipline in enumerate(self.disciplines)}

    def get_gpx_data(self):
        data = []
        self.fuelings = [0]

        for d, discipline in enumerate(self.disciplines):

            gpx_info = self.gpx_data[d].split(",x")

            if len(gpx_info[0]) > 0:
                nlaps = 1 if len(gpx_info) == 1 else int(gpx_info[1])
                df = gpx.get_data(filename=gpx_info[0], nlaps=nlaps)
            else:
                step = 11
                df = pd.DataFrame(np.linspace(0, self.distances[d], step), columns=["distance"]).assign(
                    altitude=np.linspace(0, self.elevations[d], step)
                )

            #if (corr := self.distances[d] / df.distance.iloc[-1]) > 0:
            corr = self.distances[d] / df.distance.iloc[-1]
            if corr > 0:
                df["distance"] *= corr

            df["elevation"] = (df["altitude"] - df["altitude"].iloc[0]).diff().fillna(0.0)
            df["aelevation"] = df["elevation"].clip(0.0, 1000)

            if self.elevations[d] == 0 and df.aelevation.sum() != 0:
                self.elevations[d] = df.aelevation.sum()
            elif (corr := self.elevations[d] / df.aelevation.sum()) > 0:
                df["aelevation"] *= corr

            data.append(df.assign(sequence=d * 2).assign(discipline=discipline))

            self.fuelings += self.dfuelings[d]

        self.fuelings = sorted(list(set(self.fuelings)))

        if (
            len(self.disciplines) > 1
            and self.disciplines[0] == "swimming"
            and ".gpx" not in self.gpx_data[0]
            and ".gpx" in self.gpx_data[1]
        ):
            data[0]["altitude"] = data[1]["altitude"].iloc[0]

        return gpx.enrich_data(pd.concat(data))

    @staticmethod
    def load_races_configs():
        races_db = firestore.Client().collection("races")
        races_stream = races_db.stream()
        races_configs = {doc.id: doc.to_dict() for doc in races_stream}
        return races_configs
