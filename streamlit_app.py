import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime
from datetime import time
import trianer
from streamlit_folium import folium_static
import folium

from google.cloud import firestore


st.set_option("deprecation.showPyplotGlobalUse", False)

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"


st.sidebar.markdown("""[website](https://trianer.guydegnol.net/)""")


athletes = firestore.Client().collection("athletes")
docs = athletes.stream()

athletes_configs = {}

gdata = pd.DataFrame()
for doc in docs:
    athletes_configs[doc.id] = doc.to_dict()

default_user = "sylvia"

athletes_names = athletes_configs.keys()
if "kath_name" not in st.session_state:
    st.session_state["kath_name"] = default_user


def update_data():
    at_name = st.session_state["kath_name"]
    at_config = athletes_configs[at_name]
    for p in ["weight", "birthday", "natation", "transition1", "cyclisme", "transition2", "course"]:
        if p in at_config:
            st.session_state[p] = at_config[p] if p != "birthday" else at_config[p].date()


races_names = ["Elsassman (L)", "Elsassman (M)", "Elsassman (S)", "Deauville (L)"]
ath_name = st.sidebar.selectbox("Athlete", athletes_names, key="kath_name", on_change=update_data)
race_name = st.sidebar.selectbox("Epreuve", races_names, key="race_name")


for p in ["weight", "birthday", "natation", "transition1", "cyclisme", "transition2", "course"]:
    if p not in st.session_state:
        st.session_state[p] = athletes_configs[st.session_state["kath_name"]][p]


def configure_athlete():

    with st.form("athlete_form"):

        st.write("Mon nom est ", ath_name)

        weight = st.number_input(
            "Poids (en kg)", min_value=50, max_value=100, value=st.session_state["weight"], key="weight"
        )
        st.write("Mon poids est de", weight, " kg")

        birthday = st.date_input("Anniversaire", st.session_state["birthday"], key="birthday")
        st.write("Je suis né le ", birthday)

        # Every form must have a submit button.
        submitted = st.form_submit_button("Sauvegarder")
        if submitted:
            athletes_configs[ath_name]["weight"] = weight
            athletes_configs[ath_name]["birthday"] = datetime.datetime.combine(birthday, datetime.time(0, 0))

            st.write(ath_name, athletes_configs[ath_name])
            firestore.Client().collection("athletes").document(ath_name).set(athletes_configs[ath_name])

            st.write("Sauvegarde faite")


def configure_race():
    epreuve = st.selectbox("Epreuve", ["Elsassman", "Deauville", "Bois", "Nouvelle"], key="epreuve")
    longueur = st.selectbox("Longueur", ["S", "M", "L"], index=2, key="longueur")
    st.text_input("Ajouter une nouvelle epreuve")

    tri = trianer.Triathlon(epreuve=epreuve, longueur=longueur)
    folium_static(tri.show_gpx_track())

    input = st.file_uploader("")

    if input is None:
        st.write("Or use sample dataset to try the application")
        sample = st.checkbox("Download sample data from GitHub")

    st.button("Re-run")


def configure_performance():

    with st.form("performance_form"):

        st.write("Performance estimée de ", ath_name)
        natation = st.select_slider(
            "Allure pour la natation",
            options=[f"{m}min{s:02.0f}s/100m" for m in range(1, 4) for s in np.linspace(0, 55, 12)],
            value=st.session_state["natation"],
            key="natation",
        )

        transition1 = st.select_slider(
            "Transition nat./cycl.",
            options=[f"{m}min{s:02.0f}s" for m in range(1, 10) for s in np.linspace(0, 50, 6)],
            value=st.session_state["transition1"],
            key="transition1",
        )

        cyclisme = st.number_input(
            "Vitesse à plat en cyclisme",
            min_value=20,
            max_value=45,
            value=st.session_state["cyclisme"],
            key="cyclisme",
        )

        transition2 = st.select_slider(
            "Transition cycl./course",
            options=[f"{m}min{s:02.0f}s" for m in range(1, 10) for s in np.linspace(0, 50, 6)],
            value=st.session_state["transition2"],
            key="transition2",
        )

        course = st.select_slider(
            "Vitesse en course à pieds",
            options=[f"{m}min{s:02.0f}s/km" for m in range(3, 8) for s in np.linspace(0, 55, 12)],
            value=st.session_state["course"],
            key="course",
        )

        # Every form must have a submit button.
        submitted2 = st.form_submit_button("Sauvegarder 2")  # , on_click=update_data)
        if submitted2:
            athletes_configs[ath_name]["natation"] = natation
            athletes_configs[ath_name]["transition1"] = transition1
            athletes_configs[ath_name]["cyclisme"] = cyclisme
            athletes_configs[ath_name]["transition2"] = transition2
            athletes_configs[ath_name]["course"] = course

            st.write(athletes_configs[ath_name])
            firestore.Client().collection("athletes").document(ath_name).set(athletes_configs[ath_name])

            st.write("Sauvegarde faite")


