import datetime
from .variable import Variable
from .labels import Labels
from ..race.races import available_races

import streamlit as st

svariables = [
    # Performances
    dict(
        key="swimming_sX100m",
        help="Pace is how much time you need to swim 100m",
        srange="t:1:5:1",
        default=datetime.time(2, 0),
        input_format="slider",
    ),
    dict(
        key="running_sXkm",
        help="Pace is how much time you need to run 1km (flat surface)",
        srange="t:3:10:5",
        default=datetime.time(5, 30),
        input_format="slider",
    ),
    dict(
        key="cycling_kmXh",
        help="Speed is the distance you do in an hour (flat surface)",
        srange="i:16:50:1",
        default=30,
    ),
    # Transitions
    dict(
        key="transition_swi2cyc_s",
        help="Transition time between swimming and cycling in minutes:seconds",
        srange="t:1:5:15",
        default=datetime.time(2, 0),
        input_format="slider",
    ),
    dict(
        key="transition_cyc2run_s",
        help="Transition time between cycling and running in minutes:seconds",
        srange="t:1:5:15",
        default=datetime.time(2, 0),
        input_format="slider",
    ),
    # Race conditions
    dict(
        key="disciplines",
        srange=["swimming", "cycling", "running"],
        help="running_lengh",
        default=["swimming", "running"],
        input_format="multiselect",
    ),
    dict(key="swimming_lengh", srange="f:0.0:4.0:0.1", help="swimming_lengh", default=1.5),
    dict(key="cycling_lengh", srange="i:0:200:1", help="cycling_lengh", default=40),
    dict(key="running_lengh", srange="i:0:200:1", help="running_lengh", default=10),
    dict(
        key="cycling_dplus",
        help="Positive elevation gain during cycling in meter",
        srange="i:0:5000:10",
        default=0,
    ),
    dict(
        key="running_dplus",
        help="Positive elevation gain during running in meter",
        srange="i:0:10000:5",
        default=0,
    ),
    dict(
        key="temperature_race",
        label="Temperature (°C)",
        help="Expected temperature in degres Celsius",
        srange="i:0:40:1",
        default=22,
    ),
    dict(
        key="temperature_menu_race",
        srange=["temp_auto", "temp_manual", "temp_from_date"],
        help="The method to estimate the temperature",
        default="temp_auto",
        input_format="radio",
    ),
    dict(
        key="dtemperature_race",
        label="Date temp. (°C)",
        help="Expected temperature in degres Celsius",
        # srange="d:0:365:1",
        default=datetime.date.today(),
        input_format="date_input",
    ),
    dict(
        key="race_format",
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
        input_format="selectbox",
    ),
    dict(
        key="race_menu",
        help="You can either use a default format, load an known race or build your own race",
        srange=["existing_format", "existing_race", "personalized_format"],
        default="existing_format",
        input_format="radio",
    ),
    dict(
        key="race_default",
        srange=[r for r, c in available_races.items() if "type" not in c],
        help="Format of the selected race",
        default="Bois-le-Roi (L)",
        label="",
        input_format="selectbox",
    ),
    dict(
        key="sex",
        srange=["female", "male"],
        help="Metabolism varies differently between man and woman",
        default="female",
        input_format="radio",
    ),
    # Profile
    dict(
        key="language",
        srange=["En", "Fr"],
        help="To switch language/Pour changer de langue",
        default="En",
        input_format="radio",
    ),
    dict(
        key="beta_mode",
        help="To activate beta mode",
        default=False,
        input_format="checkbox",
    ),
    dict(key="weight_kg", help="Your weight (in kg)", srange="i:40:100:1", default=70),
    dict(key="vo2max", help="Your Vo2 max (in ml/kg/min)", srange="i:30:80:1", default=45),
    dict(
        key="year_of_birth",
        srange="i:1930:2018:1",
        help="Year of birth is used to have a better estimation of energy spent",
        default=1980,
    ),
    dict(
        key="sudation",
        srange="i:1:10:1",
        help="If the athlete sweat a lot",
        default=5,
        input_format="slider",
    ),
    dict(key="height_cm", help="You height in centimeters", srange="i:100:240:1", default=175),
    # Transitions
    dict(
        key="target_time",
        help="Target time in minutes:seconds",
        srange="t:2:5:30",
        default=datetime.time(4, 30),
        input_format="slider",
    ),
]


@st.cache_data
def load_default_data():
    st.write("Loading default data")
    variables = {v["key"]: Variable(**v) for v in svariables}

    variables["pcycling_dplus"] = Variable.clone(variables["cycling_dplus"], "pcycling_dplus")
    variables["prunning_dplus"] = Variable.clone(variables["running_dplus"], "prunning_dplus")

    variables["temperature_format"] = Variable.clone(variables["temperature_race"], "temperature_format")
    variables["temperature_perso"] = Variable.clone(variables["temperature_race"], "temperature_perso")

    variables["temperature_menu_format"] = Variable.clone(
        variables["temperature_menu_race"], "temperature_menu_format"
    )
    variables["temperature_menu_perso"] = Variable.clone(variables["temperature_menu_race"], "temperature_menu_perso")

    variables["dtemperature_format"] = Variable.clone(variables["dtemperature_race"], "dtemperature_format")
    variables["dtemperature_perso"] = Variable.clone(variables["dtemperature_race"], "dtemperature_perso")

    return variables


# Some menu
Labels.add_label("beta_mode", en="Beta mode activation", fr="Activation du mode beta")
# Labels.add_label(
#    "height_cm", en="Height (cm)", fr="Taille (cm)", hen="You height in centimeters", srange="i:100:240:1", default=175
# )
