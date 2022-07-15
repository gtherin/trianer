import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime
import trianer
from streamlit_folium import folium_static
import os


from google.cloud import firestore


st.set_option("deprecation.showPyplotGlobalUse", False)


# if os.path.exists("/home/guydegnol/projects/trianer/trianer_db_credentials.json"):
#    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"


st.sidebar.markdown("""[website](https://trianer.guydegnol.net/)""")


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_athletes_configs():
    st.info("Load athletes from db")
    athletes_db = firestore.Client().collection("athletes")
    athletes_stream = athletes_db.stream()
    athletes_configs = {doc.id: doc.to_dict() for doc in athletes_stream}
    return athletes_configs


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_races_configs():
    st.info("Load races from db")
    races_db = firestore.Client().collection("races")
    races_stream = races_db.stream()
    races_configs = {doc.id: doc.to_dict() for doc in races_stream}
    return races_configs


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_default_user():
    st.info("Call load_default_user")
    return "guydegnol"


current_user = load_default_user()
athletes_configs = load_athletes_configs()
races_configs = load_races_configs()


if not "initialized" in st.session_state:
    st.info("Init session state")
    st.session_state.current_user = current_user
    st.session_state.krace_name = "Elsassman (L)"

    for p in ["weight", "natation", "course"]:
        st.session_state[p] = athletes_configs[current_user][p]

    st.session_state.initialized = True


athletes_names = athletes_configs.keys()
races_names = [r for r in races_configs.keys() if "Info" not in r]


def session_state2athletes_configs():
    for p in ["natation", "course"]:
        athletes_configs[current_user][p] = st.session_state[p]


def athletes_configs2session_state():
    for p in ["natation", "course"]:
        st.session_state[p] = athletes_configs[current_user][p]


def check_differences():
    current_user = st.session_state.current_user

    do_submit = False

    changes = {}
    for p in ["natation", "course"]:
        if athletes_configs[current_user][p] != st.session_state[p]:
            st.write(athletes_configs[current_user][p], st.session_state[p])
            changes[p] = {f"{athletes_configs[current_user][p]} => {st.session_state[p]}"}
            do_submit = True
            athletes_configs[current_user][p] = st.session_state[p]

    if do_submit:
        st.info(f"For {current_user}, update {changes}")
        # firestore.Client().collection("athletes").document(current_user).set(athletes_configs[current_user])


def configure_race():
    check_differences()
    st.text_input("Ajouter une nouvelle epreuve")


def configure_performance():

    athletes_configs2session_state()
    check_differences()
    if 1:

        st.select_slider(
            "Allure pour la natation",
            options=[f"{m}min{s:02.0f}s/100m" for m in range(1, 4) for s in np.linspace(0, 55, 12)],
            # value=athletes_configs[st.session_state["current_user"]]["natation"],
            value=st.session_state["natation"],
            key="natation",
        )

        course = st.select_slider(
            "Vitesse en course à pieds",
            options=[f"{m}min{s:02.0f}s/km" for m in range(3, 8) for s in np.linspace(0, 55, 12)],
            # value=athletes_configs[st.session_state["current_user"]]["course"],
            value=st.session_state["course"],
            key="course",
        )

        st.write("Info", {k: v for k, v in st.session_state.items() if k in ["natation", "course"]}, course)


def configure_physiology():
    check_differences()
    with st.expander("Parametres generaux"):
        st.number_input("Poids (en kg)", min_value=50, max_value=100, key="weight")


def simulate_race():
    check_differences()
    st.metric("Athlete", st.session_state["current_user"])
    st.metric("Natation, minutes par 100m", st.session_state["natation"], 2)


page_names_to_funcs = {
    "Simuler l'epreuve": simulate_race,
    "Configurer l'epreuve": configure_race,
    "Parametres de performance": configure_performance,
    "Parametres physiologiques": configure_physiology,
}


def main():

    # st.sidebar.selectbox("Athlete", athletes_names, key="current_user")  # , on_change=update_perf_data)

    # demo_name = st.sidebar.radio("Menu", page_names_to_funcs.keys())
    # st.write(
    #    "athletes_configs", {k: v for k, v in athletes_configs[current_user].items() if k in ["natation", "course"]}
    # )
    # st.write("session_state", {k: v for k, v in st.session_state.items() if k in ["natation", "course"]})
    # st.write("session_state", st.session_state)
    # page_names_to_funcs[demo_name]()

    st.metric("Athlete", 10)


main()
