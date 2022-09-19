import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import datetime
import trianer
import extra_streamlit_components as stx

from streamlit_folium import folium_static
import os


st.set_option("deprecation.showPyplotGlobalUse", False)


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
all_cookies = cookie_manager.get_all()


def update_cookie(key):
    val = st.session_state[key]
    fval = str(val) if type(val) == datetime.time else val
    cookie_manager.set(key, fval, expires_at=datetime.datetime(year=2023, month=2, day=2))


trianer.set_var_on_change_function(update_cookie)
trianer.set_var_cookies(all_cookies)


info_box = st.empty()


@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True)
def load_races_configs():
    return trianer.Race.load_races_configs()


races_configs = load_races_configs()


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


def configure_physiology():
    st.select_slider(
        "Allure pour la shit",
        options=[f"{m+1}min{s:02.0f}s/100m" for m in range(1, 2) for s in np.linspace(0, 55, 12)],
    )

    st.subheader("Calories")
    st.pyplot(trianer.show_kcalories())

    fig, ax = plt.subplots(figsize=(15, 4))
    for w in [80 * 0.9, 80, 80 * 1.1]:
        kcalories = trianer.get_kcalories(w, discipline="swimming").set_index("speed")["atl"]
        kcalories.plot(ax=ax)
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(15, 4))
    for w in [80 * 0.9, 80, 80 * 1.1]:
        kcalories = trianer.get_kcalories(w, discipline="running").set_index("speed")["atl"]
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


def main():

    with st.expander("Athlete's performances", expanded=True):

        col1, col2, col3 = st.columns(3)
        with col1:
            swimming_sX100m = trianer.get_var_slider("swimming_sX100m")

        with col2:
            cycling_kmXh = trianer.get_var_number("cycling_kmXh")

        with col3:
            running_sXkm = trianer.get_var_slider("running_sXkm")

        col1, col2 = st.columns(2)
        with col1:
            transition_swi2cyc_s = trianer.get_var_slider("transition_swi2cyc_s")

        with col2:
            transition_cyc2run_s = trianer.get_var_slider("transition_cyc2run_s")

    with st.expander("Athlete's details", expanded=True):
        weight_kg = trianer.get_var_number("weight_kg")
        # height_cm = trianer.get_var_number("height_cm")
        # year_of_birth = trianer.get_var_date("year_of_birth")
        # st.date_input("Anniversaire", key="birthday")

    epreuve = "Elsassman (L)"

    athlete = trianer.Athlete(
        name="John Doe",
        config=dict(
            swimming_sX100m=swimming_sX100m,
            cycling_kmXh=cycling_kmXh,
            running_sXkm=running_sXkm,
            transition_swi2cyc_s=transition_swi2cyc_s,
            transition_cyc2run_s=transition_cyc2run_s,
            weight_kg=weight_kg,
        ),
    )

    simulation = trianer.Triathlon(epreuve=epreuve, races_configs=races_configs, athlete=athlete, info_box=info_box)
    with st.expander("Show race gpx track", expanded=False):
        folium_static(simulation.show_gpx_track())

    with st.expander("Show race details", expanded=True):
        xaxis = st.radio("x axis", ["Total distance", "Total time", "Time of day"], horizontal=True)
        st.pyplot(simulation.show_race_details(xaxis=xaxis))
        st.pyplot(simulation.show_nutrition(xaxis=xaxis))
    with st.expander("F&B", expanded=True):
        # st.dataframe(simulation.show_roadmap(), width=300)
        st.markdown(simulation.show_roadmap().to_html(), unsafe_allow_html=True)

    with st.expander("Cookies management", expanded=False):
        st.write(all_cookies)
        st.write(
            dict(
                swimming_sX100m=swimming_sX100m,
                cycling_kmXh=cycling_kmXh,
                running_sXkm=running_sXkm,
                transition_swi2cyc_s=transition_swi2cyc_s,
                transition_cyc2run_s=transition_cyc2run_s,
                weight_kg=weight_kg,
            )
        )
        cookie = st.text_input("Cookie", key="2")
        if st.button("Delete"):
            cookie_manager.delete(cookie)

    # st.sidebar.markdown("""[website](https://trianer.guydegnol.net/)""")
    # st.sidebar.selectbox("Epreuve", races_names, key="krace_name")


if __name__ == "__main__":
    main()