def configure_physiologie():

    with st.expander("Parametres generaux"):
        configure_athlete()

    with st.form("physiologie_form"):

        with st.expander("Data format"):
            st.write(
                "The dataset can contain multiple columns but you will need to select a column to be used as dates and a second column containing the metric you wish to forecast. The columns will be renamed as **ds** and **y** to be compliant with Prophet. Even though we are using the default Pandas date parser, the ds (datestamp) column should be of a format expected by Pandas, ideally YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a timestamp. The y column must be numeric."
            )

        nutrition = st.select_slider(
            "Allure pour la natation",
            options=[f"{m+1}min{s:02.0f}s/100m" for m in range(1, 2) for s in np.linspace(0, 55, 12)],
        )

        hydra = st.number_input("Hydratation", min_value=50, max_value=100, value=80)

        st.subheader("Calories")
        st.pyplot(trianer.show_kcalories())

        st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
        st.write("My favorite color is", hydra)

        fig, ax = plt.subplots(figsize=(15, 4))
        for w in [80 * 0.9, 80, 80 * 1.1]:
            kcalories = trianer.get_kcalories(w, discipline="cyclisme").set_index("speed")["atl"]
            kcalories.plot(ax=ax)
        st.pyplot(fig)

        fig, ax = plt.subplots(figsize=(15, 4))
        for w in [80 * 0.9, 80, 80 * 1.1]:
            kcalories = trianer.get_kcalories(w, discipline="course").set_index("speed")["atl"]
            kcalories.plot(ax=ax)
        st.pyplot(fig)

        st.subheader("Hydratation")

        # 1000/1100 kcal pour les hommes et 800/900 kcal par repas

        fig, ax = plt.subplots(figsize=(15, 4))

        temp = np.arange(0, 40)
        hydr = pd.Series(-np.clip(temp * 100 - 600, 400, 2500), index=temp).to_frame(name="hydration")
        hydr *= 1.5
        sudation = 5
        hydr.plot(ax=ax)

        st.pyplot(fig)

        # Every form must have a submit button.
        submitted3 = st.form_submit_button("Sauvegarder 3")  # , on_click=update_data)
        if submitted3:
            # athletes_configs[ath_name]["course"] = course
            st.write(athletes_configs[ath_name])
            # firestore.Client().collection("athletes").document(ath_name).set(athletes_configs[ath_name])

            st.write("Sauvegarde faite")


def simulate_race():
    # trianer.Triathlon(epreuve=epreuve, longueur=longueur).show_weather_forecasts()

    guillaume = trianer.Triathlon(
        epreuve="Elsassman",
        longueur="L",
        temperature=[17, 21],
        athlete=trianer.Athlete(
            name=st.session_state["kath_name"],
            poids=st.session_state["weight"],
            natation=st.session_state["natation"],
            cyclisme=f"{st.session_state['cyclisme']}km/h",
            course=st.session_state["course"],
            transitions="10min",
            sudation="faible",
        ),
    )
    folium_static(guillaume.show_gpx_track())

    st.write(
        "natation ",
        st.session_state["natation"],
        ", cyclisme ",
        st.session_state["cyclisme"],
        " km/h, course ",
        st.session_state["course"],
    )
    st.pyplot(guillaume.show_race_details())
    # st.pyplot(guillaume.show_race_details(xaxis = "itime"))
    st.pyplot(guillaume.show_nutrition())
    # st.dataframe(guillaume.show_roadmap(), width=300)
    st.markdown(guillaume.show_roadmap().to_html(), unsafe_allow_html=True)


page_names_to_funcs = {
    "Simuler l'epreuve'": simulate_race,
    "Configurer l'epreuve": configure_race,
    "Parametres de performance": configure_performance,
    "Parametres physiologiques": configure_physiologie,
}


demo_name = st.sidebar.radio("", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
