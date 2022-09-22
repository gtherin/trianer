import datetime
import os
import json
import time
import logging

import numpy as np
import pandas as pd


def get_default_datetime():
    return datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)


class Point:
    @staticmethod
    def get_anchor_value(point, anchor):
        return point[point.find(f"<{anchor}>") + len(f"<{anchor}>") : point.find(f"</{anchor}>")]

    @staticmethod
    def get_latitude(point):
        for p in point.split():
            if "lat=" in p:
                return float(p[5:-2])

    @staticmethod
    def get_longitude(point):
        for p in point.split():
            if "lon=" in p:
                return float(p[5:-2])

    @staticmethod
    def get_altitude(point):
        return np.round(float(Point.get_anchor_value(point, "ele")), 2)

    @staticmethod
    def get_time(point):
        if "time" not in point:
            return get_default_datetime()
        ttime = Point.get_anchor_value(point, "time")
        return datetime.datetime.strptime(ttime[:19], "%Y-%m-%dT%H:%M:%S")

    @staticmethod
    def update_altitude(altitude, point):
        fpoint = point[: point.find("<ele>") + len("<ele>")] + "%.2f" % altitude + point[point.find("</ele>") :]
        return fpoint

    @staticmethod
    def delete_extensions(point):
        if "<extensions>" not in point:
            return point
        return point[: point.find("<extensions>")] + point[point.find("</extensions>") + len("</extensions>") :]

    def __init__(self, point):
        self.is_valid_gpx = "<ele>" in point
        self.is_valid_tcx = "<AltitudeMeters>" in point

        self.point = point
        self.latitude = -1
        self.longitude = -1
        self.altitude = -1
        self.distance = -1
        self.dtime = get_default_datetime()
        self.temperature = -1
        self.hr = -1

        if self.is_valid_gpx:
            self.point = "<trkpt" + point
            self.latitude = self.get_latitude(self.point)
            self.longitude = self.get_longitude(self.point)
            self.altitude = self.get_altitude(self.point)
            self.dtime = self.get_time(self.point)
            if "gpxtpx:atemp" in point:
                self.temperature = Point.get_anchor_value(self.point, "gpxtpx:atemp")
            if "gpxtpx:hr" in point:
                self.hr = Point.get_anchor_value(self.point, "gpxtpx:hr")
        elif self.is_valid_tcx:
            self.point = "<Trackpoint" + point
            self.latitude = Point.get_anchor_value(self.point, "LatitudeDegrees")
            self.longitude = Point.get_anchor_value(self.point, "LongitudeDegrees")
            self.altitude = Point.get_anchor_value(self.point, "AltitudeMeters")
            self.dtime = Point.get_anchor_value(self.point, "Time")
            self.distance = Point.get_anchor_value(self.point, "DistanceMeters")

    def get_formatted_point(self):
        if not self.is_valid:
            return self.point
        point = Point.delete_extensions(self.point)
        # S'il n'y a pas d'extensions : (et commenter ligne au dessus
        point = Point.update_altitude(self.altitude, point)
        return point


def clean_file(filename, filters):

    if not os.path.exists(filename):
        print(f"{filename}: File does not exist")
        return

    xml = open(filename, "r").read().split("<trkpt")

    text = ""
    for p in xml:
        point = Point(p)

        for filter in filters:
            ctime = point.dtime.time()

            altitude_offset = 0
            if ctime >= filter["min_time"] and ctime <= filter["max_time"]:
                if type(filter["altitude_offset"]) == dict:
                    altitude_global_offset = filter["altitude_offset"]["max"] - filter["altitude_offset"]["min"]

                    altitude_offset = altitude_global_offset * (
                        get_diff_in_seconds(ctime, filter["min_time"]) / filter["diff_time"]
                    )
                    altitude_offset += filter["altitude_offset"]["min"]

                else:
                    altitude_offset = filter["altitude_offset"]

                print("%s: Altitude %s offset to %sm" % (filename, point.dtime.time(), int(altitude_offset)))
                point.altitude += altitude_offset

        text += point.get_formatted_point()

    with open(filename.replace(".gpx", "_hr.gpx"), "w") as f:
        f.write(text)


