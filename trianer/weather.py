import datetime
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_default_coordonates(altitude=False) -> tuple:
    # (latitude, longitude, altitude)
    # 53 rue rebeval by default
    if altitude:
        return (48.875017, 2.3795896, 70)
    else:
        return (48.875017, 2.3795896)


def get_weather(coordonates=None, start=None, end=None):

    from meteostat import Point, Daily

    # Set time period
    if start is None:
        start = datetime.datetime(2018, 1, 1)
    if end is None:
        end = datetime.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)

    if coordonates is None:
        coordonates = get_default_coordonates()

    point = Point(*coordonates)

    # Get daily data for 2018
    data = Daily(point, start, end)
    weather = data.fetch()

    return weather


def get_htmin_max(coordonates, start_time):
    if coordonates is None:
        # (latitude, longitude, altitude)
        # 53 rue rebeval by default
        coordonates = (48.875017179462446, 2.3795896457900936, 70)

    # coordonates = (45.188529, 5.724524, 70)
    print(coordonates, start_time, start_time.month)

    # Get historical data
    pdf = get_weather(coordonates=[coordonates[0], coordonates[1], 0], start=None, end=None)

    pdf = pdf[pdf.index.month == start_time.month]
    htemps = pdf.groupby(pdf.index.year).mean().ewm(3).mean().iloc[-1].to_dict()
    htmin, htmax = np.mean(htemps["tmin"]), np.mean(htemps["tmax"])
    return (htmin, htmax)


def get_forecasts(coordonates=None, start=None, end=None):
    """https://wttr.in/:help"""

    if coordonates is None:
        # (latitude, longitude, altitude)
        # 53 rue rebeval by default
        coordonates = (48.875017179462446, 2.3795896457900936, 70)

    # Get historical data
    pdf = get_weather(coordonates=[coordonates[0], coordonates[1], 200], start=None, end=None)
    pdf = pdf[pdf.index.month == 7]
    htemps = pdf.groupby(pdf.index.year).mean().ewm(3).mean().iloc[-1].to_dict()
    htmin, htmax = np.mean(htemps["tmin"]), np.mean(htemps["tmax"])

    if type(coordonates) == tuple:
        coordonates = "%2.2f,%2.2f" % (coordonates[0], coordonates[1])

    # Extract temperatures
    res = requests.get(f"https://wttr.in/{coordonates}?pqT&lang=fr")
    tt = [t[-8:-1].split("(") for t in res.text.split("°C")]

    # Get one temperature per day quarters
    tt = [int(t[0][-3:]) if len(t) > 1 else int(t[0][-3:]) for t in tt[:-1]]
    temp_forecast = tt[-4]
    tmin, tmax = tt[-4], tt[-2]
    tmin, tmax = htmin, htmax

    res = requests.get(f"https://wttr.in/{coordonates}?lang=fr")

    fig, ax = plt.subplots(figsize=(18, 3))
    ax.plot(np.arange(24), (tmin + 0.5 * (tmax - tmin) * (1 + np.sin(0.25 * np.arange(24) + np.pi))), color="yellow")
    return temp_forecast


def get_intraday_temperature(start_time, tmin, tmax):
    minutes = np.arange(24 * 60)

    index = pd.to_datetime(start_time).floor("D") + pd.to_timedelta(minutes, unit="min")
    temp = np.round(tmin + 0.5 * (tmax - tmin) * (1 + np.sin(0.25 * minutes / 60.0 + np.pi)), 2)

    return pd.Series(temp, index=index).to_frame(name="temperature")


def merge_temperature_forecasts(data, coordonates=None, start_time=datetime.datetime.now(), temperature=None):

    htmin, htmax = get_htmin_max(coordonates, start_time)
    if temperature is None:
        tmin, tmax = htmin, htmax
    elif type(temperature) == list:
        tmin, tmax = temperature
    else:
        tmin, tmax = temperature, temperature
    # print(htmin, htmax)

    if "temperature" in data.columns:
        del data["temperature"]

    itemps = get_intraday_temperature(start_time, tmin, tmax)
    data = data.merge(itemps, how="left", left_on=data["dtime"].dt.floor("min"), right_index=True)
    data["temperature"] = data["temperature"].ffill().bfill()
    return data
