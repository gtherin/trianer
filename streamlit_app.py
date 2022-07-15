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


if os.path.exists("/home/guydegnol/projects/trianer/trianer_db_credentials.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"


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

    for p in ["weight", "birthday", "natation", "transition1", "cyclisme", "transition2", "course"]:
        st.session_state[p] = athletes_configs[current_user][p]

    st.session_state.initialized = True


athletes_names = athletes_configs.keys()
races_names = [r for r in races_configs.keys() if "Info" not in r]


def update_perf_data():

    return
    current_user = st.session_state.current_user
    st.info(current_user)
    st.info(st.session_state)

    # current_user = st.session_state["current_user"]
    for p in ["weight", "natation", "transition1", "cyclisme", "transition2", "course"]:
        st.session_state[p] = athletes_configs[current_user][p]

    # firestore.Client().collection("athletes").document(current_user).set(athletes_configs[current_user])


def check_differences():
    current_user = st.session_state.current_user

    do_submit = False

    changes = {}
    for p in ["weight", "natation", "transition1", "cyclisme", "transition2", "course"]:
        if athletes_configs[current_user][p] != st.session_state[p]:
            st.write(athletes_configs[current_user][p], st.session_state[p])
            changes[p] = {f"{athletes_configs[current_user][p]} => {st.session_state[p]}"}
            do_submit = True
            athletes_configs[current_user][p] = st.session_state[p]
    # config["birthday"] = datetime.datetime.combine(birthday, datetime.time(0, 0))

    if do_submit:
        st.info(f"For {current_user}, update {changes}")
        firestore.Client().collection("athletes").document(current_user).set(athletes_configs[current_user])

    return


def update_data():
    # current_user = st.session_state["current_user"]
    return

    # for p in ["weight", "natation", "transition1", "cyclisme", "transition2", "course"]:
    #    athletes_configs[current_user][p] = st.session_state[p]
    # config["birthday"] = datetime.datetime.combine(birthday, datetime.time(0, 0))

    # for p in ["weight", "birthday", "natation", "transition1", "cyclisme", "transition2", "course"]:
    #    if p in config:
    #        st.session_state[p] = config[p] if p != "birthday" else config[p].date()

    # firestore.Client().collection("athletes").document(current_user).set(athletes_configs[current_user])


st.sidebar.selectbox("Athlete", athletes_names, key="current_user", on_change=update_perf_data)
st.sidebar.selectbox("Epreuve", races_names, key="krace_name")


def configure_race():
    check_differences()
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
    check_differences()
    # config = trianer.PerformanceData()
    # Show the UI for your config
    # config.parameter_block()

    # with st.form("performance_form"):
    if 1:

        # st.write("Info", st.session_state, athletes_configs)

        # st.write("Performance estimée de ", ath_name)
        st.select_slider(
            "Allure pour la natation",
            options=[f"{m}min{s:02.0f}s/100m" for m in range(1, 4) for s in np.linspace(0, 55, 12)],
            value=athletes_configs[st.session_state["current_user"]]["natation"],
            # value=st.session_state["natation"],
            key="natation",
        )

        st.select_slider(
            "Transition nat./cycl.",
            options=[f"{m}min{s:02.0f}s" for m in range(1, 10) for s in np.linspace(0, 50, 6)],
            # value=st.session_state["transition1"],
            key="transition1",
        )

        st.number_input(
            "Vitesse à plat en cyclisme",
            min_value=20,
            max_value=45,
            # value=st.session_state["cyclisme"],
            key="cyclisme",
        )

        st.select_slider(
            "Transition cycl./course",
            options=[f"{m}min{s:02.0f}s" for m in range(1, 10) for s in np.linspace(0, 50, 6)],
            # value=athletes_configs[st.session_state["current_user"]]["transition2"],
            value=st.session_state["transition2"],
            key="transition2",
        )

        st.select_slider(
            "Vitesse en course à pieds",
            options=[f"{m}min{s:02.0f}s/km" for m in range(3, 8) for s in np.linspace(0, 55, 12)],
            # value=athletes_configs[st.session_state["current_user"]]["course"],
            value=st.session_state["course"],
            key="course",
        )

        st.write("Info", st.session_state)

        # Every form must have a submit button.
        if 0:  # st.form_submit_button("Sauvegarder les performances", on_click=update_data):
            st.write(
                "Sauvegarde faite pour ",
                st.session_state["current_user"],
                athletes_configs[st.session_state["current_user"]],
            )
            # st.write("Sauvegarde faite", st.session_state, athletes_configs)
            # st.write("Sauvegarde faite")


def configure_physiology():
    check_differences()
    if 1:  # with st.form("athlete_form"):
        with st.expander("Parametres generaux"):

            # st.write("Mon nom est ", ath_name)

            st.number_input("Poids (en kg)", min_value=50, max_value=100, key="weight")
            # st.write("Mon poids est de", weight, " kg")

            st.date_input("Anniversaire", key="birthday")
            # st.write("Je suis né le ", birthday)

            # if st.form_submit_button("Sauvegarde des changements", on_click=update_data):
            #    st.write("Sauvegarde faite")

        with st.expander("Data format"):
            st.write(
                "The dataset can contain multiple columns but you will need to select a column to be used as dates and a second column containing the metric you wish to forecast. The columns will be renamed as **ds** and **y** to be compliant with Prophet. Even though we are using the default Pandas date parser, the ds (datestamp) column should be of a format expected by Pandas, ideally YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a timestamp. The y column must be numeric."
            )

        st.select_slider(
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

        # if st.form_submit_button("Sauvegarder 3", on_click=update_data):
        #    st.write("Sauvegarde faite")


def simulate_race():
    check_differences()
    # trianer.Triathlon(epreuve=epreuve, longueur=longueur).show_weather_forecasts()

    epreuve = st.session_state["krace_name"]
    current_user = st.session_state["current_user"]

    athlete = trianer.Athlete(name=current_user, config=athletes_configs[current_user])

    # st.write("Info", st.session_state, athletes_configs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Athlete", st.session_state["current_user"])
        athlete.get_nat_pace(st.session_state["natation"])
        # st.metric("Natation, minutes par 100m", st.session_state["natation"], 2)
    with col2:
        st.metric("transition nat/cyc, minutes", st.session_state["transition1"])
        st.metric("Cyclisme, km par heure", st.session_state["cyclisme"], 22 - 30)
    with col3:
        st.metric("transition cyc/course, minutes", st.session_state["transition2"])
        st.metric("Course, minutes par km", st.session_state["course"], 5)

    simulation = trianer.Triathlon(epreuve=epreuve, races_configs=races_configs, athlete=athlete)
    folium_static(simulation.show_gpx_track())

    st.pyplot(simulation.show_race_details())
    # st.pyplot(simulation.show_race_details(xaxis = "itime"))
    st.pyplot(simulation.show_nutrition())
    # st.dataframe(simulation.show_roadmap(), width=300)
    st.markdown(simulation.show_roadmap().to_html(), unsafe_allow_html=True)


page_names_to_funcs = {
    "Simuler l'epreuve": simulate_race,
    "Configurer l'epreuve": configure_race,
    "Parametres de performance": configure_performance,
    "Parametres physiologiques": configure_physiology,
}


demo_name = st.sidebar.radio("", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