def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    """Calculate the great circle distance between two points on the earth (specified in decimal degrees or in radians)"""
    lat1, lon1, lat2, lon2 = np.radians([lat1.values, lon1.values, lat2.values, lon2.values])
    a = np.sin((lat2 - lat1) / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2.0) ** 2
    return earth_radius * 2 * np.arcsin(np.sqrt(a))


def get_requests(filename):
    import requests

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    url_req = requests.get(filename)
    url_req.encoding = "UTF-8"

    return url_req


def get_data_from_file(filename):

    ext = filename.split(".")[-1]

    if "http" in filename:
        url_req = get_requests(filename)
        xml = url_req.text.split("<trkpt")
    elif ext == "tcx":
        xml = open(filename, "r").read().split("<Trackpoint")
    else:
        for d in ["./data", "../data"]:
            dfilename = f"{d}/{filename}"
            if os.path.exists(dfilename):
                xml = open(dfilename, "r").read().split("<trkpt")

    data = []
    for p in xml:
        point = Point(p)
        if point.longitude != -1:
            data.append(
                [
                    point.latitude,
                    point.longitude,
                    point.altitude,
                    point.distance,
                    point.dtime,
                    point.temperature,
                    point.hr,
                ]
            )

    return pd.DataFrame(data, columns=["latitude", "longitude", "altitude", "distance", "dtime", "temperature", "hr"])


def get_diff_in_seconds(time1, time2):
    return (
        datetime.datetime.combine(datetime.date.today(), time1)
        - datetime.datetime.combine(datetime.date.today(), time2)
    ).seconds


def enrich_data(data, target_distance=None, target_elelevation=None):

    # FIlter distance
    data["fdistance"] = data["distance"].diff().clip(0, 10000).fillna(0.0).cumsum()

    # Calculate elevation
    data["elevation"] = (data["altitude"] - data["altitude"].iloc[0]).diff().fillna(0.0)

    # Calculate slope
    # Apply filter on 1 hour <=> 1 km
    distance_1kmh = pd.to_datetime(data["fdistance"] * 1000 * 3.6, unit="s", errors="coerce")
    data["slope"] = 100 * data["altitude"].diff() / data["distance"].diff() / 1000
    data["slope"] = (
        data["slope"].clip(-25, 25).ewm(times=distance_1kmh, halflife=datetime.timedelta(hours=1)).mean().fillna(0.0)
    )

    # Calculcate speed
    # data["speed"] = 3600 * (data["distance"].diff().ewm(10).mean() / data["dtime"].diff().dt.seconds).fillna(0.0)
    if "hr" in data.columns:
        data["hr"] = data["hr"].astype(float)

    return data.set_index("fdistance")


def get_data(filename=None, nlaps=1, info_box=None):

    # import streamlit as st

    # if info_box is None:
    #    info_box = st.empty()

    # info_box.info(f"⏳ Read {filename}")

    # if "pace_data" not in filename and "http" not in filename:
    #    filename = "http://trianer.guydegnol.net/" + filename

    data = get_data_from_file(filename)
    data = pd.concat([data] * nlaps)

    if data["distance"].mean() < 0:
        data["distance"] = (
            pd.Series(
                haversine(data.latitude.shift(), data.longitude.shift(), data.latitude, data.longitude),
                index=data.index,
            )
            .fillna(0)
            .cumsum()
        )

    # data["altitude"] = sp.signal.savgol_filter(data["altitude"], 5, 4)
    data["altitude"] = pd.Series(data["altitude"]).apply(lambda x: int(5 * round(float(x) / 5)))

    # info_box.empty()
    return data


def clean_files():

    filters = json.load(open("anon_gpx.json", "r"))

    for filename, filters in filters.items():

        for filter in filters:
            filter["min_time"] = datetime.datetime.strptime(filter["min_time"], "%H:%M:%S").time()
            filter["max_time"] = datetime.datetime.strptime(filter["max_time"], "%H:%M:%S").time()
            filter["diff_time"] = get_diff_in_seconds(filter["max_time"], filter["min_time"])

        clean_file(filename, filters)


if __name__ == "__main__":
    clean_files()
