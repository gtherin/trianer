import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime
from datetime import time
import trianer
from streamlit_folium import folium_static
import folium

st.set_option("deprecation.showPyplotGlobalUse", False)


st.sidebar.markdown("""[website](https://trianer.guydegnol.net/)""")


if "sath_name" not in st.session_state:
    st.session_state["sath_name"] = "Sylvia"


def configure_athlete():
    def update_athlete_name():
        # athletes_names = ["Guillaume", "Cyrille", "Sylvia", "Vanina", "Nouveau"]
        st.session_state.sath_name = st.session_state.ath_name

    athletes_names = ["Guillaume", "Cyrille", "Sylvia", "Vanina"]

    ath_name = st.selectbox("Athlete", athletes_names, key="sath_name")

    # st.text_input(ath_name, value=ath_name, on_change=update_athlete_name)

    st.write("Mon nom est ", ath_name)

    poids = st.number_input("Poids (en kg)", min_value=50, max_value=100, value=80)
    st.write("Mon poids est de", poids)

    birthday = st.date_input("Anniversaire", datetime.date(1979, 11, 2))
    st.write("Je suis né le ", birthday)


def configure_race():
    epreuve = st.selectbox("Epreuve", ["Elsassman", "Deauville", "Bois", "Nouvelle"])
    longueur = st.selectbox("Longueur", ["S", "M", "L"], index=2)
    tri = trianer.Triathlon(epreuve=epreuve, longueur=longueur)
    folium_static(tri.show_gpx_track())

    input = st.file_uploader("")

    if input is None:
        st.write("Or use sample dataset to try the application")
        sample = st.checkbox("Download sample data from GitHub")

    st.button("Re-run")


def configure_performance():
    natation = st.select_slider(
        "Allure pour la natation",
        options=[f"{m+1}min{s:02.0f}s/100m" for m in range(1, 2) for s in np.linspace(0, 55, 12)],
    )

    transition1 = st.select_slider(
        "Transition nat./cycl.",
        options=[f"{m+1}min{s:02.0f}s" for m in range(1, 2) for s in np.linspace(0, 50, 6)],
    )

    cyclisme = st.number_input("Vitesse à plat en cyclisme", min_value=20, max_value=45, value=28)

    transition2 = st.select_slider(
        "Transition cycl./course",
        options=[f"{m+1}min{s:02.0f}s" for m in range(0, 2) for s in np.linspace(0, 50, 6)],
    )

    course = st.select_slider(
        "Vitesse en course à pieds",
        options=[f"{m+1}min{s:02.0f}s/km" for m in range(1, 2) for s in np.linspace(0, 55, 12)],
    )


def configure_physiologie():

    with st.expander("Data format"):
        st.write(
            "The dataset can contain multiple columns but you will need to select a column to be used as dates and a second column containing the metric you wish to forecast. The columns will be renamed as **ds** and **y** to be compliant with Prophet. Even though we are using the default Pandas date parser, the ds (datestamp) column should be of a format expected by Pandas, ideally YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a timestamp. The y column must be numeric."
        )

    natation = st.select_slider(
        "Allure pour la natation",
        options=[f"{m+1}min{s:02.0f}s/100m" for m in range(1, 2) for s in np.linspace(0, 55, 12)],
    )

    hydra = st.number_input("Hydratation", min_value=50, max_value=100, value=80)

    st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
    st.write("My favorite color is", hydra)


page_names_to_funcs = {
    "Athlete": configure_athlete,
    "Epreuve": configure_race,
    "Performance": configure_performance,
    "Physiologie": configure_physiologie,
}

demo_name = st.sidebar.radio("Configuration", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()


# trianer.Triathlon(epreuve=epreuve, longueur=longueur).show_weather_forecasts()

"""
guillaume = trianer.Triathlon(
    epreuve=epreuve,
    longueur=longueur,
    temperature=[17, 21],
    athlete=trianer.Athlete(
        name="Guillaume",
        poids=poids,
        natation="2min15s/100m",
        cyclisme="25.0km/h",
        course="6min0s/km",
        transitions="10min",
        sudation="faible",
    ),
)


with st.echo():
    folium_static(guillaume.show_gpx_track())

st.write("Natation ", natation, "min/100m, cyclisme ", cyclisme, " km/h, course ", course, " min/km")
st.pyplot(guillaume.show_race_details())
# st.pyplot(guillaume.show_race_details(xaxis = "itime"))
st.pyplot(guillaume.show_nutrition())
st.table(guillaume.show_roadmap())
"""
