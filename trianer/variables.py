import numpy as np
import datetime
from .variable import Variable


variables = [
    # Performances
    dict(
        key="swimming_sX100m",
        label="Swimming pace (min/100m)",
        help="Pace is how much time you need to swim 100m",
        srange="t:1:5:1",
        default=datetime.time(2, 0),
    ),
    dict(
        key="running_sXkm",
        label="Running pace (min/km)",
        help="Pace is how much time you need to run 1km (flat surface)",
        srange="t:3:10:5",
        default=datetime.time(5, 30),
    ),
    dict(
        key="cycling_kmXh",
        label="Cycling speed (km/h)",
        help="Speed is the distance you do in an hour (flat surface)",
        srange="i:16:50:1",
        default=30,
    ),
    # Transitions
    dict(
        key="transition_swi2cyc_s",
        label="Transition time swi./cyc. (min:sec)",
        help="Transition time between swimming and cycling in minutes:seconds",
        srange="t:1:5:15",
        default=datetime.time(2, 0),
    ),
    dict(
        key="transition_cyc2run_s",
        label="Transition time cyc./run. (min:sec)",
        help="Transition time between cycling and running in minutes:seconds",
        srange="t:1:5:15",
        default=datetime.time(2, 0),
    ),
    # Race conditions
    dict(
        key="disciplines",
        srange=["swimming", "cycling", "running"],
        help="running_lengh",
        default=["swimming", "running"],
    ),
    dict(key="swimming_lengh", srange="f:0.0:4.0:0.1", help="swimming_lengh", default=1.5),
    dict(key="cycling_lengh", srange="i:0:200:1", help="cycling_lengh", default=40),
    dict(key="running_lengh", srange="i:0:200:1", help="running_lengh", default=10),
    dict(
        key="cycling_dplus",
        label="Positive elevation gain cyc. (m)",
        help="Positive elevation gain during cycling in meter",
        srange="i:0:5000:10",
        default=0,
    ),
    dict(
        key="running_dplus",
        label="Positive elevation gain run. (m)",
        help="Positive elevation gain during running in meter",
        srange="i:0:10000:5",
        default=0,
    ),
    dict(
        key="pcycling_dplus",
        label="Positive elevation gain cyc. (m)",
        help="Positive elevation gain during cycling in meter",
        srange="i:0:5000:10",
        default=0,
    ),
    dict(
        key="prunning_dplus",
        label="Positive elevation gain run. (m)",
        help="Positive elevation gain during running in meter",
        srange="i:0:10000:5",
        default=0,
    ),
    dict(
        key="temperature",
        label="Temperature (°C)",
        help="Expected temperature in degres Celsius",
        srange="i:0:40:1",
        default=22,
    ),
    dict(
        key="dtemperature",
        label="Temperature (°C)",
        help="Expected temperature in degres Celsius",
        srange="d:0:365:1",
        default=datetime.date.today(),
    ),
    dict(
        key="race_format",
        label="Race format",
        help="Format of the selected race",
        srange=[
            "Ironman",
            "Half-Ironman (70.3)",
            "Triathlon (L)",
            "Triathlon (M)",
            "Triathlon (S)",
            "Marathon",
            "Half-Marathon",
        ],
        default="Half-Ironman (70.3)",
    ),
    dict(
        key="race_menu",
        label="Type of race",
        help="You can either use a default format, load an known race or build your own race",
        srange=["Existing format", "Existing race", "Personalized format"],
        default="Existing format",
    ),
    dict(key="athlete_switch", label="Athlete's performances", help=None, srange="b", default=True),
    dict(key="race_default", srange="s", help="Format of the selected race", default="Bois-le-Roi (L)", label=""),
    dict(
        key="sex",
        label="Sex",
        srange=["Female", "Male"],
        help="Metabolism is different on average between man and woman",
        default="Female",
    ),
    dict(key="weight_kg", label="Weight (kg)", help="Your weight (in kg)", srange="i:40:100:1", default=70),
    dict(
        key="year_of_birth",
        srange="i:1920:2018:1",
        help="Year of birth is used to have a better estimation of energy spent",
        default=1980,
    ),
    dict(key="height_cm", label="Height (cm)", help="You height in centimeters", srange="i:100:240:1", default=170),
]

variables = {v["key"]: Variable(**v) for v in variables}
