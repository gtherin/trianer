import datetime
import os
import json
import logging

# WARNING: numpy not available for Francois
import numpy as np
import pandas as pd

from .gpx_formatter import Point


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


def get_file(filename, read=False):
    if "http" in filename:
        url_req = get_requests(filename)
        if read:
            xml = url_req.text
        return filename
    else:
        for d in ["./data", "../data"]:
            dfilename = f"{d}/{filename}"
            if os.path.exists(dfilename):
                if read:
                    return open(dfilename, "r").read()
                return dfilename


def get_data_from_file(filename):
    # WARNING: not available for Francois
    import pandas as pd

    print(filename)
    xml = get_file(filename, read=True)

    if "<trkpt" in xml:
        splitter = "<trkpt"
    elif "<wpt" in xml:
        splitter = "<wpt"
    elif "<Trackpoint" in xml:
        splitter = "<Trackpoint"
    elif "<ns3:TrackPointExtension" in xml:
        splitter = "<ns3:TrackPointExtension"

    xml = xml.split(splitter)

    data = []
    for p in xml:
        point = Point(p, splitter=splitter)
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


def get_data(filename=None, nlaps=1):
    #    filename = "http://trianer.guydegnol.net/" + filename
    import pandas as pd

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

    data["speed"] = 3600.0 * data.distance.diff() / data.dtime.diff().dt.seconds

    # data["altitude"] = sp.signal.savgol_filter(data["altitude"], 5, 4)
    data["altitude"] = pd.Series(data["altitude"]).apply(lambda x: int(5 * round(float(x) / 5)))

    return data
