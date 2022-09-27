import datetime
import numpy as np
import pandas as pd
import logging

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import matplotlib
import time
import sys


from ..race import weather
from .. import nutrition
from ..core.labels import gl

logging.getLogger("matplotlib.font_manager").disabled = True
logging.getLogger("matplotlib").setLevel(logging.ERROR)
pd.plotting.register_matplotlib_converters()


def show_gpx_track(triathlon):
    from branca.element import Figure
    import folium

    fig = Figure(width=900, height=300)
    trimap = folium.Map(location=triathlon.get_mean_coordonates(use_map=True), zoom_start=10)
    fig.add_child(trimap)

    from folium.plugins import MarkerCluster

    marker_cluster = MarkerCluster().add_to(trimap)
    for discipline in triathlon.race.disciplines:

        gpx = triathlon.get_gpx(triathlon.gpx, discipline)
        gpx = gpx.dropna(subset=["latitude", "longitude"])
        if "latitude" not in gpx.columns or np.isnan(gpx["latitude"].mean()) or gpx.empty:
            continue

        folium.PolyLine(
            list(zip(gpx["latitude"], gpx["longitude"])),
            color=triathlon.get_color(discipline),
            weight=3,
            opacity=0.8,
        ).add_to(trimap)

    # icon = folium.Icon(color='darkblue', icon_color='white', icon='star', angle=0, prefix='fa')
    # icon = folium.DivIcon(html=f"""<div style="color: blue">1</div>""")

    for f in [10, 20, 30, 40, 50, 60, 70]:

        si = triathlon.gpx.index.searchsorted(f)
        if si == len(triathlon.gpx):
            continue
        r = triathlon.gpx.iloc[si]
        folium.Marker(
            location=[r["latitude"], r["longitude"]],
            popup="Ravito",
            icon=folium.DivIcon(html=f"""<div style="color: black; background-color:white">{f}</div>"""),
        ).add_to(marker_cluster)

    for f in triathlon.race.fuelings:
        si = triathlon.gpx.index.searchsorted(f)
        if si == len(triathlon.gpx):
            continue
        r = triathlon.gpx.iloc[si]
        if np.isnan(r["latitude"] * r["longitude"]):
            continue
        folium.Marker(
            location=[r["latitude"], r["longitude"]],
            popup="Ravito",
            icon=folium.Icon(color="red", icon_color="darkblue", icon="coffee", angle=0, prefix="fa"),
        ).add_to(marker_cluster)
    return trimap
