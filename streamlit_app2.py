import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime
import trianer
import time
import extra_streamlit_components as stx

from streamlit_folium import folium_static
import os
import streamlit as st
from persist import persist, load_widget_state

from google.cloud import firestore


import datetime


@st.cache(allow_output_mutation=True)
def get_manager():
    return stx.CookieManager()


st.set_option("deprecation.showPyplotGlobalUse", False)


if os.path.exists("/home/guydegnol/projects/trianer/trianer_db_credentials.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/guydegnol/projects/trianer/trianer_db_credentials.json"


info_box = st.empty()

cookie_manager = get_manager()


def get_time_variables():
    return ["swimming_sX100m", "transition_swi2cyc_s", "transition_cyc2run_s", "running_sXkm"]


def format_db2st(config):
    nconfig = {}
    for field, value in config.items():
        if field in get_time_variables():
            nconfig[field] = datetime.time(int(value / 60), value % 60)
        else:
            nconfig[field] = value
    return nconfig


def format_stdb(config):
    nconfig = {}
    for field, value in config.items():
        if field in get_time_variables():
            nconfig[field] = value.hour * 60 + value.minute
        else:
            nconfig[field] = value

    # config["birthday"] = datetime.datetime.combine(birthday, datetime.time(0, 0))
    return nconfig


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_athletes_configs():

    # info_box.info("Load athletes from db")
    time.sleep(1)

    athletes_db = firestore.Client().collection("athletes")
    athletes_stream = athletes_db.stream()
    athletes_configs = {doc.id: format_db2st(doc.to_dict()) for doc in athletes_stream}
    # info_box.empty()

    cookies = cookie_manager.get_all()

    # value = cookie_manager.get(cookie=cookie)
    st.write(athletes_configs["guydegnol"])
    # st.write(value)
    # cookie = st.text_input("Cookie", key="1")
    # val = st.text_input("Value")
    # cookie_manager.set(cookie, val, expires_at=datetime.datetime(year=2024, month=1, day=1))

    st.write(cookies)

    return athletes_configs


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_races_configs():
    # info_box.info("Load races from db")
    time.sleep(1)
    races_db = firestore.Client().collection("races")
    races_stream = races_db.stream()
    races_configs = {doc.id: doc.to_dict() for doc in races_stream}
    # info_box.empty()
    return races_configs


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_default_user():
    # info_box.info("Call load_default_user")
    time.sleep(1)
    # info_box.empty()
    return "guydegnol"


current_user = load_default_user()
athletes_configs = load_athletes_configs()
races_configs = load_races_configs()


def check_differences():
    current_user = st.session_state.current_user

    do_submit = False

    changes = {}

    for p in [
        "weight_kg",
        "swimming_sX100m",
        "transition_swi2cyc_s",
        "cycling_kmXh",
        "transition_cyc2run_s",
        "running_sXkm",
    ]:
        if athletes_configs[current_user][p] != st.session_state[p]:
            st.write(athletes_configs[current_user][p], st.session_state[p])
            changes[p] = {f"{athletes_configs[current_user][p]} => {st.session_state[p]}"}
            do_submit = True
            athletes_configs[current_user][p] = st.session_state[p]

    if do_submit:
        info_box.info(f"For {current_user}, update {changes}")
        time.sleep(2)
        firestore.Client().collection("athletes").document(current_user).set(
            format_stdb(athletes_configs[current_user])
        )
        info_box.empty()


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

    st.header("Change settings")

    st.slider(
        "Allure pour la natation",
        value=athletes_configs[current_user]["swimming_sX100m"],
        min_value=datetime.time(1, 0),
        max_value=datetime.time(5, 0),
        step=datetime.timedelta(minutes=5),
        key=persist("swimming_sX100m"),
    )

    st.slider(
        "Transition nat./cycl.",
        value=athletes_configs[current_user]["transition_swi2cyc_s"],
        min_value=datetime.time(1, 0),
        max_value=datetime.time(5, 0),
        step=datetime.timedelta(minutes=15),
        key=persist("transition_swi2cyc_s"),
    )

    st.number_input(
        "Vitesse à plat en cyclisme",
        min_value=20,
        max_value=45,
        value=athletes_configs[current_user]["cycling_kmXh"],
        key=persist("cycling_kmXh"),
    )

    st.slider(
        "Transition nat./cycl.",
        value=athletes_configs[current_user]["transition_cyc2run_s"],
        min_value=datetime.time(1, 0),
        max_value=datetime.time(5, 0),
        step=datetime.timedelta(minutes=15),
        key=persist("transition_cyc2run_s"),
    )

    st.slider(
        "Allure pour la course à pieds",
        value=athletes_configs[current_user]["running_sXkm"],
        min_value=datetime.time(3, 0),
        max_value=datetime.time(10, 0),
        step=datetime.timedelta(minutes=5),
        key=persist("running_sXkm"),
    )


def configure_physiology():
    # check_differences()
    if 1:  # with st.form("athlete_form"):
        with st.expander("Parametres generaux"):

            st.number_input("Poids (en kg)", min_value=50, max_value=100, key=persist("weight_kg"))
            # st.write("Mon poids est de", weight, " kg")

            st.date_input("Anniversaire", key="birthday")
            # st.write("Je suis né le ", birthday)

        with st.expander("Data format"):
            st.write(
                "The dataset can contain multiple columns but you will need to select a column to be used as dates and a second column containing the metric you wish to forecast. The columns will be renamed as **ds** and **y** to be compliant with Prophet. Even though we are using the default Pandas date parser, the ds (datestamp) column should be of a format expected by Pandas, ideally YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a timestamp. The y column must be numeric."
            )

        st.select_slider(
            "Allure pour la shit",
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


def simulate_race():

    check_differences()

    epreuve = st.session_state["krace_name"]
    current_user = st.session_state["current_user"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Athlete", st.session_state["current_user"])
        st.metric("Natation, secs pour 100m", str(st.session_state["swimming_sX100m"]))
    with col2:
        st.metric("transition nat/cyc, minutes", str(st.session_state["transition_swi2cyc_s"]))
        st.metric("Cyclisme, km par heure", str(st.session_state["cycling_kmXh"]), 22 - 30)
    with col3:
        st.metric("transition cyc/course, minutes", str(st.session_state["transition_cyc2run_s"]))
        st.metric("Course, minutes par km", str(st.session_state["running_sXkm"]), 5)

    athlete = trianer.Athlete(name=current_user, config=athletes_configs[current_user])
    simulation = trianer.Triathlon(epreuve=epreuve, races_configs=races_configs, athlete=athlete, info_box=info_box)
    folium_static(simulation.show_gpx_track())

    st.pyplot(simulation.show_race_details())
    # st.pyplot(simulation.show_race_details(xaxis = "itime"))
    st.pyplot(simulation.show_nutrition())
    # st.dataframe(simulation.show_roadmap(), width=300)
    st.markdown(simulation.show_roadmap().to_html(), unsafe_allow_html=True)


def main():

    if "page" not in st.session_state:

        st.session_state.update(
            {
                "page": "home",
                "weight_kg": athletes_configs[current_user]["weight_kg"],
                "swimming_sX100m": athletes_configs[current_user]["swimming_sX100m"],
                "transition_swi2cyc_s": athletes_configs[current_user]["transition_swi2cyc_s"],
                "cycling_kmXh": athletes_configs[current_user]["cycling_kmXh"],
                "transition_cyc2run_s": athletes_configs[current_user]["transition_cyc2run_s"],
                "running_sXkm": athletes_configs[current_user]["running_sXkm"],
            }
        )

    if not "initialized" in st.session_state:

        with info_box.empty():
            info_box.info(f"⏳ Init session state")
            time.sleep(1)
            info_box.empty()

        st.session_state.current_user = current_user
        st.session_state.krace_name = "Elsassman (L)"

        st.session_state.initialized = True

    athletes_names = athletes_configs.keys()
    races_names = [r for r in races_configs.keys() if "Info" not in r]

    st.sidebar.markdown("""[website](https://trianer.guydegnol.net/)""")
    st.sidebar.selectbox("Athlete", athletes_names, key="current_user")
    st.sidebar.selectbox("Epreuve", races_names, key="krace_name")

    page = st.sidebar.radio("Menu", tuple(PAGES.keys()), format_func=str.capitalize)
    PAGES[page]()


PAGES = {
    "Simuler l'epreuve": simulate_race,
    "Configurer l'epreuve": configure_race,
    "Parametres de performance": configure_performance,
    "Parametres physiologiques": configure_physiology,
}


if __name__ == "__main__":
    load_widget_state()
    main()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Get Cookie:")
        cookie = st.text_input("Cookie", key="0")
        clicked = st.button("Get")
        if clicked:
            value = cookie_manager.get(cookie=cookie)
            st.write(value)
    with c2:
        st.subheader("Set Cookie:")
        cookie = st.text_input("Cookie", key="1")
        val = st.text_input("Value")
        if st.button("Add"):
            cookie_manager.set(cookie, val, expires_at=datetime.datetime(year=2023, month=2, day=2))
    with c3:
        st.subheader("Delete Cookie:")
        cookie = st.text_input("Cookie", key="2")
        if st.button("Delete"):
            cookie_manager.delete(cookie)

    chosen_id = stx.tab_bar(
        data=[
            stx.TabBarItemData(id=1, title="ToDo", description="Tasks to take care of"),
            stx.TabBarItemData(id=2, title="Done", description="Tasks taken care of"),
            stx.TabBarItemData(id=3, title="Overdue", description="Tasks missed out"),
        ],
        default=1,
    )
    st.info(f"{chosen_id=}")

    val = stx.stepper_bar(steps=["Ready", "Get Set", "Go"])
    st.info(f"Phase #{val}")
